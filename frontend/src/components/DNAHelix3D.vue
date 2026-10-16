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
      <div class="hud-card hud-top-left">
        <div class="hud-card-header">
          <span class="hud-label">Código Espectral de Bases</span>
        </div>
        <div class="spectral-legend-grid">
          <span class="spectral-pill a"><span class="swatch"></span>A · Adenina</span>
          <span class="spectral-pill t"><span class="swatch"></span>T · Timina</span>
          <span class="spectral-pill c"><span class="swatch"></span>C · Citosina</span>
          <span class="spectral-pill g"><span class="swatch"></span>G · Guanina</span>
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

// Colores de bases alineados con el sistema espectral de BioSIM
const baseColors = {
  A: { main: 0xf43f5e, emissive: 0x9f1239, rim: 0xfecdd3, name: 'Adenina' },   // Coral Carmín
  T: { main: 0x10b981, emissive: 0x065f46, rim: 0xa7f3d0, name: 'Timina' },    // Esmeralda Jade
  C: { main: 0x06b6d4, emissive: 0x155e75, rim: 0xa5f3fc, name: 'Citosina' },  // Cian Zafiro
  G: { main: 0xf59e0b, emissive: 0xb45309, rim: 0xfef08a, name: 'Guanina' }   // Ámbar Topacio
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

// Parámetros Estructurales de Doble Hélice B-DNA
const HELIX_RADIUS = 2.65;
const VERTICAL_STEP = 0.58;
const ANGLE_STEP = (Math.PI * 2) / 10.5; // ~34.3° por par de bases
const MINOR_GROOVE_OFFSET = 2.42; // ~138° desfase de surco menor
const BACKBONE_CORE_RADIUS = 0.28; // Radio del tubo conector interno
const MONOMER_POD_RADIUS = 0.48; // Radio de cada monómero globular de desoxirribosa
const BASE_LOBE_RADIUS = 0.24; // Radio de los lóbulos de las bases nitrogenadas

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

// Shader GLSL Avanzado para el Esqueleto Bio-Polimérico de Azúcar-Fosfato
function createBackboneShader(isBackground = false) {
  const mat = new THREE.ShaderMaterial({
    uniforms: {
      uTime: { value: 0 },
      uBaseColor: { value: new THREE.Color(0x0284c7) },
      uCoreColor: { value: new THREE.Color(0x00274d) },
      uRimColor: { value: new THREE.Color(0x70d6ff) },
      uOpacity: { value: isBackground ? 0.38 : 0.96 }
    },
    vertexShader: `
      varying vec3 vNormal;
      varying vec3 vViewPos;
      varying vec3 vWorldPos;
      varying vec2 vUv;
      uniform float uTime;

      void main() {
        vUv = uv;
        vec3 pos = position;

        // Estrías periódicas que esculpen los surcos de los monómeros
        float rib = sin(pos.y * 12.0) * 0.024;
        pos += normal * rib;

        vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
        vViewPos = -mvPosition.xyz;
        vWorldPos = (modelMatrix * vec4(pos, 1.0)).xyz;
        vNormal = normalize(normalMatrix * normal);
        gl_Position = projectionMatrix * mvPosition;
      }
    `,
    fragmentShader: `
      uniform vec3 uBaseColor;
      uniform vec3 uCoreColor;
      uniform vec3 uRimColor;
      uniform float uTime;
      uniform float uOpacity;
      varying vec3 vNormal;
      varying vec3 vViewPos;
      varying vec3 vWorldPos;
      varying vec2 vUv;

      // Simplex 3D noise simplificado para textura biológica micro-celular
      vec3 mod289(vec3 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
      vec4 mod289(vec4 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
      vec4 permute(vec4 x) { return mod289(((x*34.0)+1.0)*x); }
      vec4 taylorInvSqrt(vec4 r) { return 1.79284291400159 - 0.85373472095314 * r; }

      float snoise(vec3 v) {
        const vec2 C = vec2(1.0/6.0, 1.0/3.0);
        const vec4 D = vec4(0.0, 0.5, 1.0, 2.0);
        vec3 i  = floor(v + dot(v, C.yyy));
        vec3 x0 = v - i + dot(i, C.xxx);
        vec3 g = step(x0.yzx, x0.xyz);
        vec3 l = 1.0 - g;
        vec3 i1 = min(g.xyz, l.zxy);
        vec3 i2 = max(g.xyz, l.zxy);
        vec3 x1 = x0 - i1 + C.xxx;
        vec3 x2 = x0 - i2 + C.yyy;
        vec3 x3 = x0 - D.yyy;
        i = mod289(i);
        vec4 p = permute(permute(permute(
                   i.z + vec4(0.0, i1.z, i2.z, 1.0))
                 + i.y + vec4(0.0, i1.y, i2.y, 1.0))
                 + i.x + vec4(0.0, i1.x, i2.x, 1.0));
        float n_ = 0.142857142857;
        vec3 ns = n_ * D.wyz - D.xzx;
        vec4 j = p - 49.0 * floor(p * ns.z * ns.z);
        vec4 x_ = floor(j * ns.z);
        vec4 y_ = floor(j - 7.0 * x_);
        vec4 x = x_ *ns.x + ns.yyyy;
        vec4 y = y_ *ns.x + ns.yyyy;
        vec4 h = 1.0 - abs(x) - abs(y);
        vec4 b0 = vec4(x.xy, y.xy);
        vec4 b1 = vec4(x.zw, y.zw);
        vec4 s0 = floor(b0)*2.0 + 1.0;
        vec4 s1 = floor(b1)*2.0 + 1.0;
        vec4 sh = -step(h, vec4(0.0));
        vec4 a0 = b0.xzyw + s0.xzyw*sh.xxyy;
        vec4 a1 = b1.xzyw + s1.xzyw*sh.zzww;
        vec3 p0 = vec3(a0.xy, h.x);
        vec3 p1 = vec3(a0.zw, h.y);
        vec3 p2 = vec3(a1.xy, h.z);
        vec3 p3 = vec3(a1.zw, h.w);
        vec4 norm = taylorInvSqrt(vec4(dot(p0,p0), dot(p1,p1), dot(p2, p2), dot(p3,p3)));
        p0 *= norm.x; p1 *= norm.y; p2 *= norm.z; p3 *= norm.w;
        vec4 m = max(0.6 - vec4(dot(x0,x0), dot(x1,x1), dot(x2,x2), dot(x3,x3)), 0.0);
        m = m * m;
        return 42.0 * dot(m*m, vec4(dot(p0,x0), dot(p1,x1), dot(p2,x2), dot(p3,x3)));
      }

      void main() {
        vec3 n = normalize(vNormal);
        vec3 v = normalize(vViewPos);

        // Perturbación sutil de micro-rugosidad orgánica celular
        float noiseVal = snoise(vWorldPos * 3.4);
        n = normalize(n + vec3(noiseVal * 0.12));

        // Fresnel de borde intenso idéntico a la imagen de referencia
        float fresnel = pow(1.0 - abs(dot(n, v)), 1.75);

        // Dispersión biológica subsuperficial (Subsurface Scattering approximation)
        vec3 lightDir = normalize(vec3(1.2, 1.8, 1.0));
        float sss = max(0.0, dot(n, lightDir) * 0.5 + 0.5);

        // Onda bioeléctrica luminosa que recorre la espiral
        float pulseWave = sin(vWorldPos.y * 1.5 - uTime * 2.0) * 0.5 + 0.5;

        // Bandas de absorción en las hendiduras segmentadas
        float grooveCreep = sin(vWorldPos.y * 10.5) * 0.15;

        vec3 coreGrad = mix(uCoreColor, uBaseColor, sss + grooveCreep);
        vec3 finalColor = mix(coreGrad, uRimColor, clamp(fresnel * 1.45, 0.0, 1.0));
        finalColor += uRimColor * pulseWave * 0.35;

        // Reflejo especular brillante de biolaboratorio
        vec3 halfDir = normalize(lightDir + v);
        float spec = pow(max(dot(n, halfDir), 0.0), 45.0);
        finalColor += vec3(0.9, 0.98, 1.0) * spec * 0.75;

        gl_FragColor = vec4(finalColor, uOpacity);
      }
    `,
    transparent: true,
    side: THREE.DoubleSide
  });
  backboneMaterials.push(mat);
  return mat;
}

// Shader para las Bases Nitrogenadas (Efecto Gel Translúcido con Resplandor Interno)
function createBaseGelShader(colorHex, emissiveHex, rimHex, isSelected = false) {
  const mat = new THREE.ShaderMaterial({
    uniforms: {
      uTime: { value: 0 },
      uBaseColor: { value: new THREE.Color(colorHex) },
      uEmissiveColor: { value: new THREE.Color(emissiveHex) },
      uRimColor: { value: new THREE.Color(rimHex) },
      uSelected: { value: isSelected ? 1.0 : 0.0 }
    },
    vertexShader: `
      varying vec3 vNormal;
      varying vec3 vViewPos;
      varying vec3 vWorldPos;

      void main() {
        vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
        vViewPos = -mvPosition.xyz;
        vWorldPos = (modelMatrix * vec4(position, 1.0)).xyz;
        vNormal = normalize(normalMatrix * normal);
        gl_Position = projectionMatrix * mvPosition;
      }
    `,
    fragmentShader: `
      uniform vec3 uBaseColor;
      uniform vec3 uEmissiveColor;
      uniform vec3 uRimColor;
      uniform float uTime;
      uniform float uSelected;
      varying vec3 vNormal;
      varying vec3 vViewPos;
      varying vec3 vWorldPos;

      void main() {
        vec3 n = normalize(vNormal);
        vec3 v = normalize(vViewPos);

        float fresnel = pow(1.0 - abs(dot(n, v)), 1.9);
        vec3 lightDir = normalize(vec3(0.8, 1.5, 1.0));
        float diff = max(dot(n, lightDir), 0.0) * 0.65 + 0.35;

        // Pulso eléctrico si está seleccionada
        float pulse = uSelected * (sin(uTime * 5.0) * 0.3 + 0.7);

        vec3 body = mix(uEmissiveColor, uBaseColor, diff);
        vec3 col = mix(body, uRimColor, clamp(fresnel * (1.2 + pulse * 0.8), 0.0, 1.0));
        col += uRimColor * pulse * 0.45;

        // Especular nítido
        vec3 halfDir = normalize(lightDir + v);
        float spec = pow(max(dot(n, halfDir), 0.0), 32.0);
        col += vec3(1.0) * spec * 0.6;

        gl_FragColor = vec4(col, 0.95);
      }
    `,
    transparent: true
  });
  baseMaterials.push(mat);
  return mat;
}

// Constructor de la Doble Hélice Principal
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

  const strand1Points = [];
  const strand2Points = [];
  const axisPoints = [];

  // 1. Definir trayectoria central: Curvada S-Bend (In Vivo) o Recta (Lineal)
  for (let i = 0; i < N; i++) {
    const s = i / (N - 1);
    const y = (i - (N - 1) / 2) * VERTICAL_STEP;
    let axisX = 0;
    let axisZ = 0;

    if (trajectoryMode.value === 'curved') {
      // Curva macromolecular sinuosa y orgánica
      axisX = Math.sin(s * Math.PI * 1.8) * 2.2;
      axisZ = Math.cos(s * Math.PI * 1.3) * 1.5;
    }
    axisPoints.push(new THREE.Vector3(axisX, y, axisZ));
  }

  const axisCurve = new THREE.CatmullRomCurve3(axisPoints);

  // 2. Calcular coordenadas helicoidales a lo largo de la trayectoria con Surco Mayor y Menor
  const podGeo = new THREE.SphereGeometry(MONOMER_POD_RADIUS, 18, 14);
  podGeo.scale(0.85, 0.65, 1.25); // Forma anatómica de vaina de desoxirribosa

  const sharedBackboneMat = createBackboneShader();

  for (let i = 0; i < N; i++) {
    const theta1 = i * ANGLE_STEP;
    const theta2 = theta1 + MINOR_GROOVE_OFFSET;
    const center = axisPoints[i];

    // Orientación tangente y normal local
    const p1 = new THREE.Vector3(
      center.x + HELIX_RADIUS * Math.cos(theta1),
      center.y,
      center.z + HELIX_RADIUS * Math.sin(theta1)
    );

    const p2 = new THREE.Vector3(
      center.x + HELIX_RADIUS * Math.cos(theta2),
      center.y,
      center.z + HELIX_RADIUS * Math.sin(theta2)
    );

    strand1Points.push(p1);
    strand2Points.push(p2);

    // Monómero abultado de desoxirribosa en Hebra 1
    const pod1 = new THREE.Mesh(podGeo, sharedBackboneMat);
    pod1.position.copy(p1);
    pod1.lookAt(center);
    mainHelixGroup.add(pod1);

    // Monómero abultado de desoxirribosa en Hebra 2
    const pod2 = new THREE.Mesh(podGeo, sharedBackboneMat);
    pod2.position.copy(p2);
    pod2.lookAt(center);
    mainHelixGroup.add(pod2);
  }

  // 3. Cadenas Continuas Internas (Vaina Continua que une los monómeros)
  if (N >= 2) {
    const curve1 = new THREE.CatmullRomCurve3(strand1Points);
    const tubeGeo1 = new THREE.TubeGeometry(curve1, N * 24, BACKBONE_CORE_RADIUS, 20, false);
    const tubeMesh1 = new THREE.Mesh(tubeGeo1, sharedBackboneMat);
    mainHelixGroup.add(tubeMesh1);

    const curve2 = new THREE.CatmullRomCurve3(strand2Points);
    const tubeGeo2 = new THREE.TubeGeometry(curve2, N * 24, BACKBONE_CORE_RADIUS, 20, false);
    const tubeMesh2 = new THREE.Mesh(tubeGeo2, sharedBackboneMat);
    mainHelixGroup.add(tubeMesh2);
  }

  // 4. Peldaños de Pares de Bases Nitrogenadas (Lóbulos Orgánicos Sólidos)
  for (let i = 0; i < N; i++) {
    const p1 = strand1Points[i];
    const p2 = strand2Points[i];
    const b1 = seq[i];
    const b2 = complementMap[b1] || 'T';
    const isSelected = (i === props.selectedPosition);

    const colorDef1 = baseColors[b1] || baseColors.A;
    const colorDef2 = baseColors[b2] || baseColors.T;

    const dir = new THREE.Vector3().subVectors(p2, p1);
    const totalDist = dir.length();
    const unitDir = dir.clone().normalize();

    // Las purinas (A, G) son anatómicamente más largas (~55%) que las pirimidinas (T, C, ~45%)
    const isPurine1 = (b1 === 'A' || b1 === 'G');
    const frac1 = isPurine1 ? 0.44 : 0.38;
    const frac2 = isPurine1 ? 0.38 : 0.44;

    const len1 = totalDist * frac1;
    const len2 = totalDist * frac2;

    const mat1 = createBaseGelShader(colorDef1.main, colorDef1.emissive, colorDef1.rim, isSelected);
    const mat2 = createBaseGelShader(colorDef2.main, colorDef2.emissive, colorDef2.rim, isSelected);

    // Lóbulo Cápsula Base 1
    const lobeGeo1 = new THREE.CapsuleGeometry(BASE_LOBE_RADIUS, Math.max(0.1, len1 - BASE_LOBE_RADIUS * 2), 14, 18);
    const mesh1 = new THREE.Mesh(lobeGeo1, mat1);
    const center1 = p1.clone().addScaledVector(unitDir, len1 * 0.5);
    mesh1.position.copy(center1);
    mesh1.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), unitDir);
    mesh1.userData = { index: i, base: b1, strand: 1 };
    mainHelixGroup.add(mesh1);
    clickableObjects.push(mesh1);

    // Lóbulo Cápsula Base 2
    const lobeGeo2 = new THREE.CapsuleGeometry(BASE_LOBE_RADIUS, Math.max(0.1, len2 - BASE_LOBE_RADIUS * 2), 14, 18);
    const mesh2 = new THREE.Mesh(lobeGeo2, mat2);
    const center2 = p2.clone().addScaledVector(unitDir.clone().negate(), len2 * 0.5);
    mesh2.position.copy(center2);
    mesh2.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), unitDir);
    mesh2.userData = { index: i, base: b2, strand: 2 };
    mainHelixGroup.add(mesh2);
    clickableObjects.push(mesh2);

    // Puentes de Hidrógeno Centrales (2 pines para A-T, 3 pines para C-G)
    const midPoint = new THREE.Vector3().addVectors(p1, p2).multiplyScalar(0.5);
    const bondsCount = (b1 === 'C' || b1 === 'G') ? 3 : 2;
    const gapLen = totalDist - len1 - len2;

    const bondMat = new THREE.MeshStandardMaterial({
      color: isSelected ? 0x70d6ff : 0x38bdf8,
      emissive: isSelected ? 0x70d6ff : 0x0284c7,
      emissiveIntensity: isSelected ? 2.5 : 1.4,
      roughness: 0.15,
      metalness: 0.3
    });

    const bondGeo = new THREE.CylinderGeometry(0.045, 0.045, Math.max(0.15, gapLen), 8);

    for (let b = 0; b < bondsCount; b++) {
      const yShift = (b - (bondsCount - 1) / 2) * 0.14;
      const bMesh = new THREE.Mesh(bondGeo, bondMat);
      const bPos = midPoint.clone().add(new THREE.Vector3(0, yShift, 0));
      bMesh.position.copy(bPos);
      bMesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), unitDir);
      mainHelixGroup.add(bMesh);
    }

    // Halo bioeléctrico de selección en el par activo
    if (isSelected) {
      const haloGeo = new THREE.TorusGeometry(HELIX_RADIUS * 1.15, 0.06, 12, 32);
      const haloMat = new THREE.MeshBasicMaterial({
        color: 0x70d6ff,
        transparent: true,
        opacity: 0.85,
        blending: THREE.AdditiveBlending
      });
      const halo = new THREE.Mesh(haloGeo, haloMat);
      halo.position.copy(midPoint);
      halo.rotation.x = Math.PI / 2;
      mainHelixGroup.add(halo);
    }
  }

  // Ajuste y encuadre automático dinámico según la longitud N de la cadena
  fitCameraToHelix(N);
}

// Función de encuadre orbital inteligente para evitar que la hélice se corte
function fitCameraToHelix(N) {
  if (!camera || !controls) return;
  const totalHeight = N * VERTICAL_STEP;
  const fovRad = (camera.fov * Math.PI) / 180;
  const aspect = (camera.aspect && camera.aspect > 0) ? camera.aspect : 1.0;
  const effectiveWidth = (HELIX_RADIUS * 2.6) + (trajectoryMode.value === 'curved' ? 5.5 : 0);
  const effectiveHeight = totalHeight + 4.5;

  const distV = (effectiveHeight * 0.5) / Math.tan(fovRad * 0.5);
  const distH = (effectiveWidth * 0.5) / (Math.tan(fovRad * 0.5) * aspect);
  const targetDist = Math.max(17.0, Math.max(distV, distH) * 1.18);

  const currentDir = new THREE.Vector3(0.18, 0.08, 0.98).normalize();
  camera.position.copy(currentDir.multiplyScalar(targetDist));
  camera.near = 0.5;
  camera.far = Math.max(1200, targetDist * 4.5);
  camera.updateProjectionMatrix();

  controls.target.set(0, 0, 0);
  controls.minDistance = 5.0;
  controls.maxDistance = targetDist * 3.5;
  controls.update();
}



// Constructor de Fórmulas Químicas Realistas en Suspensión Acuosa
function buildChemicalAtmosphere(parentGroup) {
  const types = ['purine', 'pyrimidine', 'ribose', 'phosphate'];
  const textures = types.map(t => createChemicalTexture(t));
  const sprites = [];

  for (let i = 0; i < 48; i++) {
    const tex = textures[i % textures.length];
    const mat = new THREE.SpriteMaterial({
      map: tex,
      transparent: true,
      opacity: 0.18 + Math.random() * 0.28,
      blending: THREE.AdditiveBlending,
      depthWrite: false
    });

    const sprite = new THREE.Sprite(mat);
    const scale = 2.8 + Math.random() * 3.4;
    sprite.scale.set(scale, scale, 1);

    sprite.position.set(
      (Math.random() - 0.5) * 44,
      (Math.random() - 0.5) * 36,
      -6 - Math.random() * 22
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
  // Niebla oceánica profunda
  scene.fog = new THREE.FogExp2(0x021c3b, 0.022);

  camera = new THREE.PerspectiveCamera(36, width / height, 0.1, 1000);
  camera.position.set(3.5, 1.5, 17.5);

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
  renderer.setSize(width, height);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.45;
  container.appendChild(renderer.domElement);

  // OrbitControls con amortiguación suave
  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.minDistance = 4.0;
  controls.maxDistance = 42.0;
  controls.target.set(0, 0, 0);

  // Iluminación Cinemática de Laboratorio
  const ambientLight = new THREE.AmbientLight(0x062846, 1.8);
  scene.add(ambientLight);

  const keyLight = new THREE.DirectionalLight(0xe0f2fe, 3.2);
  keyLight.position.set(16, 20, 14);
  scene.add(keyLight);

  const fillLight = new THREE.DirectionalLight(0x0284c7, 2.2);
  fillLight.position.set(-16, -12, -8);
  scene.add(fillLight);

  const rimLight = new THREE.DirectionalLight(0x70d6ff, 3.8);
  rimLight.position.set(2, -14, -16);
  scene.add(rimLight);

  // Partículas Bokeh (Capa 1: Orbes Grandes Difusos)
  const bokehTex = createBokehTexture();
  bokehGroup = new THREE.Group();
  scene.add(bokehGroup);

  for (let i = 0; i < 28; i++) {
    const sMat = new THREE.SpriteMaterial({
      map: bokehTex,
      transparent: true,
      opacity: 0.22 + Math.random() * 0.35,
      blending: THREE.AdditiveBlending,
      depthWrite: false
    });
    const sp = new THREE.Sprite(sMat);
    const sz = 1.8 + Math.random() * 3.6;
    sp.scale.set(sz, sz, 1);
    sp.position.set(
      (Math.random() - 0.5) * 32,
      (Math.random() - 0.5) * 28,
      (Math.random() - 0.5) * 20
    );
    sp.userData = {
      baseY: sp.position.y,
      speed: 0.001 + Math.random() * 0.0015,
      phase: Math.random() * Math.PI * 2
    };
    bokehGroup.add(sp);
  }

  // Partículas Bokeh (Capa 2: Polvo Fino Bioluminiscente)
  const dustGeo = new THREE.BufferGeometry();
  const dustCount = 480;
  const dustPos = new Float32Array(dustCount * 3);
  for (let i = 0; i < dustCount * 3; i += 3) {
    dustPos[i] = (Math.random() - 0.5) * 42;
    dustPos[i + 1] = (Math.random() - 0.5) * 38;
    dustPos[i + 2] = (Math.random() - 0.5) * 28;
  }
  dustGeo.setAttribute('position', new THREE.BufferAttribute(dustPos, 3));
  const dustMat = new THREE.PointsMaterial({
    color: 0x70d6ff,
    size: 0.08,
    map: bokehTex,
    transparent: true,
    opacity: 0.55,
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
  background: radial-gradient(ellipse at 42% 38%, #09477d 0%, #04294f 35%, #01162c 70%, #000814 100%);
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

.spectral-pill.a { color: #f43f5e; }
.spectral-pill.t { color: #10b981; }
.spectral-pill.c { color: #06b6d4; }
.spectral-pill.g { color: #f59e0b; }

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

.base-badge.a { background: rgba(244, 63, 94, 0.2); color: #f43f5e; border-color: #f43f5e; }
.base-badge.t { background: rgba(16, 185, 129, 0.2); color: #10b981; border-color: #10b981; }
.base-badge.c { background: rgba(6, 182, 212, 0.2); color: #06b6d4; border-color: #06b6d4; }
.base-badge.g { background: rgba(245, 158, 11, 0.2); color: #f59e0b; border-color: #f59e0b; }

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
  background-color: #70d6ff;
  box-shadow: 0 0 6px #70d6ff;
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
</style>
