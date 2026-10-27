<template>
  <div class="dna-3d-card md3-card-outlined" :class="{ 'cinema-expanded': isExpanded }">
    <!-- Header de Tarjeta MD3 (Tonal Surface Header) -->
    <div class="card-header">
      <div class="header-main">
        <div class="header-avatar">
          <Icon name="dna" size="22" />
        </div>
        <div class="header-titles">
          <h3 class="title-text">Modelo Atómico Tridimensional (B-DNA)</h3>
          <span class="subhead-text">
            Modelo Atómico Real reactivo · {{ atomicStats.totalAtoms }} átomos, enlaces covalentes y puentes H Watson-Crick
          </span>
        </div>
      </div>

      <div class="header-chips">
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
          <Icon name="biotech" size="14" class="chip-lead" />
          <span class="font-mono">{{ displayedSequence.length }} bp · {{ atomicStats.totalAtoms }} átomos</span>
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
      <!-- Capa Modelo Atómico Real -->
      <div 
        ref="atomicCanvasHolder" 
        class="atomic-canvas-box"
      ></div>

      <!-- HUD Atómico Superior Izquierdo: Leyenda Biofísica Atómica Original -->
      <div class="hud-card hud-top-left">
        <div class="hud-card-header">
          <span class="hud-label">Modelo Atómico Real (ADN-B)</span>
        </div>
        <div class="spectral-legend-grid">
          <span class="spectral-pill a"><span class="swatch" style="background:#8cccff"></span>A · Adenina</span>
          <span class="spectral-pill t"><span class="swatch" style="background:#4080f2"></span>T · Timina</span>
          <span class="spectral-pill g"><span class="swatch" style="background:#bfe0ff"></span>G · Guanina</span>
          <span class="spectral-pill c"><span class="swatch" style="background:#2659d9"></span>C · Citosina</span>
          <span class="spectral-pill caz"><span class="swatch" style="background:#738cbf"></span>Azúcar (Caz)</span>
          <span class="spectral-pill o"><span class="swatch" style="background:#a6d9ff"></span>Oxígeno (O)</span>
          <span class="spectral-pill p"><span class="swatch" style="background:#3373e6"></span>Fósforo (P)</span>
          <span class="spectral-pill bond"><span class="swatch rod" style="background:#4a6390"></span>Enlace Covalente</span>
          <span class="spectral-pill hbond"><span class="swatch pin" style="background:#8fb4e0"></span>Puente H</span>
        </div>
      </div>

      <!-- HUD Atómico Superior Derecho: Detalle del Par -->
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
            <span>Desoxirribosa (Caz) ↔ Fosfato (PO₄)</span>
          </div>
          <div class="hud-bb-line">
            <span class="hud-bb-tag">3' Hebra:</span>
            <span>Antiparalela (Caz ↔ PO₄)</span>
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
        <button class="md3-icon-btn" @click="resetCamera" title="Restablecer vista inicial">
          <Icon name="refresh" size="18" />
        </button>
      </div>

      <!-- HUD Inferior: Indicador de Navegación -->
      <div class="hud-bottom-dock">
        <div class="dock-content">
          <Icon name="info" size="16" class="dock-icon" />
          <span>Modelo Atómico Real: Arrastra para orbitar · Rueda para zoom · Clic en cualquier átomo para seleccionar par</span>
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
import { 
  generateAtomicDNA, 
  ATOMIC_PALETTE, 
  ATOMIC_RADII, 
  COMPLEMENT_MAP 
} from '../sim/atomicDnaGenerator.js';

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
const atomicCanvasHolder = ref(null);
const isExpanded = ref(false);
const isAutoRotating = ref(true);

let renderer = null;
let scene = null;
let camera = null;
let controls = null;
let mainHelixGroup = null;
let animId = null;
const clickableObjects = [];

const camPos0 = new THREE.Vector3();
const target0 = new THREE.Vector3();

const atomicStats = ref({
  totalAtoms: 0,
  totalBonds: 0,
  pairsCount: 0
});

const cleanFullSequence = computed(() => {
  return props.sequence.toUpperCase().replace(/[^ATCG]/g, '') || 'ATCGATCGATCG';
});

// Modo de visualización: 'full' (todo el gen en 3D) o 'window' (ventana 64 bp para secuencias muy largas)
const viewMode3D = ref('full');

function toggleViewMode3D() {
  viewMode3D.value = (viewMode3D.value === 'full') ? 'window' : 'full';
}

// Secuencia procesada para el renderizador 3D
const displayedSequence = computed(() => {
  const clean = cleanFullSequence.value;
  if (clean.length < 8) {
    let extended = clean;
    while (extended.length < 8) {
      extended += clean;
    }
    return extended.slice(0, 8);
  }
  if (viewMode3D.value === 'window' && clean.length > 64) {
    const sel = (props.selectedPosition !== null && props.selectedPosition !== undefined && props.selectedPosition >= 0) ? props.selectedPosition : 0;
    const start = Math.max(0, Math.min(sel - 32, clean.length - 64));
    return clean.slice(start, start + 64);
  }
  return clean;
});

// Desplazamiento inicial si estamos en modo ventana
const windowStartOffset = computed(() => {
  if (viewMode3D.value === 'window' && cleanFullSequence.value.length > 64) {
    const sel = (props.selectedPosition !== null && props.selectedPosition !== undefined && props.selectedPosition >= 0) ? props.selectedPosition : 0;
    return Math.max(0, Math.min(sel - 32, cleanFullSequence.value.length - 64));
  }
  return 0;
});

const selectedBaseData = computed(() => {
  const clean = props.sequence.toUpperCase().replace(/[^ATCG]/g, '');
  const pos = props.selectedPosition;
  if (!clean || pos === null || pos === undefined || pos < 0 || pos >= clean.length) return null;
  const s1 = clean[pos];
  const s2 = COMPLEMENT_MAP[s1] || 'T';

  const bonds = (s1 === 'A' || s1 === 'T') ? 2 : 3;
  return {
    pos,
    strand1: s1,
    strand2: s2,
    bonds
  };
});

// ========================================================
// GENERADOR Y RENDERIZADOR ATÓMICO 100% FIEL A ADN PRUEBA
// ========================================================
function buildDNAHelix(reframe = false) {
  if (!mainHelixGroup || !scene) return;

  // Limpiar grupo previo
  while (mainHelixGroup.children.length > 0) {
    const obj = mainHelixGroup.children[0];
    mainHelixGroup.remove(obj);
    if (obj.geometry) obj.geometry.dispose();
    if (obj.material) {
      if (Array.isArray(obj.material)) obj.material.forEach(m => m.dispose());
      else obj.material.dispose();
    }
  }
  clickableObjects.length = 0;

  const seq = displayedSequence.value;
  if (!seq || !seq.length) return;

  // 1. Generar la estructura molecular mediante el generador canónico centrado en Z=0
  const atomicData = generateAtomicDNA(seq, true);
  const atoms = atomicData.atoms;
  const bonds = atomicData.bonds;

  atomicStats.value = {
    totalAtoms: atomicData.totalAtoms,
    totalBonds: atomicData.totalBonds,
    pairsCount: atomicData.pairs.length
  };

  const selGlobal = props.selectedPosition;
  const offset = windowStartOffset.value;
  const selLocal = (selGlobal !== null && selGlobal !== undefined) ? (selGlobal - offset) : -1;

  // 2. Malla instanciada de ÁTOMOS (Esferas idénticas a ADN Prueba)
  const geoEsfera = new THREE.SphereGeometry(1, 24, 18);
  const matEsfera = new THREE.MeshStandardMaterial({ 
    roughness: 0.32, 
    metalness: 0.08 
  });
  const mallaAtomos = new THREE.InstancedMesh(geoEsfera, matEsfera, atoms.length);
  const dummy = new THREE.Object3D();
  const color = new THREE.Color();
  const atomPairMap = [];

  atoms.forEach((a, i) => {
    dummy.position.set(a[0], a[1], a[2]);
    const r = (ATOMIC_RADII[a[3]] || 0.7) * 1.15;
    dummy.scale.setScalar(r);
    dummy.updateMatrix();
    mallaAtomos.setMatrixAt(i, dummy.matrix);

    // Detección de par seleccionado para realce luminoso
    const pairIdx = a[5];
    const isSelected = (pairIdx === selLocal);

    if (isSelected) {
      color.setHex(0xffffff);
    } else {
      color.setHex(ATOMIC_PALETTE[a[4]] ?? 0x94a3b8);
    }
    mallaAtomos.setColorAt(i, color);

    atomPairMap.push(pairIdx + offset);
  });

  mallaAtomos.instanceMatrix.needsUpdate = true;
  if (mallaAtomos.instanceColor) mallaAtomos.instanceColor.needsUpdate = true;
  mallaAtomos.userData = { atomPairMap };
  clickableObjects.push(mallaAtomos);
  mainHelixGroup.add(mallaAtomos);

  // 3. Malla instanciada de ENLACES (Cilindros de enlaces covalentes y puentes H)
  const geoCil = new THREE.CylinderGeometry(1, 1, 1, 10);
  const matCil = new THREE.MeshStandardMaterial({ 
    roughness: 0.5, 
    metalness: 0.05 
  });
  const mallaEnlaces = new THREE.InstancedMesh(geoCil, matCil, bonds.length);
  const up = new THREE.Vector3(0, 1, 0);
  const p1 = new THREE.Vector3();
  const p2 = new THREE.Vector3();
  const dir = new THREE.Vector3();
  const med = new THREE.Vector3();

  bonds.forEach((e, i) => {
    const a1 = atoms[e[0]];
    const a2 = atoms[e[1]];
    if (!a1 || !a2) return;

    p1.set(a1[0], a1[1], a1[2]);
    p2.set(a2[0], a2[1], a2[2]);
    dir.subVectors(p2, p1);
    const len = dir.length();
    med.addVectors(p1, p2).multiplyScalar(0.5);

    dummy.position.copy(med);
    dummy.quaternion.setFromUnitVectors(up, dir.normalize());
    const isH = (e[2] === 'h');
    const radius = isH ? 0.09 : 0.17;
    dummy.scale.set(radius, len, radius);
    dummy.updateMatrix();
    mallaEnlaces.setMatrixAt(i, dummy.matrix);

    // Color del enlace según tipo y selección
    const isSelected = (e[3] === selLocal);
    if (isSelected) {
      color.setHex(isH ? 0xa5f3fc : 0x7dd3fc);
    } else {
      color.setHex(isH ? 0x8fb4e0 : 0x4a6390);
    }
    mallaEnlaces.setColorAt(i, color);
  });

  mallaEnlaces.instanceMatrix.needsUpdate = true;
  if (mallaEnlaces.instanceColor) mallaEnlaces.instanceColor.needsUpdate = true;
  mainHelixGroup.add(mallaEnlaces);

  // 4. Anillo horizontal de selección en el par activo (Fiel a la Referencia)
  if (selLocal >= 0 && selLocal < atomicData.pairs.length) {
    const activePair = atomicData.pairs[selLocal];
    const ringGeo = new THREE.RingGeometry(12.5, 14.2, 48);
    const ringMat = new THREE.MeshBasicMaterial({ 
      color: 0x38bdf8, 
      side: THREE.DoubleSide, 
      transparent: true, 
      opacity: 0.75 
    });
    const ringMesh = new THREE.Mesh(ringGeo, ringMat);
    ringMesh.position.set(0, 0, activePair.centerZ);
    mainHelixGroup.add(ringMesh);

    const sl = new THREE.PointLight(0x38bdf8, 2.5, 30.0);
    sl.position.set(0, 0, activePair.centerZ);
    mainHelixGroup.add(sl);
  }

  if (reframe) {
    encuadrar(atoms.map(a => [a[0], a[1], a[2]]));
  }
}

// Encuadre de cámara vertical natural
function encuadrar(puntos) {
  if (!camera || !controls || !puntos.length) return;

  const caja = new THREE.Box3();
  // Los puntos locales [x, y, z] se mapean a espacio de mundo vertical [x, z, -y] con rotation.x = -PI/2
  puntos.forEach(p => caja.expandByPoint(new THREE.Vector3(p[0], p[2], -p[1])));
  const centro = caja.getCenter(new THREE.Vector3());
  const tam = caja.getSize(new THREE.Vector3());
  const dist = Math.max(tam.x, tam.y, tam.z) * 1.55;

  camera.position.set(0, centro.y, dist);
  controls.target.set(0, centro.y, 0);
  camPos0.copy(camera.position);
  target0.copy(controls.target);
  controls.update();
}

function initScene() {
  const container = atomicCanvasHolder.value || canvasContainer.value;
  if (!container) return;

  const width = container.clientWidth || 600;
  const height = container.clientHeight || 580;

  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x020612);
  scene.fog = new THREE.Fog(0x020612, 180, 520);

  camera = new THREE.PerspectiveCamera(40, width / height, 0.1, 3000);

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false, powerPreference: 'high-performance' });
  renderer.setSize(width, height);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.15;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  container.appendChild(renderer.domElement);

  // Iluminación fiel a ADN Prueba
  scene.add(new THREE.HemisphereLight(0xbfd9ff, 0x0a1230, 0.85));

  const clave = new THREE.DirectionalLight(0xffffff, 1.9);
  clave.position.set(60, 90, 50);
  scene.add(clave);

  const borde = new THREE.DirectionalLight(0x60a5fa, 1.4);
  borde.position.set(-70, -30, -60);
  scene.add(borde);

  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.06;
  controls.autoRotate = true;
  controls.autoRotateSpeed = 0.9;
  controls.minDistance = 6.0;
  controls.maxDistance = 2500.0;

  mainHelixGroup = new THREE.Group();
  // Rota -PI/2 en X para que el eje Z del generador atómico sea el eje vertical Y
  mainHelixGroup.rotation.x = -Math.PI / 2;
  scene.add(mainHelixGroup);

  buildDNAHelix(true);

  // Raycaster para selección interactiva precisa al hacer clic en cualquier átomo
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
        if (obj.userData?.atomPairMap && hit.instanceId !== undefined) {
          const globalPairIdx = obj.userData.atomPairMap[hit.instanceId];
          if (globalPairIdx !== undefined) {
            emit('selectBase', globalPairIdx);
          }
        }
      }
    }
  });

  animate();
}

function animate() {
  animId = requestAnimationFrame(animate);
  controls?.update();
  if (renderer && scene && camera) {
    renderer.render(scene, camera);
  }
}

let resizeObserver = null;

function onWindowResize() {
  const container = atomicCanvasHolder.value || canvasContainer.value;
  if (!renderer || !camera || !container) return;
  const width = container.clientWidth;
  const height = container.clientHeight;
  if (width <= 0 || height <= 0) return;
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
  renderer.setSize(width, height);
}

function toggleAutoRotate() {
  isAutoRotating.value = !isAutoRotating.value;
  if (controls) controls.autoRotate = isAutoRotating.value;
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
  if (!camera || !controls) return;
  camera.position.copy(camPos0);
  controls.target.copy(target0);
  controls.update();
}

watch(() => props.sequence, () => {
  buildDNAHelix(true);
});

watch(() => [props.selectedPosition, viewMode3D.value], () => {
  buildDNAHelix(false);
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
  setTimeout(onWindowResize, 60);
  setTimeout(onWindowResize, 250);
});

onUnmounted(() => {
  if (animId) cancelAnimationFrame(animId);
  window.removeEventListener('resize', onWindowResize);
  if (resizeObserver) {
    resizeObserver.disconnect();
    resizeObserver = null;
  }
  if (controls) controls.dispose();
  if (renderer) renderer.dispose();
});
</script>

<style scoped>
/* Contenedor Principal de la Tarjeta */
.dna-3d-card {
  position: relative;
  background-color: var(--md-sys-color-surface-container-low, #0b1329);
  border-radius: var(--md-sys-shape-corner-medium, 16px);
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
  border: 1px solid rgba(56, 189, 248, 0.15);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
}

.dna-3d-card.cinema-expanded {
  position: fixed;
  inset: 12px;
  z-index: 1000;
  height: calc(100vh - 24px) !important;
  box-shadow: 0 0 50px rgba(0, 0, 0, 0.9), 0 0 20px rgba(56, 189, 248, 0.3);
  border: 1px solid #38bdf8;
}

/* Header de la tarjeta */
.card-header {
  padding: 0.85rem 1.25rem;
  background-color: var(--md-sys-color-surface-container, #0f172a);
  border-bottom: 1px solid rgba(56, 189, 248, 0.12);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.header-main {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.header-avatar {
  width: 42px;
  height: 42px;
  border-radius: var(--md-sys-shape-corner-small, 8px);
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
  font-size: 1.05rem;
  color: #f1f5f9;
  font-weight: 700;
  letter-spacing: -0.2px;
  margin: 0;
}

.subhead-text {
  font-size: 0.78rem;
  color: #94a3b8;
}

.header-chips {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.chip-lead {
  color: #38bdf8;
}

.interactive-chip {
  cursor: pointer;
  background-color: var(--md-sys-color-surface-container, #1e293b);
  border: 1px solid rgba(56, 189, 248, 0.3);
  transition: all 0.2s ease;
}

.interactive-chip:hover {
  background-color: #334155;
  border-color: #38bdf8;
  transform: translateY(-1px);
}

.atomic-canvas-box {
  width: 100%;
  height: 100%;
  min-height: 600px;
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
  background: #020612;
}

.dna-3d-card.cinema-expanded .canvas-wrapper {
  height: calc(100vh - 120px);
}

.canvas-wrapper:active {
  cursor: grabbing;
}

/* Floating HUDs */
.hud-card {
  position: absolute;
  background: rgba(11, 19, 41, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(56, 189, 248, 0.25);
  border-radius: var(--md-sys-shape-corner-medium, 12px);
  padding: 0.85rem 1rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
  z-index: 10;
  pointer-events: auto;
}

.hud-top-left {
  top: 1rem;
  left: 1rem;
  max-width: 320px;
}

.hud-top-right {
  top: 1rem;
  right: 1rem;
  min-width: 260px;
}

.hud-card-header {
  margin-bottom: 0.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  padding-bottom: 0.25rem;
}

.hud-label {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: #38bdf8;
}

/* Leyenda Atómica */
.spectral-legend-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.45rem 0.5rem;
}

.spectral-pill {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.75rem;
  color: #cbd5e1;
  font-family: monospace;
}

.swatch {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}

.swatch.rod {
  border-radius: 2px;
  width: 12px;
  height: 4px;
}

.swatch.pin {
  border-radius: 1px;
  width: 12px;
  height: 2px;
  background: repeating-linear-gradient(90deg, #8fb4e0 0, #8fb4e0 2px, transparent 2px, transparent 4px) !important;
}

/* Nucleótido Dúplex Activo */
.pair-display-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin: 0.5rem 0;
}

.base-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.25rem 0.65rem;
  border-radius: var(--md-sys-shape-corner-small, 6px);
  background: rgba(30, 41, 59, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.base-badge.a { border-color: #8cccff; color: #8cccff; }
.base-badge.t { border-color: #4080f2; color: #4080f2; }
.base-badge.g { border-color: #bfe0ff; color: #bfe0ff; }
.base-badge.c { border-color: #2659d9; color: #60a5fa; }

.base-letter {
  font-size: 1.4rem;
  font-weight: 700;
  line-height: 1;
}

.strand-id {
  font-size: 0.6rem;
  opacity: 0.7;
}

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
  width: 6px;
  height: 6px;
  background-color: #8fb4e0;
  border-radius: 50%;
  box-shadow: 0 0 6px #8fb4e0;
}

.bond-caption {
  font-size: 0.68rem;
  color: #94a3b8;
}

.hud-backbone-detail {
  font-size: 0.7rem;
  color: #94a3b8;
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.hud-bb-tag {
  color: #38bdf8;
  font-family: monospace;
  margin-right: 0.25rem;
}

/* Floating Toolbar */
.hud-toolbar {
  position: absolute;
  bottom: 3.5rem;
  right: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  z-index: 10;
}

.md3-icon-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(56, 189, 248, 0.25);
  color: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  backdrop-filter: blur(8px);
}

.md3-icon-btn:hover {
  background: rgba(56, 189, 248, 0.2);
  border-color: #38bdf8;
  color: #38bdf8;
}

.md3-icon-btn.active {
  background: rgba(56, 189, 248, 0.3);
  border-color: #38bdf8;
  color: #38bdf8;
}

/* Bottom Navigation Dock */
.hud-bottom-dock {
  position: absolute;
  bottom: 0.75rem;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(15, 23, 42, 0.8);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 9999px;
  padding: 0.35rem 1rem;
  z-index: 10;
  pointer-events: none;
}

.dock-content {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.72rem;
  color: #94a3b8;
}

.dock-icon {
  color: #38bdf8;
}
</style>
