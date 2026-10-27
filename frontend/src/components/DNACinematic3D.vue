<template>
  <div class="dna-cinematic-container" ref="containerRef">
    <div ref="canvasRef" class="webgl-canvas-box"></div>

    <!-- HUD Overlay -->
    <div class="cinematic-hud">
      <div class="hud-pill-badge">
        <span class="glow-dot"></span>
        <span class="badge-title">Render Cinemático B-DNA</span>
        <span class="badge-sub">{{ activeSequence.length }} pb · Doble Hélice HD</span>
      </div>

      <div class="cinematic-legend">
        <div class="legend-item">
          <span class="swatch-tube"></span>
          <span>Esqueleto fino con perlas moleculares</span>
        </div>
        <div class="legend-item">
          <span class="swatch-chain"></span>
          <span>Cadena de perlas finas unidas</span>
        </div>
        <div class="legend-item">
          <span class="swatch-ball"></span>
          <span>Bola terminal grande (sin unirse al centro)</span>
        </div>
      </div>

      <div class="hud-selection-card" v-if="selectedPairData">
        <div class="sel-header">
          <span class="sel-label">Par #{{ selectedPosition + 1 }}</span>
          <span class="sel-bonds">{{ selectedPairData.bonds }} enlaces H</span>
        </div>
        <div class="sel-duplex">
          <span class="duplex-base s1">{{ selectedPairData.base1 }}</span>
          <span class="duplex-bridge">···</span>
          <span class="duplex-base s2">{{ selectedPairData.base2 }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, computed } from 'vue';
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const props = defineProps({
  sequence: { type: String, default: '' },
  selectedPosition: { type: Number, default: 0 },
  autoRotate: { type: Boolean, default: true }
});

const emit = defineEmits(['selectBase']);

const containerRef = ref(null);
const canvasRef = ref(null);

// Secuencia canónica por defecto (40 pb)
const DEFAULT_CANONICAL_SEQ = 'GATTACAGGCTATCCGATACGTTAGCCATGGCATTCGAAT';
const activeSequence = computed(() => {
  const clean = (props.sequence || '').toUpperCase().replace(/[^ATCG]/g, '');
  return clean.length >= 2 ? clean : DEFAULT_CANONICAL_SEQ;
});

const COMPLEMENT = { A: 'T', T: 'A', C: 'G', G: 'C' };
const H_BONDS = { A: 2, T: 2, G: 3, C: 3 };

const selectedPairData = computed(() => {
  const seq = activeSequence.value;
  const idx = Math.min(Math.max(0, props.selectedPosition || 0), seq.length - 1);
  const b1 = seq[idx] || 'A';
  return { index: idx, base1: b1, base2: COMPLEMENT[b1] || 'T', bonds: H_BONDS[b1] || 2 };
});

// ---------------- Three.js state ----------------
let renderer = null;
let scene = null;
let camera = null;
let controls = null;
let animFrameId = null;
let resizeObserver = null;
let raycaster = null;
let mouse = null;

let mainHelixGroup = null;
let backdrop = null;
let selectionRing = null;
let clickableNodes = [];
let rungCenters = [];

// ---------------- Constantes B-DNA ----------------
const HELIX_RADIUS = 10.0;
const RISE_PER_BP = 3.4;
const TWIST_PER_BP = (36 * Math.PI) / 180;
const MINOR_GROOVE_OFFSET = 2.4;

// ---------------- Paleta ----------------
const COL_STRAND = 0x2b54bf;       // azul real del esqueleto
const COL_WIRE = 0x38bdf8;         // alambre cian
const COL_BALL_DARK = 0x1d4ed8;    // bola grande terminal azul cobalto
const BEAD_COLORS = [0x2f5fd8, 0x3b73e6, 0x4cc3e8, 0x60a5fa];

// ---------------- Utilidades ----------------
function mulberry32(a) {
  return function () {
    a |= 0; a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function hashString(str) {
  let h = 2166136261;
  for (let i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

let glowTexCache = null;
function getGlowTexture() {
  if (glowTexCache) return glowTexCache;
  const c = document.createElement('canvas');
  c.width = c.height = 128;
  const ctx = c.getContext('2d');
  const g = ctx.createRadialGradient(64, 64, 0, 64, 64, 64);
  g.addColorStop(0, 'rgba(255,255,255,1)');
  g.addColorStop(0.2, 'rgba(125,211,252,0.8)');
  g.addColorStop(0.5, 'rgba(37,99,235,0.25)');
  g.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, 128, 128);
  glowTexCache = new THREE.CanvasTexture(c);
  glowTexCache.colorSpace = THREE.SRGBColorSpace;
  return glowTexCache;
}

let softDiscTexCache = null;
function getSoftDiscTexture() {
  if (softDiscTexCache) return softDiscTexCache;
  const c = document.createElement('canvas');
  c.width = c.height = 128;
  const ctx = c.getContext('2d');
  const g = ctx.createRadialGradient(64, 64, 0, 64, 64, 64);
  g.addColorStop(0, 'rgba(96,165,250,0.5)');
  g.addColorStop(0.65, 'rgba(37,99,235,0.3)');
  g.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, 128, 128);
  softDiscTexCache = new THREE.CanvasTexture(c);
  softDiscTexCache.colorSpace = THREE.SRGBColorSpace;
  return softDiscTexCache;
}

// Fondo nebulosa azul profundo
function createNebulaBackground() {
  const c = document.createElement('canvas');
  c.width = c.height = 1024;
  const ctx = c.getContext('2d');
  const lin = ctx.createLinearGradient(0, 0, 1024, 1024);
  lin.addColorStop(0, '#020817');
  lin.addColorStop(0.5, '#041026');
  lin.addColorStop(1, '#020919');
  ctx.fillStyle = lin;
  ctx.fillRect(0, 0, 1024, 1024);

  const rnd = mulberry32(7);
  for (let i = 0; i < 14; i++) {
    const x = rnd() * 1024;
    const y = rnd() * 1024;
    const r = 160 + rnd() * 280;
    const g = ctx.createRadialGradient(x, y, 0, x, y, r);
    g.addColorStop(0, 'rgba(29,78,216,0.18)');
    g.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, 1024, 1024);
  }
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

// Bokeh suave y partículas de fondo
function buildBackdrop() {
  const group = new THREE.Group();
  const rnd = mulberry32(42);

  const blobTex = getSoftDiscTexture();
  for (let i = 0; i < 24; i++) {
    const mat = new THREE.SpriteMaterial({
      map: blobTex,
      color: rnd() > 0.5 ? 0x2563eb : 0x38bdf8,
      transparent: true,
      opacity: 0.08 + rnd() * 0.12,
      blending: THREE.AdditiveBlending,
      depthWrite: false
    });
    const s = new THREE.Sprite(mat);
    const r = 35 + rnd() * 70;
    const th = rnd() * Math.PI * 2;
    s.position.set(Math.cos(th) * r, (rnd() - 0.5) * 120, Math.sin(th) * r);
    const sc = 6 + rnd() * 14;
    s.scale.set(sc, sc, 1);
    group.add(s);
  }

  const count = 180;
  const pos = new Float32Array(count * 3);
  for (let i = 0; i < count; i++) {
    const r = 18 + rnd() * 80;
    const th = rnd() * Math.PI * 2;
    pos[i * 3] = Math.cos(th) * r;
    pos[i * 3 + 1] = (rnd() - 0.5) * 130;
    pos[i * 3 + 2] = Math.sin(th) * r;
  }
  const geom = new THREE.BufferGeometry();
  geom.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  const mat = new THREE.PointsMaterial({
    size: 1.4,
    map: getGlowTexture(),
    color: 0x60a5fa,
    transparent: true,
    opacity: 0.55,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
    sizeAttenuation: true
  });
  group.add(new THREE.Points(geom, mat));
  return group;
}

// ---------------- Construcción de la hélice ----------------
function buildCinematicHelix() {
  if (!scene) return;

  if (mainHelixGroup) {
    scene.remove(mainHelixGroup);
    mainHelixGroup.traverse((obj) => {
      if (obj.geometry) obj.geometry.dispose();
      if (obj.material) {
        if (Array.isArray(obj.material)) obj.material.forEach((m) => m.dispose());
        else obj.material.dispose();
      }
    });
  }

  clickableNodes = [];
  rungCenters = [];
  mainHelixGroup = new THREE.Group();
  mainHelixGroup.rotation.order = 'ZXY';

  const seq = activeSequence.value;
  const N = seq.length;
  const rnd = mulberry32(hashString(seq));
  const totalHeight = (N - 1) * RISE_PER_BP;
  const yOffset = totalHeight / 2;

  const strandPoint = (angleOffset, f) => {
    const a = f * TWIST_PER_BP + angleOffset;
    return new THREE.Vector3(
      Math.cos(a) * HELIX_RADIUS,
      f * RISE_PER_BP - yOffset,
      Math.sin(a) * HELIX_RADIUS
    );
  };

  // ---------- 1. Esqueleto: cordón fino con perlas moleculares ----------
  const strandMat = new THREE.MeshPhysicalMaterial({
    color: COL_STRAND,
    emissive: 0x000000,
    roughness: 0.4,
    metalness: 0.1,
    clearcoat: 0.6,
    clearcoatRoughness: 0.2
  });
  const wireMat = new THREE.MeshStandardMaterial({
    color: COL_WIRE,
    emissive: 0x000000,
    roughness: 0.35,
    metalness: 0.15
  });
  const beadMat = new THREE.MeshPhysicalMaterial({
    roughness: 0.28,
    metalness: 0.08,
    clearcoat: 0.85,
    clearcoatRoughness: 0.15
  });
  const beadGeom = new THREE.SphereGeometry(1, 12, 12);
  const instancedBeads = new THREE.InstancedMesh(beadGeom, beadMat, N * 44);
  const dummy = new THREE.Object3D();
  const tmpColor = new THREE.Color();
  let beadIdx = 0;

  const segs = N * 16;

  const buildStrand = (angleOffset, wirePhase) => {
    const pts = [];
    for (let f = 0; f <= N - 1 + 1e-6; f += 0.25) pts.push(strandPoint(angleOffset, f));
    const curve = new THREE.CatmullRomCurve3(pts);

    mainHelixGroup.add(new THREE.Mesh(new THREE.TubeGeometry(curve, segs, 0.34, 10, false), strandMat));

    const frames = curve.computeFrenetFrames(segs, false);

    // Alambres entrelazados alrededor del cordón
    const wireTurns = N * 1.6;
    for (let w = 0; w < 2; w++) {
      const wp = [];
      for (let k = 0; k <= segs; k++) {
        const u = k / segs;
        const p = curve.getPointAt(u);
        const th = u * wireTurns * Math.PI * 2 + wirePhase + w * Math.PI;
        const n = frames.normals[k];
        const b = frames.binormals[k];
        wp.push(
          p.clone()
            .addScaledVector(n, Math.cos(th) * 0.52)
            .addScaledVector(b, Math.sin(th) * 0.52)
        );
      }
      const wc = new THREE.CatmullRomCurve3(wp);
      mainHelixGroup.add(new THREE.Mesh(new THREE.TubeGeometry(wc, segs * 2, 0.075, 6, false), wireMat));
    }

    // Perlas moleculares adheridas al cordón
    const samples = N * 10;
    for (let s = 0; s < samples; s++) {
      const u = s / samples;
      const p = curve.getPointAt(u);
      const fi = Math.min(segs, Math.round(u * segs));
      const n = frames.normals[fi];
      const b = frames.binormals[fi];
      const radial = new THREE.Vector3(p.x, 0, p.z).normalize();

      for (let c = 0; c < 2; c++) {
        if (beadIdx >= N * 44) break;
        const phi = rnd() * Math.PI * 2;
        const dir = new THREE.Vector3()
          .addScaledVector(n, Math.cos(phi))
          .addScaledVector(b, Math.sin(phi));
        if (dir.dot(radial) < 0 && rnd() < 0.75) dir.negate();
        dir.normalize();

        const r = 0.24 + rnd() * 0.22;
        dummy.position.copy(p).addScaledVector(dir, 0.46 + rnd() * 0.26);
        dummy.scale.setScalar(r);
        dummy.rotation.set(0, 0, 0);
        dummy.updateMatrix();
        instancedBeads.setMatrixAt(beadIdx, dummy.matrix);
        tmpColor.setHex(BEAD_COLORS[Math.floor(rnd() * BEAD_COLORS.length)]);
        instancedBeads.setColorAt(beadIdx, tmpColor);
        beadIdx++;
      }
    }
  };

  buildStrand(0, 0);
  buildStrand(MINOR_GROOVE_OFFSET, 1.3);

  instancedBeads.count = beadIdx;
  instancedBeads.instanceMatrix.needsUpdate = true;
  if (instancedBeads.instanceColor) instancedBeads.instanceColor.needsUpdate = true;
  mainHelixGroup.add(instancedBeads);

  // ---------- 2. Peldaños: Cadena de muchas bolitas pequeñas unidas + Bola grande terminal ----------
  const SPHERES_PER_ARM = 16; // Muchas bolitas densamente unidas
  const smallChainGeom = new THREE.SphereGeometry(1, 16, 16);
  const smallChainMat = new THREE.MeshPhysicalMaterial({
    roughness: 0.35,
    metalness: 0.05,
    clearcoat: 0.85,
    clearcoatRoughness: 0.15,
    emissive: 0x000000 // Sin brillo ni halo
  });
  const instancedChain = new THREE.InstancedMesh(smallChainGeom, smallChainMat, N * 2 * SPHERES_PER_ARM);
  let chainIdx = 0;

  // Bola grande terminal en el centro (azul cobalto profundo)
  const tipGeom = new THREE.SphereGeometry(1, 24, 24);
  const tipMat = new THREE.MeshPhysicalMaterial({
    color: COL_BALL_DARK,
    roughness: 0.26,
    metalness: 0.1,
    clearcoat: 0.95,
    clearcoatRoughness: 0.1,
    emissive: 0x000000 // Sin brillo ni halo
  });
  const instancedTips = new THREE.InstancedMesh(tipGeom, tipMat, N * 2);
  let tipIdx = 0;

  for (let i = 0; i < N; i++) {
    const p1 = strandPoint(0, i);
    const p2 = strandPoint(MINOR_GROOVE_OFFSET, i);
    const chord = p1.distanceTo(p2);
    const dir12 = new THREE.Vector3().subVectors(p2, p1).normalize();
    const center = new THREE.Vector3().addVectors(p1, p2).multiplyScalar(0.5);
    rungCenters.push(center);

    // Dimensiones de los brazos:
    // La bola grande central se sitúa dejando un espacio de 0.5 unidades sin tocarse en el centro
    const tipR = 0.88;
    const gapCenter = 0.5;
    const tipDist = (chord * 0.5) - (gapCenter * 0.5) - tipR;
    const startDist = 0.38;
    const endDist = tipDist - tipR * 0.65; // Penetra suavemente en la bola grande para unión total

    const buildChainArm = (rootPos, dir) => {
      // Cadena continua de muchas perlas pequeñas densamente solapadas (quedan unidas)
      for (let k = 0; k < SPHERES_PER_ARM; k++) {
        const t = k / (SPHERES_PER_ARM - 1);
        const dist = startDist + t * (endDist - startDist);
        // Radio pequeño (0.42 en la raíz decreciendo suavemente a 0.32 cerca de la bola grande)
        const r = 0.42 - 0.10 * t;

        dummy.position.copy(rootPos).addScaledVector(dir, dist);
        dummy.rotation.set(0, 0, 0);
        dummy.scale.setScalar(r);
        dummy.updateMatrix();
        instancedChain.setMatrixAt(chainIdx, dummy.matrix);

        // Degradado de color sutil de celeste a azul intenso
        tmpColor.set(0x60a5fa).lerp(new THREE.Color(0x2563eb), t);
        instancedChain.setColorAt(chainIdx, tmpColor);
        chainIdx++;
      }

      // Bola grande terminal en el centro
      dummy.position.copy(rootPos).addScaledVector(dir, tipDist);
      dummy.rotation.set(0, 0, 0);
      dummy.scale.setScalar(tipR);
      dummy.updateMatrix();
      instancedTips.setMatrixAt(tipIdx++, dummy.matrix);
    };

    buildChainArm(p1, dir12);
    buildChainArm(p2, dir12.clone().negate());

    // Zona de clic interactiva
    const hit = new THREE.Mesh(
      new THREE.SphereGeometry(2.4, 8, 8),
      new THREE.MeshBasicMaterial({ visible: false })
    );
    hit.position.copy(center);
    hit.userData = { pairIndex: i };
    mainHelixGroup.add(hit);
    clickableNodes.push(hit);
  }

  instancedChain.count = chainIdx;
  instancedChain.instanceMatrix.needsUpdate = true;
  if (instancedChain.instanceColor) instancedChain.instanceColor.needsUpdate = true;
  mainHelixGroup.add(instancedChain);

  instancedTips.count = tipIdx;
  instancedTips.instanceMatrix.needsUpdate = true;
  mainHelixGroup.add(instancedTips);

  // ---------- 3. Anillo horizontal de selección (Fiel a la Referencia) ----------
  const ringGeo = new THREE.RingGeometry(11.2, 13.8, 64);
  const ringMat = new THREE.MeshBasicMaterial({ 
    color: 0x38bdf8, 
    side: THREE.DoubleSide, 
    transparent: true, 
    opacity: 0.75 
  });
  selectionRing = new THREE.Mesh(ringGeo, ringMat);
  selectionRing.rotation.x = Math.PI / 2; // Plano horizontal XZ rodeando la hélice
  mainHelixGroup.add(selectionRing);
  updateSelection();

  // ---------- 4. Orientación vertical erguida (sin voltear) ----------
  mainHelixGroup.rotation.z = 0;
  mainHelixGroup.rotation.x = 0;

  scene.add(mainHelixGroup);
  ajustarCamara(totalHeight);
}

function updateSelection() {
  if (!selectionRing || !rungCenters.length) return;
  const idx = Math.min(Math.max(0, props.selectedPosition || 0), rungCenters.length - 1);
  selectionRing.position.set(0, rungCenters[idx].y, 0);
}

function ajustarCamara(helixHeight) {
  if (!camera || !controls) return;
  const dist = Math.max(48, Math.min(140, helixHeight * 0.82 + 20));
  camera.position.set(0, 0, dist);
  controls.target.set(0, 0, 0);
  controls.update();
}

function setupStudioLighting() {
  scene.add(new THREE.AmbientLight(0x111c38, 1.4));

  // Luz clave frontal
  const key = new THREE.DirectionalLight(0xffffff, 2.6);
  key.position.set(45, 60, 55);
  scene.add(key);

  // Luz de borde superior/trasero (definición de silueta natural, sin resplandor quemado)
  const rim = new THREE.DirectionalLight(0x7dd3fc, 2.2);
  rim.position.set(-45, 65, -55);
  scene.add(rim);

  // Luz de relleno azul
  const fill = new THREE.DirectionalLight(0x2563eb, 1.6);
  fill.position.set(-30, -50, 40);
  scene.add(fill);
}

// ---------------- Interacción ----------------
function onPointerDown(event) {
  if (!canvasRef.value || !camera) return;
  const rect = canvasRef.value.getBoundingClientRect();
  mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
  mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

  raycaster.setFromCamera(mouse, camera);
  const hits = raycaster.intersectObjects(clickableNodes, false);
  if (hits.length > 0) {
    const idx = hits[0].object.userData.pairIndex;
    if (typeof idx === 'number') emit('selectBase', idx);
  }
}

// ---------------- Loop (Render directo sin Bloom) ----------------
function animate() {
  animFrameId = requestAnimationFrame(animate);
  if (controls) controls.update();

  if (props.autoRotate && mainHelixGroup) {
    mainHelixGroup.rotation.y += 0.003;
  }
  if (backdrop) {
    backdrop.rotation.y += 0.0006;
  }

  if (renderer && scene && camera) {
    renderer.render(scene, camera);
  }
}

onMounted(() => {
  if (!canvasRef.value) return;

  const width = canvasRef.value.clientWidth || 800;
  const height = canvasRef.value.clientHeight || 550;

  renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(width, height);
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  canvasRef.value.appendChild(renderer.domElement);

  scene = new THREE.Scene();
  scene.background = createNebulaBackground();
  scene.fog = new THREE.FogExp2(0x020817, 0.004);

  camera = new THREE.PerspectiveCamera(40, width / height, 0.1, 1000);
  camera.position.set(4, 3, 70);

  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.06;
  controls.minDistance = 15;
  controls.maxDistance = 220;

  raycaster = new THREE.Raycaster();
  mouse = new THREE.Vector2();

  setupStudioLighting();
  backdrop = buildBackdrop();
  scene.add(backdrop);

  buildCinematicHelix();

  renderer.domElement.addEventListener('pointerdown', onPointerDown);

  resizeObserver = new ResizeObserver(() => {
    if (!canvasRef.value || !renderer || !camera) return;
    const w = canvasRef.value.clientWidth;
    const h = canvasRef.value.clientHeight;
    if (w > 0 && h > 0) {
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    }
  });
  resizeObserver.observe(canvasRef.value);

  animate();
});

onUnmounted(() => {
  if (animFrameId) cancelAnimationFrame(animFrameId);
  if (resizeObserver) resizeObserver.disconnect();
  if (controls) controls.dispose();
  if (renderer && renderer.domElement) {
    renderer.domElement.removeEventListener('pointerdown', onPointerDown);
    renderer.dispose();
  }
});

watch(() => props.sequence, () => {
  buildCinematicHelix();
});

watch(() => props.selectedPosition, () => {
  updateSelection();
});
</script>

<style scoped>
.dna-cinematic-container {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 520px;
  background: #020917;
  border-radius: var(--md3-shape-corner-medium, 16px);
  overflow: hidden;
  box-shadow: inset 0 0 40px rgba(0, 0, 0, 0.8), 0 8px 32px rgba(2, 6, 23, 0.6);
}

.webgl-canvas-box {
  width: 100%;
  height: 100%;
  min-height: 520px;
  cursor: grab;
}

.webgl-canvas-box:active {
  cursor: grabbing;
}

.cinematic-hud {
  position: absolute;
  top: 16px;
  left: 16px;
  right: 16px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  pointer-events: none;
  z-index: 10;
}

.hud-pill-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  background: rgba(2, 6, 23, 0.75);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(56, 189, 248, 0.35);
  border-radius: 9999px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5), 0 0 15px rgba(56, 189, 248, 0.2);
}

.glow-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #00f5ff;
  box-shadow: 0 0 10px #00f5ff, 0 0 18px #38bdf8;
  animation: pulse-glow 2s infinite ease-in-out;
}

@keyframes pulse-glow {
  0%, 100% { opacity: 0.8; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.3); }
}

.badge-title {
  font-size: 0.82rem;
  font-weight: 700;
  letter-spacing: 0.5px;
  color: #f0f9ff;
  text-transform: uppercase;
}

.badge-sub {
  font-size: 0.75rem;
  color: #38bdf8;
  font-family: monospace;
}

.cinematic-legend {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 10px 14px;
  background: rgba(2, 6, 23, 0.75);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(56, 189, 248, 0.25);
  border-radius: 12px;
  font-size: 0.72rem;
  color: #cbd5e1;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.swatch-tube {
  width: 14px;
  height: 4px;
  border-radius: 2px;
  background: linear-gradient(90deg, #2b54bf, #38bdf8);
}

.swatch-chain {
  width: 14px;
  height: 6px;
  border-radius: 3px;
  background: repeating-linear-gradient(90deg, #60a5fa 0 2px, #2563eb 2px 4px);
}

.swatch-ball {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: #1d4ed8;
}

.hud-selection-card {
  position: absolute;
  top: 75px;
  right: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 10px 14px;
  background: rgba(2, 6, 23, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(56, 189, 248, 0.4);
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.6);
}

.sel-header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  font-size: 0.75rem;
}

.sel-label {
  color: #94a3b8;
  font-weight: 600;
}

.sel-bonds {
  color: #38bdf8;
  font-family: monospace;
  font-size: 0.72rem;
}

.sel-duplex {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-family: monospace;
  font-weight: 700;
  font-size: 1.15rem;
}

.duplex-base {
  padding: 2px 8px;
  border-radius: 6px;
}

.duplex-base.s1 {
  background: rgba(56, 189, 248, 0.2);
  color: #7dd3fc;
  border: 1px solid rgba(56, 189, 248, 0.4);
}

.duplex-base.s2 {
  background: rgba(30, 64, 175, 0.35);
  color: #93c5fd;
  border: 1px solid rgba(59, 130, 246, 0.4);
}

.duplex-bridge {
  color: #00f5ff;
  letter-spacing: 2px;
  text-shadow: 0 0 8px #00f5ff;
}
</style>
