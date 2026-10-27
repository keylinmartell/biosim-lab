/**
 * atomicDnaGenerator.js — BioSIM Lab
 * Generador paramétrico de ADN Atómico Real fiel 100% al diseño de ADN Prueba (ADNAtomico.vue).
 * Permite confeccionar dinámicamente cualquier secuencia arbitraria (A, T, C, G)
 * manteniendo la escala atómica B-DNA (3.4 Å vertical, 36° twist), radios van der Waals,
 * enlaces covalentes y puentes de hidrógeno Watson-Crick.
 */

import { CANONICAL_TEMPLATES as canonicalTemplates } from './canonicalTemplates.js';

export const ATOMIC_PALETTE = {
  A: 0x8cccff,    // Adenina (celeste suave)
  T: 0x4080f2,    // Timina (azul eléctrico)
  G: 0xbfe0ff,    // Guanina (cian claro)
  C: 0x2659d9,    // Citosina (azul profundo)
  Caz: 0x738cbf,  // Desoxirribosa (azul grisáceo)
  O: 0xa6d9ff,    // Oxígeno (celeste luminoso)
  P: 0x3373e6     // Fósforo (azul cobalto)
};

export const ATOMIC_RADII = {
  C: 0.42,
  N: 0.42,
  O: 0.42,
  P: 0.55
};

export const COMPLEMENT_MAP = {
  A: 'T',
  T: 'A',
  C: 'G',
  G: 'C'
};

const TWIST_STEP = 36 * (Math.PI / 180); // 36 grados = 2 * PI / 10
const VERTICAL_STEP = 3.4; // 3.4 Angstroms por par de bases (B-DNA)

/**
 * Genera la estructura atómica completa (átomos y enlaces) para cualquier secuencia.
 * @param {string} rawSequence Secuencia de bases (ej: 'GATTACA')
 * @param {boolean} centerVertical Si se debe centrar la hélice en Z=0 (para rotación perfecta)
 * @returns {Object} { atoms, bonds, pairs, totalAtoms, totalBonds }
 */
export function generateAtomicDNA(rawSequence, centerVertical = true) {
  const seq = (rawSequence || '').toUpperCase().replace(/[^ATCG]/g, '') || 'ATCG';
  const N = seq.length;
  const zCenter = centerVertical ? ((N - 1) * VERTICAL_STEP) / 2 : 0;

  const atoms = [];
  const bonds = [];
  const pairs = [];

  let atomOffset = 0;
  const pairOffsets = [];

  for (let i = 0; i < N; i++) {
    const base = seq[i];
    const tmpl = canonicalTemplates[base] || canonicalTemplates['A'];
    const compBase = COMPLEMENT_MAP[base] || 'T';

    const angle = i * TWIST_STEP;
    const zOffset = i * VERTICAL_STEP - zCenter;
    const cos = Math.cos(angle);
    const sin = Math.sin(angle);

    const startIdx = atomOffset;
    const s1Count = tmpl.s1Len;
    const s2Count = tmpl.s2Len;

    pairOffsets.push({ startIdx, tmpl });

    // 1. Átomos del par de bases (Hebra 1 y Hebra 2 complementaria)
    tmpl.atoms.forEach((a, localIdx) => {
      const rx = a[0] * cos - a[1] * sin;
      const ry = a[0] * sin + a[1] * cos;
      const rz = a[2] + zOffset;
      const isStrand1 = localIdx < s1Count;

      atoms.push([
        Math.round(rx * 1000) / 1000,
        Math.round(ry * 1000) / 1000,
        Math.round(rz * 1000) / 1000,
        a[3], // Elemento: 'C', 'N', 'O', 'P'
        a[4], // Grupo químico: 'A', 'T', 'C', 'G', 'Caz', 'O', 'P'
        i,    // Posición del par en la secuencia (0..N-1)
        isStrand1 ? 1 : 2 // Hebra 1 o Hebra 2
      ]);
      atomOffset++;
    });

    const endIdx = atomOffset - 1;

    // 2. Enlaces covalentes internos del par
    tmpl.covalentBonds.forEach(b => {
      bonds.push([b[0] + startIdx, b[1] + startIdx, 'bond', i]);
    });

    // 3. Puentes de hidrógeno Watson-Crick (tipo 'h')
    tmpl.hBonds.forEach(b => {
      bonds.push([b[0] + startIdx, b[1] + startIdx, 'h', i]);
    });

    // 4. Enlaces fosfodiéster con el par anterior (i - 1)
    if (i > 0) {
      const prev = pairOffsets[i - 1];
      const cur = pairOffsets[i];

      // Hebra 1: 3'-O del azúcar anterior -> Fósforo (P) actual
      const p1Donor = prev.startIdx + prev.tmpl.s1DonorO;
      const p1Acceptor = cur.startIdx + cur.tmpl.s1AcceptorP;
      bonds.push([p1Donor, p1Acceptor, 'bond', i]);

      // Hebra 2 (antiparalela): 3'-O del azúcar actual -> Fósforo (P) anterior
      const p2Donor = cur.startIdx + cur.tmpl.s2DonorO;
      const p2Acceptor = prev.startIdx + prev.tmpl.s2AcceptorP;
      bonds.push([p2Donor, p2Acceptor, 'bond', i]);
    }

    // 5. Metadatos del par para la lógica reactiva y selección
    pairs.push({
      index: i,
      base1: base,
      base2: compBase,
      hBondsCount: (base === 'C' || base === 'G') ? 3 : 2,
      startAtomIdx: startIdx,
      endAtomIdx: endIdx,
      centerZ: zOffset
    });
  }

  return {
    atoms,
    bonds,
    pairs,
    totalAtoms: atoms.length,
    totalBonds: bonds.length,
    sequence: seq
  };
}
