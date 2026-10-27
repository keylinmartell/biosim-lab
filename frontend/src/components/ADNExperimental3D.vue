<!--
  ADNExperimental3D.vue — BioSim Lab
  Modelo ATÓMICO REAL de ADN-B (855 átomos, 985 enlaces, 21 pb).
  Fiel 100% al diseño de ADN Prueba (ADNAtomico.vue) con integración
  al locus especificado por la célula virtual y reglas del dogma central (Fase 2).
-->
<template>
  <div class="adn-experimental-card md3-card-outlined">
    <!-- Header de la Estación Molecular -->
    <div class="card-header">
      <div class="header-left">
        <div class="header-icon-box">
          <Icon name="dna" size="22" />
        </div>
        <div>
          <div class="title-with-badge">
            <h3>ADN-B · Modelo Atómico Real (ADN Prueba)</h3>
            <span class="locus-pill" :class="'locus-' + activeGeneId">
              Locus: {{ activeGeneId }} ({{ activeGeneProduct }}) · Hebra {{ currentLocus?.gene.strand }}
            </span>
            <span class="atomic-badge">855 átomos · 985 enlaces · 21 pb</span>
          </div>
          <span class="subtext">
            Segmento activo según especificación celular: <strong>{{ activeReason }}</strong>
          </span>
        </div>
      </div>

      <!-- Controles de Navegación -->
      <div class="header-actions">
        <div class="locus-selector-wrapper">
          <span class="sel-label">Locus:</span>
          <select v-model="selectedLocusKey" class="locus-dropdown">
            <option value="AUTO">⚡ Auto (según Célula)</option>
            <option v-for="(l, key) in availableLoci" :key="key" :value="key">
              {{ l.id }} ({{ l.product }}) — {{ l.role }}
            </option>
          </select>
        </div>

        <button class="btn-ctrl" @click="toggleRotate" :title="rotating ? 'Pausar giro' : 'Girar'">
          <Icon :name="rotating ? 'pause' : 'play_arrow'" size="15" />
          <span>{{ rotating ? 'Pausar giro' : 'Girar' }}</span>
        </button>
        <button class="btn-ctrl" @click="resetView" title="Restablecer posición inicial de la cámara">
          <Icon name="restart_alt" size="15" />
          <span>Vista inicial</span>
        </button>
      </div>
    </div>

    <!-- Visor Atómico WebGL (Fiel a ADN Prueba) con Panel Flotante -->
    <div class="adn-viewer-container">
      <div ref="holder" class="adn-canvas"></div>

      <!-- Panel Flotante Lateral Fiel a ADN Prueba -->
      <div class="adn-panel">
        <h2>ADN-B · Modelo atómico real</h2>
        <p>21 pares de bases · 855 átomos · 985 enlaces<br>
          Generado desde cero paramétricamente (ADN Prueba).</p>

        <div class="seq-info-box">
          <span class="strand-title">Locus Activo ({{ activeGeneId }}):</span>
          <p>Hebra 1 (5' → 3'):</p>
          <code>{{ active21bpStrand1 }}</code>
          <p>Hebra 2 (complementaria 3' → 5'):</p>
          <code>{{ active21bpStrand2 }}</code>
        </div>

        <!-- Leyenda de Colores Atómicos Original de ADN Prueba -->
        <p class="adn-leyenda">
          <i style="background:#8cccff"></i>A &nbsp;
          <i style="background:#4080f2"></i>T &nbsp;
          <i style="background:#bfe0ff"></i>G &nbsp;
          <i style="background:#2659d9"></i>C &nbsp;
          <i style="background:#738cbf"></i>azúcar &nbsp;
          <i style="background:#a6d9ff"></i>O &nbsp;
          <i style="background:#3373e6"></i>P
        </p>

        <p class="adn-hint">Arrastra para girar · Rueda para acercar · Clic derecho para desplazar</p>

        <div class="adn-actions">
          <button @click="toggleRotate">{{ rotating ? 'Pausar giro' : 'Girar' }}</button>
          <button @click="resetView">Vista inicial</button>
        </div>
      </div>

      <!-- Watermark de Estado Biológico -->
      <div class="watermark-status">
        <span class="status-chip" :class="{ transcribing: isTranscribing }">
          {{ isTranscribing ? 'ARN Polimerasa II Transcribiendo Hebra Molde (R19)' : 'Cromatina en Reposo' }}
        </span>
        <span v-if="p53Bound" class="status-chip p53-active">
          ✦ p53 unido al Surco Mayor (R28)
        </span>
        <span v-if="hasDsb" class="status-chip dsb-chip">
          ⚠ Rotura Doble Cadena (DSB) en Locus (R30)
        </span>
      </div>
    </div>

    <!-- Panel de Reglas del Dogma Central (Fase 2 Módulos A-F) -->
    <div class="dogma-rules-panel">
      <div class="rules-header">
        <div class="rh-title">
          <Icon name="menu_book" size="18" class="text-cyan" />
          <h4>Flujo del Dogma Central para {{ activeGeneId }} (Alberts et al. · Fase 2)</h4>
        </div>
        <div class="rh-badges">
          <span class="r-badge">R18 Ficha del Gen</span>
          <span class="r-badge">R19 Transcripción 3'→5'</span>
          <span class="r-badge">R21-R23 Splicing GU..AG</span>
          <span class="r-badge">R24 Traducción AUG..STOP</span>
        </div>
      </div>

      <div class="dogma-steps-grid">
        <!-- Paso 1: Transcripción -->
        <div class="dogma-step-card">
          <div class="dsc-head">
            <span class="step-num">1</span>
            <span class="step-name">Transcripción por Hebra Molde (R19)</span>
          </div>
          <div class="step-data">
            <span class="k">Hebra Molde (3'→5'):</span>
            <code class="code-sm template">{{ expressionResult?.template35.slice(0, 36) }}...</code>
            <span class="k">pre-ARNm (5'→3' con U):</span>
            <code class="code-sm rna">{{ expressionResult?.preRNA.slice(0, 36) }}...</code>
          </div>
        </div>

        <!-- Paso 2: Procesamiento y Splicing -->
        <div class="dogma-step-card">
          <div class="dsc-head">
            <span class="step-num">2</span>
            <span class="step-name">Procesamiento de pre-ARNm (R21-R23)</span>
          </div>
          <div class="step-data">
            <span class="k">Modificaciones postranscripcionales:</span>
            <div class="badges-row">
              <span class="mini-tag">✔ 5' Cap (m7G)</span>
              <span class="mini-tag">✔ Intrón GU..AG eliminado</span>
              <span class="mini-tag">✔ Poli-A (AAUAAA)</span>
            </div>
            <span class="k">ARNm Maduro (Exones unidos):</span>
            <code class="code-sm mature">{{ expressionResult?.mature }}</code>
          </div>
        </div>

        <!-- Paso 3: Traducción Ribosomal -->
        <div class="dogma-step-card">
          <div class="dsc-head">
            <span class="step-num">3</span>
            <span class="step-name">Traducción a Proteína (R24)</span>
          </div>
          <div class="step-data">
            <span class="k">Codones leídos (AUG $\rightarrow$ STOP):</span>
            <div class="codons-mini-track">
              <span v-for="(cd, i) in expressionResult?.codons || []" :key="i" class="cd-tag" :class="{ stop: cd.a === '*' }">
                {{ cd.c }}:{{ cd.a === '*' ? 'STOP' : AA3[cd.a] }}
              </span>
            </div>
            <span class="k">Secuencia peptídica (1 y 3 letras):</span>
            <div class="prot-result">
              <strong>{{ expressionResult?.protein }}</strong>
              <span class="prot-3">({{ expressionResult?.protein3 }})</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue';
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import Icon from './Icon.vue';
import { ATOMIC_DNA_DATA } from '../sim/dnaAtomicData';
import { buildLocus, express, pickActiveGene, AA3 } from '../sim/dnaEngine';

const props = defineProps({
  kb: { type: Object, default: () => ({}) },
  cellFate: { type: String, default: 'pluripotente' },
  cellPhase: { type: String, default: 'G1' },
  cellState: { type: Object, default: () => ({}) },
  alive: { type: Boolean, default: true }
});

const holder = ref(null);
const rotating = ref(true);
const selectedLocusKey = ref('AUTO');

let renderer = null;
let scene = null;
let camera = null;
let controls = null;
let rafId = null;
let resizeObserver = null;
const camPos0 = new THREE.Vector3();
const target0 = new THREE.Vector3();

// Loci disponibles de la base de conocimiento
const availableLoci = computed(() => {
  return props.kb?.genome?.loci || {};
});

// Selección activa del gen según la especificación celular
const activeDecision = computed(() => {
  if (selectedLocusKey.value !== 'AUTO' && availableLoci.value[selectedLocusKey.value]) {
    return {
      id: selectedLocusKey.value,
      level: 1.0,
      why: 'Selección manual del usuario',
      p53Bound: props.cellState?.p53 > 0.2 && selectedLocusKey.value === 'CDKN1A'
    };
  }
  if (!props.kb?.genome) {
    return { id: 'POU5F1', level: 1.0, why: 'Locus basal pluripotente', p53Bound: false };
  }
  return pickActiveGene(props.kb, { fate: props.cellFate, state: props.cellState });
});

const activeGeneId = computed(() => activeDecision.value.id);
const activeReason = computed(() => activeDecision.value.why);
const p53Bound = computed(() => activeDecision.value.p53Bound);
const activeGeneProduct = computed(() => availableLoci.value[activeGeneId.value]?.product || activeGeneId.value);
const hasDsb = computed(() => (props.cellState?.dsb || 0) > 0);
const isTranscribing = computed(() => props.alive && props.cellPhase !== 'M' && !hasDsb.value);

// Locus actual con coordenadas y secuencias
const currentLocus = computed(() => {
  const g = availableLoci.value[activeGeneId.value];
  if (!g) return null;
  return buildLocus(g);
});

// Segmento de 21 pb exactos para el modelo atómico
const active21bpStrand1 = computed(() => {
  if (!currentLocus.value) return ATOMIC_DNA_DATA.meta.secuencia_hebra1;
  const fwd = currentLocus.value.forward;
  if (fwd.length >= 21) return fwd.slice(0, 21);
  return fwd.padEnd(21, 'A');
});

const active21bpStrand2 = computed(() => {
  if (!currentLocus.value) return ATOMIC_DNA_DATA.meta.secuencia_hebra2;
  const rev = currentLocus.value.reverse;
  if (rev.length >= 21) return rev.slice(0, 21);
  return rev.padEnd(21, 'T');
});

// Expresión génica (Transcripción, Splicing y Traducción)
const expressionResult = computed(() => {
  if (!currentLocus.value) return null;
  return express(currentLocus.value);
});

// ==========================================
// RENDERIZADOR ATÓMICO 100% FIEL A ADN PRUEBA
// ==========================================
const PALETA = {
  A: 0x8cccff, T: 0x4080f2, G: 0xbfe0ff, C: 0x2659d9,
  Caz: 0x738cbf, O: 0xa6d9ff, P: 0x3373e6
};

function crearBase() {
  if (!holder.value) return;
  const w = holder.value.clientWidth || 800;
  const h = holder.value.clientHeight || 520;

  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(w, h);
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.15;
  renderer.outputColorSpace = THREE.SRGBColorSpace;

  holder.value.innerHTML = '';
  holder.value.appendChild(renderer.domElement);

  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x020612);
  scene.fog = new THREE.Fog(0x020612, 200, 520);

  camera = new THREE.PerspectiveCamera(40, w / h, 0.1, 3000);

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
}

function encuadrar(puntos) {
  const caja = new THREE.Box3();
  puntos.forEach((p) => caja.expandByPoint(new THREE.Vector3(p[0], p[1], p[2])));
  const centro = caja.getCenter(new THREE.Vector3());
  const tam = caja.getSize(new THREE.Vector3());
  const dist = Math.max(tam.x, tam.y, tam.z) * 1.55;
  camera.position.set(centro.x + dist * 0.55, centro.y + dist * 0.3, centro.z + dist);
  controls.target.copy(centro);
  camPos0.copy(camera.position);
  target0.copy(centro);
  controls.update();
}

function construir() {
  const radios = ATOMIC_DNA_DATA.meta.radios;
  const atomos = ATOMIC_DNA_DATA.atomos;
  const enlaces = ATOMIC_DNA_DATA.enlaces;

  // 1. Átomos (InstancedMesh esferas)
  const geoEsfera = new THREE.SphereGeometry(1, 24, 18);
  const matEsfera = new THREE.MeshStandardMaterial({ roughness: 0.32, metalness: 0.08 });
  const mallaAtomos = new THREE.InstancedMesh(geoEsfera, matEsfera, atomos.length);
  const dummy = new THREE.Object3D();
  const color = new THREE.Color();

  atomos.forEach((a, i) => {
    dummy.position.set(a[0], a[1], a[2]);
    const r = (radios[a[3]] || 0.7) * 1.15;
    dummy.scale.setScalar(r);
    dummy.updateMatrix();
    mallaAtomos.setMatrixAt(i, dummy.matrix);
    mallaAtomos.setColorAt(i, color.setHex(PALETA[a[4]] ?? 0x94a3b8));
  });
  scene.add(mallaAtomos);

  // 2. Enlaces (InstancedMesh cilindros)
  const geoCil = new THREE.CylinderGeometry(1, 1, 1, 10);
  const matCil = new THREE.MeshStandardMaterial({ roughness: 0.5, metalness: 0.05 });
  const mallaEnlaces = new THREE.InstancedMesh(geoCil, matCil, enlaces.length);
  const up = new THREE.Vector3(0, 1, 0);
  const p1 = new THREE.Vector3();
  const p2 = new THREE.Vector3();
  const dir = new THREE.Vector3();
  const med = new THREE.Vector3();

  enlaces.forEach((e, i) => {
    const a = atomos[e[0]];
    const b = atomos[e[1]];
    p1.set(a[0], a[1], a[2]);
    p2.set(b[0], b[1], b[2]);
    dir.subVectors(p2, p1);
    const len = dir.length();
    med.addVectors(p1, p2).multiplyScalar(0.5);
    dummy.position.copy(med);
    dummy.quaternion.setFromUnitVectors(up, dir.normalize());
    dummy.scale.set(e[2] === 'h' ? 0.09 : 0.17, len, e[2] === 'h' ? 0.09 : 0.17);
    dummy.updateMatrix();
    mallaEnlaces.setMatrixAt(i, dummy.matrix);
    mallaEnlaces.setColorAt(i, color.setHex(e[2] === 'h' ? 0x8fb4e0 : 0x4a6390));
  });
  scene.add(mallaEnlaces);

  encuadrar(atomos.map((a) => [a[0], a[1], a[2]]));
}

function toggleRotate() {
  rotating.value = !rotating.value;
  if (controls) controls.autoRotate = rotating.value;
}

function resetView() {
  if (!camera || !controls) return;
  camera.position.copy(camPos0);
  controls.target.copy(target0);
  controls.update();
}

function onResize() {
  if (!renderer || !holder.value) return;
  const w = holder.value.clientWidth;
  const h = holder.value.clientHeight;
  if (w <= 0 || h <= 0) return;
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
  renderer.setSize(w, h);
}

function animar() {
  rafId = requestAnimationFrame(animar);
  if (controls) controls.update();
  if (renderer && scene && camera) {
    renderer.render(scene, camera);
  }
}

// Watchers para cuando la célula cambia de estado
watch(() => [props.cellFate, props.cellState?.p53, props.cellState?.dsb, selectedLocusKey.value], () => {
  // El locus y los metadatos se actualizan reactivamente
});

onMounted(() => {
  crearBase();
  construir();
  window.addEventListener('resize', onResize);
  if (window.ResizeObserver && holder.value) {
    resizeObserver = new ResizeObserver(() => onResize());
    resizeObserver.observe(holder.value);
  }
  setTimeout(onResize, 60);
  setTimeout(onResize, 250);
  animar();
});

onBeforeUnmount(() => {
  cancelAnimationFrame(rafId);
  window.removeEventListener('resize', onResize);
  if (resizeObserver) resizeObserver.disconnect();
  if (controls) controls.dispose();
  if (renderer) renderer.dispose();
});
</script>

<style scoped>
.adn-experimental-card {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.25rem;
  background-color: var(--md-sys-color-surface-container-low);
  border-radius: var(--md-sys-shape-corner-medium);
  border: 1px solid var(--md-sys-color-outline-variant);
  border-top: 3px solid #38bdf8;
  margin-top: 1.25rem;
}

/* Card Header */
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.header-icon-box {
  width: 42px;
  height: 42px;
  border-radius: var(--md-sys-shape-corner-small);
  background: linear-gradient(135deg, rgba(56, 189, 248, 0.2), rgba(122, 229, 130, 0.15));
  display: flex;
  align-items: center;
  justify-content: center;
  color: #38bdf8;
  border: 1px solid rgba(56, 189, 248, 0.3);
}

.title-with-badge {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-wrap: wrap;
}

.card-header h3 {
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
}

.locus-pill {
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.15rem 0.6rem;
  border-radius: 999px;
  font-family: var(--md-ref-typeface-mono);
  background: rgba(56, 189, 248, 0.15);
  color: #38bdf8;
  border: 1px solid rgba(56, 189, 248, 0.35);
}

.locus-CDKN1A { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border-color: rgba(245, 158, 11, 0.4); }
.locus-PAX6 { background: rgba(168, 85, 247, 0.15); color: #c084fc; border-color: rgba(168, 85, 247, 0.4); }
.locus-SOX17 { background: rgba(234, 179, 8, 0.15); color: #facc15; border-color: rgba(234, 179, 8, 0.4); }
.locus-TBXT { background: rgba(239, 68, 68, 0.15); color: #f87171; border-color: rgba(239, 68, 68, 0.4); }

.atomic-badge {
  font-size: 0.68rem;
  color: var(--md-sys-color-on-surface-variant);
  font-family: var(--md-ref-typeface-mono);
  background: rgba(255, 255, 255, 0.05);
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
}

.subtext {
  font-size: 0.8rem;
  color: var(--md-sys-color-on-surface-variant);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.locus-selector-wrapper {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  background: var(--md-sys-color-surface-container);
  border: 1px solid var(--md-sys-color-outline-variant);
  padding: 0.25rem 0.5rem;
  border-radius: var(--md-sys-shape-corner-small);
}

.sel-label {
  font-size: 0.7rem;
  color: var(--md-sys-color-on-surface-variant);
  font-weight: 600;
}

.locus-dropdown {
  background: transparent;
  border: none;
  color: var(--md-sys-color-on-surface);
  font-size: 0.75rem;
  font-weight: 600;
  outline: none;
  cursor: pointer;
}

.btn-ctrl {
  background: var(--md-sys-color-surface-container);
  border: 1px solid var(--md-sys-color-outline-variant);
  color: var(--md-sys-color-on-surface);
  padding: 0.4rem 0.75rem;
  border-radius: var(--md-sys-shape-corner-small);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.75rem;
  font-weight: 600;
  transition: all 0.15s ease;
}

.btn-ctrl:hover {
  border-color: #38bdf8;
  color: #38bdf8;
}

/* ==========================================================
   ESTILOS ORIGINALES DE ADN PRUEBA (ADNAtomico.vue)
   ========================================================== */
.adn-viewer-container {
  position: relative;
  width: 100%;
  height: 520px;
  background: #020612;
  overflow: hidden;
  border-radius: var(--md-sys-shape-corner-small);
  border: 1px solid var(--md-sys-color-outline-variant);
  font-family: system-ui, sans-serif;
}

.adn-canvas {
  position: absolute;
  inset: 0;
}

/* Panel Flotante Fiel a ADNAtomico.vue */
.adn-panel {
  position: absolute;
  left: 16px;
  top: 16px;
  max-width: 340px;
  max-height: calc(100% - 32px);
  overflow-y: auto;
  z-index: 10;
  background: rgba(4, 12, 32, 0.85);
  border: 1px solid rgba(125, 180, 255, 0.25);
  border-radius: 12px;
  padding: 14px 16px;
  color: #dbeafe;
  backdrop-filter: blur(8px);
}

.adn-panel h2 {
  margin: 0 0 6px;
  font-size: 17px;
  color: #e0f2fe;
}

.adn-panel p {
  margin: 6px 0;
  font-size: 12px;
  line-height: 1.45;
  color: #bfdbfe;
}

.seq-info-box {
  margin: 8px 0;
}

.strand-title {
  font-size: 11px;
  font-weight: 700;
  color: #38bdf8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.adn-panel code {
  display: block;
  background: #06122b;
  border-radius: 6px;
  padding: 6px 8px;
  font-size: 11px;
  letter-spacing: 1px;
  color: #a5f3fc;
  overflow-x: auto;
  margin: 3px 0 6px;
  font-family: var(--md-ref-typeface-mono);
}

.adn-leyenda {
  font-size: 12px;
  color: #93c5fd;
  line-height: 1.7;
  margin: 8px 0;
}

.adn-leyenda i {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 4px;
  vertical-align: middle;
}

.adn-hint {
  font-size: 11px;
  color: #7dd3fc;
  margin-top: 6px;
}

.adn-actions {
  display: flex;
  gap: 8px;
  margin-top: 10px;
}

.adn-actions button {
  cursor: pointer;
  border: 1px solid rgba(125, 180, 255, 0.4);
  background: rgba(30, 64, 175, 0.35);
  color: #e0f2fe;
  border-radius: 8px;
  padding: 6px 12px;
  font-size: 12px;
  font-weight: 600;
  transition: all 0.15s ease;
}

.adn-actions button:hover {
  background: rgba(30, 64, 175, 0.6);
}

/* Watermark de Estado Biológico */
.watermark-status {
  position: absolute;
  top: 16px;
  right: 16px;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  z-index: 10;
}

.status-chip {
  font-size: 0.72rem;
  padding: 0.25rem 0.6rem;
  border-radius: 6px;
  background: rgba(4, 12, 32, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: var(--md-sys-color-on-surface-variant);
  backdrop-filter: blur(6px);
}

.status-chip.transcribing {
  color: #f472b6;
  border-color: rgba(236, 72, 153, 0.4);
  background: rgba(236, 72, 153, 0.15);
}

.status-chip.p53-active {
  color: #60a5fa;
  border-color: rgba(59, 130, 246, 0.4);
  background: rgba(59, 130, 246, 0.15);
}

.status-chip.dsb-chip {
  color: #ef4444;
  border-color: rgba(239, 68, 68, 0.4);
  background: rgba(239, 68, 68, 0.15);
}

/* ==========================================================
   PANEL INFERIOR DE REGLAS Y DOGMA CENTRAL (FASE 2)
   ========================================================== */
.dogma-rules-panel {
  background: var(--md-sys-color-surface-container);
  border: 1px solid var(--md-sys-color-outline-variant);
  border-radius: var(--md-sys-shape-corner-small);
  padding: 0.85rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.rules-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.rh-title {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.rh-title h4 {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--md-sys-color-on-surface);
}

.rh-badges {
  display: flex;
  gap: 0.35rem;
  flex-wrap: wrap;
}

.r-badge {
  font-size: 0.65rem;
  font-weight: 600;
  background: rgba(56, 189, 248, 0.1);
  color: #38bdf8;
  border: 1px solid rgba(56, 189, 248, 0.25);
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
}

.dogma-steps-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.85rem;
}

@media (max-width: 950px) {
  .dogma-steps-grid {
    grid-template-columns: 1fr;
  }
}

.dogma-step-card {
  background: var(--md-sys-color-surface-container-low);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 6px;
  padding: 0.65rem;
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.dsc-head {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.step-num {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #38bdf8;
  color: #022538;
  font-size: 0.65rem;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
}

.step-name {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--md-sys-color-on-surface);
}

.step-data {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.k {
  font-size: 0.65rem;
  color: var(--md-sys-color-on-surface-variant);
}

.code-sm {
  display: block;
  font-family: var(--md-ref-typeface-mono);
  font-size: 0.7rem;
  background: rgba(0, 0, 0, 0.4);
  padding: 0.25rem 0.45rem;
  border-radius: 4px;
  word-break: break-all;
  color: #94a3b8;
}

.code-sm.template { color: #38bdf8; }
.code-sm.rna { color: #f472b6; }
.code-sm.mature { color: #34d399; }

.badges-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  margin: 0.15rem 0;
}

.mini-tag {
  font-size: 0.62rem;
  background: rgba(52, 211, 153, 0.1);
  color: #34d399;
  border: 1px solid rgba(52, 211, 153, 0.3);
  padding: 0.1rem 0.35rem;
  border-radius: 3px;
}

.codons-mini-track {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  margin: 0.15rem 0;
}

.cd-tag {
  font-family: var(--md-ref-typeface-mono);
  font-size: 0.62rem;
  background: rgba(0, 0, 0, 0.35);
  padding: 0.15rem 0.3rem;
  border-radius: 3px;
  color: #38bdf8;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.cd-tag.stop { color: #ef4444; }

.prot-result {
  font-family: var(--md-ref-typeface-mono);
  font-size: 0.8rem;
  color: #34d399;
  display: flex;
  align-items: baseline;
  gap: 0.4rem;
}

.prot-3 {
  font-size: 0.68rem;
  color: var(--md-sys-color-on-surface-variant);
}

.text-cyan { color: #38bdf8; }
</style>
