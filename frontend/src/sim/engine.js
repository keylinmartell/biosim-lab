/**
 * BioSim Lab — Motor de simulacion determinista (sin IA en el bucle).
 *
 * - Integra ODEs simplificadas (Euler, dt fijo en segundos simulados).
 * - Eventos estocasticos (lesiones, reparacion) con PRNG con semilla -> reproducible (Prueba 7).
 * - Emite snapshots para los componentes 3D en cada frame (requestAnimationFrame).
 * - Todas las reglas referencian ids de la KB (R01..R17) para trazabilidad (Prueba 8).
 */

function mulberry32(seed) {
  let a = seed >>> 0
  return () => {
    a = (a + 0x6d2b79f5) | 0
    let t = Math.imul(a ^ (a >>> 15), 1 | a)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

const hill = (x, k, n = 2) => (x <= 0 ? 0 : x ** n / (k ** n + x ** n))
const clamp01 = (x) => Math.min(1, Math.max(0, x))
const LN2 = Math.LN2

export class CellSimulation {
  constructor(kb, plan, { seed = 42 } = {}) {
    this.kb = kb
    this.plan = plan
    this.c = { ...plan.conditions }
    this.s = { ...kb.initial_cell.state }
    this.t = 0
    this.dt = kb.time.default_dt_s
    this.speed = kb.time.default_speed_sim_s_per_real_s
    this.rng = mulberry32(seed)
    this.phase = 'G1'
    this.phaseT = 0
    this.fate = 'pluripotente'
    this.alive = true
    this.pointR = false
    this.p53HighT = 0
    this.divisions = 0
    this.queue = [...(plan.interventions || [])]
    this.log = []
    this.listeners = new Set()
    this._raf = null
    this._last = 0
    this.th = Object.fromEntries(Object.entries(kb.thresholds).map(([k, v]) => [k, v.value]))
    this.genes = kb.genes
  }

  on(fn) { this.listeners.add(fn); return () => this.listeners.delete(fn) }

  event(rule, msg, data = {}) {
    const e = { t: this.t, rule, msg, ...data }
    this.log.push(e)
    return e
  }

  // decaimiento por vida media de la KB
  k(gene) {
    const g = Object.values(this.genes).find((x) => x.product === gene)
    return g ? LN2 / g.protein_half_life_s : LN2 / 36000
  }

  applyIntervention(it) {
    const p = it.params || {}
    switch (it.type) {
      case 'pulso_radiacion': {
        const n = Math.round((p.Gy || 0) * this.th.dsb_per_Gy)
        this.s.dsb += n
        this.event('R01', `Pulso ${p.Gy} Gy -> ${n} DSB`)
        break
      }
      case 'CRISPR_corte':
        this.s.dsb += 1
        this.event('R01', `CRISPR corta ${p.gen || '?'} (${p.reparacion || 'NHEJ'}) — herramienta externa`)
        break
      case 'anadir_factor':
        if (p.factor in this.c) this.c[p.factor] = p.nivel
        this.event('-', `Anadido ${p.factor}=${p.nivel}`)
        break
      case 'retirar_factor':
        if (p.factor in this.c) this.c[p.factor] = 0
        this.event('-', `Retirado ${p.factor}`)
        break
    }
  }

  step() {
    const { s, c, dt, th, rng } = this
    if (!this.alive) return
    this.t += dt
    this.phaseT += dt

    while (this.queue.length && this.queue[0].t_s <= this.t) this.applyIntervention(this.queue.shift())

    // --- Dano espontaneo (R13): Poisson aproximado por paso
    const lesionRate = 0.002 * c.ROS * (c.oxigeno_pct / 5) + 0.0005 * c.UV_J_m2
    if (rng() < lesionRate * dt) s.lesiones_oxidativas += 1

    // --- Reparacion probabilistica con saturacion (R13)
    const repCap = c.eficiencia_reparacion * (1 + 0.5 * (s.GADD45 || 0))
    if (s.lesiones_oxidativas > 0 && rng() < (repCap * dt) / (60 * (1 + s.lesiones_oxidativas / 20))) {
      s.lesiones_oxidativas -= 1
    }
    if (s.dsb > 0 && rng() < (c.eficiencia_reparacion * dt) / (900 * (1 + s.dsb / 30))) {
      s.dsb -= 1
      if (rng() > c.eficiencia_reparacion) this.event('R13', 'DSB reparada con error (NHEJ) -> posible mutacion')
    }

    // --- ATM (R01) y p53/MDM2 (R02)
    const dmg = s.dsb + 0.1 * s.lesiones_oxidativas
    s.ATM += dt * (hill(dmg, 3) - s.ATM) / 120
    const p53ok = c.TP53_funcional ? 1 : 0
    const mdm2Deg = 0.004 * s.MDM2 * (1 - 0.9 * s.ATM)
    s.p53 += dt * p53ok * (0.00012 * (1 + 4 * s.ATM) - mdm2Deg * s.p53 - this.k('p53') * 0.2 * s.p53)
    s.p53 = clamp01(s.p53)

    // --- Dianas de p53 (R03 alta afinidad, R04 baja afinidad)
    const high = hill(s.p53, 0.3, 3), low = hill(s.p53, 0.6, 4)
    s.MDM2 += dt * (0.00005 + 0.0004 * high - this.k('MDM2') * s.MDM2)
    s.p21 += dt * (0.00001 + 0.0005 * high - this.k('p21') * s.p21)
    s.GADD45 = (s.GADD45 || 0) + dt * (0.0004 * high - this.k('GADD45') * (s.GADD45 || 0))
    s.PUMA += dt * (0.0003 * low - this.k('PUMA') * s.PUMA)
    s.BAX += dt * (0.00005 * low - this.k('BAX') * s.BAX)

    const isPSC = s.OCT4 > 0.5
    const apopTh = th.p53_apoptosis * (isPSC ? th.psc_apoptosis_factor : 1)
    if (s.p53 > apopTh) this.p53HighT += dt; else this.p53HighT = Math.max(0, this.p53HighT - dt)
    if (this.p53HighT > th.p53_sustained_s * (isPSC ? 0.5 : 1)) {
      s.caspasa = clamp01(s.caspasa + dt * 0.0005 * (s.PUMA + s.BAX))
      if (s.caspasa > 0.9) {
        this.alive = false
        this.fate = 'apoptosis'
        this.event(isPSC ? 'R17' : 'R04', 'Apoptosis: p53 alto sostenido -> PUMA/BAX -> caspasas')
      }
    }

    // --- Punto R (R05, R06, R07)
    const cdkInhib = hill(s.p21, 0.3)
    s.ciclinaD += dt * (0.0004 * c.mitogenos - this.k('ciclinaD') * s.ciclinaD)
    const kin = (s.ciclinaD + 1.5 * s.ciclinaE) * (1 - cdkInhib)
    s.RbP = clamp01(s.RbP + dt * (0.0008 * kin * (1 - s.RbP) - 0.00015 * s.RbP))
    s.E2F = s.RbP
    s.ciclinaE += dt * (0.0006 * hill(s.E2F, 0.5) - this.k('ciclinaE') * s.ciclinaE)

    // --- Red de pluripotencia y linajes (R08–R12)
    const fgf = c.LIF_o_FGF2, ra = c.acido_retinoico, bmp = c.BMP4, act = c.ActivinaA_WNT
    const core = hill(Math.min(s.OCT4, s.SOX2), 0.4)
    const kp = 1 / 21600
    s.OCT4 += dt * kp * (core * fgf * (1 - ra) * (1 - s.CDX2) - s.OCT4 + 0.05)
    s.SOX2 += dt * kp * (core * (fgf + ra * 0.8) * (1 - s.BRACHYURY) * (1 - s.SOX17) - s.SOX2 + 0.05)
    s.NANOG += dt * (1 / 7200) * (core * fgf * (1 - bmp) - s.NANOG + 0.02 * rng())
    const lk = 1 / 36000, notPluri = 1 - s.NANOG
    s.PAX6 += dt * lk * (2 * notPluri * hill(s.SOX2, 0.4) * (ra + (1 - fgf) * 0.5) * (1 - bmp) - s.PAX6 * 0.2)
    s.BRACHYURY += dt * lk * (notPluri * bmp * hill(act, 0.3) * (1 - hill(act, 0.8, 4)) - s.BRACHYURY * 0.2)
    s.SOX17 += dt * lk * (notPluri * hill(act, 0.7, 4) - s.SOX17 * 0.2)
    s.CDX2 += dt * lk * ((1 - s.OCT4) * bmp * (1 - act) - s.CDX2 * 0.2)
    for (const k of ['OCT4', 'SOX2', 'NANOG', 'PAX6', 'BRACHYURY', 'SOX17', 'CDX2']) s[k] = clamp01(s[k])
    this.updateFate()

    // --- Reportero GFP (separa proteina y fluorescencia)
    const rep = c.reportero_GFP_bajo
    if (rep && rep !== 'ninguno') {
      const drv = rep === 'E2F' ? s.E2F : s[rep] ?? 0
      s.GFP += dt * (0.0002 * drv - this.k('GFP') * s.GFP)
      s.GFP_fluor += dt * ((s.GFP - s.GFP_fluor) / (this.genes.GFP.maturation_s || 3600))
    }

    this.cellCycle()
  }

  updateFate() {
    const s = this.s, th = this.th.lineage_commit
    const lin = { ectodermo: s.PAX6, mesodermo: s.BRACHYURY, endodermo: s.SOX17, trofectodermo: s.CDX2 }
    const [best, val] = Object.entries(lin).sort((a, b) => b[1] - a[1])[0]
    const next = s.OCT4 > 0.5 && s.NANOG > 0.3 ? 'pluripotente' : val > th ? best : 'transicion'
    if (next !== this.fate && this.alive) {
      this.event(next === 'ectodermo' ? 'R09' : next === 'mesodermo' ? 'R10' : next === 'endodermo' ? 'R11' : next === 'trofectodermo' ? 'R12' : 'R08', `Destino: ${this.fate} -> ${next}`)
      this.fate = next
    }
  }

  cellCycle() {
    const s = this.s
    const dur = { G1: this.s.OCT4 > 0.5 ? 9000 : 36000, S: 28800, G2: 10800, M: 3600 }
    if (this.phase === 'G1') {
      if (!this.pointR && s.RbP > this.th.rb_point_r) {
        this.pointR = true
        this.event('R07', 'Punto R cruzado (bucle E2F-ciclinaE biestable)')
      }
      if (this.pointR && this.phaseT > dur.G1) this.go('S')
    } else if (this.phase === 'S' && this.phaseT > dur.S) this.go('G2')
    else if (this.phase === 'G2' && this.phaseT > dur.G2 && s.dsb === 0) this.go('M')
    else if (this.phase === 'M' && this.phaseT > dur.M) {
      this.divisions++
      s.RbP = 0.1; s.ciclinaE = 0.05; this.pointR = false
      this.event('-', `Division #${this.divisions}`)
      this.go('G1')
    }
  }

  go(p) { this.phase = p; this.phaseT = 0 }

  snapshot() {
    return {
      t: this.t, phase: this.phase, fate: this.fate, alive: this.alive,
      pointR: this.pointR, divisions: this.divisions, state: { ...this.s },
      lastEvents: this.log.slice(-8),
    }
  }

  advance(simSeconds) {
    const n = Math.min(Math.ceil(simSeconds / this.dt), 20000)
    for (let i = 0; i < n && this.t < this.plan.duration_s; i++) this.step()
    const snap = this.snapshot()
    this.listeners.forEach((fn) => fn(snap))
    return snap
  }

  start() {
    this._last = performance.now()
    const loop = (now) => {
      const realDt = (now - this._last) / 1000
      this._last = now
      this.advance(realDt * this.speed)
      if (this.alive && this.t < this.plan.duration_s) this._raf = requestAnimationFrame(loop)
    }
    this._raf = requestAnimationFrame(loop)
  }

  stop() { cancelAnimationFrame(this._raf) }
  setSpeed(simSecPerRealSec) { this.speed = simSecPerRealSec }

  export() {
    return {
      kb_version: this.kb.version, model_version: this.kb.model_version,
      plan: this.plan, final: this.snapshot(), log: this.log, evidence: 'simulado',
    }
  }
}
