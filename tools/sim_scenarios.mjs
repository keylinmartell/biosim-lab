import { CellSimulation } from '../frontend/src/sim/engine.js'
import fs from 'fs'
globalThis.performance ??= Date
const kb = JSON.parse(fs.readFileSync('backend/app/knowledge/biosim_kb.json'))
const base = Object.fromEntries(Object.entries(kb.conditions_schema).map(([k, v]) => [k, v.default]))
const run = (name, cond, inter = []) => {
  const s = new CellSimulation(kb, { conditions: { ...base, ...cond }, interventions: inter, duration_s: 432000 })
  for (let i = 0; i < 30; i++) s.advance(14400)
  const f = s.snapshot()
  console.log(name, '|', f.fate, f.alive, 'div', f.divisions, 'p53', f.state.p53.toFixed(2), 'OCT4', f.state.OCT4.toFixed(2), 'PAX6', f.state.PAX6.toFixed(2), 'SOX17', f.state.SOX17.toFixed(2))
}
run('control', {})
run('2Gy', {}, [{ t_s: 3600, type: 'pulso_radiacion', params: { Gy: 2 } }])
run('8Gy', {}, [{ t_s: 3600, type: 'pulso_radiacion', params: { Gy: 8 } }])
run('8Gy p53-', { TP53_funcional: false }, [{ t_s: 3600, type: 'pulso_radiacion', params: { Gy: 8 } }])
run('AR', { acido_retinoico: 1, LIF_o_FGF2: 0 })
run('Activina', { ActivinaA_WNT: 1, LIF_o_FGF2: 0 })
