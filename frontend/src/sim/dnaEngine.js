/**
 * BioSim Lab — Motor de ADN/expresion (Fase 2: Modulos A-F). Determinista, sin IA.
 * Implementa: ficha de gen (R18), transcripcion por hebra molde (R19), validacion (R20),
 * caperuza (R21), splicing GU-AG (R22), poli-A (R23), traduccion (R24), variantes (R25-27).
 */

export const CODE = (() => {
  const b = 'UCAG', aa = 'FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG'
  const t = {}
  let i = 0
  for (const x of b) for (const y of b) for (const z of b) t[x + y + z] = aa[i++]
  return t
})()

export const AA3 = { A: 'Ala', R: 'Arg', N: 'Asn', D: 'Asp', C: 'Cys', Q: 'Gln', E: 'Glu', G: 'Gly', H: 'His', I: 'Ile', L: 'Leu', K: 'Lys', M: 'Met', F: 'Phe', P: 'Pro', S: 'Ser', T: 'Thr', W: 'Trp', Y: 'Tyr', V: 'Val', '*': 'STOP' }

const COMP = { A: 'T', T: 'A', G: 'C', C: 'G' }
export const comp = (s) => s.split('').map((c) => COMP[c] || 'N').join('')
export const revcomp = (s) => comp(s).split('').reverse().join('')
export const validate = (s) => {
  const bad = [...s].map((c, i) => (/[ACGT]/.test(c) ? -1 : i)).filter((i) => i >= 0)
  return { ok: s.length > 0 && bad.length === 0, bad }
}

/** Construye el locus en la hebra directa (5'->3') con coordenadas de cada region. */
export function buildLocus(g) {
  const coding = g.parts.map((p) => p.seq).join('')
  const L = coding.length
  let pos = 0
  const regions = g.parts.map((p) => {
    const r = { type: p.type, seq: p.seq, cStart: pos, cEnd: pos + p.seq.length }
    pos += p.seq.length
    return r
  })
  const fwd = g.strand === '+' ? coding : revcomp(coding)
  // coordenadas en hebra directa
  for (const r of regions) {
    if (g.strand === '+') { r.start = r.cStart; r.end = r.cEnd }
    else { r.start = L - r.cEnd; r.end = L - r.cStart }
  }
  const prom = regions.find((r) => r.type === 'promoter')
  const tssC = prom.cEnd
  return {
    gene: g, forward: fwd, reverse: comp(fwd), length: L, regions,
    tss: g.strand === '+' ? tssC : L - tssC - 1,
    templateStrand: g.strand === '+' ? 'reverse (-)' : 'forward (+)',
  }
}

/** Expresion completa ADN -> ARN -> proteina con registro de pasos. */
export function express(locus, variant = null) {
  const g = locus.gene
  const log = []
  let coding = g.parts.map((p) => p.seq).join('')
  if (variant) coding = coding.slice(0, variant.pos) + variant.base + coding.slice(variant.pos + 1)
  const v = validate(coding)
  if (!v.ok) {
    log.push({ rule: 'R20', msg: `Secuencia invalida en posiciones ${v.bad.join(',')}: no resuelta` })
    return { valid: false, log }
  }
  const prom = locus.regions.find((r) => r.type === 'promoter')
  const tx = coding.slice(prom.cEnd) // region transcrita (desde TSS)
  // R19: molde = complementaria de la codificante, leida 3'->5'
  const template35 = comp(tx)
  const preRNA = template35.split('').map((c) => ({ A: 'U', T: 'A', G: 'C', C: 'G' }[c])).join('')
  log.push({ rule: 'R19', msg: `Hebra molde ${locus.templateStrand} leida 3'->5'; pre-ARNm 5'->3' (${preRNA.length} nt)` })
  log.push({ rule: 'R21', msg: "Caperuza 5' anadida (m7G, propiedad)" })
  // R22 splicing
  const introns = []
  let mature = ''
  let p = 0
  const txRegions = locus.regions.filter((r) => r.type !== 'promoter')
  const varIdx = variant ? variant.pos : -1
  for (const r of txRegions) {
    const seq = preRNA.slice(p, p + r.seq.length)
    p += r.seq.length
    if (r.type === 'intron') {
      const okSig = seq.startsWith('GU') && seq.endsWith('AG')
      introns.push({ seq, okSig })
      log.push({ rule: 'R22', msg: okSig ? `Intron ${seq.slice(0, 2)}...${seq.slice(-2)} retirado (${seq.length} nt)` : 'Senales de splicing ausentes: intron retenido' })
      if (!okSig) mature += seq
    } else mature += seq
  }
  const polyA = mature.includes('AAUAAA')
  if (polyA) log.push({ rule: 'R23', msg: 'Senal AAUAAA -> corte y cola poli-A' })
  // R24 traduccion
  const start = mature.indexOf('AUG')
  const codons = []
  let protein = ''
  let stopFound = false
  if (start < 0) log.push({ rule: 'R24', msg: 'Sin AUG: no se traduce' })
  else {
    for (let i = start; i + 3 <= mature.length; i += 3) {
      const c = mature.slice(i, i + 3)
      const a = CODE[c]
      codons.push({ c, a })
      if (a === '*') { stopFound = true; break }
      protein += a
    }
    log.push({ rule: 'R24', msg: stopFound ? `Traduccion AUG..STOP: ${protein.length} aa` : 'Sin codon STOP en marco: secuencia incompleta' })
  }
  return {
    valid: true, coding, tx, template35, preRNA, introns, mature, polyA, cap: true,
    codons, protein, protein3: [...protein].map((a) => AA3[a]).join('-'), stopFound, log, varIdx,
  }
}

/** Variantes didacticas automaticas sobre el codon 2 del CDS (Modulo F). */
export function didacticVariants(locus) {
  const g = locus.gene
  const exon1 = locus.regions.find((r) => r.type === 'exon')
  const pos = exon1.cStart + 3 // primera base del codon 2
  const ref = g.parts.map((x) => x.seq).join('')
  const codon = ref.slice(pos, pos + 3).replace(/T/g, 'U')
  const refAA = CODE[codon]
  const out = []
  for (let k = 0; k < 3; k++) {
    for (const b of 'ACGT') {
      const nc = codon.split(''); nc[k] = b === 'T' ? 'U' : b
      const c2 = nc.join('')
      if (c2 === codon) continue
      const a2 = CODE[c2]
      const kind = a2 === refAA ? 'sinonima' : a2 === '*' ? 'nonsense' : 'missense'
      if (!out.find((o) => o.kind === kind)) out.push({ kind, pos: pos + k, base: b, codonRef: codon, codonVar: c2, aaRef: refAA, aaVar: a2, rule: { sinonima: 'R25', missense: 'R26', nonsense: 'R27' }[kind] })
    }
  }
  return out
}

/** Pruebas de aceptacion Fase 2 (1-3, 7 + orientacion). */
export function acceptanceTests(locus) {
  const r = express(locus)
  const ex = { ...locus, gene: { ...locus.gene, parts: [{ type: 'promoter', seq: '' }, { type: 'exon', seq: 'ATGGAATTTTGA' }] } }
  const doc = express(buildLocus(ex.gene))
  return [
    { id: 'Prueba 1', name: 'Transcripcion por hebra molde', ok: r.preRNA === r.tx.replace(/T/g, 'U') },
    { id: 'Prueba 2', name: 'Splicing exacto (exon1+exon2)', ok: r.introns.every((i) => i.okSig) && r.mature.length === r.preRNA.length - r.introns.reduce((s, i) => s + i.seq.length, 0) },
    { id: 'Prueba 3', name: "Doc: AUG-GAA-UUU-UGA -> Met-Glu-Phe", ok: doc.protein === 'MEF' && doc.stopFound },
    { id: 'Orient.', name: `Gen en hebra ${locus.gene.strand}`, ok: (locus.gene.strand === '+' ? locus.forward : revcomp(locus.forward)) === r.coding },
    { id: 'Prueba 7', name: 'Reproducibilidad', ok: JSON.stringify(express(locus).protein) === JSON.stringify(r.protein) },
  ]
}

/** Elige el gen activo segun el estado celular (reglas R03/R28, R08-R12). */
export function pickActiveGene(kb, snap) {
  const map = kb.genome.lineage_gene
  const s = snap.state
  if (s.dsb > 0 || s.p53 > 0.3) return { id: map.dano, level: Math.min(1, s.p21 || 0), why: 'Dano en ADN: p53 activa CDKN1A (R28)', p53Bound: s.p53 > 0.2 }
  const f = snap.fate === 'transicion' || snap.fate === 'apoptosis' ? 'pluripotente' : snap.fate
  const prod = { pluripotente: 'OCT4', ectodermo: 'PAX6', endodermo: 'SOX17', mesodermo: 'BRACHYURY', trofectodermo: 'CDX2' }[f]
  return { id: map[f], level: s[prod] ?? 0, why: `Especificacion: ${f} -> ${map[f]}`, p53Bound: false }
}
