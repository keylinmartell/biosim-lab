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
          <span class="subhead-text">Visualización biofísica orgánica de alta fidelidad: monómeros de desoxirribosa, pares de bases y puentes de H</span>
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

        <div class="md3-chip">
          <Icon name="tag" size="14" class="chip-lead" />
          <span class="font-mono">{{ displayedSequence.length }} bp mostrados</span>
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
      <!-- HUD Superior Izquierdo: Leyenda Espectral de Nucleótidos -->
      <!-- HUD Superior Izquierdo: Leyenda Biofísica Macromolecular -->
      <div class="hud-card hud-top-left">
        <div class="hud-card-header">
          <span class="hud-label">Estructura Macromolecular</span>
        </div>
        <div class="spectral-legend-grid">
          <span class="spectral-pill a"><span class="swatch"></span>A · Adenina (Rojo)</span>
          <span class="spectral-pill t"><span class="swatch"></span>T · Timina (Verde)</span>
          <span class="spectral-pill c"><span class="swatch"></span>C · Citosina (Azul)</span>
          <span class="spectral-pill g"><span class="swatch"></span>G · Guanina (Amarillo)</span>
          <span class="spectral-pill phosphate"><span class="swatch"></span>Fosfato (PO₄³⁻)</span>
          <span class="spectral-pill sugar"><span class="swatch"></span>2'-Desoxirribosa</span>
          <span class="spectral-pill bond"><span class="swatch rod"></span>Enlace Covalente</span>
          <span class="spectral-pill hbond"><span class="swatch pin"></span>Puentes H (2/3)</span>
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
            <span>Fosfato (PO₄³⁻) + 2'-Desoxirribosa</span>
          </div>
          <div class="hud-bb-line">
            <span class="hud-bb-tag">3' Antiparalela:</span>
            <span>2'-Desoxirribosa + Fosfato (PO₄³⁻)</span>
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
          <span>Rotación 360° · Zoom orbital · Haz clic en cualquier peldaño para inspeccionar su par y enlaces de hidrógeno</span>
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
const trajectoryMode = ref('curved'); // 'curved' (S-curve in vivo) o 'linear' (recta técnica)
const isAutoRotating = ref(true);

let renderer = null;
let scene = null;
let camera = null;
let controls = null;
let mainHelixGroup = null;
let molecularDiagramsGroup = null;
let bokehGroup = null;
let animId = null;
const startTime = performance.now();

const complementMap = { A: 'T', T: 'A', C: 'G', G: 'C' };

// Colores de bases alineados con el sistema macromolecular del modelo de referencia
const baseColors = {
  A: { main: 0xef4444, emissive: 0x7f1d1d, rim: 0xfca5a5, name: 'Adenina', hex: '#ef4444' },   // Rojo brillante
  T: { main: 0x22c55e, emissive: 0x14532d, rim: 0x86efac, name: 'Timina', hex: '#22c55e' },    // Verde esmeralda
  C: { main: 0x2563eb, emissive: 0x1e3a8a, rim: 0x93c5fd, name: 'Citosina', hex: '#2563eb' },  // Azul zafiro
  G: { main: 0xeab308, emissive: 0x713f12, rim: 0xfef08a, name: 'Guanina', hex: '#eab308' }   // Amarillo dorado
};

// Extender la secuencia a un mínimo de 30-36 pares en modo in vivo para mostrar las 3+ vueltas majestuosas
const displayedSequence = computed(() => {
  const clean = props.sequence.toUpperCase().replace(/[^ATCG]/g, '');
  if (!clean) return 'ATCGATCGATCG';
  if (trajectoryMode.value === 'linear') return clean;
  // En modo in vivo, extendemos cíclicamente hasta al menos 32 bases para la presencia macromolecular
  if (clean.length < 32) {
    let extended = clean;
    while (extended.length < 32) {
      extended += clean;
    }
    return extended.slice(0, 32);
  }
  return clean;
});

const helixTurns = computed(() => {
  return (displayedSequence.value.length / 10.5).toFixed(1);
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

// Parámetros Estructurales de Doble Hélice B-DNA (Ball-and-Stick Macromolecular)
const HELIX_RADIUS = 2.65;
const VERTICAL_STEP = 0.60;
const ANGLE_STEP = (Math.PI * 2) / 10.5; // ~34.3° por par de bases
const MINOR_GROOVE_OFFSET = 2.42; // ~138° desfase de surco menor

// Dimensiones atómicas según render biofísico de referencia
const PHOSPHATE_RADIUS = 0.40;     // Esfera de fosfato (Ámbar / Naranja)
const PHOSPHATE_SAT_RADIUS = 0.20; // Átomo satélite de oxígeno (-O)
const SUGAR_RADIUS = 0.33;         // Esfera de desoxirribosa (Gris plateado)
const SUGAR_SAT_RADIUS = 0.17;     // Átomo satélite de desoxirribosa
const BASE_CORE_RADIUS = 0.26;     // Esferas primarias de bases nitrogenadas
const BASE_BRANCH_RADIUS = 0.19;   // Esferas satélite de bases nitrogenadas
const COVALENT_BOND_RADIUS = 0.08; // Varillas cilíndricas de enlaces covalentes (Grafito metálico)
const HBOND_PIN_RADIUS = 0.044;    // Pines de puentes de hidrógeno (Plateado brillante)

const clickableObjects = [];
let backboneMaterials = [];
let baseMaterials = [];

// Generador de Textura de Bokeh Difuso
function createBokehTexture() {
  const canvas = document.createElement('canvas');
  canvas.width = 128;
  canvas.height = 128;
  const ctx = canvas.getContext('2d');
  const gradient = ctx.createRadialGradient(64, 64, 0, 64, 64, 60);
  gradient.addColorStop(0, 'rgba(255, 255, 255, 1)');
  gradient.addColorStop(0.2, 'rgba(112, 214, 255, 0.85)');
  gradient.addColorStop(0.5, 'rgba(2, 132, 199, 0.35)');
  gradient.addColorStop(0.8, 'rgba(2, 132, 199, 0.08)');
  gradient.addColorStop(1, 'rgba(2, 132, 199, 0)');
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, 128, 128);
  const texture = new THREE.CanvasTexture(canvas);
  texture.needsUpdate = true;
  return texture;
}

// Generador Procedural de Diagramas Químicos Reales (Purinas, Pirimidinas, Desoxirribosa, Fosfato)
function createChemicalTexture(type) {
  const canvas = document.createElement('canvas');
  canvas.width = 256;
  canvas.height = 256;
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, 256, 256);

  ctx.strokeStyle = 'rgba(112, 214, 255, 0.75)';
  ctx.fillStyle = 'rgba(224, 242, 254, 0.85)';
  ctx.lineWidth = 2.8;
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';
  ctx.font = 'bold 15px monospace';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';

  const cx = 128;
  const cy = 128;

  function drawHexagon(x, y, r, doubleBonds = [0, 2]) {
    const pts = [];
    for (let i = 0; i < 6; i++) {
      const a = (i / 6) * Math.PI * 2;
      pts.push({ x: x + Math.cos(a) * r, y: y + Math.sin(a) * r });
    }
    ctx.beginPath();
    ctx.moveTo(pts[0].x, pts[0].y);
    for (let i = 1; i < 6; i++) ctx.lineTo(pts[i].x, pts[i].y);
    ctx.closePath();
    ctx.stroke();

    doubleBonds.forEach(idx => {
      const p1 = pts[idx];
      const p2 = pts[(idx + 1) % 6];
      const mx = (p1.x + p2.x) * 0.5;
      const my = (p1.y + p2.y) * 0.5;
      const inX = x - mx;
      const inY = y - my;
      const len = Math.hypot(inX, inY);
      const offX = (inX / len) * 6;
      const offY = (inY / len) * 6;
      ctx.beginPath();
      ctx.moveTo(p1.x + offX, p1.y + offY);
      ctx.lineTo(p2.x + offX, p2.y + offY);
      ctx.stroke();
    });
    return pts;
  }

  function drawPentagon(x, y, r, attachPts) {
    const pts = [];
    for (let i = 0; i < 5; i++) {
      const a = (i / 5) * Math.PI * 2 - Math.PI / 10;
      pts.push({ x: x + Math.cos(a) * r, y: y + Math.sin(a) * r });
    }
    ctx.beginPath();
    ctx.moveTo(pts[0].x, pts[0].y);
    for (let i = 1; i < 5; i++) ctx.lineTo(pts[i].x, pts[i].y);
    ctx.closePath();
    ctx.stroke();
  }

  if (type === 'purine') {
    // Biciclo fusionado tipo Adenina/Guanina
    drawHexagon(cx - 24, cy, 42, [0, 2]);
    drawPentagon(cx + 42, cy, 34);
    ctx.fillText('N', cx - 24, cy - 42);
    ctx.fillText('N', cx + 64, cy - 14);
    ctx.fillText('NH₂', cx - 68, cy - 35);
  } else if (type === 'pyrimidine') {
    // Anillo hexagonal simple tipo Timina/Citosina
    drawHexagon(cx, cy, 48, [1, 3]);
    ctx.fillText('N', cx, cy - 48);
    ctx.fillText('NH', cx, cy + 48);
    ctx.fillText('=O', cx + 64, cy);
    ctx.fillText('CH₃', cx - 62, cy - 20);
  } else if (type === 'ribose') {
    // Anillo furanosa de 5 miembros de desoxirribosa
    drawPentagon(cx, cy, 46);
    ctx.fillText('O', cx, cy - 46);
    ctx.fillText('OH', cx - 52, cy + 44);
    ctx.fillText('5\'', cx + 52, cy - 35);
    ctx.fillText('3\'', cx + 45, cy + 45);
  } else {
    // Grupo fosfato
    ctx.fillText('P', cx, cy);
    ctx.beginPath();
    ctx.moveTo(cx, cy - 12); ctx.lineTo(cx, cy - 44);
    ctx.moveTo(cx + 10, cy - 12); ctx.lineTo(cx + 10, cy - 44); // doble enlace =O
    ctx.moveTo(cx, cy + 12); ctx.lineTo(cx, cy + 40);
    ctx.moveTo(cx - 12, cy); ctx.lineTo(cx - 40, cy);
    ctx.moveTo(cx + 12, cy); ctx.lineTo(cx + 40, cy);
    ctx.stroke();
    ctx.fillText('O', cx, cy - 54);
    ctx.fillText('O⁻', cx, cy + 52);
    ctx.fillText('⁻O', cx - 52, cy);
    ctx.fillText('O', cx + 52, cy);
  }

  const texture = new THREE.CanvasTexture(canvas);
  texture.needsUpdate = true;
  return texture;
}

// Cache de Geometrías Esféricas para Máximo Rendimiento WebGL
const sphereGeomCache = {};
function getSphereGeom(radius) {
  const key = radius.toFixed(2);
  if (!sphereGeomCache[key]) {
    sphereGeomCache[key] = new THREE.SphereGeometry(radius, 24, 20);
  }
  return sphereGeomCache[key];
}

// Materiales Macromoleculares Satinados (Idénticos al Render de Referencia: Sólidos, sin sobreexposición ni emisión)
let pbrMaterials = null;
function initPBRMaterials() {
  if (pbrMaterials) return pbrMaterials;

  // Fosfato (PO₄³⁻): Ámbar / Naranja dorado sólido satinado
  const phosphateMat = new THREE.MeshStandardMaterial({
    color: 0xdf7a1e,
    roughness: 0.32,
    metalness: 0.08
  });

  // Azúcar (2'-Desoxirribosa): Gris pizarra / plata neutro sólido
  const sugarMat = new THREE.MeshStandardMaterial({
    color: 0x8fa0b2,
    roughness: 0.35,
    metalness: 0.08
  });

  // Enlaces Covalentes & Fosfodiéster: Grafito carbón oscuro
  const bondRodMat = new THREE.MeshStandardMaterial({
    color: 0x2d3748,
    roughness: 0.42,
    metalness: 0.15
  });

  // Puentes de Hidrógeno: Pines metálicos plateados
  const hBondMat = new THREE.MeshStandardMaterial({
    color: 0x94a3b8,
    roughness: 0.30,
    metalness: 0.35
  });

  // Bases Nitrogenadas: Colores puros, ricos y sólidos (Rojo, Verde, Azul, Amarillo)
  const baseMats = {
    A: new THREE.MeshStandardMaterial({
      color: 0xc53030, // Adenina: Rojo carmín profundo
      roughness: 0.32,
      metalness: 0.06
    }),
    T: new THREE.MeshStandardMaterial({
      color: 0x228b45, // Timina: Verde esmeralda rico
      roughness: 0.32,
      metalness: 0.06
    }),
    C: new THREE.MeshStandardMaterial({
      color: 0x2563eb, // Citosina: Azul real profundo
      roughness: 0.32,
      metalness: 0.06
    }),
    G: new THREE.MeshStandardMaterial({
      color: 0xd99b00, // Guanina: Amarillo dorado / mostaza
      roughness: 0.32,
      metalness: 0.06
    })
  };

  // Materiales de alta luminiscencia para el par de nucleótidos seleccionado
  const selectedSugarMat = new THREE.MeshStandardMaterial({
    color: 0xffffff,
    emissive: 0x38bdf8,
    emissiveIntensity: 0.75,
    roughness: 0.15
  });

  const selectedHbondMat = new THREE.MeshStandardMaterial({
    color: 0xffffff,
    emissive: 0x70d6ff,
    emissiveIntensity: 1.4,
    roughness: 0.05
  });

  // Versiones resaltadas para par seleccionado (brillo bioeléctrico de la base activa)
  const baseSelectedMats = {
    A: new THREE.MeshStandardMaterial({
      color: 0xff4d4d,
      emissive: 0xef4444,
      emissiveIntensity: 0.95,
      roughness: 0.18
    }),
    T: new THREE.MeshStandardMaterial({
      color: 0x4ade80,
      emissive: 0x22c55e,
      emissiveIntensity: 0.95,
      roughness: 0.18
    }),
    C: new THREE.MeshStandardMaterial({
      color: 0x60a5fa,
      emissive: 0x2563eb,
      emissiveIntensity: 0.95,
      roughness: 0.18
    }),
    G: new THREE.MeshStandardMaterial({
      color: 0xfacc15,
      emissive: 0xeab308,
      emissiveIntensity: 0.95,
      roughness: 0.18
    })
  };

  pbrMaterials = {
    phosphateMat,
    sugarMat,
    selectedSugarMat,
    bondRodMat,
    hBondMat,
    selectedHbondMat,
    baseMats,
    baseSelectedMats
  };
  return pbrMaterials;
}

// Función auxiliar para agregar una esfera atómica
function addAtomSphere(group, pos, radius, material, userData = null) {
  const geo = getSphereGeom(radius);
  const mesh = new THREE.Mesh(geo, material);
  mesh.position.copy(pos);
  if (userData) {
    mesh.userData = userData;
    clickableObjects.push(mesh);
  }
  group.add(mesh);
  return mesh;
}

// Función auxiliar para conectar dos puntos con un cilindro (Varilla / Enlace)
function addCylinderBetween(group, pA, pB, radius, material) {
  const dir = new THREE.Vector3().subVectors(pB, pA);
  const len = dir.length();
  if (len < 0.005) return null;
  const mid = new THREE.Vector3().addVectors(pA, pB).multiplyScalar(0.5);
  const geo = new THREE.CylinderGeometry(radius, radius, len, 12);
  const mesh = new THREE.Mesh(geo, material);
  mesh.position.copy(mid);
  mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir.clone().normalize());
  group.add(mesh);
  return mesh;
}

// Ensambla el cluster molecular ball-and-stick de una base nitrogenada
function buildBaseCluster(group, sugarPos, unitDir, crossDir, upDir, isPurine, baseMat, bondMat, index, baseLetter, strandNum) {
  const uData = { index, base: baseLetter, strand: strandNum };
  // Extensión de la base hacia el eje central
  const baseSpan = isPurine ? 0.95 : 0.72;

  // 1. Enlace N-glicosídico covalente desde el azúcar a la base
  const p1 = sugarPos.clone().addScaledVector(unitDir, isPurine ? 0.32 : 0.28);
  addCylinderBetween(group, sugarPos, p1, COVALENT_BOND_RADIUS, bondMat);
  addAtomSphere(group, p1, BASE_CORE_RADIUS, baseMat, uData);

  let terminalPoint = p1;

  if (isPurine) {
    // Purina (A, G): Estructura bicíclica con 3 esferas nucleares y 3 satélites
    const p2 = sugarPos.clone().addScaledVector(unitDir, 0.64);
    const p3 = sugarPos.clone().addScaledVector(unitDir, baseSpan);
    addCylinderBetween(group, p1, p2, COVALENT_BOND_RADIUS, bondMat);
    addCylinderBetween(group, p2, p3, COVALENT_BOND_RADIUS, bondMat);
    addAtomSphere(group, p2, BASE_CORE_RADIUS, baseMat, uData);
    addAtomSphere(group, p3, BASE_CORE_RADIUS, baseMat, uData);
    terminalPoint = p3;

    // Átomos anulares / satélites de purina (geometría hexagonal + pentagonal)
    const sat1 = p1.clone().addScaledVector(crossDir, 0.28).addScaledVector(upDir, 0.16);
    const sat2 = p2.clone().addScaledVector(crossDir, -0.30).addScaledVector(upDir, -0.14);
    const sat3 = p2.clone().addScaledVector(crossDir, 0.26).addScaledVector(upDir, 0.18);

    addCylinderBetween(group, p1, sat1, COVALENT_BOND_RADIUS * 0.85, bondMat);
    addCylinderBetween(group, p2, sat2, COVALENT_BOND_RADIUS * 0.85, bondMat);
    addCylinderBetween(group, p2, sat3, COVALENT_BOND_RADIUS * 0.85, bondMat);

    addAtomSphere(group, sat1, BASE_BRANCH_RADIUS, baseMat, uData);
    addAtomSphere(group, sat2, BASE_BRANCH_RADIUS, baseMat, uData);
    addAtomSphere(group, sat3, BASE_BRANCH_RADIUS, baseMat, uData);
  } else {
    // Pirimidina (T, C): Anillo simple con 2 esferas nucleares y 2 satélites
    const p2 = sugarPos.clone().addScaledVector(unitDir, baseSpan);
    addCylinderBetween(group, p1, p2, COVALENT_BOND_RADIUS, bondMat);
    addAtomSphere(group, p2, BASE_CORE_RADIUS, baseMat, uData);
    terminalPoint = p2;

    const sat1 = p1.clone().addScaledVector(crossDir, 0.26).addScaledVector(upDir, 0.16);
    const sat2 = p2.clone().addScaledVector(crossDir, -0.26).addScaledVector(upDir, -0.14);

    addCylinderBetween(group, p1, sat1, COVALENT_BOND_RADIUS * 0.85, bondMat);
    addCylinderBetween(group, p2, sat2, COVALENT_BOND_RADIUS * 0.85, bondMat);

    addAtomSphere(group, sat1, BASE_BRANCH_RADIUS, baseMat, uData);
    addAtomSphere(group, sat2, BASE_BRANCH_RADIUS, baseMat, uData);
  }

  return terminalPoint;
}

// Constructor de la Doble Hélice Macromolecular Ball-and-Stick
function buildDNAHelix() {
  if (!mainHelixGroup) return;

  // Limpiar geometría anterior
  while (mainHelixGroup.children.length > 0) {
    const obj = mainHelixGroup.children[0];
    mainHelixGroup.remove(obj);
    if (obj.geometry) obj.geometry.dispose();
  }
  clickableObjects.length = 0;
  backboneMaterials.length = 0;
  baseMaterials.length = 0;

  const seq = displayedSequence.value;
  const N = seq.length;
  if (!N) return;

  const mats = initPBRMaterials();

  // 1. Definir trayectoria central: Curvada S-Bend (In Vivo) o Recta (Lineal)
  const axisPoints = [];
  for (let i = 0; i < N; i++) {
    const s = i / (N - 1);
    const y = (i - (N - 1) / 2) * VERTICAL_STEP;
    let axisX = 0;
    let axisZ = 0;

    if (trajectoryMode.value === 'curved') {
      axisX = Math.sin(s * Math.PI * 1.8) * 2.2;
      axisZ = Math.cos(s * Math.PI * 1.3) * 1.5;
    }
    axisPoints.push(new THREE.Vector3(axisX, y, axisZ));
  }

  // 2. Coordenadas de Azúcares (Desoxirribosas) y Fosfatos a lo largo de cada hebra
  const sugarPoints1 = [];
  const sugarPoints2 = [];
  const phosPoints1 = [];
  const phosPoints2 = [];

  const R_SUGAR = HELIX_RADIUS * 0.90;
  const R_PHOS = HELIX_RADIUS * 1.08;

  for (let i = 0; i < N; i++) {
    const center = axisPoints[i];
    const theta1 = i * ANGLE_STEP;
    const theta2 = theta1 + MINOR_GROOVE_OFFSET;

    const s1 = new THREE.Vector3(
      center.x + R_SUGAR * Math.cos(theta1),
      center.y,
      center.z + R_SUGAR * Math.sin(theta1)
    );
    const s2 = new THREE.Vector3(
      center.x + R_SUGAR * Math.cos(theta2),
      center.y,
      center.z + R_SUGAR * Math.sin(theta2)
    );
    sugarPoints1.push(s1);
    sugarPoints2.push(s2);

    if (i < N - 1) {
      const nextCenter = axisPoints[i + 1];
      const midCenter = new THREE.Vector3().addVectors(center, nextCenter).multiplyScalar(0.5);
      const thetaPhos1 = theta1 + ANGLE_STEP * 0.5;
      const thetaPhos2 = theta2 + ANGLE_STEP * 0.5;

      const p1 = new THREE.Vector3(
        midCenter.x + R_PHOS * Math.cos(thetaPhos1),
        midCenter.y,
        midCenter.z + R_PHOS * Math.sin(thetaPhos1)
      );
      const p2 = new THREE.Vector3(
        midCenter.x + R_PHOS * Math.cos(thetaPhos2),
        midCenter.y,
        midCenter.z + R_PHOS * Math.sin(thetaPhos2)
      );
      phosPoints1.push(p1);
      phosPoints2.push(p2);
    }
  }

  const cleanSeq = props.sequence.toUpperCase().replace(/[^ATCG]/g, '');

  // 3. Construir el Esqueleto Azúcar-Fosfato (Ball-and-Stick Covalente)
  for (let i = 0; i < N; i++) {
    const center = axisPoints[i];
    const s1 = sugarPoints1[i];
    const s2 = sugarPoints2[i];
    const b1 = seq[i];
    const b2 = complementMap[b1] || 'T';
    const seqIndex = cleanSeq.length ? (i % cleanSeq.length) : i;
    const isSelected = (props.selectedPosition !== null && props.selectedPosition !== undefined && i === props.selectedPosition);

    // Esfera de Azúcar (Desoxirribosa - Gris Plateado) en Hebra 1
    const sugarMat1 = isSelected ? mats.selectedSugarMat : mats.sugarMat;
    addAtomSphere(mainHelixGroup, s1, SUGAR_RADIUS, sugarMat1, { index: i, base: b1, strand: 1 });
    // Átomo satélite de azúcar (C2'/OH)
    const s1Tangent = new THREE.Vector3(-(s1.z - center.z), 0, s1.x - center.x).normalize();
    const satS1 = s1.clone().addScaledVector(s1Tangent, 0.28).add(new THREE.Vector3(0, 0.12, 0));
    addCylinderBetween(mainHelixGroup, s1, satS1, COVALENT_BOND_RADIUS * 0.75, mats.bondRodMat);
    addAtomSphere(mainHelixGroup, satS1, SUGAR_SAT_RADIUS, sugarMat1, { index: i, base: b1, strand: 1 });

    // Esfera de Azúcar en Hebra 2
    const sugarMat2 = isSelected ? mats.selectedSugarMat : mats.sugarMat;
    addAtomSphere(mainHelixGroup, s2, SUGAR_RADIUS, sugarMat2, { index: i, base: b2, strand: 2 });
    const s2Tangent = new THREE.Vector3(-(s2.z - center.z), 0, s2.x - center.x).normalize();
    const satS2 = s2.clone().addScaledVector(s2Tangent, 0.28).add(new THREE.Vector3(0, 0.12, 0));
    addCylinderBetween(mainHelixGroup, s2, satS2, COVALENT_BOND_RADIUS * 0.75, mats.bondRodMat);
    addAtomSphere(mainHelixGroup, satS2, SUGAR_SAT_RADIUS, sugarMat2, { index: i, base: b2, strand: 2 });

    // Enlaces de Fosfato intermonómeros
    if (i < N - 1) {
      const p1 = phosPoints1[i];
      const p2 = phosPoints2[i];

      // Enlace Sugar[i] -> Phos[i] -> Sugar[i+1] en Hebra 1
      addCylinderBetween(mainHelixGroup, s1, p1, COVALENT_BOND_RADIUS, mats.bondRodMat);
      addCylinderBetween(mainHelixGroup, p1, sugarPoints1[i + 1], COVALENT_BOND_RADIUS, mats.bondRodMat);
      addAtomSphere(mainHelixGroup, p1, PHOSPHATE_RADIUS, mats.phosphateMat);
      // Átomo satélite de oxígeno (-O) en Fosfato
      const p1Outward = new THREE.Vector3(p1.x - center.x, 0, p1.z - center.z).normalize();
      const satP1 = p1.clone().addScaledVector(p1Outward, 0.32).add(new THREE.Vector3(0, 0.10, 0));
      addCylinderBetween(mainHelixGroup, p1, satP1, COVALENT_BOND_RADIUS * 0.75, mats.bondRodMat);
      addAtomSphere(mainHelixGroup, satP1, PHOSPHATE_SAT_RADIUS, mats.phosphateMat);

      // Enlace Sugar[i] -> Phos[i] -> Sugar[i+1] en Hebra 2
      addCylinderBetween(mainHelixGroup, s2, p2, COVALENT_BOND_RADIUS, mats.bondRodMat);
      addCylinderBetween(mainHelixGroup, p2, sugarPoints2[i + 1], COVALENT_BOND_RADIUS, mats.bondRodMat);
      addAtomSphere(mainHelixGroup, p2, PHOSPHATE_RADIUS, mats.phosphateMat);
      const p2Outward = new THREE.Vector3(p2.x - center.x, 0, p2.z - center.z).normalize();
      const satP2 = p2.clone().addScaledVector(p2Outward, 0.32).add(new THREE.Vector3(0, 0.10, 0));
      addCylinderBetween(mainHelixGroup, p2, satP2, COVALENT_BOND_RADIUS * 0.75, mats.bondRodMat);
      addAtomSphere(mainHelixGroup, satP2, PHOSPHATE_SAT_RADIUS, mats.phosphateMat);
    }
  }

  // 4. Construir Peldaños de Bases Nitrogenadas y Puentes de Hidrógeno
  for (let i = 0; i < N; i++) {
    const s1 = sugarPoints1[i];
    const s2 = sugarPoints2[i];
    const b1 = seq[i];
    const b2 = complementMap[b1] || 'T';
    const seqIndex = cleanSeq.length ? (i % cleanSeq.length) : i;
    const isSelected = (props.selectedPosition !== null && props.selectedPosition !== undefined && i === props.selectedPosition);

    const isPurine1 = (b1 === 'A' || b1 === 'G');
    const isPurine2 = (b2 === 'A' || b2 === 'G');

    const mat1 = isSelected ? (mats.baseSelectedMats[b1] || mats.baseSelectedMats.A) : (mats.baseMats[b1] || mats.baseMats.A);
    const mat2 = isSelected ? (mats.baseSelectedMats[b2] || mats.baseSelectedMats.T) : (mats.baseMats[b2] || mats.baseMats.T);

    const dirTo2 = new THREE.Vector3().subVectors(s2, s1);
    const unit1to2 = dirTo2.clone().normalize();
    const unit2to1 = unit1to2.clone().negate();

    const upDir = new THREE.Vector3(0, 1, 0);
    const crossDir1 = new THREE.Vector3().crossVectors(unit1to2, upDir).normalize();
    const crossDir2 = new THREE.Vector3().crossVectors(unit2to1, upDir).normalize();

    // Ensamblar cluster ball-and-stick de Base 1 (Hebra 1)
    const term1 = buildBaseCluster(mainHelixGroup, s1, unit1to2, crossDir1, upDir, isPurine1, mat1, mats.bondRodMat, i, b1, 1);

    // Ensamblar cluster ball-and-stick de Base 2 (Hebra 2)
    const term2 = buildBaseCluster(mainHelixGroup, s2, unit2to1, crossDir2, upDir, isPurine2, mat2, mats.bondRodMat, i, b2, 2);

    // Puentes de Hidrógeno Centrales: 2 pines para A=T, 3 pines para C≡G
    const hBondCount = (b1 === 'C' || b1 === 'G') ? 3 : 2;
    const pinOffsetStep = 0.14;
    const pinMat = isSelected ? mats.selectedHbondMat : mats.hBondMat;
    const pinRadius = isSelected ? HBOND_PIN_RADIUS * 1.35 : HBOND_PIN_RADIUS;

    for (let p = 0; p < hBondCount; p++) {
      const yShift = (p - (hBondCount - 1) / 2) * pinOffsetStep;
      const shiftVec = new THREE.Vector3(0, yShift, 0);
      const pinStart = term1.clone().add(shiftVec);
      const pinEnd = term2.clone().add(shiftVec);

      addCylinderBetween(mainHelixGroup, pinStart, pinEnd, pinRadius, pinMat);
    }

    // Iluminación Focal y Halo Holográfico Bioluminiscente si el par está seleccionado
    if (isSelected) {
      const midPoint = new THREE.Vector3().addVectors(s1, s2).multiplyScalar(0.5);

      // 1. Luz puntual bioluminiscente que ilumina realmente los átomos del par seleccionado
      const selectLight = new THREE.PointLight(0x38bdf8, 3.8, 6.5);
      selectLight.position.copy(midPoint);
      mainHelixGroup.add(selectLight);

      // 2. Anillo holográfico exterior pulsante
      const haloGeo = new THREE.TorusGeometry(HELIX_RADIUS * 1.15, 0.08, 16, 48);
      const haloMat = new THREE.MeshBasicMaterial({
        color: 0x38bdf8,
        transparent: true,
        opacity: 0.9,
        blending: THREE.AdditiveBlending
      });
      const halo = new THREE.Mesh(haloGeo, haloMat);
      halo.position.copy(midPoint);
      halo.rotation.x = Math.PI / 2;
      halo.userData = { isPulseHalo: true, baseScale: 1.0 };
      mainHelixGroup.add(halo);

      // 3. Anillo concéntrico interior pulsante
      const innerHaloGeo = new THREE.TorusGeometry(HELIX_RADIUS * 0.72, 0.04, 12, 36);
      const innerHaloMat = new THREE.MeshBasicMaterial({
        color: 0x7dd3fc,
        transparent: true,
        opacity: 0.75,
        blending: THREE.AdditiveBlending
      });
      const innerHalo = new THREE.Mesh(innerHaloGeo, innerHaloMat);
      innerHalo.position.copy(midPoint);
      innerHalo.rotation.x = Math.PI / 2;
      innerHalo.userData = { isPulseHalo: true, baseScale: 0.95 };
      mainHelixGroup.add(innerHalo);

      // 4. Haz de luz cilíndrico holográfico conectando ambas hebras (3' y 5')
      const beamDir = new THREE.Vector3().subVectors(s2, s1);
      const beamLen = beamDir.length();
      const beamGeo = new THREE.CylinderGeometry(0.32, 0.32, beamLen, 16, 1, true);
      const beamMat = new THREE.MeshBasicMaterial({
        color: 0x38bdf8,
        transparent: true,
        opacity: 0.22,
        blending: THREE.AdditiveBlending,
        side: THREE.DoubleSide
      });
      const beamMesh = new THREE.Mesh(beamGeo, beamMat);
      beamMesh.position.copy(midPoint);
      beamMesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), beamDir.clone().normalize());
      mainHelixGroup.add(beamMesh);

      // 5. Marcadores de posición beacon en los azúcares 5' y 3'
      const beaconGeo = new THREE.SphereGeometry(0.20, 14, 14);
      const beaconMat = new THREE.MeshBasicMaterial({
        color: 0x70d6ff,
        transparent: true,
        opacity: 0.85,
        blending: THREE.AdditiveBlending
      });
      const b1Mesh = new THREE.Mesh(beaconGeo, beaconMat);
      b1Mesh.position.copy(s1);
      b1Mesh.userData = { isPulseHalo: true, baseScale: 1.0 };
      mainHelixGroup.add(b1Mesh);

      const b2Mesh = new THREE.Mesh(beaconGeo, beaconMat);
      b2Mesh.position.copy(s2);
      b2Mesh.userData = { isPulseHalo: true, baseScale: 1.0 };
      mainHelixGroup.add(b2Mesh);
    }
  }

  // Ajuste y encuadre automático dinámico según la longitud N de la cadena
  fitCameraToHelix(N);
}

// Función de encuadre orbital inteligente para que la hélice se vea cercana, nítida y vibrante desde el inicio
function fitCameraToHelix(N) {
  if (!camera || !controls) return;
  const totalHeight = N * VERTICAL_STEP;
  const fovRad = (camera.fov * Math.PI) / 180;
  const aspect = (camera.aspect && camera.aspect > 0) ? camera.aspect : 1.0;
  const effectiveWidth = (HELIX_RADIUS * 2.6) + (trajectoryMode.value === 'curved' ? 4.0 : 0);
  const effectiveHeight = totalHeight + 1.5;

  const distV = (effectiveHeight * 0.5) / Math.tan(fovRad * 0.5);
  const distH = (effectiveWidth * 0.5) / (Math.tan(fovRad * 0.5) * aspect);
  // Encuadre cercano e inmersivo desde el inicio: llena el visor con colores vivos y detalle
  const targetDist = Math.max(12.0, Math.max(distV, distH) * 0.88);

  const currentDir = new THREE.Vector3(0.18, 0.08, 0.98).normalize();
  camera.position.copy(currentDir.multiplyScalar(targetDist));
  camera.near = 0.5;
  camera.far = Math.max(1200, targetDist * 4.5);
  camera.updateProjectionMatrix();

  controls.target.set(0, 0, 0);
  controls.minDistance = 3.0;
  controls.maxDistance = targetDist * 3.5;
  controls.update();
}



// Constructor de Fórmulas Químicas Realistas en Suspensión Acuosa
function buildChemicalAtmosphere(parentGroup) {
  const types = ['purine', 'pyrimidine', 'ribose', 'phosphate'];
  const textures = types.map(t => createChemicalTexture(t));
  const sprites = [];

  for (let i = 0; i < 32; i++) {
    const tex = textures[i % textures.length];
    const mat = new THREE.SpriteMaterial({
      map: tex,
      transparent: true,
      opacity: 0.12 + Math.random() * 0.18,
      blending: THREE.AdditiveBlending,
      depthWrite: false
    });

    const sprite = new THREE.Sprite(mat);
    const scale = 2.4 + Math.random() * 2.8;
    sprite.scale.set(scale, scale, 1);

    // Ubicados en el fondo lejano para no entorpecer la vista de la doble hélice
    sprite.position.set(
      (Math.random() - 0.5) * 44,
      (Math.random() - 0.5) * 36,
      -12 - Math.random() * 20
    );

    sprite.userData = {
      baseY: sprite.position.y,
      speed: 0.0008 + Math.random() * 0.0012,
      phase: Math.random() * Math.PI * 2,
      rotSpeed: (Math.random() - 0.5) * 0.0015
    };

    parentGroup.add(sprite);
    sprites.push(sprite);
  }

  return sprites;
}

let chemicalSprites = [];

function initScene() {
  const container = canvasContainer.value;
  if (!container) return;

  const width = container.clientWidth || 600;
  const height = container.clientHeight || 580;

  scene = new THREE.Scene();
  // SIN NIEBLA: Eliminamos la niebla para que los colores no se opaquen ni se laven a la distancia

  camera = new THREE.PerspectiveCamera(36, width / height, 0.1, 1000);
  camera.position.set(2.5, 1.2, 14.5);

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
  renderer.setSize(width, height);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05; // Exposición balanceada de estudio fotorrealista sin sobreexposición
  container.appendChild(renderer.domElement);

  // OrbitControls con amortiguación suave
  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.minDistance = 3.0;
  controls.maxDistance = 45.0;
  controls.target.set(0, 0, 0);

  // Iluminación de Estudio Biofísico Equilibrada (Como en la Fotografía de Referencia)
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.95);
  scene.add(ambientLight);

  const keyLight = new THREE.DirectionalLight(0xfffcf5, 2.0);
  keyLight.position.set(16, 20, 14);
  scene.add(keyLight);

  const fillLight = new THREE.DirectionalLight(0xdbeafe, 0.85);
  fillLight.position.set(-16, -10, 8);
  scene.add(fillLight);

  const rimLight = new THREE.DirectionalLight(0xfff7ed, 1.2);
  rimLight.position.set(2, -12, -14);
  scene.add(rimLight);

  // Partículas Bokeh (Capa 1: Orbes en el fondo lejano para no entorpecer la visión)
  const bokehTex = createBokehTexture();
  bokehGroup = new THREE.Group();
  scene.add(bokehGroup);

  for (let i = 0; i < 22; i++) {
    const sMat = new THREE.SpriteMaterial({
      map: bokehTex,
      transparent: true,
      opacity: 0.15 + Math.random() * 0.25,
      blending: THREE.AdditiveBlending,
      depthWrite: false
    });
    const sp = new THREE.Sprite(sMat);
    const sz = 1.6 + Math.random() * 3.0;
    sp.scale.set(sz, sz, 1);
    sp.position.set(
      (Math.random() - 0.5) * 36,
      (Math.random() - 0.5) * 32,
      -10 - Math.random() * 20 // En el fondo, detrás del modelo
    );
    sp.userData = {
      baseY: sp.position.y,
      speed: 0.001 + Math.random() * 0.0015,
      phase: Math.random() * Math.PI * 2
    };
    bokehGroup.add(sp);
  }

  // Partículas Bokeh (Capa 2: Polvo Fino Bioluminiscente en Fondo)
  const dustGeo = new THREE.BufferGeometry();
  const dustCount = 360;
  const dustPos = new Float32Array(dustCount * 3);
  for (let i = 0; i < dustCount * 3; i += 3) {
    dustPos[i] = (Math.random() - 0.5) * 44;
    dustPos[i + 1] = (Math.random() - 0.5) * 40;
    dustPos[i + 2] = -12 - Math.random() * 24; // Fondo lejano para no entorpecer los colores del ADN
  }
  dustGeo.setAttribute('position', new THREE.BufferAttribute(dustPos, 3));
  const dustMat = new THREE.PointsMaterial({
    color: 0x70d6ff,
    size: 0.08,
    map: bokehTex,
    transparent: true,
    opacity: 0.40,
    blending: THREE.AdditiveBlending,
    depthWrite: false
  });
  scene.add(new THREE.Points(dustGeo, dustMat));



  // Fórmulas Químicas Flotantes
  molecularDiagramsGroup = new THREE.Group();
  scene.add(molecularDiagramsGroup);
  chemicalSprites = buildChemicalAtmosphere(molecularDiagramsGroup);

  // Doble Hélice Principal
  mainHelixGroup = new THREE.Group();
  mainHelixGroup.rotation.z = -0.35;
  mainHelixGroup.rotation.x = 0.18;
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
        const hit = intersects[0].object;
        if (hit.userData && hit.userData.index !== undefined) {
          emit('selectBase', hit.userData.index);
        }
      }
    }
  });

  animate();
}

function animate() {
  animId = requestAnimationFrame(animate);
  const t = (performance.now() - startTime) * 0.001;

  // Actualizar uniforms de shaders
  backboneMaterials.forEach(m => {
    if (m.uniforms && m.uniforms.uTime) m.uniforms.uTime.value = t;
  });
  baseMaterials.forEach(m => {
    if (m.uniforms && m.uniforms.uTime) m.uniforms.uTime.value = t;
  });

  // Rotación suave del modelo
  if (mainHelixGroup && isAutoRotating.value) {
    mainHelixGroup.rotation.y += 0.0036;
  }

  // Pulso holográfico suave en los anillos y marcadores del par seleccionado
  if (mainHelixGroup) {
    const pulse = 1.0 + Math.sin(t * 4.5) * 0.08;
    mainHelixGroup.traverse(child => {
      if (child.userData && child.userData.isPulseHalo) {
        const base = child.userData.baseScale || 1.0;
        child.scale.set(base * pulse, base * pulse, base * pulse);
      }
    });
  }



  // Flotación de fórmulas químicas
  if (chemicalSprites && chemicalSprites.length > 0) {
    chemicalSprites.forEach(s => {
      s.position.y = s.userData.baseY + Math.sin(t * 1.2 + s.userData.phase) * 0.55;
    });
  }

  // Flotación de orbes bokeh
  if (bokehGroup) {
    bokehGroup.children.forEach(b => {
      b.position.y = b.userData.baseY + Math.sin(t * 0.8 + b.userData.phase) * 0.45;
    });
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
  mainHelixGroup.rotation.set(0.18, 0, -0.35);
}

watch(() => [props.sequence, props.selectedPosition, trajectoryMode.value], () => {
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

.spectral-pill.a { color: #ef4444; }
.spectral-pill.t { color: #22c55e; }
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

.base-badge.a { background: rgba(239, 68, 68, 0.2); color: #ef4444; border-color: #ef4444; }
.base-badge.t { background: rgba(34, 197, 94, 0.2); color: #22c55e; border-color: #22c55e; }
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
