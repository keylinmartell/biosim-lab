<template>
  <div class="dna-3d-card md3-card-outlined" :class="{ 'cinema-expanded': isExpanded }">
    <!-- Header de Tarjeta MD3 (Tonal Surface Header) -->
    <div class="card-header">
      <div class="header-main">
        <div class="header-avatar">
          <Icon name="dna" size="22" />
        </div>
        <div class="header-titles">
          <h3 class="title-text">
            {{ packagingMode === 'linear' ? 'Modelo Atómico Tridimensional (B-DNA)' : 'Cromatina Pluripotente · Collar de Perlas (Alberts et al.)' }}
          </h3>
          <span class="subhead-text">
            {{ atomicStats.nucleosomes }} Nucleosomas ({{ atomicStats.octamerSubunits }} histonas core + {{ atomicStats.h1Count }} H1 lábil) · {{ atomicStats.totalAtoms }} átomos de ADN
          </span>
        </div>
      </div>

      <div class="header-chips">
        <!-- Selector de Empaquetamiento en Histonas -->
        <button 
          class="md3-chip interactive-chip" 
          @click="cyclePackagingMode"
          title="Alternar entre Fibra de Cromatina con Histonas (Collar de Perlas), Escala Alberts 147 pb y ADN Lineal"
        >
          <Icon name="hub" size="14" class="chip-lead" />
          <span class="font-mono">
            {{ packagingMode === 'chromatin_adaptive' ? 'Cromatina (Collar de Perlas)' : packagingMode === 'chromatin_alberts' ? 'Alberts Estricto (147+53 pb)' : 'ADN-B Lineal' }}
          </span>
        </button>

        <!-- Botón Modal: Inducción de Daño en el Molde -->
        <button 
          class="md3-chip interactive-chip damage-trigger-chip" 
          @click="$emit('openDamageDialog')"
          title="Abrir panel de Inducción de Daño en el Molde (Ambiental / CRISPR-Cas9)"
        >
          <Icon name="bolt" size="14" class="chip-lead text-amber" />
          <span>Inducir Daño</span>
        </button>

        <!-- Botón Patrullaje y Reparación p53 -->
        <button 
          class="md3-chip interactive-chip p53-trigger-chip" 
          @click="triggerP53Patrol"
          :class="{ 'p53-active': p53State.active }"
          :title="p53State.active ? 'p53 patrullando la cadena...' : 'Iniciar patrullaje y reparación por p53'"
        >
          <Icon name="psychology" size="14" class="chip-lead text-emerald" />
          <span>{{ p53State.active ? 'p53 Activo' : 'Patrullaje p53' }}</span>
        </button>

        <div class="md3-chip">
          <Icon name="biotech" size="14" class="chip-lead" />
          <span class="font-mono">
            Seq: {{ cleanFullSequence.length }} pb ({{ atomicStats.renderedBp }} pb 3D) · {{ atomicStats.totalHistones }} Histonas
          </span>
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
    <div class="canvas-wrapper" :class="{ 'pan-mode': dragMode === 'pan' }" ref="canvasContainer">
      <!-- Indicador de Pool Nuclear Libre de p53/Mdm2 (Zona aparte) -->
      <div v-if="!p53State.active" class="p53-idle-badge">
        <span class="idle-dot"></span>
        <span>Reservorio Nuclear: {{ p53State.p53UnitsCount }} Complejos p53/Mdm2</span>
      </div>

      <!-- RECUADRO PROMINENTE DE DAÑO Y ENZIMA ACTIVA AL DETENERSE p53 -->
      <div v-if="activeInspectionCard" class="damage-inspection-card">
        <div class="card-accent-line"></div>
        <div class="card-top-line">
          <div class="badge-left">
            <span class="pulse-warning-dot"></span>
            <span class="bp-coord font-mono">SEGMENTO pb {{ activeInspectionCard.position }}</span>
          </div>
          <span :class="['card-state-pill', activeInspectionCard.repaired ? 'repaired' : 'active']">
            {{ activeInspectionCard.repaired ? 'REPARADO ✓' : 'INTERVENCIÓN p53' }}
          </span>
        </div>
        
        <div class="card-damage-kind">
          <Icon name="bolt" size="16" class="damage-bolt" />
          <span>{{ activeInspectionCard.damageKind }}</span>
        </div>

        <div class="card-enzyme-action">
          <span class="enz-prefix">Enzima / Vía Activa:</span>
          <strong class="enz-badge">{{ activeInspectionCard.enzymeName }}</strong>
        </div>
      </div>

      <!-- Barra superior de estado de patrullaje p53 -->
      <div v-if="p53State.active && !activeInspectionCard" class="p53-hud-pill">
        <span class="p53-pulse-dot"></span>
        <span class="p53-pos-tag font-mono">p53 ({{ p53State.p53UnitsCount }} complejos):</span>
        <strong class="p53-label-text">{{ p53State.repairLabel }}</strong>
      </div>

      <!-- Alerta de Apoptosis en Pantalla si el daño supera el umbral crítico -->
      <div v-if="p53State.isApoptosis" class="apoptosis-overlay-banner">
        <div class="apoptosis-alert-card">
          <Icon name="warning" size="24" class="text-rose" />
          <div class="alert-texts">
            <h4>APOPTOSIS CELULAR ACTIVADA</h4>
            <p>Umbral crítico irreparable superado (Alberts et al.). Acumulación masiva de p53 $\rightarrow$ Activación de PUMA / BAX $\rightarrow$ Permeabilización mitocondrial (MOMP).</p>
          </div>
        </div>
      </div>
      <!-- Capa Modelo Atómico Real + Histonas -->
      <div 
        ref="atomicCanvasHolder" 
        class="atomic-canvas-box"
      ></div>

      <!-- HUD Superior Izquierdo: Leyenda Atómica + Octámero de Histonas (Alberts et al.) -->
      <div class="hud-card hud-top-left">
        <div class="hud-card-header">
          <span class="hud-label">ADN-B + Octámero de Histonas y H1</span>
        </div>
        <div class="spectral-legend-grid">
          <span class="spectral-pill a"><span class="swatch" style="background:#8cccff"></span>A · Adenina</span>
          <span class="spectral-pill t"><span class="swatch" style="background:#4080f2"></span>T · Timina</span>
          <span class="spectral-pill g"><span class="swatch" style="background:#bfe0ff"></span>G · Guanina</span>
          <span class="spectral-pill c"><span class="swatch" style="background:#2659d9"></span>C · Citosina</span>
          <span class="spectral-pill caz"><span class="swatch" style="background:#738cbf"></span>Azúcar (Caz)</span>
          <span class="spectral-pill p"><span class="swatch" style="background:#3373e6"></span>Fósforo (P)</span>
          <span class="spectral-pill"><span class="swatch" style="background:#00e5ff"></span>Histona H2A</span>
          <span class="spectral-pill"><span class="swatch" style="background:#10b981"></span>Histona H2B</span>
          <span class="spectral-pill"><span class="swatch" style="background:#3b82f6"></span>Histona H3</span>
          <span class="spectral-pill"><span class="swatch" style="background:#c084fc"></span>Histona H4</span>
          <span class="spectral-pill"><span class="swatch" style="background:#f43f5e"></span>H1 (Ambos lados)</span>
          <span class="spectral-pill hbond"><span class="swatch pin" style="background:#8fb4e0"></span>Puente H</span>
        </div>

        <!-- Resumen de Cálculo Estequiométrico Alberts et al. -->
        <div class="stoich-box" v-if="packagingMode !== 'linear'">
          <div class="stoich-line">
            <span>Regla Alberts (147 pb core + 53 pb linker):</span>
            <strong>{{ atomicStats.theoreticalNucleosomes }}</strong>
          </div>
          <div class="stoich-line">
            <span>Octámeros activos (1.75 vueltas levógiras):</span>
            <strong>{{ atomicStats.nucleosomes }} × (2·H2A, 2·H2B, 2·H3, 2·H4) = {{ atomicStats.octamerSubunits }} subunidades</strong>
          </div>
          <div class="stoich-line">
            <span>Histona H1 (Cromatosoma pluripotente):</span>
            <strong>{{ atomicStats.h1Count }} moléculas H1 (anclaje bilateral)</strong>
          </div>
        </div>
      </div>

      <!-- HUD Atómico Superior Derecho: Detalle del Par -->
      <div class="hud-card hud-top-right" v-if="selectedBaseData">
        <div class="hud-card-header">
          <span class="hud-label">Nucleótido Dúplex (Posición {{ effectiveSelectedPos }})</span>
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
            <span class="hud-bb-tag">Estado:</span>
            <span>{{ packagingMode === 'linear' ? 'Doble hélice expuesta' : 'Enrollado en Superhélice Levógira (1.75 vueltas)' }}</span>
          </div>
        </div>
      </div>

      <!-- Barra de Herramientas Flotante MD3 -->
      <div class="hud-toolbar">
        <div class="toolbar-mode-group">
          <button 
            :class="['md3-icon-btn', { active: dragMode === 'rotate' }]" 
            @click="setDragMode('rotate')" 
            title="Modo Girar: Clic arrastra para orbitar la cromatina en 3D"
          >
            <Icon name="rotate" size="18" />
          </button>
          <button 
            :class="['md3-icon-btn', { active: dragMode === 'pan' }]" 
            @click="setDragMode('pan')" 
            title="Modo Mover: Clic arrastra para desplazar la fibra"
          >
            <Icon name="pan_tool" size="18" />
          </button>
        </div>

        <div class="toolbar-sep"></div>

        <button class="md3-icon-btn" @click="panUp" title="Desplazar arriba">
          <Icon name="arrow_upward" size="18" />
        </button>
        <button class="md3-icon-btn" @click="panDown" title="Desplazar abajo">
          <Icon name="arrow_downward" size="18" />
        </button>

        <div class="toolbar-sep"></div>

        <button class="md3-icon-btn" @click="zoomIn" title="Acercar par seleccionado (+)">
          <Icon name="zoom_in" size="18" />
        </button>
        <button class="md3-icon-btn" @click="zoomOut" title="Ver fibra de cromatina completa (-)">
          <Icon name="zoom_out" size="18" />
        </button>

        <div class="toolbar-sep"></div>

        <button 
          :class="['md3-icon-btn', { active: isAutoRotating }]" 
          @click="toggleAutoRotate" 
          :title="isAutoRotating ? 'Pausar rotación automática' : 'Reanudar rotación automática'"
        >
          <Icon name="3d_rotation" size="18" />
        </button>
        <button class="md3-icon-btn" @click="resetCamera" title="Restablecer vista inicial completa">
          <Icon name="refresh" size="18" />
        </button>
      </div>

      <!-- HUD Inferior: Indicador de Conformación Pre-Replicativa -->
      <div class="hud-bottom-dock">
        <div class="dock-content">
          <Icon name="info" size="16" class="dock-icon" />
          <span>Conformación Pre-Replicativa (Eucromatina Pluripotente) · Rueda: Zoom al cursor · Clic en átomo: Inspeccionar par</span>
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
    default: 'GATTACAGGCTATCCGATACG'
  },
  selectedPosition: {
    type: Number,
    default: 0
  },
  lesions: {
    type: Array,
    default: () => []
  },
  activeAgent: {
    type: String,
    default: 'uv_radiation'
  },
  isSevereDamage: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['selectBase', 'update:selectedPosition', 'openDamageDialog', 'p53Repaired']);


const p53State = ref({
  active: false,
  currentPos: 0,
  repairLabel: 'Patrullando...',
  isApoptosis: false,
  p53UnitsCount: 2
});

const activeInspectionCard = ref(null);

let p53MeshGroup = null;
let mdm2Mesh = null;
let ubiquitinGroup = null;
let p53UnitsList = [];
let p53AnimId = null;

function getDamageInspectionData(agent, pos) {
  if (agent === 'uv_radiation') {
    return {
      damageKind: 'Radiación Ultravioleta (Fotodímero Timina-Timina)',
      enzymeName: 'NER · TFIIH (Helicasas XPB/XPD) + Endonucleasas XPF/XPG'
    };
  }
  if (agent === 'oxidative_ros') {
    return {
      damageKind: 'Estrés Oxidativo ROS (8-oxo-Guanina)',
      enzymeName: 'BER · Glicosilasa OGG1 + Endonucleasa APE1 + ADN Pol β'
    };
  }
  if (agent === 'deamination') {
    return {
      damageKind: 'Desaminación Espontánea (Citosina → Uracilo)',
      enzymeName: 'BER · Uracilo-ADN Glicosilasa (UNG) + ADN Ligasa'
    };
  }
  return {
    damageKind: 'Lesión Dirigida / Rotura CRISPR-Cas9',
    enzymeName: 'HR · Complejo RAD51 + 53BP1 + ADN Ligasa'
  };
}

function triggerP53Patrol() {
  if (p53State.value.active || !lastGeneratedPairs.length) return;
  if (p53AnimId) clearTimeout(p53AnimId);

  p53State.value.active = true;
  p53State.value.isApoptosis = false;
  p53State.value.repairLabel = 'Entrando por el extremo del ADN...';
  activeInspectionCard.value = null;

  // Desacoplar Mdm2 morado y ubiquitinas blancas en todas las unidades
  p53UnitsList.forEach(u => {
    if (u.mdm2) u.mdm2.position.set(0, 7.5, 0);
    if (u.ubi) u.ubi.position.set(0, 11.5, 0);
  });

  const totalPairs = lastGeneratedPairs.length;
  // Conjunto de índices 3D que están dañados
  const pending3DRepairs = new Set(damaged3DPairIndices);
  const totalDamageCount = (props.lesions && props.lesions.length) ? props.lesions.length : damaged3DPairIndices.length;

  // Lógica de apoptosis: Daño masivo / severo según punto de control biológico (≥ 4 lesiones o severe)
  const isFatalApoptosis = props.isSevereDamage || (totalDamageCount >= 4);

  function restoreSingle3DPairToNormal(pair3DIdx) {
    // 1. Retirar baliza roja de este par 3D específico
    const beacon = mainHelixGroup.getObjectByName('lesion_beacon_' + pair3DIdx);
    if (beacon) mainHelixGroup.remove(beacon);

    // 2. Restaurar cada átomo de este par 3D exacto a su color propio canónico
    if (mallaAtomosRef && lastGeneratedAtoms.length) {
      const dummyObj = new THREE.Object3D();
      const atomColor = new THREE.Color();

      lastGeneratedAtoms.forEach((a, ai) => {
        // a[7] es estrictamente el índice 3D del par
        if (a[7] === pair3DIdx) {
          const properHex = ATOMIC_PALETTE[a[4]] ?? 0x94a3b8;
          atomColor.setHex(properHex);
          mallaAtomosRef.setColorAt(ai, atomColor);

          const r = ATOMIC_RADII[a[3]] || 0.45;
          dummyObj.position.set(a[0], a[1], a[2]);
          dummyObj.scale.setScalar(r);
          dummyObj.rotation.set(0, 0, 0);
          dummyObj.updateMatrix();
          mallaAtomosRef.setMatrixAt(ai, dummyObj.matrix);
        }
      });
      mallaAtomosRef.instanceMatrix.needsUpdate = true;
      if (mallaAtomosRef.instanceColor) mallaAtomosRef.instanceColor.needsUpdate = true;
    }

    // 3. Restaurar los enlaces de este par 3D
    if (mallaEnlacesRef && lastGeneratedBonds.length) {
      const bondColor = new THREE.Color();
      lastGeneratedBonds.forEach((b, bi) => {
        if (b[3] === pair3DIdx) {
          const isH = (b[2] === 'h');
          bondColor.setHex(isH ? 0x8fb4e0 : 0x4a6390);
          mallaEnlacesRef.setColorAt(bi, bondColor);
        }
      });
      if (mallaEnlacesRef.instanceColor) mallaEnlacesRef.instanceColor.needsUpdate = true;
    }
  }

  let leadBp = 0;

  function stepPatrol() {
    if (!p53State.value.active) return;

    // Desplazar todo el convoy a lo largo de la cadena entrando por bp = 0
    p53UnitsList.forEach((u, i) => {
      u.currentBp = leadBp - i * 2;

      if (u.currentBp >= 0 && u.currentBp < totalPairs) {
        const pair = lastGeneratedPairs[u.currentBp];
        if (pair && pair.centerPos) {
          const wobble = Math.sin(Date.now() * 0.008 + i) * 0.8;
          u.group.position.set(pair.centerPos[0], pair.centerPos[1] + 1.8 + wobble, pair.centerPos[2]);
        }
      } else if (u.currentBp < 0) {
        const firstPair = lastGeneratedPairs[0];
        if (firstPair) {
          u.group.position.set(firstPair.centerPos[0] + (u.currentBp * 2.5), firstPair.centerPos[1] + 3.0, firstPair.centerPos[2]);
        }
      }
    });

    p53State.value.currentPos = Math.max(0, Math.min(leadBp, totalPairs - 1));

    // Comprobar si en este punto exacto (leadBp) hay un daño pendiente
    if (pending3DRepairs.has(leadBp)) {
      const curPair = lastGeneratedPairs[leadBp];
      const origIndex = curPair ? (curPair.originalIndex ?? (leadBp % cleanFullSequence.value.length)) : leadBp;
      const info = getDamageInspectionData(props.activeAgent, origIndex);

      // Mostrar el cuadro de daño y la enzima
      activeInspectionCard.value = {
        position: leadBp,
        origPosition: origIndex,
        damageKind: info.damageKind,
        enzymeName: info.enzymeName,
        repaired: false,
        isApoptosis: isFatalApoptosis
      };
      p53State.value.repairLabel = info.damageKind + ' → ' + info.enzymeName;

      // Fase 1: p53 anclado en la lesión inspeccionando (1.8 segundos)
      setTimeout(() => {
        if (isFatalApoptosis) {
          // Si el daño es grande, NO puede reparar: se declara fallo en la lesión
          if (activeInspectionCard.value) {
            activeInspectionCard.value.damageKind = 'Daño Insuperable / Sobrecarga de Lesiones';
            activeInspectionCard.value.enzymeName = 'Vía PUMA / BAX Activada (Fallo de Checkpoint)';
          }
          pending3DRepairs.delete(leadBp);

          setTimeout(() => {
            activeInspectionCard.value = null;
            leadBp++;
            if (leadBp < totalPairs) {
              p53AnimId = setTimeout(stepPatrol, 140);
            } else {
              finishPatrol();
            }
          }, 1500);

        } else {
          // Daño reparable: ESE par cambia inmediatamente a su color propio canónico del ADN
          restoreSingle3DPairToNormal(leadBp);
          pending3DRepairs.delete(leadBp);
          if (activeInspectionCard.value) {
            activeInspectionCard.value.repaired = true;
          }

          // Fase 2: Pausa con REPARADO visible (1.3 segundos) antes de seguir a la siguiente
          setTimeout(() => {
            activeInspectionCard.value = null;
            leadBp++;
            if (leadBp < totalPairs) {
              p53AnimId = setTimeout(stepPatrol, 140);
            } else {
              finishPatrol();
            }
          }, 1300);
        }

      }, 1800);

    } else {
      // Avanzar al siguiente segmento
      leadBp++;
      if (leadBp < totalPairs + (p53UnitsList.length * 2)) {
        p53AnimId = setTimeout(stepPatrol, 70);
      } else {
        finishPatrol();
      }
    }
  }

  function finishPatrol() {
    activeInspectionCard.value = null;

    if (isFatalApoptosis) {
      // DAÑO GRANDE: SE PRODUCE APOPTOSIS
      p53State.value.isApoptosis = true;
      p53State.value.repairLabel = 'Umbral crítico superado → Apoptosis Celular (Puma / Bax)';
      setTimeout(() => {
        p53State.value.active = false;
        // Retornar a reposo
        p53UnitsList.forEach(u => {
          if (u.floatingAnchor) {
            u.group.position.set(u.floatingAnchor[0], u.floatingAnchor[1], u.floatingAnchor[2]);
          }
          if (u.mdm2) u.mdm2.position.set(0, 1.9, 0);
          if (u.ubi) u.ubi.position.set(0, 0, 0);
        });
      }, 5000);
    } else {
      // REPARACIÓN EXITOSA
      p53State.value.repairLabel = 'ADN 100% Reparado ✓ · Hebra Íntegra';
      setTimeout(() => {
        p53State.value.active = false;
        p53UnitsList.forEach(u => {
          if (u.floatingAnchor) {
            u.group.position.set(u.floatingAnchor[0], u.floatingAnchor[1], u.floatingAnchor[2]);
          }
          if (u.mdm2) u.mdm2.position.set(0, 1.9, 0);
          if (u.ubi) u.ubi.position.set(0, 0, 0);
        });
        emit('p53Repaired');
      }, 1600);
    }
  }

  stepPatrol();
}

const internalSelectedPos = ref(props.selectedPosition ?? 0);
const packagingMode = ref('chromatin_adaptive'); // 'chromatin_adaptive' | 'chromatin_alberts' | 'linear'

// Guardamos los pares generados para que zoomIn y el selector apunten a la coordenada 3D exacta
let lastGeneratedPairs = [];
let lastGeneratedAtoms = [];
let lastGeneratedBonds = [];
let mallaAtomosRef = null;
let mallaEnlacesRef = null;
let damaged3DPairIndices = [];

function cyclePackagingMode() {
  if (packagingMode.value === 'chromatin_adaptive') {
    packagingMode.value = 'chromatin_alberts';
  } else if (packagingMode.value === 'chromatin_alberts') {
    packagingMode.value = 'linear';
  } else {
    packagingMode.value = 'chromatin_adaptive';
  }
  buildDNAHelix(true);
}

watch(() => props.selectedPosition, (newVal) => {
  if (newVal !== undefined && newVal !== null) {
    internalSelectedPos.value = newVal;
    buildDNAHelix(false);
  }
});

const effectiveSelectedPos = computed(() => {
  const maxLen = cleanFullSequence.value.length;
  const raw = (internalSelectedPos.value !== null && internalSelectedPos.value !== undefined)
    ? internalSelectedPos.value
    : (props.selectedPosition ?? 0);
  if (maxLen <= 0) return 0;
  return Math.max(0, Math.min(raw, maxLen - 1));
});

const canvasContainer = ref(null);
const atomicCanvasHolder = ref(null);
const isExpanded = ref(false);
const isAutoRotating = ref(false);
const dragMode = ref('rotate');

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
  pairsCount: 0,
  renderedBp: 0,
  nucleosomes: 0,
  theoreticalNucleosomes: '',
  octamerSubunits: 0,
  h1Count: 0,
  totalHistones: 0
});

const cleanFullSequence = computed(() => {
  return props.sequence.toUpperCase().replace(/[^ATCG]/g, '') || 'GATTACAGGCTATCCGATACG';
});

const selectedBaseData = computed(() => {
  const clean = cleanFullSequence.value;
  const pos = effectiveSelectedPos.value;
  if (!clean || pos < 0 || pos >= clean.length) return null;
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

function buildDNAHelix(reframe = false) {
  if (!mainHelixGroup || !scene) return;

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

  const seq = cleanFullSequence.value;
  if (!seq || !seq.length) return;

  mainHelixGroup.rotation.x = packagingMode.value === 'linear' ? -Math.PI / 2 : 0;

  // Genera exactamente los pares de bases de `seq` (sin clonar ni alterar la muestra)
  const atomicData = generateAtomicDNA(seq, true, packagingMode.value);
  const { atoms, bonds, pairs, histoneSpheres, h1Rods, stoichiometry } = atomicData;
  lastGeneratedPairs = pairs;
  lastGeneratedAtoms = atoms;
  lastGeneratedBonds = bonds;

  atomicStats.value = {
    totalAtoms: atomicData.totalAtoms,
    totalBonds: atomicData.totalBonds,
    pairsCount: pairs.length,
    renderedBp: stoichiometry.renderedBp,
    nucleosomes: stoichiometry.nucleosomeCount,
    theoreticalNucleosomes: stoichiometry.albertsRatioText,
    octamerSubunits: stoichiometry.octamerSubunits,
    h1Count: stoichiometry.h1Count,
    totalHistones: stoichiometry.totalHistoneProteins
  };

  const selPos = effectiveSelectedPos.value;
  const dummy = new THREE.Object3D();
  const color = new THREE.Color();

  // Conjunto de posiciones con daño (lesiones ambientales o mutaciones)
  const damagedPositions = new Set(
    (props.lesions || []).map(l => (typeof l === 'object' && l.position !== undefined) ? Number(l.position) : Number(l))
  );

  // 1. ÁTOMOS DE LA SECUENCIA REAL (Resalta suavemente el par seleccionado)
  const geoEsfera = new THREE.SphereGeometry(1, 20, 16);
  const matEsfera = new THREE.MeshStandardMaterial({ roughness: 0.3, metalness: 0.08 });
  const mallaAtomos = new THREE.InstancedMesh(geoEsfera, matEsfera, atoms.length);
  const atomPairMap = [];

  atoms.forEach((a, i) => {
    dummy.position.set(a[0], a[1], a[2]);
    const isSelectedPair = (a[7] === selPos);
    const isDamagedPair = damagedPositions.has(a[7]);
    const r = (ATOMIC_RADII[a[3]] || 0.45) * (isDamagedPair ? 1.55 : (isSelectedPair ? 1.4 : 1.15));
    dummy.scale.setScalar(r);
    dummy.rotation.set(0, 0, 0);
    dummy.updateMatrix();
    mallaAtomos.setMatrixAt(i, dummy.matrix);

    if (isDamagedPair) {
      color.setHex(0xff1a1a); // Rojo fuego de daño
    } else if (isSelectedPair) {
      color.setHex(0x38bdf8).lerp(new THREE.Color(0xffffff), 0.55);
    } else {
      color.setHex(ATOMIC_PALETTE[a[4]] ?? 0x94a3b8);
    }
    mallaAtomos.setColorAt(i, color);
    atomPairMap.push(a[5]);
  });

  mallaAtomos.instanceMatrix.needsUpdate = true;
  if (mallaAtomos.instanceColor) mallaAtomos.instanceColor.needsUpdate = true;
  mallaAtomos.userData = { atomPairMap };
  mallaAtomosRef = mallaAtomos;
  clickableObjects.push(mallaAtomos);
  mainHelixGroup.add(mallaAtomos);

  // 2. ENLACES COVALENTES Y PUENTES DE HIDRÓGENO
  const geoCil = new THREE.CylinderGeometry(1, 1, 1, 8);
  const matCil = new THREE.MeshStandardMaterial({ roughness: 0.45, metalness: 0.05 });
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

    const bPairIdx = e[3];
    const isDamagedBond = damagedPositions.has(bPairIdx);

    if (isDamagedBond) {
      color.setHex(0xff3b30);
    } else {
      color.setHex(isH ? 0x8fb4e0 : 0x4a6390);
    }
    mallaEnlaces.setColorAt(i, color);
  });

  mallaEnlaces.instanceMatrix.needsUpdate = true;
  if (mallaEnlaces.instanceColor) mallaEnlaces.instanceColor.needsUpdate = true;
  mallaEnlacesRef = mallaEnlaces;
  mainHelixGroup.add(mallaEnlaces);

  // 3. OCTÁMEROS DE HISTONAS + ANCLAJES LATERALES DE HISTONA H1 (Rosa/Magenta en ambos lados)
  if (histoneSpheres.length > 0) {
    const geoHist = new THREE.SphereGeometry(1, 24, 18);
    const matHist = new THREE.MeshStandardMaterial({
      roughness: 0.32,
      metalness: 0.12
    });
    const mallaHistonas = new THREE.InstancedMesh(geoHist, matHist, histoneSpheres.length);

    histoneSpheres.forEach((hs, idx) => {
      dummy.position.set(hs[0], hs[1], hs[2]);
      dummy.rotation.set(0, 0, 0);
      dummy.scale.setScalar(hs[3]);
      dummy.updateMatrix();
      mallaHistonas.setMatrixAt(idx, dummy.matrix);

      color.setHex(hs[4]);
      mallaHistonas.setColorAt(idx, color);
    });

    mallaHistonas.instanceMatrix.needsUpdate = true;
    if (mallaHistonas.instanceColor) mallaHistonas.instanceColor.needsUpdate = true;
    mainHelixGroup.add(mallaHistonas);
  }

  // 4. PUENTES DE RECOGIMIENTO Y TALLO DE HISTONA H1
  if (h1Rods.length > 0) {
    const geoRod = new THREE.CylinderGeometry(1, 0.85, 1, 14);
    h1Rods.forEach(rod => {
      const matRod = new THREE.MeshStandardMaterial({
        color: rod.color,
        roughness: 0.28,
        metalness: 0.15,
        emissive: rod.color,
        emissiveIntensity: 0.22
      });

      p1.set(rod.start[0], rod.start[1], rod.start[2]);
      p2.set(rod.end[0], rod.end[1], rod.end[2]);
      dir.subVectors(p2, p1);
      const len = dir.length();
      med.addVectors(p1, p2).multiplyScalar(0.5);

      const meshRod = new THREE.Mesh(geoRod, matRod);
      meshRod.position.copy(med);
      meshRod.quaternion.setFromUnitVectors(up, dir.normalize());
      meshRod.scale.set(rod.radius, len, rod.radius);
      mainHelixGroup.add(meshRod);
    });
  }

  // 5. ANILLO INDICADOR 3D ORIENTADO EN EL PAR DE BASES SELECCIONADO (funciona en curva y en línea)
  if (selPos >= 0 && selPos < pairs.length) {
    const activePair = pairs[selPos];
    const ringGeo = new THREE.RingGeometry(11.2, 12.8, 48);
    const ringMat = new THREE.MeshBasicMaterial({
      color: 0x38bdf8,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.9
    });
    const ringMesh = new THREE.Mesh(ringGeo, ringMat);
    const [cx, cy, cz] = activePair.centerPos;
    ringMesh.position.set(cx, cy, cz);

    if (activePair.tangent) {
      const normalZ = new THREE.Vector3(0, 0, 1);
      const tang = new THREE.Vector3(
        activePair.tangent[0],
        activePair.tangent[1],
        activePair.tangent[2]
      ).normalize();
      ringMesh.quaternion.setFromUnitVectors(normalZ, tang);
    }
    mainHelixGroup.add(ringMesh);
  }

  // 6. BALIZAS RESPLANDECIENTES DE DAÑO EN CADA PAR 3D LESIONADO
  damaged3DPairIndices = [];
  pairs.forEach((p, pIdx) => {
    if (damagedPositions.has(pIdx)) {
      damaged3DPairIndices.push(pIdx);
      if (p.centerPos) {
        const [dx, dy, dz] = p.centerPos;
        const damRingGeo = new THREE.TorusGeometry(8.5, 0.95, 12, 32);
        const damRingMat = new THREE.MeshStandardMaterial({
          color: 0xff1e00,
          emissive: 0xff3b30,
          emissiveIntensity: 0.9,
          roughness: 0.2
        });
        const damMesh = new THREE.Mesh(damRingGeo, damRingMat);
        damMesh.position.set(dx, dy, dz);
        if (p.tangent) {
          damMesh.quaternion.setFromUnitVectors(
            new THREE.Vector3(0, 0, 1),
            new THREE.Vector3(p.tangent[0], p.tangent[1], p.tangent[2]).normalize()
          );
        }
        damMesh.name = 'lesion_beacon_' + pIdx;
        mainHelixGroup.add(damMesh);
      }
    }
  });

      // 7. COMPLEJOS MOLECULARES p53 / Mdm2 / Ubiquitina (Tamaño molecular elegante y proporcionado)
  p53MeshGroup = new THREE.Group();
  p53MeshGroup.name = 'p53_complex_group';

  const numLesions = damagedPositions.size;
  const p53Count = numLesions > 0 ? Math.min(8, Math.max(2, numLesions * 2)) : 2;
  p53State.value.p53UnitsCount = p53Count;

  // Materiales requeridos: p53 ÁMBAR, Mdm2 MORADO, Ubiquitina BLANCA
  const matP53Amber = new THREE.MeshStandardMaterial({ 
    color: 0xf59e0b, 
    roughness: 0.25, 
    metalness: 0.2,
    emissive: 0xd97706,
    emissiveIntensity: 0.45 
  });

  const matMdm2Purple = new THREE.MeshStandardMaterial({ 
    color: 0x8b5cf6, 
    roughness: 0.35, 
    metalness: 0.15,
    emissive: 0x6d28d9,
    emissiveIntensity: 0.35
  });

  const matUbiWhite = new THREE.MeshStandardMaterial({ 
    color: 0xffffff, 
    roughness: 0.2, 
    metalness: 0.1, 
    emissive: 0xffffff, 
    emissiveIntensity: 0.5 
  });

  // Geometría reducida a escala molecular fina (mucho más chicos)
  const geoP53 = new THREE.SphereGeometry(1.5, 18, 14);
  const geoMdm2 = new THREE.SphereGeometry(1.15, 16, 12);
  const geoUbi = new THREE.SphereGeometry(0.48, 12, 10);

  p53UnitsList = [];
  const firstP = pairs[0]?.centerPos || [0, 0, 0];

  for (let u = 0; u < p53Count; u++) {
    const unitGroup = new THREE.Group();
    unitGroup.name = 'p53_unit_' + u;

    // Bola ámbar central (p53)
    const p53Mesh = new THREE.Mesh(geoP53, matP53Amber);
    unitGroup.add(p53Mesh);

    // Mdm2 morado pegado al lateral
    const mdm2M = new THREE.Mesh(geoMdm2, matMdm2Purple);
    mdm2M.position.set(0, 1.9, 0);
    mdm2M.name = 'mdm2_sub_' + u;
    unitGroup.add(mdm2M);

    // Bolitas blancas de ubiquitina pegadas en la unión Mdm2-p53
    const ubiG = new THREE.Group();
    ubiG.name = 'ubi_group_' + u;
    const u1 = new THREE.Mesh(geoUbi, matUbiWhite); u1.position.set(0.7, 1.7, 0.4); ubiG.add(u1);
    const u2 = new THREE.Mesh(geoUbi, matUbiWhite); u2.position.set(-0.7, 1.7, 0.4); ubiG.add(u2);
    const u3 = new THREE.Mesh(geoUbi, matUbiWhite); u3.position.set(0, 2.6, 0.3); ubiG.add(u3);
    unitGroup.add(ubiG);

    // Posición de reposo: Separado cómodamente del ADN (12 Å debajo de la entrada), sin estar lejos
    const anchor = [
      firstP[0] + (u - p53Count / 2) * 5.0,
      firstP[1] - 12.0,
      firstP[2] + 4.0 + (u % 2) * 2.5
    ];
    unitGroup.position.set(anchor[0], anchor[1], anchor[2]);

    p53MeshGroup.add(unitGroup);
    p53UnitsList.push({
      group: unitGroup,
      mdm2: mdm2M,
      ubi: ubiG,
      floatingAnchor: anchor,
      currentBp: 0
    });
  }

  mainHelixGroup.add(p53MeshGroup);

  if (reframe) {
    const allPts = atoms.map(a => [a[0], a[1], a[2]]);
    p53UnitsList.forEach(u => {
      if (u.floatingAnchor) allPts.push(u.floatingAnchor);
    });
    encuadrar(allPts);
  }
}

function encuadrar(puntos) {
  if (!camera || !controls || !puntos.length) return;

  const caja = new THREE.Box3();
  const isLinear = packagingMode.value === 'linear';
  puntos.forEach(p => {
    if (isLinear) {
      caja.expandByPoint(new THREE.Vector3(p[0], p[2], -p[1]));
    } else {
      caja.expandByPoint(new THREE.Vector3(p[0], p[1], p[2]));
    }
  });

  const centro = caja.getCenter(new THREE.Vector3());
  const tam = caja.getSize(new THREE.Vector3());
  const maxDim = Math.max(tam.x, tam.y, tam.z);
  const dist = isLinear ? maxDim * 1.55 : maxDim * 1.15;

  camera.position.set(centro.x, centro.y, dist);
  controls.target.copy(centro);
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
  scene.background = new THREE.Color(0x030b24);
  scene.fog = new THREE.Fog(0x030b24, 350, 1200);

  camera = new THREE.PerspectiveCamera(40, width / height, 0.1, 4000);

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false, powerPreference: 'high-performance' });
  renderer.setSize(width, height);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.25;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  container.appendChild(renderer.domElement);

  scene.add(new THREE.AmbientLight(0x0c4a6e, 1.4));
  scene.add(new THREE.HemisphereLight(0xbfd9ff, 0x030b24, 0.95));

  const clave = new THREE.DirectionalLight(0xe0f2fe, 2.4);
  clave.position.set(60, 90, 80);
  scene.add(clave);

  const borde = new THREE.DirectionalLight(0x38bdf8, 1.8);
  borde.position.set(-70, -40, -60);
  scene.add(borde);

  const bgGeo = new THREE.BufferGeometry();
  const bgPos = new Float32Array(250 * 3);
  for (let i = 0; i < 250 * 3; i += 3) {
    bgPos[i] = (Math.random() - 0.5) * 420;
    bgPos[i + 1] = (Math.random() - 0.5) * 280;
    bgPos[i + 2] = (Math.random() - 0.5) * 200;
  }
  bgGeo.setAttribute('position', new THREE.BufferAttribute(bgPos, 3));
  const bgMat = new THREE.PointsMaterial({
    color: 0x38bdf8,
    size: 0.9,
    transparent: true,
    opacity: 0.35,
    blending: THREE.AdditiveBlending
  });
  scene.add(new THREE.Points(bgGeo, bgMat));

  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.06;
  controls.autoRotate = isAutoRotating.value;
  controls.autoRotateSpeed = 0.7;
  controls.minDistance = 6.0;
  controls.maxDistance = 3000.0;
  controls.screenSpacePanning = true;
  controls.enableZoom = false;

  controls.mouseButtons = {
    LEFT: dragMode.value === 'pan' ? THREE.MOUSE.PAN : THREE.MOUSE.ROTATE,
    MIDDLE: THREE.MOUSE.DOLLY,
    RIGHT: THREE.MOUSE.PAN
  };

  mainHelixGroup = new THREE.Group();
  scene.add(mainHelixGroup);

  buildDNAHelix(true);

  container.addEventListener('wheel', handleCanvasWheel, { passive: false });

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
            internalSelectedPos.value = globalPairIdx;
            emit('selectBase', globalPairIdx);
            emit('update:selectedPosition', globalPairIdx);
            buildDNAHelix(false); // Redibuja de inmediato el anillo y el resaltado en el par clicado
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

  // Animación de p53 en posición inicial: FUERA DEL ADN, flotando y moviéndose orgánicamente
  if (!p53State.value.active && p53UnitsList.length > 0) {
    const t = Date.now() * 0.0016;
    p53UnitsList.forEach((u, i) => {
      if (u.floatingAnchor && u.group) {
        const hoverX = Math.cos(t * 1.2 + i * 1.5) * 4.2;
        const hoverY = Math.sin(t * 1.5 + i * 1.8) * 4.5;
        const hoverZ = Math.sin(t * 1.0 + i * 1.2) * 3.6;
        u.group.position.set(
          u.floatingAnchor[0] + hoverX,
          u.floatingAnchor[1] + hoverY,
          u.floatingAnchor[2] + hoverZ
        );
        u.group.rotation.y += 0.006;
      }
    });
  }

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

function setDragMode(mode) {
  dragMode.value = mode;
  if (!controls) return;
  controls.mouseButtons.LEFT = mode === 'pan' ? THREE.MOUSE.PAN : THREE.MOUSE.ROTATE;
  controls.autoRotate = mode === 'pan' ? false : isAutoRotating.value;
}

function toggleAutoRotate() {
  isAutoRotating.value = !isAutoRotating.value;
  if (controls) controls.autoRotate = isAutoRotating.value;
}

function toggleExpand() {
  isExpanded.value = !isExpanded.value;
  nextTick(() => onWindowResize());
}

function panUp() {
  if (!camera || !controls) return;
  const offset = new THREE.Vector3(0, 12, 0);
  camera.position.add(offset);
  controls.target.add(offset);
  controls.update();
}

function panDown() {
  if (!camera || !controls) return;
  const offset = new THREE.Vector3(0, -12, 0);
  camera.position.add(offset);
  controls.target.add(offset);
  controls.update();
}

// Zoom directo al par de bases seleccionado (tanto en modo cromatina curva como en modo lineal)
function zoomIn() {
  if (!camera || !controls) return;
  const sel = effectiveSelectedPos.value;
  if (sel >= 0 && sel < lastGeneratedPairs.length) {
    const pair = lastGeneratedPairs[sel];
    const [px, py, pz] = pair.centerPos;
    const worldTarget = packagingMode.value === 'linear'
      ? new THREE.Vector3(px, pz, -py)
      : new THREE.Vector3(px, py, pz);

    controls.target.copy(worldTarget);
    const camDir = camera.position.clone().sub(worldTarget).normalize();
    if (camDir.lengthSq() < 0.01) camDir.set(0, 0, 1);
    camera.position.copy(worldTarget).add(camDir.multiplyScalar(28.0));
    controls.update();
  }
}

function zoomOut() {
  resetCamera();
}

function handleCanvasWheel(e) {
  e.preventDefault();
  if (!camera || !controls || !scene) return;
  const container = atomicCanvasHolder.value || canvasContainer.value;
  if (!container) return;

  const rect = container.getBoundingClientRect();
  const mouse = new THREE.Vector2(
    ((e.clientX - rect.left) / rect.width) * 2 - 1,
    -((e.clientY - rect.top) / rect.height) * 2 + 1
  );

  const zoomFactor = e.deltaY < 0 ? 0.88 : 1.14;
  const raycaster = new THREE.Raycaster();
  raycaster.setFromCamera(mouse, camera);

  let focusPoint = new THREE.Vector3();
  const hits = raycaster.intersectObjects(clickableObjects, false);

  if (hits.length > 0) {
    focusPoint.copy(hits[0].point);
  } else {
    const camDir = new THREE.Vector3();
    camera.getWorldDirection(camDir);
    const plane = new THREE.Plane();
    plane.setFromNormalAndCoplanarPoint(camDir.clone().negate(), controls.target);
    if (!raycaster.ray.intersectPlane(plane, focusPoint)) {
      focusPoint.copy(controls.target);
    }
  }

  const camToFocus = camera.position.clone().sub(focusPoint);
  const targetToFocus = controls.target.clone().sub(focusPoint);
  const currentDist = camera.position.distanceTo(controls.target);
  const nextDist = currentDist * zoomFactor;

  if (nextDist >= controls.minDistance && nextDist <= controls.maxDistance) {
    camera.position.copy(focusPoint).add(camToFocus.multiplyScalar(zoomFactor));
    controls.target.copy(focusPoint).add(targetToFocus.multiplyScalar(zoomFactor));
    controls.update();
  }
}

function resetCamera() {
  if (!camera || !controls) return;
  camera.position.copy(camPos0);
  controls.target.copy(target0);
  controls.update();
}

watch(() => props.sequence, () => {
  internalSelectedPos.value = 0;
  buildDNAHelix(true);
});

watch(() => props.lesions, (newLesions) => {
  buildDNAHelix(false);
  if (newLesions && newLesions.length > 0) {
    nextTick(() => {
      triggerP53Patrol();
    });
  }
}, { deep: true });

watch(() => props.activeAgent, () => {
  buildDNAHelix(false);
});

onMounted(() => {
  initScene();
  window.addEventListener('resize', onWindowResize);
  if (canvasContainer.value) {
    resizeObserver = new ResizeObserver(() => onWindowResize());
    resizeObserver.observe(canvasContainer.value);
  }
  setTimeout(onWindowResize, 60);
});

onUnmounted(() => {
  if (animId) cancelAnimationFrame(animId);
  window.removeEventListener('resize', onWindowResize);
  const container = atomicCanvasHolder.value || canvasContainer.value;
  if (container) container.removeEventListener('wheel', handleCanvasWheel);
  if (resizeObserver) resizeObserver.disconnect();
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
  background: radial-gradient(ellipse at 50% 50%, #0c1a2e 0%, #06111e 65%, #040812 100%);
}

.dna-3d-card.cinema-expanded .canvas-wrapper {
  height: calc(100vh - 120px);
}

.canvas-wrapper:active {
  cursor: grabbing;
}

.canvas-wrapper.pan-mode {
  cursor: move;
}

.canvas-wrapper.pan-mode:active {
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
  gap: 0.35rem;
  z-index: 10;
  align-items: center;
}

.toolbar-mode-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(56, 189, 248, 0.25);
  border-radius: 20px;
  padding: 3px;
}

.toolbar-sep {
  width: 20px;
  height: 1px;
  background: rgba(56, 189, 248, 0.25);
  margin: 0.1rem auto;
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

/* Resumen de Cálculo Estequiométrico Alberts et al. */
.stoich-box {
  margin-top: 0.65rem;
  padding-top: 0.5rem;
  border-top: 1px solid rgba(56, 189, 248, 0.2);
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.68rem;
  color: #94a3b8;
}
.stoich-line {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
}
.stoich-line strong {
  color: #38bdf8;
  font-family: monospace;
}

.damage-trigger-chip {
  background: rgba(245, 158, 11, 0.12) !important;
  border-color: rgba(245, 158, 11, 0.45) !important;
  color: #fbbf24 !important;
  font-weight: 600;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.damage-trigger-chip:hover {
  background: rgba(245, 158, 11, 0.25) !important;
  border-color: #f59e0b !important;
  color: #fef3c7 !important;
  box-shadow: 0 0 12px rgba(245, 158, 11, 0.35);
  transform: translateY(-1px);
}

.text-amber {
  color: #fbbf24;
}

/* Botón y Badge de p53 */
.p53-trigger-chip {
  background: rgba(16, 185, 129, 0.12) !important;
  border-color: rgba(16, 185, 129, 0.45) !important;
  color: #34d399 !important;
  font-weight: 600;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}
.p53-trigger-chip:hover, .p53-trigger-chip.p53-active {
  background: rgba(16, 185, 129, 0.25) !important;
  border-color: #10b981 !important;
  color: #a7f3d0 !important;
  box-shadow: 0 0 12px rgba(16, 185, 129, 0.4);
}
.text-emerald {
  color: #34d399;
}
.p53-idle-badge {
  position: absolute;
  bottom: 2.8rem;
  left: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(15, 23, 42, 0.85);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(245, 158, 11, 0.35);
  border-radius: 9999px;
  padding: 0.35rem 0.85rem;
  font-size: 0.72rem;
  color: #fbbf24;
  font-weight: 600;
  pointer-events: none;
  z-index: 15;
}
.idle-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #f59e0b;
  box-shadow: 0 0 6px #f59e0b;
}
.text-rose {
  color: #f43f5e;
}
.p53-hud-pill.apoptosis-pill {
  border-color: #f43f5e !important;
  box-shadow: 0 0 20px rgba(244, 63, 94, 0.45) !important;
  background: rgba(30, 10, 20, 0.95) !important;
}
.p53-pulse-dot.red-pulse {
  background: #f43f5e !important;
  box-shadow: 0 0 10px #f43f5e !important;
}

/* Banner Flotante de Apoptosis en Pantalla */
.apoptosis-overlay-banner {
  position: absolute;
  bottom: 3.5rem;
  left: 50%;
  transform: translateX(-50%);
  z-index: 30;
  pointer-events: none;
  animation: bounceIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.apoptosis-alert-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: rgba(15, 5, 10, 0.92);
  backdrop-filter: blur(12px);
  border: 1.5px solid #f43f5e;
  border-radius: 12px;
  padding: 0.85rem 1.4rem;
  box-shadow: 0 8px 32px rgba(244, 63, 94, 0.4);
  max-width: 580px;
}
.alert-texts h4 {
  margin: 0;
  color: #f43f5e;
  font-size: 0.92rem;
  font-weight: 800;
  letter-spacing: 0.05em;
}
.alert-texts p {
  margin: 0.2rem 0 0 0;
  color: #fecdd3;
  font-size: 0.74rem;
  line-height: 1.35;
}

/* RECUADRO PROMINENTE DE INSPECCIÓN Y REPARACIÓN p53 */
.damage-inspection-card {
  position: absolute;
  top: 1.25rem;
  left: 50%;
  transform: translateX(-50%);
  z-index: 40;
  background: rgba(11, 19, 38, 0.94);
  backdrop-filter: blur(14px);
  border: 1.5px solid rgba(245, 158, 11, 0.65);
  border-radius: 12px;
  padding: 0.85rem 1.35rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6), 0 0 25px rgba(245, 158, 11, 0.35);
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  min-width: 420px;
  max-width: 540px;
  animation: fadeInDown 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
  pointer-events: none;
}
.card-accent-line {
  position: absolute;
  top: 0;
  left: 10%;
  right: 10%;
  height: 2px;
  background: linear-gradient(90deg, transparent, #f59e0b, #10b981, transparent);
}
.card-top-line {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.badge-left {
  display: flex;
  align-items: center;
  gap: 0.45rem;
}
.pulse-warning-dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: #f59e0b;
  box-shadow: 0 0 10px #f59e0b;
  animation: pulse 0.9s infinite alternate;
}
.bp-coord {
  color: #fbbf24;
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.05em;
}
.card-state-pill {
  font-size: 0.68rem;
  font-weight: 800;
  padding: 0.2rem 0.6rem;
  border-radius: 9999px;
  letter-spacing: 0.06em;
}
.card-state-pill.active {
  background: rgba(245, 158, 11, 0.2);
  color: #fbbf24;
  border: 1px solid rgba(245, 158, 11, 0.4);
}
.card-state-pill.repaired {
  background: rgba(16, 185, 129, 0.25);
  color: #34d399;
  border: 1px solid #10b981;
}
.card-damage-kind {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  color: #f87171;
  font-size: 0.82rem;
  font-weight: 700;
}
.damage-bolt {
  color: #f87171;
}
.card-enzyme-action {
  display: flex;
  align-items: baseline;
  gap: 0.45rem;
  font-size: 0.76rem;
  color: #94a3b8;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  padding-top: 0.35rem;
}
.enz-prefix {
  color: #94a3b8;
  font-size: 0.72rem;
}
.enz-badge {
  color: #38bdf8;
  font-weight: 700;
}

/* Badge Flotante Conciso p53 (Solo enzima y mecanismo activo) */
.p53-hud-pill {
  position: absolute;
  top: 1rem;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 0.55rem;
  background: rgba(15, 23, 42, 0.88);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(52, 211, 153, 0.45);
  border-radius: 9999px;
  padding: 0.45rem 1.1rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4), 0 0 16px rgba(16, 185, 129, 0.25);
  z-index: 25;
  pointer-events: none;
  animation: fadeInDown 0.25s ease-out;
}
.p53-pulse-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #34d399;
  box-shadow: 0 0 8px #34d399;
  animation: pulse 1s infinite alternate;
}
.p53-pos-tag {
  color: #94a3b8;
  font-size: 0.76rem;
  font-weight: 500;
}
.p53-label-text {
  color: #f0fdf4;
  font-size: 0.82rem;
  font-weight: 700;
  letter-spacing: 0.02em;
}

</style>
