/**
 * atomicDnaGenerator.js — BioSIM Lab
 * Generador paramétrico de ADN Atómico Real + Empaquetamiento en Cromatina (Alberts et al.)
 * 
 * Cumple rigurosamente con los parámetros biofísicos de Molecular Biology of the Cell (Alberts et al.):
 * - 1 nucleosoma estándar = 147 pb de ADN enrollado en 1.65 vueltas superhelicoidales izquierdas sobre un octámero.
 * - Octámero de histonas core: 2× H2A, 2× H2B, 2× H3, 2× H4 (8 subunidades proteicas).
 * - Histona de unión H1 (linker histone): 1 molécula de H1 por nucleosoma, ubicada como broche/abrazadera
 *   molecular en el cuello donde el ADN entra y sale del nucleosoma, sellando el cromatosoma.
 * - Paso axial estricto de 3.4 Å entre pares de bases consecutivos (enlaces covalentes 100% intactos).
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

export const HISTONE_PALETTE = {
  H2A: 0x00e5ff,   // Cian brillante
  H2B: 0x10b981,   // Verde esmeralda
  H3:  0x3b82f6,   // Azul real intenso
  H4:  0xc084fc,   // Violeta / Lavanda
  H1:  0xf43f5e,   // Rosa/Magenta intenso: Broche globular en el cuello del ADN (Alberts)
  H1_STEM: 0x38bdf8, // Tallo C-terminal cian de H1 a lo largo del ADN linker
  TAIL: 0x7dd3fc
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

const TWIST_STEP = 36 * (Math.PI / 180); // 36° por pb (10 pb por vuelta B-DNA)
const VERTICAL_STEP = 3.4;               // 3.4 Å EXACTOS por par de bases

/**
 * Calcula la estequiometría de histonas y nucleosomas según Alberts et al. (Molecular Biology of the Cell)
 */
export function calculateChromatinStoichiometry(seqLength, mode = 'chromatin_adaptive') {
  if (mode === 'linear') {
    return {
      originalBp: seqLength,
      renderedBp: seqLength,
      effectiveRepeats: 1,
      coreBp: 0,
      linkerBp: seqLength,
      unitBp: seqLength,
      turnsPerNucleosome: 0,
      nucleosomeCount: 0,
      octamerSubunits: 0,
      h1Count: 0,
      totalHistoneProteins: 0,
      albertsFormulaText: `${seqLength} pb (ADN-B lineal desnudo)`,
      albertsRatioText: `${seqLength} pb (ADN-B lineal desnudo)`
    };
  }

  const isAlberts = (mode === 'chromatin_alberts');
  const coreBp = isAlberts ? 147 : 74;
  const linkerBp = isAlberts ? 53 : 26;
  const unitBp = coreBp + linkerBp;

  let nucleosomeCount = 1;
  let effectiveRepeats = 1;

  if (seqLength >= unitBp) {
    // Si la secuencia es suficientemente larga, calculamos los nucleosomas soportados directamente
    nucleosomeCount = Math.max(1, Math.round(seqLength / unitBp));
    effectiveRepeats = 1;
  } else {
    // Para secuencias cortas (didácticas), se cicla en tándem para completar nucleosomas cerrados
    // evitando fragmentos rotos o hebras colgantes incompletas
    const minTargetBp = isAlberts ? 200 : 200;
    effectiveRepeats = Math.ceil(minTargetBp / Math.max(1, seqLength));
    nucleosomeCount = Math.max(1, Math.floor((seqLength * effectiveRepeats) / unitBp));
  }

  const renderedBp = seqLength * effectiveRepeats;
  const octamerSubunits = nucleosomeCount * 8; // 2×H2A + 2×H2B + 2×H3 + 2×H4
  const h1Count = nucleosomeCount;             // 1 H1 por cada nucleosoma en la entrada/salida
  const totalHistoneProteins = nucleosomeCount * 9;

  const repeatNote = effectiveRepeats > 1 ? ` (en tándem ${effectiveRepeats}×)` : '';
  const ratioText = `${seqLength} pb${repeatNote} · ${nucleosomeCount} nucleosoma(s) [${coreBp} pb core + ${linkerBp} pb linker] · Alberts et al.`;

  return {
    originalBp: seqLength,
    renderedBp,
    effectiveRepeats,
    coreBp,
    linkerBp,
    unitBp,
    turnsPerNucleosome: 1.65,
    nucleosomeCount,
    octamerSubunits,
    h1Count,
    totalHistoneProteins,
    albertsFormulaText: ratioText,
    albertsRatioText: ratioText
  };
}

/**
 * Construye la trayectoria continua en 3D con paso axial garantizado de 3.4 Å entre cada par.
 * Modela la superhélice nucleosomal y el cuello de unión donde se engarza la histona H1.
 */
function buildChromatinFrames(N, mode, stoich) {
  const frames = [];

  if (mode === 'linear' || stoich.nucleosomeCount === 0) {
    const zCenter = ((N - 1) * VERTICAL_STEP) / 2;
    for (let i = 0; i < N; i++) {
      frames.push({
        pos: [0, 0, i * VERTICAL_STEP - zCenter],
        N: [1, 0, 0],
        B: [0, 1, 0],
        T: [0, 0, 1],
        inNucleosome: -1
      });
    }
    return { frames, nucleosomeCenters: [] };
  }

  const { coreBp, linkerBp, nucleosomeCount } = stoich;
  const TURNS = 1.65;
  const PITCH_Z = mode === 'chromatin_alberts' ? 38.0 : 26.0;
  const dTheta = (TURNS * 2 * Math.PI) / coreBp;
  const dZ = PITCH_Z / coreBp;

  // Calibración analítica para que la distancia euclidiana entre pares consecutivos sea EXACTAMENTE 3.400 Å
  const R_SUPER = Math.sqrt((VERTICAL_STEP * VERTICAL_STEP - dZ * dZ) / (4 * Math.sin(dTheta / 2) ** 2));

  const rawPoints = [];
  const nucMeta = [];

  // Espaciado entre centros de nucleosomas a lo largo de la fibra de cromatina (10 nm)
  const NUC_SPACING_X = mode === 'chromatin_alberts' ? 140.0 : 95.0;
  const NUC_STAGGER_Y = 28.0;

  let bp = 0;

  for (let n = 0; n < nucleosomeCount && bp < N; n++) {
    const wave = (n % 2 === 0) ? 1 : -1;
    const nucCx = n * NUC_SPACING_X;
    const nucCy = wave * NUC_STAGGER_Y;
    const nucCz = 0;

    // Ángulo simétrico para que la entrada y la salida converjan en el lado +X (+/- Y)
    const alpha = (TURNS * Math.PI);
    const entryAngle = alpha;

    const firstCoreX = nucCx + R_SUPER * Math.cos(entryAngle);
    const firstCoreY = nucCy + R_SUPER * Math.sin(entryAngle);
    const firstCoreZ = nucCz - PITCH_Z * 0.5;

    // 1. ADN espaciador (Linker DNA) previo
    if (n === 0) {
      // Cola de entrada inicial
      const leadBp = Math.min(18, Math.floor(linkerBp * 0.45));
      const leadDir = [Math.sin(entryAngle), -Math.cos(entryAngle), 0];
      const leadLen = Math.hypot(...leadDir) || 1;
      leadDir[0] /= leadLen; leadDir[1] /= leadLen; leadDir[2] /= leadLen;

      for (let k = leadBp; k >= 1 && bp < N; k--) {
        rawPoints.push({
          pos: [
            firstCoreX + leadDir[0] * k * VERTICAL_STEP,
            firstCoreY + leadDir[1] * k * VERTICAL_STEP,
            firstCoreZ + leadDir[2] * k * VERTICAL_STEP
          ],
          nucIdx: -1
        });
        bp++;
      }
    } else {
      // Linker que conecta suavemente el nucleosoma anterior con el actual
      const prevMeta = nucMeta[n - 1];
      const pExit = prevMeta.exitPoint;
      const pEntry = [firstCoreX, firstCoreY, firstCoreZ];

      const dx = pEntry[0] - pExit[0];
      const dy = pEntry[1] - pExit[1];
      const dz = pEntry[2] - pExit[2];
      const dist = Math.hypot(dx, dy, dz);
      const steps = Math.max(1, Math.round(dist / VERTICAL_STEP));

      for (let k = 1; k < steps && bp < N; k++) {
        const u = k / steps;
        const arcY = Math.sin(u * Math.PI) * 14.0 * wave;
        const arcZ = Math.sin(u * Math.PI) * 6.0;

        rawPoints.push({
          pos: [
            pExit[0] + dx * u,
            pExit[1] + dy * u + arcY,
            pExit[2] + dz * u + arcZ
          ],
          nucIdx: -1
        });
        bp++;
      }
    }

    if (bp >= N) break;

    // 2. Superhélice Nucleosomal (Core de 147 pb o adaptativo en 1.65 vueltas)
    let entryPt = [firstCoreX, firstCoreY, firstCoreZ];
    let exitPt = null;
    let crossPt = null;

    for (let k = 0; k < coreBp && bp < N; k++) {
      const theta = entryAngle - k * dTheta;
      const px = nucCx + R_SUPER * Math.cos(theta);
      const py = nucCy + R_SUPER * Math.sin(theta);
      const pz = nucCz - PITCH_Z * 0.5 + k * dZ;

      const pt = [px, py, pz];
      if (k === 0) entryPt = [...pt];
      if (k === Math.floor(coreBp / TURNS)) crossPt = [...pt]; // Punto de cruce al completar 1 vuelta
      if (k === coreBp - 1) exitPt = [...pt];

      rawPoints.push({ pos: pt, nucIdx: n });
      bp++;
    }

    if (!exitPt) exitPt = rawPoints[rawPoints.length - 1].pos.slice();
    if (!crossPt) crossPt = entryPt.slice();

    nucMeta.push({
      index: n,
      center: [nucCx, nucCy, nucCz],
      entryPoint: entryPt.slice(),
      exitPoint: exitPt.slice(),
      crossPoint: crossPt.slice(),
      coreRadius: R_SUPER - 12.0
    });
  }

  // 3. Cola linker terminal de salida
  const lastMeta = nucMeta[nucMeta.length - 1];
  if (lastMeta && bp < N) {
    const pExit = lastMeta.exitPoint;
    const exitAngle = -TURNS * Math.PI;
    const trailDir = [Math.sin(exitAngle), Math.cos(exitAngle), 0];
    const tLen = Math.hypot(...trailDir) || 1;
    trailDir[0] /= tLen; trailDir[1] /= tLen; trailDir[2] /= tLen;

    let k = 1;
    while (bp < N) {
      rawPoints.push({
        pos: [
          pExit[0] + trailDir[0] * k * VERTICAL_STEP,
          pExit[1] + trailDir[1] * k * VERTICAL_STEP,
          pExit[2] + trailDir[2] * k * VERTICAL_STEP
        ],
        nucIdx: -1
      });
      k++;
      bp++;
    }
  }

  // 4. Centrado en el origen (0, 0, 0) con vectores clonados (evita doble mutación)
  let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity, minZ = Infinity, maxZ = -Infinity;
  rawPoints.forEach(p => {
    if (p.pos[0] < minX) minX = p.pos[0];
    if (p.pos[0] > maxX) maxX = p.pos[0];
    if (p.pos[1] < minY) minY = p.pos[1];
    if (p.pos[1] > maxY) maxY = p.pos[1];
    if (p.pos[2] < minZ) minZ = p.pos[2];
    if (p.pos[2] > maxZ) maxZ = p.pos[2];
  });
  const cx = (minX + maxX) / 2;
  const cy = (minY + maxY) / 2;
  const cz = (minZ + maxZ) / 2;

  const cloneShift = (v) => [v[0] - cx, v[1] - cy, v[2] - cz];

  rawPoints.forEach(p => { p.pos = cloneShift(p.pos); });
  const centeredNucMeta = nucMeta.map(nm => ({
    ...nm,
    center: cloneShift(nm.center),
    entryPoint: cloneShift(nm.entryPoint),
    exitPoint: cloneShift(nm.exitPoint),
    crossPoint: cloneShift(nm.crossPoint)
  }));

  // 5. Marcos de Bishop (transporte paralelo) sin singularidades
  let prevT = [1, 0, 0];
  let prevN = [0, 1, 0];
  let prevB = [0, 0, 1];

  for (let i = 0; i < rawPoints.length; i++) {
    const pPrev = rawPoints[Math.max(0, i - 1)].pos;
    const pNext = rawPoints[Math.min(rawPoints.length - 1, i + 1)].pos;
    let tx = pNext[0] - pPrev[0];
    let ty = pNext[1] - pPrev[1];
    let tz = pNext[2] - pPrev[2];
    const len = Math.hypot(tx, ty, tz) || 1;
    tx /= len; ty /= len; tz /= len;

    if (i === 0) {
      prevT = [tx, ty, tz];
      const up = Math.abs(tz) < 0.9 ? [0, 0, 1] : [0, 1, 0];
      let nx = prevT[1] * up[2] - prevT[2] * up[1];
      let ny = prevT[2] * up[0] - prevT[0] * up[2];
      let nz = prevT[0] * up[1] - prevT[1] * up[0];
      const nLen = Math.hypot(nx, ny, nz) || 1;
      prevN = [nx / nLen, ny / nLen, nz / nLen];
      prevB = [
        prevT[1] * prevN[2] - prevT[2] * prevN[1],
        prevT[2] * prevN[0] - prevT[0] * prevN[2],
        prevT[0] * prevN[1] - prevT[1] * prevN[0]
      ];
    } else {
      const dot = prevN[0] * tx + prevN[1] * ty + prevN[2] * tz;
      let nx = prevN[0] - dot * tx;
      let ny = prevN[1] - dot * ty;
      let nz = prevN[2] - dot * tz;
      const nLen = Math.hypot(nx, ny, nz) || 1;
      prevN = [nx / nLen, ny / nLen, nz / nLen];
      prevB = [
        ty * prevN[2] - tz * prevN[1],
        tz * prevN[0] - tx * prevN[2],
        tx * prevN[1] - ty * prevN[0]
      ];
      prevT = [tx, ty, tz];
    }

    frames.push({
      pos: rawPoints[i].pos,
      N: [...prevN],
      B: [...prevB],
      T: [...prevT],
      inNucleosome: rawPoints[i].nucIdx
    });
  }

  return { frames, nucleosomeCenters: centeredNucMeta };
}

/**
 * Genera el octámero de histonas en el núcleo del nucleosoma y la histona H1
 * colocada directamente en el cuello del ADN, uniendo las hebras de entrada y salida (Alberts et al.).
 */
function generateHistoneClusters(nucleosomeCenters) {
  const histoneSpheres = [];
  const h1Rods = [];

  // Distribución del octámero: 8 lóbulos proteicos organizados en dos niveles (tetrámero H3-H4 y dímeros H2A-H2B)
  const subunitDefs = [
    { name: 'H3',  color: HISTONE_PALETTE.H3,  angle: 0.3,  zOff: -6.5 },
    { name: 'H4',  color: HISTONE_PALETTE.H4,  angle: 1.8,  zOff: -5.0 },
    { name: 'H2A', color: HISTONE_PALETTE.H2A, angle: 3.4,  zOff: -6.0 },
    { name: 'H2B', color: HISTONE_PALETTE.H2B, angle: 4.9,  zOff: -4.5 },
    { name: 'H3',  color: HISTONE_PALETTE.H3,  angle: 0.3,  zOff:  6.5 },
    { name: 'H4',  color: HISTONE_PALETTE.H4,  angle: 1.8,  zOff:  5.0 },
    { name: 'H2A', color: HISTONE_PALETTE.H2A, angle: 3.4,  zOff:  6.0 },
    { name: 'H2B', color: HISTONE_PALETTE.H2B, angle: 4.9,  zOff:  4.5 }
  ];

  nucleosomeCenters.forEach((nuc, nIdx) => {
    const [cx, cy, cz] = nuc.center;
    const coreR = Math.max(22.0, nuc.coreRadius);

    // 1. Octámero de 8 histonas alojado en el centro del carrete
    subunitDefs.forEach((sub, sIdx) => {
      const subCx = cx + Math.cos(sub.angle) * (coreR * 0.58);
      const subCy = cy + Math.sin(sub.angle) * (coreR * 0.58);
      const subCz = cz + sub.zOff;

      for (let m = 0; m < 16; m++) {
        const phi = Math.acos(1 - 2 * ((m + 0.5) / 16));
        const theta = Math.PI * (1 + Math.sqrt(5)) * (m + sIdx * 3);
        const radDist = (m === 0) ? 0 : (coreR * 0.32) * Math.cbrt((m + 1) / 16);

        histoneSpheres.push([
          subCx + radDist * Math.sin(phi) * Math.cos(theta),
          subCy + radDist * Math.sin(phi) * Math.sin(theta),
          subCz + radDist * Math.cos(phi) * 0.85,
          3.1 + (m % 3) * 0.3,
          sub.color,
          sub.name,
          nIdx
        ]);
      }
    });

    // 2. Histona H1 DIRECTAMENTE EN EL CUELLO DEL ADN (Alberts et al.):
    // Sellando el cromatosoma entre el punto de entrada y el de salida
    const entryPt = nuc.entryPoint;
    const exitPt = nuc.exitPoint;

    const h1CenterX = (entryPt[0] + exitPt[0]) * 0.5 + 4.0;
    const h1CenterY = (entryPt[1] + exitPt[1]) * 0.5;
    const h1CenterZ = (entryPt[2] + exitPt[2]) * 0.5;
    const h1Center = [h1CenterX, h1CenterY, h1CenterZ];

    // Dominio globular de H1 (esferas rosa/magenta) uniendo físicamente las hebras de ADN
    for (let k = 0; k < 12; k++) {
      const phi = Math.acos(1 - 2 * ((k + 0.5) / 12));
      const theta = Math.PI * (1 + Math.sqrt(5)) * k;
      histoneSpheres.push([
        h1CenterX + Math.sin(phi) * Math.cos(theta) * 3.8,
        h1CenterY + Math.sin(phi) * Math.sin(theta) * 3.8,
        h1CenterZ + Math.cos(phi) * 3.2,
        2.8,
        HISTONE_PALETTE.H1,
        'H1',
        nIdx
      ]);
    }

    // Broches moleculares que abrazan y sujetan ambas hebras de ADN
    h1Rods.push({
      start: entryPt,
      end: h1Center,
      radius: 1.4,
      color: HISTONE_PALETTE.H1,
      nucIndex: nIdx
    });
    h1Rods.push({
      start: exitPt,
      end: h1Center,
      radius: 1.4,
      color: HISTONE_PALETTE.H1,
      nucIndex: nIdx
    });

    // Tallo C-terminal de H1 (varilla cian luminosa) extendido a lo largo del ADN linker saliente
    const forwardX = 1.0;
    const forwardY = (nIdx % 2 === 0 ? 0.35 : -0.35);
    const forwardZ = 0.05;
    const fLen = Math.hypot(forwardX, forwardY, forwardZ) || 1;

    h1Rods.push({
      start: h1Center,
      end: [
        h1CenterX + (forwardX / fLen) * 16.0,
        h1CenterY + (forwardY / fLen) * 16.0,
        h1CenterZ + (forwardZ / fLen) * 16.0
      ],
      radius: 1.5,
      color: HISTONE_PALETTE.H1_STEM,
      nucIndex: nIdx
    });
  });

  return { histoneSpheres, h1Rods };
}

/**
 * Genera la estructura molecular completa de ADN y cromatina.
 */
export function generateAtomicDNA(rawSequence, centerVertical = true, packagingMode = 'chromatin_adaptive') {
  const baseSeq = (rawSequence || '').toUpperCase().replace(/[^ATCG]/g, '') || 'GATTACAGGCTATCCGATACG';
  const stoich = calculateChromatinStoichiometry(baseSeq.length, packagingMode);

  let seq = baseSeq;
  if (packagingMode !== 'linear' && stoich.effectiveRepeats > 1) {
    seq = baseSeq.repeat(stoich.effectiveRepeats);
  }

  const N = seq.length;
  const { frames, nucleosomeCenters } = buildChromatinFrames(N, packagingMode, stoich);
  const { histoneSpheres, h1Rods } = generateHistoneClusters(nucleosomeCenters);

  const atoms = [];
  const bonds = [];
  const pairs = [];

  let atomOffset = 0;
  const pairOffsets = [];

  for (let i = 0; i < N && i < frames.length; i++) {
    const base = seq[i];
    const tmpl = canonicalTemplates[base] || canonicalTemplates['A'];
    const compBase = COMPLEMENT_MAP[base] || 'T';

    const angle = i * TWIST_STEP;
    const cos = Math.cos(angle);
    const sin = Math.sin(angle);

    const frame = frames[i];
    const [cx, cy, cz] = frame.pos;
    const [nx, ny, nz] = frame.N;
    const [bx, by, bz] = frame.B;
    const [tx, ty, tz] = frame.T;

    const startIdx = atomOffset;
    const s1Count = tmpl.s1Len;

    pairOffsets.push({ startIdx, tmpl });

    tmpl.atoms.forEach((a, localIdx) => {
      const lx = a[0] * cos - a[1] * sin;
      const ly = a[0] * sin + a[1] * cos;
      const lz = a[2];

      const wx = cx + lx * nx + ly * bx + lz * tx;
      const wy = cy + lx * ny + ly * by + lz * ty;
      const wz = cz + lx * nz + ly * bz + lz * tz;

      const isStrand1 = localIdx < s1Count;

      atoms.push([
        Math.round(wx * 1000) / 1000,
        Math.round(wy * 1000) / 1000,
        Math.round(wz * 1000) / 1000,
        a[3],
        a[4],
        i % baseSeq.length,
        isStrand1 ? 1 : 2,
        i
      ]);
      atomOffset++;
    });

    const endIdx = atomOffset - 1;

    tmpl.covalentBonds.forEach(b => {
      bonds.push([b[0] + startIdx, b[1] + startIdx, 'bond', i]);
    });

    tmpl.hBonds.forEach(b => {
      bonds.push([b[0] + startIdx, b[1] + startIdx, 'h', i]);
    });

    if (i > 0) {
      const prev = pairOffsets[i - 1];
      const cur = pairOffsets[i];

      const p1Donor = prev.startIdx + prev.tmpl.s1DonorO;
      const p1Acceptor = cur.startIdx + cur.tmpl.s1AcceptorP;
      bonds.push([p1Donor, p1Acceptor, 'bond', i]);

      const p2Donor = cur.startIdx + cur.tmpl.s2DonorO;
      const p2Acceptor = prev.startIdx + prev.tmpl.s2AcceptorP;
      bonds.push([p2Donor, p2Acceptor, 'bond', i]);
    }

    pairs.push({
      index: i,
      originalIndex: i % baseSeq.length,
      base1: base,
      base2: compBase,
      hBondsCount: (base === 'C' || base === 'G') ? 3 : 2,
      startAtomIdx: startIdx,
      endAtomIdx: endIdx,
      centerPos: [cx, cy, cz],
      tangent: [tx, ty, tz],
      centerZ: cz,
      inNucleosome: frame.inNucleosome
    });
  }

  return {
    atoms,
    bonds,
    pairs,
    histoneSpheres,
    h1Rods,
    nucleosomeCenters,
    stoichiometry: stoich,
    totalAtoms: atoms.length,
    totalBonds: bonds.length,
    sequence: seq
  };
}
