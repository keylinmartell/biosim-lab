<template>
  <div class="dna-3d-card md3-card-outlined" :class="{ 'cinema-expanded': isExpanded }">
    <!-- Header de Tarjeta MD3 (Tonal Surface Header) -->
    <div class="card-header">
      <div class="header-main">
        <div class="header-avatar">
          <Icon name="dna" size="22" />
        </div>
        <div class="header-titles">
          <h3 class="title-text">Modelo Macromolecular Tridimensional (B-DNA)</h3>
          <span class="subhead-text">Visualización modular paramétrica de alta fidelidad: esqueleto alternante, grupos 2x2 y puentes de H</span>
        </div>
      </div>

      <div class="header-chips">
        <!-- Selector de Modo de Curvatura (Cinemático In Vivo vs Lineal Analítico) -->
        <button 
          class="md3-chip interactive-chip" 
          @click="toggleTrajectoryMode"
          :title="trajectoryMode === 'curved' ? 'Cambiar a modo lineal estricto' : 'Cambiar a modo cinemático in vivo'"
        >
          <Icon name="dna" size="14" class="chip-lead" />
          <span class="font-mono">Modo: {{ trajectoryMode === 'curved' ? 'Curva In Vivo' : 'Eje Lineal' }}</span>
        </button>

        <!-- Selector de Vista: Gen Completo vs Ventana Activa si la secuencia es larga -->
        <button 
          class="md3-chip interactive-chip" 
          v-if="cleanFullSequence.length > 64"
          @click="toggleViewMode3D"
          :title="viewMode3D === 'full' ? 'Cambiar a ventana de inspección detallada (64 bp)' : 'Cambiar a vista genómica completa'"
        >
          <Icon name="visibility" size="14" class="chip-lead" />
          <span class="font-mono">3D: {{ viewMode3D === 'full' ? `Gen Completo (${cleanFullSequence.length} bp)` : `Ventana (64 bp)` }}</span>
        </button>

        <div class="md3-chip">
          <Icon name="tag" size="14" class="chip-lead" />
          <span class="font-mono">{{ displayedSequence.length }} bp en 3D</span>
        </div>

        <button 
          class="md3-chip interactive-chip" 
          @click="toggleExpand"
          :title="isExpanded ? 'Contraer vista' : 'Expandir vista inmersiva'"
        >
          <Icon name="open_in_full" size="14" class="chip-lead" />
          <span>{{ isExpanded ? 'Contraer' : 'Expandir' }}</span>
        </button>
      </div>
    </div>

    <!-- Contenedor del Canvas WebGL 3D -->
    <div class="canvas-wrapper" ref="canvasContainer">
      <!-- HUD Superior Izquierdo: Leyenda Biofísica Macromolecular -->
      <div class="hud-card hud-top-left">
        <div class="hud-card-header">
          <span class="hud-label">Estructura Macromolecular Modular</span>
        </div>
        <div class="spectral-legend-grid">
          <span class="spectral-pill a"><span class="swatch"></span>A · Adenina (Verde)</span>
          <span class="spectral-pill t"><span class="swatch"></span>T · Timina (Rojo)</span>
          <span class="spectral-pill c"><span class="swatch"></span>C · Citosina (Azul)</span>
          <span class="spectral-pill g"><span class="swatch"></span>G · Guanina (Amarillo)</span>
          <span class="spectral-pill phosphate"><span class="swatch"></span>Fosfato (Naranja)</span>
          <span class="spectral-pill sugar"><span class="swatch"></span>Desoxirribosa (Gris)</span>
          <span class="spectral-pill bond"><span class="swatch rod"></span>Enlace Esqueleto</span>
          <span class="spectral-pill hbond"><span class="swatch pin"></span>Puentes H (Punteado)</span>
        </div>
      </div>

      <!-- HUD Superior Derecho: Detalle del Par y Esqueleto Azúcar-Fosfato -->
      <div class="hud-card hud-top-right" v-if="selectedBaseData">
        <div class="hud-card-header">
          <span class="hud-label">Nucleótido Dúplex (Posición {{ selectedPosition }})</span>
        </div>
        <div class="pair-display-row">
          <div :class="['base-badge', selectedBaseData.strand1.toLowerCase()]">
            <span class="strand-id">5'</span>
            <span class="base-letter font-mono">{{ selectedBaseData.strand1 }}</span>
          </div>

          <div class="h-bond-indicator">
            <span class="bond-dots">
              <span class="dot" v-for="n in selectedBaseData.bonds" :key="n"></span>
            </span>
            <span class="bond-caption font-mono">{{ selectedBaseData.bonds }} enlaces H</span>
          </div>

          <div :class="['base-badge', selectedBaseData.strand2.toLowerCase()]">
            <span class="strand-id">3'</span>
            <span class="base-letter font-mono">{{ selectedBaseData.strand2 }}</span>
          </div>
        </div>

        <div class="hud-backbone-detail">
          <div class="hud-bb-line">
            <span class="hud-bb-tag">5' Hebra:</span>
            <span>Desoxirribosa (Gris) ↔ Fosfato (Naranja)</span>
          </div>
          <div class="hud-bb-line">
            <span class="hud-bb-tag">3' Antiparalela:</span>
            <span>Desoxirribosa (Gris) ↔ Fosfato (Naranja)</span>
          </div>
        </div>
      </div>

      <!-- Barra de Herramientas Flotante MD3 -->
      <div class="hud-toolbar">
        <button 
          :class="['md3-icon-btn', { active: isAutoRotating }]" 
          @click="toggleAutoRotate" 
          :title="isAutoRotating ? 'Pausar rotación automática' : 'Reanudar rotación automática'"
        >
          <Icon name="rotate" size="18" />
        </button>
        <button class="md3-icon-btn" @click="zoomIn" title="Acercar zoom">
          <Icon name="zoom" size="18" />
        </button>
        <button class="md3-icon-btn" @click="zoomOut" title="Alejar zoom">
          <Icon name="zoom_in" size="18" style="transform: rotate(180deg);" />
        </button>
        <button class="md3-icon-btn" @click="resetCamera" title="Restablecer perspectiva cenital">
          <Icon name="refresh" size="18" />
        </button>
        <button class="md3-icon-btn" @click="toggleTrajectoryMode" :title="trajectoryMode === 'curved' ? 'Modo lineal' : 'Modo curva in vivo'">
          <Icon name="dna" size="18" />
        </button>
      </div>

      <!-- HUD Inferior: Indicador de Navegación -->
      <div class="hud-bottom-dock">
        <div class="dock-content">
          <Icon name="info" size="16" class="dock-icon" />
          <span>Rotación 360° · Zoom orbital · Clic en cualquier bloque o azúcar para inspeccionar su par y puentes de hidrógeno</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, computed, nextTick } from 'vue';
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import Icon from './Icon.vue';

const props = defineProps({
  sequence: {
    type: String,
    required: true,
    default: 'ATCGATCGATCG'
  },
  selectedPosition: {
    type: Number,
    default: 0
  }
});

const emit = defineEmits(['selectBase']);

const canvasContainer = ref(null);
const isExpanded = ref(false);
const trajectoryMode = ref('linear'); // 'linear' (eje vertical estricto) o 'curved' (curva in vivo)
const isAutoRotating = ref(true);

let renderer = null;
let scene = null;
let camera = null;
let controls = null;
let mainHelixGroup = null;
let animId = null;

const complementMap = { A: 'T', T: 'A', C: 'G', G: 'C' };

const cleanFullSequence = computed(() => {
  return props.sequence.toUpperCase().replace(/[^ATCG]/g, '') || 'ATCGATCGATCG';
});

// Modo de visualización: 'full' (todo el gen en 3D mediante GPU Instancing) o 'window' (ventana 64 bp para inspección cercana)
const viewMode3D = ref('full');

function toggleViewMode3D() {
  viewMode3D.value = (viewMode3D.value === 'full') ? 'window' : 'full';
}

// Secuencia procesada para el renderizador 3D
const displayedSequence = computed(() => {
  const clean = cleanFullSequence.value;
  if (clean.length < 16) {
    let extended = clean;
    while (extended.length < 16) {
      extended += clean;
    }
    return extended.slice(0, 16);
  }
  if (viewMode3D.value === 'window' && clean.length > 64) {
    const sel = (props.selectedPosition !== null && props.selectedPosition !== undefined && props.selectedPosition >= 0) ? props.selectedPosition : 0;
    const start = Math.max(0, Math.min(sel - 32, clean.length - 64));
    return clean.slice(start, start + 64);
  }
  return clean;
});

const selectedBaseData = computed(() => {
  const clean = props.sequence.toUpperCase().replace(/[^ATCG]/g, '');
  const pos = props.selectedPosition;
  if (!clean || pos === null || pos === undefined || pos < 0 || pos >= clean.length) return null;
  const s1 = clean[pos];
  const s2 = complementMap[s1] || 'T';
  const bonds = (s1 === 'C' || s1 === 'G') ? 3 : 2;
  return { strand1: s1, strand2: s2, bonds };
});

// ==========================================
// ========================================================
// PARÁMETROS GEOMÉTRICOS — DOBLE HÉLICE B-DNA (MODELO MOLECULAR)
// ========================================================
const HELIX_RADIUS = 13.2;              // Radio exterior del esqueleto (fosfatos)
const VERTICAL_STEP = 5.0;             // Separación vertical entre pares de bases
const ANGLE_STEP = (Math.PI * 2) / 10; // 36° por par de bases (B-DNA)

// Offsets del modelo molecular
const SUGAR_INWARD = 2.4;     // Desplazamiento del azúcar hacia adentro (más agrupado con fosfatos)

// Tamaños de esferas
const R_BACKBONE = 0.95;   // Fosfato (naranja) y Desoxirribosa (gris)
const R_BASE = 0.78;       // Esferas de bases nitrogenadas (un tin más pequeñas que el esqueleto)
const R_HBOND = 0.15;      // Micro-esferas blancas de puentes y enlaces punteados
const R_BACKBONE_ROD = 0.20; // Varillas cilíndricas del esqueleto entre esferas
const dOffset = R_BASE * 1.35; // Offset del rombo con apertura central

const clickableObjects = [];

// ==========================================
// CACHÉ DE GEOMETRÍAS Y MATERIALES PBR
// ==========================================
let geomBackbone = null;
let geomBase = null;
let geomHBond = null;

function getGeometries() {
  // Siempre crear geometrías frescas con los radios actuales (sin caché de radio obsoleto)
  if (!geomBackbone) geomBackbone = new THREE.SphereGeometry(R_BACKBONE, 26, 20);
  if (!geomBase) geomBase = new THREE.SphereGeometry(R_BASE, 20, 16);
  if (!geomHBond) geomHBond = new THREE.SphereGeometry(R_HBOND, 12, 10);
  return { geomBackbone, geomBase, geomHBond };
}

function resetGeometryCache() {
  if (geomBackbone) { geomBackbone.dispose(); geomBackbone = null; }
  if (geomBase) { geomBase.dispose(); geomBase = null; }
  if (geomHBond) { geomHBond.dispose(); geomHBond = null; }
}

let pbrMaterials = null;
function initPBRMaterials() {
  if (pbrMaterials) return pbrMaterials;

  // 5. Material plástico mate satinado (roughness: 0.35, metalness: 0.05)
  const PBR_OPTS = { roughness: 0.35, metalness: 0.05 };

  // Esqueleto exterior
  const phosphateMat = new THREE.MeshStandardMaterial({
    color: 0xff7700, // Naranja brillante
    ...PBR_OPTS
  });

  const sugarMat = new THREE.MeshStandardMaterial({
    color: 0xd1d5db, // Gris claro neutro
    ...PBR_OPTS
  });

  const bondRodMat = new THREE.MeshStandardMaterial({
    color: 0x94a3b8, // Cilindro liso gris
    ...PBR_OPTS
  });

  // Bases Nitrogenadas:
  // Verde = Adenina (A), Rojo = Timina (T), Amarillo = Guanina (G), Azul = Citosina (C)
  const baseMats = {
    A: new THREE.MeshStandardMaterial({ color: 0x22c55e, ...PBR_OPTS }), // Verde
    T: new THREE.MeshStandardMaterial({ color: 0xef4444, ...PBR_OPTS }), // Rojo
    G: new THREE.MeshStandardMaterial({ color: 0xfacc15, ...PBR_OPTS }), // Amarillo
    C: new THREE.MeshStandardMaterial({ color: 0x2563eb, ...PBR_OPTS })  // Azul
  };

  // Puentes de hidrógeno: Micro-esferas blancas (puntos punteados del peldaño)
  const hBondMat = new THREE.MeshStandardMaterial({
    color: 0xffffff,
    roughness: 0.28,
    metalness: 0.05
  });

  // Resaltado para par activo seleccionado
  const selectedSugarMat = new THREE.MeshStandardMaterial({
    color: 0xffffff,
    emissive: 0x38bdf8,
    emissiveIntensity: 0.60,
    roughness: 0.25,
    metalness: 0.05
  });

  const selectedHBondMat = new THREE.MeshStandardMaterial({
    color: 0xffffff,
    emissive: 0x70d6ff,
    emissiveIntensity: 0.90,
    roughness: 0.20,
    metalness: 0.05
  });

  const selectedBaseMats = {
    A: new THREE.MeshStandardMaterial({ color: 0x4ade80, emissive: 0x22c55e, emissiveIntensity: 0.60, ...PBR_OPTS }),
    T: new THREE.MeshStandardMaterial({ color: 0xf87171, emissive: 0xef4444, emissiveIntensity: 0.60, ...PBR_OPTS }),
    G: new THREE.MeshStandardMaterial({ color: 0xfde047, emissive: 0xeab308, emissiveIntensity: 0.60, ...PBR_OPTS }),
    C: new THREE.MeshStandardMaterial({ color: 0x60a5fa, emissive: 0x2563eb, emissiveIntensity: 0.60, ...PBR_OPTS })
  };

  pbrMaterials = {
    phosphateMat,
    sugarMat,
    selectedSugarMat,
    bondRodMat,
    hBondMat,
    selectedHBondMat,
    baseMats,
    selectedBaseMats
  };
  return pbrMaterials;
}

// Auxiliar: agrega una esfera a la escena
function addSphereMesh(group, geom, mat, pos, userData = null) {
  const mesh = new THREE.Mesh(geom, mat);
  mesh.position.copy(pos);
  if (userData) {
    mesh.userData = userData;
    clickableObjects.push(mesh);
  }
  group.add(mesh);
  return mesh;
}

// Auxiliar: conecta exactamente dos esferas de la misma hebra con un cilindro liso gris
function addCylinderBetween(group, pA, pB, radius, material) {
  const dir = new THREE.Vector3().subVectors(pB, pA);
  const len = dir.length();
  if (len < 0.01) return null;
  const mid = new THREE.Vector3().addVectors(pA, pB).multiplyScalar(0.5);
  const geo = new THREE.CylinderGeometry(radius, radius, len, 16);
  const mesh = new THREE.Mesh(geo, material);
  mesh.position.copy(mid);
  mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir.clone().normalize());
  group.add(mesh);
  return mesh;
}

// ========================================================
// ========================================================
// ========================================================
// GENERADOR GEOMÉTRICO — DOBLE HÉLICE B-DNA (GPU INSTANCED MESH)
// Renderiza secuencias completas (ej: 1.182 bp de TP53) a 60 FPS
// usando InstancedMesh para comprimir miles de esferas y varillas
// en sólo 8 órdenes de dibujo (Draw Calls) directas a la GPU.
// ========================================================
function buildDNAHelix() {
  if (!mainHelixGroup) return;

  while (mainHelixGroup.children.length > 0) {
    const obj = mainHelixGroup.children[0];
    mainHelixGroup.remove(obj);
    if (obj.geometry) obj.geometry.dispose();
  }
  clickableObjects.length = 0;
  resetGeometryCache();

  const seq = displayedSequence.value;
  const N = seq.length;
  if (!N) return;

  const mats = initPBRMaterials();
  const geoms = getGeometries();

  const yOfLevel = (t) => (t - (N - 1) / 2) * VERTICAL_STEP;

  // Punto helicoidal
  const helixPt = (t, strandPhase, radius) => {
    const angle = t * ANGLE_STEP + strandPhase;
    return new THREE.Vector3(
      radius * Math.cos(angle),
      yOfLevel(t),
      radius * Math.sin(angle)
    );
  };

  const R_SUGAR = HELIX_RADIUS - SUGAR_INWARD;
  const R_PHOSPHATE = HELIX_RADIUS;

  const strand1Sugars = [];
  const strand2Sugars = [];

  const sugarTransforms = [];
  const phosphateTransforms = [];
  const rodTransforms = [];

  const addRod = (pA, pB) => {
    const dir = new THREE.Vector3().subVectors(pB, pA);
    const len = dir.length();
    if (len < 0.01) return;
    const mid = new THREE.Vector3().addVectors(pA, pB).multiplyScalar(0.5);
    const q = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir.clone().normalize());
    rodTransforms.push({ pos: mid, quat: q, scale: new THREE.Vector3(1, len, 1) });
  };

  // Construcción del esqueleto de ambas hebras
  const buildStrandData = (strandPhase, strandIndex, outSugars) => {
    const units = [];
    for (let i = -1; i <= N; i++) {
      const isActualBase = (i >= 0 && i < N);
      const s1Pos = helixPt(i, strandPhase, R_SUGAR);
      if (isActualBase) {
        outSugars[i] = s1Pos;
      }
      const p1Pos = helixPt(i + 0.16, strandPhase, R_PHOSPHATE);
      const s2Pos = helixPt(i + 0.32, strandPhase, R_SUGAR);
      const p2Pos = helixPt(i + 0.48, strandPhase, R_PHOSPHATE);

      sugarTransforms.push(s1Pos);
      phosphateTransforms.push(p1Pos);
      sugarTransforms.push(s2Pos);
      phosphateTransforms.push(p2Pos);

      units.push({ s1Pos, p1Pos, s2Pos, p2Pos });
    }

    for (let u = 0; u < units.length; u++) {
      const unit = units[u];
      addRod(unit.s1Pos, unit.s2Pos);
      addRod(unit.p1Pos, unit.p2Pos);
      addRod(unit.s1Pos, unit.p1Pos);
      addRod(unit.p1Pos, unit.s2Pos);
      addRod(unit.s2Pos, unit.p2Pos);
      if (u < units.length - 1) {
        addRod(unit.p2Pos, units[u + 1].s1Pos);
      }
    }
  };

  buildStrandData(0, 1, strand1Sugars);
  buildStrandData(Math.PI, 2, strand2Sugars);

  // Bases y peldaños centrales
  const baseTransforms = { A: [], T: [], C: [], G: [] };
  const hBondTransforms = [];
  const baseHitMap = { A: [], T: [], C: [], G: [] };

  const up = new THREE.Vector3(0, 1, 0);

  // Offset real para calcular el mapeo de clic si estamos en ventana
  let baseOffset = 0;
  if (viewMode3D.value === 'window' && cleanFullSequence.value.length > 64) {
    const sel = (props.selectedPosition !== null && props.selectedPosition !== undefined && props.selectedPosition >= 0) ? props.selectedPosition : 0;
    baseOffset = Math.max(0, Math.min(sel - 32, cleanFullSequence.value.length - 64));
  }

  for (let i = 0; i < N; i++) {
    const realIndex = i + baseOffset;
    const isSelected = props.selectedPosition !== null && realIndex === props.selectedPosition;
    const b1 = seq[i];
    const b2 = complementMap[b1] || 'T';

    const posS1 = strand1Sugars[i];
    const posS2 = strand2Sugars[i];
    if (!posS1 || !posS2) continue;

    const toS2 = new THREE.Vector3().subVectors(posS2, posS1);
    toS2.y = 0;
    const rungDir = toS2.clone().normalize();
    const rungMid = new THREE.Vector3((posS1.x + posS2.x) / 2, yOfLevel(i), (posS1.z + posS2.z) / 2);

    const distFromSugarToBase = 5.0;
    const center1 = posS1.clone().addScaledVector(rungDir, distFromSugarToBase);
    center1.y = yOfLevel(i);
    const center2 = posS2.clone().addScaledVector(rungDir, -distFromSugarToBase);
    center2.y = yOfLevel(i);

    // Puntas exteriores e interiores de los rombos de bases
    const tip1_out = center1.clone().addScaledVector(rungDir, -(dOffset + R_BASE));
    const tip1_in = center1.clone().addScaledVector(rungDir, (dOffset + R_BASE));
    const tip2_out = center2.clone().addScaledVector(rungDir, (dOffset + R_BASE));
    const tip2_in = center2.clone().addScaledVector(rungDir, -(dOffset + R_BASE));

    const sugar1_surf = posS1.clone().addScaledVector(rungDir, R_BACKBONE);
    const sugar2_surf = posS2.clone().addScaledVector(rungDir, -R_BACKBONE);

    // Enlaces de micro-puntos Azúcar ↔ Base (5 puntos blancos)
    for (let d = 1; d <= 5; d++) {
      const t = d / 6;
      const pt1 = new THREE.Vector3().lerpVectors(sugar1_surf, tip1_out, t);
      pt1.y = yOfLevel(i);
      hBondTransforms.push(pt1);

      const pt2 = new THREE.Vector3().lerpVectors(sugar2_surf, tip2_out, t);
      pt2.y = yOfLevel(i);
      hBondTransforms.push(pt2);
    }

    // Cluster molecular en ROMBO de 4 esferas por cada nucleótido (Izquierda, Derecha, Arriba, Abajo)
    const addCluster = (center, bLetter, strandNum) => {
      [[-dOffset, 0], [dOffset, 0], [0, dOffset], [0, -dOffset]].forEach(([du, dv]) => {
        const p = center.clone().addScaledVector(rungDir, du).addScaledVector(up, dv);
        baseTransforms[bLetter].push(p);
        baseHitMap[bLetter].push({ index: realIndex, base: bLetter, strand: strandNum });
      });
    };
    addCluster(center1, b1, 1);
    addCluster(center2, b2, 2);

    // Puentes de hidrógeno centrales entre los dos rombos (8 puntos blancos)
    for (let d = 1; d <= 8; d++) {
      const t = d / 9;
      const pt = new THREE.Vector3().lerpVectors(tip1_in, tip2_in, t);
      pt.y = yOfLevel(i);
      hBondTransforms.push(pt);
    }

    // Aura bioluminiscente de selección
    if (isSelected) {
      const sl = new THREE.PointLight(0x38bdf8, 3.5, 24.0);
      sl.position.copy(rungMid);
      mainHelixGroup.add(sl);

      const haloGeo = new THREE.RingGeometry(HELIX_RADIUS * 0.8, HELIX_RADIUS * 1.1, 32);
      const haloMat = new THREE.MeshBasicMaterial({ color: 0x38bdf8, side: THREE.DoubleSide, transparent: true, opacity: 0.75 });
      const halo = new THREE.Mesh(haloGeo, haloMat);
      halo.position.copy(rungMid);
      halo.rotation.x = Math.PI / 2;
      mainHelixGroup.add(halo);
    }
  }

  // ==========================================
  // DISPATCH A LA GPU MEDIANTE INSTANCED MESH
  // ==========================================
  const dummy = new THREE.Object3D();

  // 1. Fosfatos (InstancedMesh)
  if (phosphateTransforms.length > 0) {
    const meshP = new THREE.InstancedMesh(geoms.geomBackbone, mats.phosphateMat, phosphateTransforms.length);
    for (let j = 0; j < phosphateTransforms.length; j++) {
      dummy.position.copy(phosphateTransforms[j]);
      dummy.quaternion.identity();
      dummy.scale.set(1, 1, 1);
      dummy.updateMatrix();
      meshP.setMatrixAt(j, dummy.matrix);
    }
    meshP.instanceMatrix.needsUpdate = true;
    mainHelixGroup.add(meshP);
  }

  // 2. Azúcares (InstancedMesh)
  if (sugarTransforms.length > 0) {
    const meshS = new THREE.InstancedMesh(geoms.geomBackbone, mats.sugarMat, sugarTransforms.length);
    for (let j = 0; j < sugarTransforms.length; j++) {
      dummy.position.copy(sugarTransforms[j]);
      dummy.quaternion.identity();
      dummy.scale.set(1, 1, 1);
      dummy.updateMatrix();
      meshS.setMatrixAt(j, dummy.matrix);
    }
    meshS.instanceMatrix.needsUpdate = true;
    mainHelixGroup.add(meshS);
  }

  // 3. Varillas del esqueleto y puentes (Cilindro unitario instanciado)
  if (rodTransforms.length > 0) {
    const unitCylGeo = new THREE.CylinderGeometry(R_BACKBONE_ROD, R_BACKBONE_ROD, 1.0, 8);
    const meshR = new THREE.InstancedMesh(unitCylGeo, mats.bondRodMat, rodTransforms.length);
    for (let j = 0; j < rodTransforms.length; j++) {
      const { pos, quat, scale } = rodTransforms[j];
      dummy.position.copy(pos);
      dummy.quaternion.copy(quat);
      dummy.scale.copy(scale);
      dummy.updateMatrix();
      meshR.setMatrixAt(j, dummy.matrix);
    }
    meshR.instanceMatrix.needsUpdate = true;
    mainHelixGroup.add(meshR);
  }

  // 4. Bases A, T, C, G (InstancedMesh por base con mapa de clic interactivo)
  ['A', 'T', 'C', 'G'].forEach((baseLetter) => {
    const transforms = baseTransforms[baseLetter];
    if (transforms && transforms.length > 0) {
      const meshB = new THREE.InstancedMesh(geoms.geomBase, mats.baseMats[baseLetter], transforms.length);
      for (let j = 0; j < transforms.length; j++) {
        dummy.position.copy(transforms[j]);
        dummy.quaternion.identity();
        dummy.scale.set(1, 1, 1);
        dummy.updateMatrix();
        meshB.setMatrixAt(j, dummy.matrix);
      }
      meshB.instanceMatrix.needsUpdate = true;
      meshB.userData = { instanceMap: baseHitMap[baseLetter] };
      clickableObjects.push(meshB);
      mainHelixGroup.add(meshB);
    }
  });

  // 5. Puntos de enlace y Puentes de Hidrógeno
  if (hBondTransforms.length > 0) {
    const meshH = new THREE.InstancedMesh(geoms.geomHBond, mats.hBondMat, hBondTransforms.length);
    for (let j = 0; j < hBondTransforms.length; j++) {
      dummy.position.copy(hBondTransforms[j]);
      dummy.quaternion.identity();
      dummy.scale.set(1, 1, 1);
      dummy.updateMatrix();
      meshH.setMatrixAt(j, dummy.matrix);
    }
    meshH.instanceMatrix.needsUpdate = true;
    mainHelixGroup.add(meshH);
  }

  fitCameraToHelix(N);
}

// CÁMARA: encuadre frontal dinámico según longitud N (soporta 12 a 2.000+ bp)
function fitCameraToHelix(N) {
  if (!camera || !controls || !mainHelixGroup) return;

  const count = Math.max(1, N || 12);
  const totalHeight = count * VERTICAL_STEP; // altura vertical total
  const fovRad = (camera.fov * Math.PI) / 360; // 19°
  const idealDistance = Math.max(72.0, ((totalHeight / 2) / Math.tan(fovRad)) * 1.15);

  camera.near = 1.0;
  camera.far = Math.max(4000.0, idealDistance * 5.0);
  camera.position.set(0, 0, idealDistance);
  camera.updateProjectionMatrix();

  controls.target.set(0, 0, 0);
  controls.minDistance = 6.0;
  controls.maxDistance = Math.max(2500.0, idealDistance * 3.5);
  controls.update();

  const midIndex = Math.floor(count / 2);
  const midAngle = midIndex * ANGLE_STEP;
  mainHelixGroup.rotation.set(0.05, midAngle + Math.PI / 2, -0.05);
}

function initScene() {
  const container = canvasContainer.value;
  if (!container) return;

  const width = container.clientWidth || 600;
  const height = container.clientHeight || 580;

  scene = new THREE.Scene();

  camera = new THREE.PerspectiveCamera(38, width / height, 1.0, 3500);
  camera.position.set(0, 0, 75.0);

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
  renderer.setSize(width, height);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;
  container.appendChild(renderer.domElement);

  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.minDistance = 6.0;
  controls.maxDistance = 2000.0;
  controls.target.set(0, 0, 0);

  // Iluminación PBR equilibrada de estudio
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.75);
  scene.add(ambientLight);

  // Luz principal clave (Key Light)
  const keyLight = new THREE.DirectionalLight(0xfff8ee, 2.0);
  keyLight.position.set(35, 45, 40);
  scene.add(keyLight);

  // Luz de relleno suave (Fill Light)
  const fillLight = new THREE.DirectionalLight(0xdbeafe, 0.90);
  fillLight.position.set(-40, -15, 30);
  scene.add(fillLight);

  // Luz trasera de silueta (Rim Light)
  const rimLight = new THREE.DirectionalLight(0xffffff, 0.80);
  rimLight.position.set(0, -30, -40);
  scene.add(rimLight);

  // Grupo principal de la hélice
  mainHelixGroup = new THREE.Group();
  scene.add(mainHelixGroup);

  buildDNAHelix();

  // Raycaster para selección interactiva
  const raycaster = new THREE.Raycaster();
  const mouse = new THREE.Vector2();
  let clickStartPos = { x: 0, y: 0 };

  container.addEventListener('pointerdown', (e) => {
    clickStartPos = { x: e.clientX, y: e.clientY };
  });

  container.addEventListener('pointerup', (e) => {
    const dist = Math.hypot(e.clientX - clickStartPos.x, e.clientY - clickStartPos.y);
    if (dist < 6 && container) {
      const rect = container.getBoundingClientRect();
      mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
      raycaster.setFromCamera(mouse, camera);

      const intersects = raycaster.intersectObjects(clickableObjects, false);
      if (intersects.length > 0) {
        const hit = intersects[0];
        const obj = hit.object;
        if (obj.isInstancedMesh && obj.userData?.instanceMap) {
          const data = obj.userData.instanceMap[hit.instanceId];
          if (data && data.index !== undefined) {
            emit('selectBase', data.index);
          }
        } else if (obj.userData && obj.userData.index !== undefined) {
          emit('selectBase', obj.userData.index);
        }
      }
    }
  });

  animate();
}

function animate() {
  animId = requestAnimationFrame(animate);

  // Rotación continua suave del modelo
  if (mainHelixGroup && isAutoRotating.value) {
    mainHelixGroup.rotation.y += 0.0035;
  }

  controls?.update();
  if (renderer && scene && camera) {
    renderer.render(scene, camera);
  }
}

let resizeObserver = null;

function onWindowResize() {
  if (!renderer || !camera || !canvasContainer.value) return;
  const width = canvasContainer.value.clientWidth;
  const height = canvasContainer.value.clientHeight;
  if (width <= 0 || height <= 0) return;
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
  renderer.setSize(width, height);
  fitCameraToHelix(displayedSequence.value.length);
}

function toggleAutoRotate() {
  isAutoRotating.value = !isAutoRotating.value;
}

function toggleTrajectoryMode() {
  trajectoryMode.value = (trajectoryMode.value === 'curved') ? 'linear' : 'curved';
  buildDNAHelix();
}

function toggleExpand() {
  isExpanded.value = !isExpanded.value;
  nextTick(() => {
    onWindowResize();
  });
}

function zoomIn() {
  if (!camera) return;
  camera.position.multiplyScalar(0.85);
  controls?.update();
}

function zoomOut() {
  if (!camera) return;
  camera.position.multiplyScalar(1.18);
  controls?.update();
}

function resetCamera() {
  if (!camera || !controls || !mainHelixGroup) return;
  fitCameraToHelix(displayedSequence.value.length);
  controls.target.set(0, 0, 0);
  controls.update();
  const N = displayedSequence.value.length;
  const midIndex = Math.floor(N / 2);
  const midAngle = midIndex * ANGLE_STEP;
  mainHelixGroup.rotation.set(0.06, midAngle + Math.PI / 2, -0.06);
}

watch(() => [props.sequence, props.selectedPosition, trajectoryMode.value, viewMode3D.value], () => {
  buildDNAHelix();
});

onMounted(() => {
  initScene();
  window.addEventListener('resize', onWindowResize);
  if (canvasContainer.value) {
    resizeObserver = new ResizeObserver(() => {
      onWindowResize();
    });
    resizeObserver.observe(canvasContainer.value);
  }
});

onUnmounted(() => {
  if (animId) cancelAnimationFrame(animId);
  window.removeEventListener('resize', onWindowResize);
  if (resizeObserver) {
    resizeObserver.disconnect();
    resizeObserver = null;
  }
  if (renderer && renderer.domElement && renderer.domElement.parentNode) {
    renderer.domElement.parentNode.removeChild(renderer.domElement);
  }
  if (renderer) renderer.dispose();
});
</script>

<style scoped>
.dna-3d-card {
  display: flex;
  flex-direction: column;
  background-color: var(--md-sys-color-surface-container);
  border-radius: var(--md-sys-shape-corner-medium);
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.45);
  border: 1px solid var(--md-sys-color-outline-variant);
  transition: all var(--md-sys-motion-duration-medium) ease;
}

.dna-3d-card.cinema-expanded {
  grid-column: 1 / -1;
  position: relative;
  z-index: 20;
}

/* Header */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.9rem 1.4rem;
  background-color: var(--md-sys-color-surface-container-high);
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
  flex-wrap: wrap;
  gap: 0.8rem;
}

.header-main {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.header-avatar {
  width: 42px;
  height: 42px;
  border-radius: var(--md-sys-shape-corner-small);
  background: linear-gradient(135deg, rgba(14, 165, 233, 0.25) 0%, rgba(2, 132, 199, 0.35) 100%);
  border: 1px solid rgba(56, 189, 248, 0.3);
  color: #38bdf8;
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-titles {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.title-text {
  font: var(--md-sys-typescale-title-medium);
  color: #f1f5f9;
  font-weight: 700;
  letter-spacing: -0.2px;
}

.subhead-text {
  font: var(--md-sys-typescale-body-small);
  color: #94a3b8;
}

.header-chips {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.chip-lead {
  color: var(--md-sys-color-primary);
}

.interactive-chip {
  cursor: pointer;
  background-color: var(--md-sys-color-surface-container);
  border: 1px solid rgba(56, 189, 248, 0.3);
  transition: all 0.2s ease;
}

.interactive-chip:hover {
  background-color: var(--md-sys-color-surface-container-highest);
  border-color: #38bdf8;
  transform: translateY(-1px);
}

/* Canvas Area */
.canvas-wrapper {
  position: relative;
  width: 100%;
  height: 600px;
  min-height: 600px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: grab;
  background: radial-gradient(ellipse at 50% 50%, #0d1117 0%, #06080c 55%, #010204 100%);
}

.dna-3d-card.cinema-expanded .canvas-wrapper {
  height: 720px;
}

.canvas-wrapper:active {
  cursor: grabbing;
}

/* HUD Cards */
.hud-card {
  position: absolute;
  background: rgba(11, 19, 32, 0.88);
  border: 1px solid rgba(56, 189, 248, 0.25);
  border-radius: var(--md-sys-shape-corner-small);
  padding: 0.65rem 0.9rem;
  backdrop-filter: blur(12px);
  pointer-events: none;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5);
  z-index: 5;
}

.hud-card-header {
  margin-bottom: 0.4rem;
}

.hud-label {
  font: var(--md-sys-typescale-label-small);
  color: #7dd3fc;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.hud-top-left {
  top: 1.1rem;
  left: 1.2rem;
}

.spectral-legend-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.35rem 0.65rem;
}

.spectral-pill {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-family: var(--md-ref-typeface-mono);
  font-size: 0.72rem;
  font-weight: 600;
}

.spectral-pill .swatch {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  box-shadow: 0 0 6px currentColor;
}

.spectral-pill.a { color: #22c55e; }
.spectral-pill.t { color: #ef4444; }
.spectral-pill.c { color: #2563eb; }
.spectral-pill.g { color: #eab308; }
.spectral-pill.phosphate { color: #f59e0b; }
.spectral-pill.sugar { color: #94a3b8; }
.spectral-pill.bond { color: #64748b; }
.spectral-pill.hbond { color: #f8fafc; }

.spectral-pill .swatch.rod {
  width: 10px;
  height: 4px;
  border-radius: 2px;
  background-color: #334155;
  box-shadow: 0 0 4px #334155;
}
.spectral-pill .swatch.pin {
  width: 10px;
  height: 3px;
  border-radius: 1px;
  background-color: #f8fafc;
  box-shadow: 0 0 6px #ffffff;
}

.hud-top-right {
  top: 1.1rem;
  right: 1.2rem;
}

.pair-display-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.base-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.25rem 0.55rem;
  border-radius: var(--md-sys-shape-corner-extra-small);
  border: 1px solid transparent;
}

.base-badge .strand-id {
  font-size: 0.58rem;
  opacity: 0.75;
}

.base-badge .base-letter {
  font-size: 1.05rem;
  font-weight: 800;
}

.base-badge.a { background: rgba(34, 197, 94, 0.2); color: #22c55e; border-color: #22c55e; }
.base-badge.t { background: rgba(239, 68, 68, 0.2); color: #ef4444; border-color: #ef4444; }
.base-badge.c { background: rgba(37, 99, 235, 0.2); color: #2563eb; border-color: #2563eb; }
.base-badge.g { background: rgba(234, 179, 8, 0.2); color: #eab308; border-color: #eab308; }

.h-bond-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.2rem;
}

.bond-dots {
  display: flex;
  gap: 0.25rem;
}

.bond-dots .dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background-color: #f8fafc;
  box-shadow: 0 0 6px #ffffff;
}

.bond-caption {
  font-size: 0.62rem;
  color: #94a3b8;
}

/* Toolbar Flotante */
.hud-toolbar {
  position: absolute;
  right: 1.2rem;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  background: rgba(11, 19, 32, 0.88);
  border: 1px solid rgba(56, 189, 248, 0.25);
  border-radius: var(--md-sys-shape-corner-small);
  padding: 0.4rem;
  backdrop-filter: blur(12px);
  z-index: 5;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5);
}

.md3-icon-btn {
  width: 34px;
  height: 34px;
  border-radius: var(--md-sys-shape-corner-extra-small);
  background: transparent;
  border: 1px solid transparent;
  color: #94a3b8;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.18s ease;
}

.md3-icon-btn:hover {
  background: rgba(56, 189, 248, 0.15);
  color: #38bdf8;
  border-color: rgba(56, 189, 248, 0.35);
}

.md3-icon-btn.active {
  background: rgba(14, 165, 233, 0.25);
  color: #70d6ff;
  border-color: #38bdf8;
}

/* Bottom Dock */
.hud-bottom-dock {
  position: absolute;
  bottom: 1.1rem;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(11, 19, 32, 0.88);
  border: 1px solid rgba(56, 189, 248, 0.25);
  border-radius: var(--md-sys-shape-corner-full);
  padding: 0.4rem 1.1rem;
  backdrop-filter: blur(12px);
  pointer-events: none;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5);
  z-index: 5;
}

.dock-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.7rem;
  color: #94a3b8;
}

.dock-icon {
  color: #38bdf8;
}

.hud-backbone-detail {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  margin-top: 0.45rem;
  padding-top: 0.45rem;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  font-size: 0.65rem;
  color: #cbd5e1;
}

.hud-bb-line {
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.hud-bb-tag {
  font-family: var(--md-ref-typeface-mono);
  font-weight: 700;
  color: #38bdf8;
  font-size: 0.62rem;
}

@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
    padding: 0.85rem 1rem;
  }

  .header-chips {
    width: 100%;
    overflow-x: auto;
    flex-wrap: nowrap;
    padding-bottom: 0.2rem;
  }

  .canvas-wrapper {
    height: 460px;
    min-height: 400px;
  }

  .dna-3d-card.cinema-expanded .canvas-wrapper {
    height: 520px;
  }

  .hud-top-left {
    top: 0.65rem;
    left: 0.65rem;
    padding: 0.45rem 0.65rem;
  }

  .spectral-legend-grid {
    grid-template-columns: 1fr 1fr;
    gap: 0.2rem 0.45rem;
  }

  .spectral-pill {
    font-size: 0.64rem;
  }

  .hud-top-right {
    top: auto;
    bottom: 3.2rem;
    right: 0.65rem;
    padding: 0.45rem 0.65rem;
    max-width: 220px;
  }

  .hud-backbone-detail {
    display: none;
  }

  .hud-toolbar {
    right: 0.5rem;
    top: 40%;
    padding: 0.25rem;
    gap: 0.3rem;
  }

  .md3-icon-btn {
    width: 32px;
    height: 32px;
  }

  .hud-bottom-dock {
    width: calc(100% - 1.2rem);
    left: 0.6rem;
    transform: none;
    padding: 0.3rem 0.65rem;
    bottom: 0.6rem;
  }

  .dock-content {
    font-size: 0.62rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}
</style>
