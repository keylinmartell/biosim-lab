<template>
  <div ref="cardRoot" class="dna-3d-card md3-card-outlined" :class="{ 'cinema-expanded': isExpanded }">
    <!-- Header de Tarjeta MD3 (Tonal Surface Header) -->
    <div class="card-header">
      <div class="header-main">
        <div class="header-avatar">
          <Icon name="dna" size="22" />
        </div>
        <div class="header-titles">
          <h3 class="title-text">
            {{ packagingMode === 'linear' ? 'Modelo Atómico Tridimensional (B-DNA)' : 'Fibra de Cromatina (Alberts et al. · 147 pb)' }}
          </h3>
          <span class="subhead-text">
            {{ atomicStats.nucleosomes }} Nucleosomas ({{ atomicStats.octamerSubunits }} histonas core + {{ atomicStats.h1Count }} H1 lábil) · {{ atomicStats.totalAtoms }} átomos de ADN
          </span>
        </div>
      </div>

      <div class="header-chips">
        <!-- Barra de Herramientas de Navegación 3D Integrada -->
        <div class="header-nav-toolbar">
          <div class="nav-mode-pill">
            <button 
              :class="['nav-tool-btn', { active: dragMode === 'rotate' }]" 
              @click="setDragMode('rotate')" 
              title="Modo Girar: Clic y arrastra para orbitar en 3D"
            >
              <Icon name="rotate" size="15" />
            </button>
            <button 
              :class="['nav-tool-btn', { active: dragMode === 'pan' }]" 
              @click="setDragMode('pan')" 
              title="Modo Mover: Clic y arrastra para desplazar la fibra"
            >
              <Icon name="pan_tool" size="15" />
            </button>
          </div>

          <div class="nav-tools-divider"></div>

          <button class="nav-tool-btn" @click="panUp" title="Desplazar arriba">
            <Icon name="arrow_upward" size="15" />
          </button>
          <button class="nav-tool-btn" @click="panDown" title="Desplazar abajo">
            <Icon name="arrow_downward" size="15" />
          </button>

          <div class="nav-tools-divider"></div>

          <button class="nav-tool-btn" @click="zoomIn" title="Acercar par seleccionado (+)">
            <Icon name="zoom_in" size="16" />
          </button>
          <button class="nav-tool-btn" @click="zoomOut" title="Ver fibra completa (-)">
            <Icon name="zoom_out" size="16" />
          </button>

          <div class="nav-tools-divider"></div>

          <button 
            :class="['nav-tool-btn', { active: isAutoRotating }]" 
            @click="toggleAutoRotate" 
            :title="isAutoRotating ? 'Pausar rotación' : 'Rotación automática'"
          >
            <Icon name="3d_rotation" size="15" />
          </button>
          <button class="nav-tool-btn" @click="resetCamera" title="Restablecer vista inicial">
            <Icon name="refresh" size="15" />
          </button>
        </div>

        <!-- Selector de Empaquetamiento en Histonas -->
        <button 
          class="md3-chip interactive-chip" 
          @click="cyclePackagingMode"
          title="Alternar entre Fibra de Cromatina (Alberts et al. · 147 pb) y ADN-B Lineal"
        >
          <Icon name="hub" size="14" class="chip-lead" />
          <span class="font-mono">
            {{ packagingMode === 'chromatin_alberts' ? 'Cromatina (Alberts 147 pb)' : 'ADN-B Lineal' }}
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
      <div v-if="p53State.active && !activeInspectionCard && !p53State.isApoptosis" class="p53-hud-pill">
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

      <!-- Barra Interactiva de Identificación y Enfoque de Complejos 3D (Alberts et al.) -->
      <div class="molecular-complex-focus-bar" aria-label="Mapa de Complejos 3D sobre el ADN">
        <button 
          class="complex-focus-pill" 
          :class="{ active: activeFocusKey === 'all' }"
          @click="focusOnComplex('all')"
          title="Ver escena molecular completa"
        >
          <span class="cf-dot" style="background:#38bdf8"></span>
          <span>Vista Global</span>
        </button>
        <button 
          class="complex-focus-pill" 
          :class="{ active: activeFocusKey === 'p53' }"
          @click="focusOnComplex('p53')"
          title="Enfocar Tetrámero p53, Fosfatos Ser15/Ser20 y Ligasa E3 MDM2-Ubiquitina"
        >
          <span class="cf-dot" style="background:#f59e0b"></span>
          <span>p53 Tetrámero · MDM2</span>
        </button>
        <button 
          class="complex-focus-pill" 
          :class="{ active: activeFocusKey === 'cdk46' }"
          @click="focusOnComplex('cdk46')"
          title="Enfocar complejo iniciador G1 Ciclina D–CDK4/6"
        >
          <span class="cf-dot" style="background:#eab308"></span>
          <span>Ciclina D–CDK4/6</span>
        </button>
        <button 
          class="complex-focus-pill" 
          :class="{ active: activeFocusKey === 'cdk2' }"
          @click="focusOnComplex('cdk2')"
          title="Enfocar Ciclina E–CDK2 y la pinza inhibidora alostérica p21 (CIP1/WAF1)"
        >
          <span class="cf-dot" style="background:#38bdf8"></span>
          <span>Ciclina E–CDK2 · p21</span>
        </button>
        <button 
          class="complex-focus-pill" 
          :class="{ active: activeFocusKey === 'rb_e2f' }"
          @click="focusOnComplex('rb_e2f')"
          title="Enfocar Locus Promotor en el ADN: Factor E2F–DP1 y Bolsillo de Rb (Punto R)"
        >
          <span class="cf-dot" style="background:#ec4899"></span>
          <span>Promotor Rb · E2F</span>
        </button>
        <button 
          v-if="(props.lesions || []).length > 0"
          class="complex-focus-pill sensor-pill" 
          :class="{ active: activeFocusKey === 'sensor' }"
          @click="focusOnComplex('sensor')"
          title="Enfocar Sensores de Daño anclados al ADN (MRN–ATM / RPA–ATR / OGG1)"
        >
          <span class="cf-dot" style="background:#ef4444"></span>
          <span>Sensores en Lesión ({{ (props.lesions || []).length }})</span>
        </button>
      </div>

      <!-- HUD Superior Izquierdo: Leyenda en la esquina superior izquierda con flechita para desplegar -->
      <div class="hud-corner-dropdown corner-left" :class="{ open: showLegend }">
        <button 
          class="hud-corner-pill-btn" 
          @click="showLegend = !showLegend" 
          type="button"
          title="Desplegar Leyenda Atómica"
        >
          <span class="pill-title">Leyenda</span>
          <Icon :name="showLegend ? 'chevron_up' : 'chevron_down'" size="15" class="pill-arrow" />
        </button>

        <div class="hud-dropdown-panel" v-show="showLegend">
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
            <span class="spectral-pill"><span class="swatch" style="background:#f43f5e"></span>H1 (Broche exterior)</span>
            <span class="spectral-pill hbond"><span class="swatch pin" style="background:#8fb4e0"></span>Puente H</span>
          </div>
        </div>
      </div>

      <!-- HUD Superior Derecho: Nucleótido Dúplex en la esquina pegado arriba -->
      <div class="hud-corner-dropdown corner-right" v-if="selectedBaseData">
        <div class="hud-corner-pill-card">
          <div class="pair-display-row compact-corner">
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

          <div class="corner-pair-label">
            <span class="c-pos font-mono">Posición {{ effectiveSelectedPos }}</span>
            <span class="c-type font-mono">{{ packagingMode === 'linear' ? 'B-DNA' : '1.65v Histonas' }}</span>
          </div>
        </div>
      </div>

      <!-- DOCK COMPACTO DE DOBLE CADENA: ENLACES H, ESQUELETO AZÚCAR-FOSFATO Y POLARIDAD 5' / 3' -->
      <div class="bottom-nucleotide-dock" v-if="cleanFullSequence">
        <!-- Extremo Izquierdo: Polaridad 5' (P) / 3' (OH) -->
        <div class="dock-polarity-col left">
          <span class="dock-polarity-tag p5" title="Extremo 5' Fosfato libre (PO₄³⁻)">5' (P)</span>
          <div class="dock-polarity-stem"></div>
          <span class="dock-polarity-tag p3" title="Extremo 3' Hidroxilo libre (-OH)">3' (OH)</span>
        </div>

        <!-- Pista Horizontal de Desplazamiento Independiente -->
        <div class="nucleotide-scroll-track" ref="nucleotideScrollRef">
          <div 
            v-for="pair in duplexBasePairs" 
            :key="pair.idx"
            :data-idx="pair.idx"
            :class="['dock-base-column', pair.b1.toLowerCase(), { active: effectiveSelectedPos === pair.idx, damaged: isBaseDamaged(pair.idx) }]"
            @click="selectPairFromLadder(pair.idx)"
            :title="`Par ${pair.idx}: ${pair.b1}=${pair.b2} (${pair.bonds} enlaces H)${isBaseDamaged(pair.idx) ? ' [LESIÓN ACTIVA]' : ''}`"
          >
            <!-- Coordenada del par -->
            <span class="dock-pos-idx font-mono">{{ pair.idx }}</span>

            <!-- Esqueleto Superior Azúcar-Fosfato (5'→3') -->
            <div class="dock-bb-monomer top" title="Monómero 5': Fosfato (P) + Desoxirribosa (D)">
              <span class="dock-bb-dot phosphate" title="Fosfato (PO₄³⁻)">P</span>
              <span class="dock-bb-hyphen">—</span>
              <span class="dock-bb-dot sugar" title="2'-Desoxirribosa">D</span>
              <div class="dock-bb-stem-down"></div>
            </div>

            <!-- Base Nitrogenada Sentido 5'→3' -->
            <div class="dock-base-capsule primary" :title="`Base Hebra Sentido: ${pair.b1}`">
              <span class="dock-letter font-mono">{{ pair.b1 }}</span>
            </div>

            <!-- Enlaces de Hidrógeno Watson-Crick (2 líneas para A=T, 3 líneas para C≡G) -->
            <div class="dock-hydrogen-bonds" :title="`${pair.bonds} puentes de hidrógeno (${pair.b1 === 'A' || pair.b1 === 'T' ? 'A=T' : 'C≡G'})`">
              <span class="dock-h-line" v-for="n in pair.bonds" :key="n"></span>
            </div>

            <!-- Base Nitrogenada Antisentido 3'→5' -->
            <div class="dock-base-capsule comp" :title="`Base Complementaria: ${pair.b2}`">
              <span class="dock-letter font-mono">{{ pair.b2 }}</span>
            </div>

            <!-- Esqueleto Inferior Azúcar-Fosfato Antiparalelo (3'→5') -->
            <div class="dock-bb-monomer bottom" title="Monómero 3': Desoxirribosa (D) + Fosfato (P)">
              <div class="dock-bb-stem-up"></div>
              <span class="dock-bb-dot sugar" title="2'-Desoxirribosa">D</span>
              <span class="dock-bb-hyphen">—</span>
              <span class="dock-bb-dot phosphate" title="Fosfato (PO₄³⁻)">P</span>
            </div>

            <!-- Baliza de Lesión / Daño si existe -->
            <span class="dock-damage-beacon" v-if="isBaseDamaged(pair.idx)" title="Lesión activa en esta base"></span>
          </div>
        </div>

        <!-- Extremo Derecho: Polaridad 3' (OH) / 5' (P) -->
        <div class="dock-polarity-col right">
          <span class="dock-polarity-tag p3" title="Extremo 3' Hidroxilo libre (-OH)">3' (OH)</span>
          <div class="dock-polarity-stem"></div>
          <span class="dock-polarity-tag p5" title="Extremo 5' Fosfato libre (PO₄³⁻)">5' (P)</span>
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
  },
  cellState: {
    type: Object,
    default: null
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
const showLegend = ref(false);

let p53MeshGroup = null;
let mdm2Mesh = null;
let ubiquitinGroup = null;
let p53UnitsList = [];
let p53AnimId = null;
let swarmCenter = [0, 0, 0];

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
  if (agent === 'tobacco' || agent === 'benzopyrene') {
    return {
      damageKind: 'Humo de Tabaco (Aducto Voluminoso BPDE-dG en Guanina)',
      enzymeName: 'NER · Complejo XPC/TFIIH + Endonucleasas ERCC1-XPF / XPG'
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

  // Desacoplar MDM2 morado y ubiquitinas blancas hacia la zona nuclear lejana
  p53UnitsList.forEach(u => {
    if (u.mdm2Group && u.distantAnchor) {
      // Impulso inicial hacia zona lejana lejos del ADN y p53
      u.mdm2Group.position.y += 4.0;
    }
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

    // El enjambre de p53 se mueve JUNTO (no en fila), centrando el grupo en el par actual leadBp
    if (leadBp >= 0 && leadBp < totalPairs) {
      const pair = lastGeneratedPairs[leadBp];
      if (pair && pair.centerPos) {
        swarmCenter = [pair.centerPos[0], pair.centerPos[1] + 2.0, pair.centerPos[2]];
      }
    } else if (leadBp < 0) {
      const firstPair = lastGeneratedPairs[0];
      if (firstPair) {
        swarmCenter = [firstPair.centerPos[0] + (leadBp * 2.5), firstPair.centerPos[1] + 3.0, firstPair.centerPos[2]];
      }
    } else {
      const lastPair = lastGeneratedPairs[totalPairs - 1];
      if (lastPair) {
        swarmCenter = [lastPair.centerPos[0] + 5.0, lastPair.centerPos[1] + 3.0, lastPair.centerPos[2]];
      }
    }

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
      // Avanzar al siguiente segmento (como van juntos, patrullan dinámicamente)
      leadBp++;
      if (leadBp < totalPairs + 2) {
        p53AnimId = setTimeout(stepPatrol, 85);
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
            if (u.mdm2Group) {
              u.mdm2Group.position.set(u.floatingAnchor[0], u.floatingAnchor[1] + 2.2, u.floatingAnchor[2]);
            }
          }
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
            if (u.mdm2Group) {
              u.mdm2Group.position.set(u.floatingAnchor[0], u.floatingAnchor[1] + 2.2, u.floatingAnchor[2]);
            }
          }
        });
        emit('p53Repaired');
      }, 1600);
    }
  }

  stepPatrol();
}

const cleanFullSequence = computed(() => {
  return props.sequence.toUpperCase().replace(/[^ATCG]/g, '') || 'GATTACAGGCTATCCGATACG';
});

const internalSelectedPos = ref(props.selectedPosition ?? 0);
const selected3DPairIdx = ref(null);
const packagingMode = ref('chromatin_alberts'); // 'chromatin_alberts' | 'linear'

// Guardamos los pares generados para que zoomIn y el selector apunten a la coordenada 3D exacta
let lastGeneratedPairs = [];
let lastGeneratedAtoms = [];
let lastGeneratedBonds = [];
let mallaAtomosRef = null;
let mallaEnlacesRef = null;
let damaged3DPairIndices = [];

function cyclePackagingMode() {
  packagingMode.value = (packagingMode.value === 'chromatin_alberts') ? 'linear' : 'chromatin_alberts';
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
const cardRoot = ref(null);
function onFullscreenChange() {
  const inFs = !!document.fullscreenElement;
  if (!inFs && isExpanded.value) {
    isExpanded.value = false;
    nextTick(() => onWindowResize());
  }
}
if (typeof document !== 'undefined') document.addEventListener('fullscreenchange', onFullscreenChange);
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

const nucleotideScrollRef = ref(null);

const duplexBasePairs = computed(() => {
  const seq = cleanFullSequence.value;
  if (!seq) return [];
  const list = [];
  for (let i = 0; i < seq.length; i++) {
    const b1 = seq[i];
    const b2 = COMPLEMENT_MAP[b1] || 'T';
    const bonds = (b1 === 'A' || b1 === 'T') ? 2 : 3;
    list.push({ idx: i, b1, b2, bonds });
  }
  return list;
});

function isBaseDamaged(idx) {
  if (props.lesions && props.lesions.length) {
    return props.lesions.some(l => (typeof l === 'number' ? l === idx : l.position === idx));
  }
  return false;
}

function selectPairFromLadder(idx) {
  internalSelectedPos.value = idx;
  emit('selectBase', idx);
  emit('update:selectedPosition', idx);
  buildDNAHelix(false);
  scrollSelectedIntoView(idx);
}

function scrollSelectedIntoView(idx) {
  if (!nucleotideScrollRef.value) return;
  const col = nucleotideScrollRef.value.querySelector(`[data-idx="${idx}"]`);
  if (col) {
    col.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
  }
}

watch(effectiveSelectedPos, (newPos) => {
  if (newPos !== null && newPos !== undefined) {
    nextTick(() => scrollSelectedIntoView(newPos));
  }
});


// ===== Lesiones Químicas del ADN (Alberts Cap. 5) =====
const AGENT_LESION = {
  uv_radiation: 'dimer',
  oxidative_ros: 'oxoG',
  deamination: 'uracil',
  tobacco: 'adduct',
  benzopyrene: 'adduct',
  crispr: 'dsb',
  ionizing: 'dsb'
};

const LESION_STYLE = {
  dsb:    { color: 0xff2d2d, label: 'Rotura Doble Cadena (DSB) · MRN-ATM' },
  oxoG:   { color: 0xf97316, label: '8-oxoG · BER (OGG1)' },
  dimer:  { color: 0xa855f7, label: 'Dímero Pirimidina · NER (TFIIH/XPC)' },
  adduct: { color: 0xeab308, label: 'Aducto BPDE-dG · NER (XPF/XPG)' },
  uracil: { color: 0x84cc16, label: 'Uracilo · BER (UNG)' }
};

function normalizeLesionType(raw, agent) {
  const r = String(raw || '').toLowerCase();
  if (LESION_STYLE[raw]) return raw;
  if (r.includes('uv') || r.includes('dimer') || r.includes('dímero')) return 'dimer';
  if (r.includes('oxo') || r.includes('ros') || r.includes('oxid')) return 'oxoG';
  if (r.includes('deamin') || r.includes('uracil')) return 'uracil';
  if (r.includes('tobacco') || r.includes('adduct') || r.includes('bpde')) return 'adduct';
  if (r.includes('dsb') || r.includes('crispr') || r.includes('break')) return 'dsb';
  return AGENT_LESION[agent] || 'dsb';
}

function baseCentroid(atoms, pair, strand) {
  const c = new THREE.Vector3();
  let n = 0;
  for (let k = pair.startAtomIdx; k <= pair.endAtomIdx; k++) {
    const a = atoms[k];
    if (a[6] === strand && 'ATGC'.includes(a[4])) {
      c.x += a[0]; c.y += a[1]; c.z += a[2]; n++;
    }
  }
  return n ? c.multiplyScalar(1 / n) : null;
}

function addStick(group, p1, p2, r, mat) {
  const d = new THREE.Vector3().subVectors(p2, p1);
  const m = new THREE.Mesh(new THREE.CylinderGeometry(r, r, d.length(), 10), mat);
  m.position.copy(p1).addScaledVector(d, 0.5);
  m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), d.normalize());
  group.add(m);
}

function buildLesionDecorations(atoms, bonds, pairs, lesionTypeMap) {
  if (!lesionTypeMap.size) return;
  const g = new THREE.Group();
  g.name = 'lesion_decorations';
  const glow = (hex, ei = 0.8) => new THREE.MeshStandardMaterial({ color: hex, emissive: hex, emissiveIntensity: ei, roughness: 0.3 });

  lesionTypeMap.forEach((type, idx) => {
    const pair = pairs[idx];
    if (!pair) return;
    const center = new THREE.Vector3(...pair.centerPos);
    const b1 = baseCentroid(atoms, pair, 1);
    if (!b1) return;
    const out = new THREE.Vector3().subVectors(b1, center).normalize();

    if (type === 'oxoG') {
      const o = b1.clone().addScaledVector(out, 2.4);
      const om = new THREE.Mesh(new THREE.SphereGeometry(0.75, 18, 14), glow(0xff3b30, 0.9));
      om.position.copy(o); g.add(om);
      addStick(g, b1.clone().addScaledVector(out, 1.2), o, 0.18, glow(0xf97316, 0.5));
    } else if (type === 'dimer') {
      const nb = pairs[idx + 1] || pairs[idx - 1];
      const b2 = nb && baseCentroid(atoms, nb, 1);
      if (b2) {
        const side = new THREE.Vector3().crossVectors(out, new THREE.Vector3().subVectors(b2, b1)).normalize().multiplyScalar(0.7);
        const mat = glow(0xa855f7, 0.9);
        addStick(g, b1.clone().add(side), b2.clone().add(side), 0.2, mat);
        addStick(g, b1.clone().sub(side), b2.clone().sub(side), 0.2, mat);
      }
    } else if (type === 'adduct') {
      const mat = glow(0xeab308, 0.55);
      const anchor = b1.clone().addScaledVector(out, 1.6);
      const tip = b1.clone().addScaledVector(out, 3.2);
      addStick(g, anchor, tip, 0.16, mat);
      const ringGeo = new THREE.TorusGeometry(0.85, 0.16, 6, 6);
      const lateral = new THREE.Vector3(...pair.tangent).normalize();
      const offs = [[0, 0], [1.47, 0], [0.735, 1.27], [2.2, 1.27]];
      offs.forEach(([u, v]) => {
        const r = new THREE.Mesh(ringGeo, mat);
        r.position.copy(tip).addScaledVector(out, 0.85 + v).addScaledVector(lateral, u - 1.1);
        r.lookAt(r.position.clone().add(new THREE.Vector3().crossVectors(out, lateral)));
        g.add(r);
      });
    } else if (type === 'uracil') {
      const m = new THREE.Mesh(new THREE.SphereGeometry(0.6, 14, 10), new THREE.MeshStandardMaterial({ color: 0x84cc16, wireframe: true }));
      m.position.copy(b1).addScaledVector(out, 2.0); g.add(m);
    } else if (type === 'dsb') {
      bonds.forEach(e => {
        const a1 = atoms[e[0]], a2 = atoms[e[1]];
        if (e[3] !== idx || !a1 || !a2 || a1[7] === a2[7] || e[2] === 'h') return;
        [a1, a2].forEach(a => {
          const m = new THREE.Mesh(new THREE.SphereGeometry(0.8, 16, 12), glow(0xff2d2d, 1.1));
          m.position.set(a[0], a[1], a[2]); m.userData.pulse = true; g.add(m);
        });
      });
    }
  });
  mainHelixGroup.add(g);
}

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
  const maxSeqLen = cleanFullSequence.value.length || 1;

  // Determinar el par 3D activo para el anillo azul y el resaltado
  let active3DIndex = selected3DPairIdx.value;
  if (active3DIndex === null || active3DIndex < 0 || active3DIndex >= pairs.length || 
      (pairs[active3DIndex]?.originalIndex !== selPos && (active3DIndex % maxSeqLen) !== selPos)) {
    active3DIndex = pairs.findIndex(p => p.originalIndex === selPos);
    if (active3DIndex === -1) active3DIndex = Math.min(selPos, Math.max(0, pairs.length - 1));
    selected3DPairIdx.value = active3DIndex;
  }

  const dummy = new THREE.Object3D();
  const color = new THREE.Color();

  // Conjunto de posiciones con daño (lesiones ambientales o mutaciones)
  const damagedPositions = new Set(
    (props.lesions || []).map(l => (typeof l === 'object' && l.position !== undefined) ? Number(l.position) : Number(l))
  );

  const lesionTypeMap = new Map();
  (props.lesions || []).forEach(l => {
    const pos = (typeof l === 'object' && l.position !== undefined) ? Number(l.position) : Number(l);
    const t = normalizeLesionType(typeof l === 'object' ? l.type : null, props.activeAgent);
    lesionTypeMap.set(pos, t);
  });
  const lesionOf = (idx) => lesionTypeMap.get(idx);

  // 1. ÁTOMOS DE LA SECUENCIA REAL (Resalta suavemente el par 3D exacto seleccionado)
  const geoEsfera = new THREE.SphereGeometry(1, 20, 16);
  const matEsfera = new THREE.MeshStandardMaterial({ roughness: 0.3, metalness: 0.08 });
  const mallaAtomos = new THREE.InstancedMesh(geoEsfera, matEsfera, atoms.length);
  const atomPairMap = [];

  atoms.forEach((a, i) => {
    dummy.position.set(a[0], a[1], a[2]);
    const isSelectedPair = (a[7] === active3DIndex);
    const isDamagedPair = damagedPositions.has(a[7]);
    const r = (ATOMIC_RADII[a[3]] || 0.45) * (isDamagedPair ? 1.55 : (isSelectedPair ? 1.4 : 1.15));
    dummy.scale.setScalar(r);
    dummy.rotation.set(0, 0, 0);
    dummy.updateMatrix();
    mallaAtomos.setMatrixAt(i, dummy.matrix);

    const lt = lesionOf(a[7]);
    if (isDamagedPair) {
      color.setHex(LESION_STYLE[lt]?.color ?? 0xff1a1a);
    } else if (isSelectedPair) {
      color.setHex(0x38bdf8).lerp(new THREE.Color(0xffffff), 0.55);
    } else {
      color.setHex(ATOMIC_PALETTE[a[4]] ?? 0x94a3b8);
    }
    mallaAtomos.setColorAt(i, color);
    // Guardar a[7] (el índice 3D exacto del par) para que el clic identifique ese par preciso
    atomPairMap.push(a[7]);
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
  if (active3DIndex >= 0 && active3DIndex < pairs.length) {
    const activePair = pairs[active3DIndex];
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

  // 6. IDENTIFICAR PARES 3D LESIONADOS (Sin círculos ni balizas externas: solo la cadena en rojo refleja el daño)
  damaged3DPairIndices = [];
  pairs.forEach((p, pIdx) => {
    if (damagedPositions.has(pIdx)) {
      damaged3DPairIndices.push(pIdx);
    }
  });

  // 7. COMPLEJOS MACROMOLECULARES p53 (TETRÁMERO D2) / MDM2 (RING E3) / UBIQUITINA (Alberts Cap. 17)
  p53MeshGroup = new THREE.Group();
  p53MeshGroup.name = 'p53_complex_group';

  const numLesions = damagedPositions.size;
  const p53Count = numLesions > 0 ? Math.min(6, Math.max(2, numLesions * 2)) : 2;
  p53State.value.p53UnitsCount = p53Count;

  const matP53Amber = new THREE.MeshStandardMaterial({ 
    color: 0xf59e0b, 
    roughness: 0.25, 
    metalness: 0.22,
    emissive: 0xd97706,
    emissiveIntensity: 0.48 
  });
  const matP53CoreLink = new THREE.MeshStandardMaterial({
    color: 0xfbbf24,
    roughness: 0.3,
    metalness: 0.2,
    emissive: 0xb45309,
    emissiveIntensity: 0.35
  });

  const matMdm2Purple = new THREE.MeshStandardMaterial({ 
    color: 0x8b5cf6, 
    roughness: 0.32, 
    metalness: 0.18,
    emissive: 0x6d28d9,
    emissiveIntensity: 0.42
  });

  const matUbiWhite = new THREE.MeshStandardMaterial({ 
    color: 0xffffff, 
    roughness: 0.18, 
    metalness: 0.1, 
    emissive: 0xe2e8f0, 
    emissiveIntensity: 0.55 
  });

  const geoP53Sub = new THREE.SphereGeometry(1.15, 18, 16);
  const geoP53TetAxis = new THREE.CylinderGeometry(0.32, 0.32, 2.4, 12);
  const geoMdm2 = new THREE.SphereGeometry(1.30, 18, 16);
  const geoMdm2Ring = new THREE.TorusGeometry(1.05, 0.24, 10, 28);
  const geoUbi = new THREE.SphereGeometry(0.62, 16, 12);

  // Caja delimitadora real de todos los átomos del ADN + histonas para ubicar complejos sin colisión
  let minY = Infinity, maxY = -Infinity;
  let minX = Infinity, maxX = -Infinity;
  let minZ = Infinity, maxZ = -Infinity;
  atoms.forEach(a => {
    if (a[0] < minX) minX = a[0];
    if (a[0] > maxX) maxX = a[0];
    if (a[1] < minY) minY = a[1];
    if (a[1] > maxY) maxY = a[1];
    if (a[2] < minZ) minZ = a[2];
    if (a[2] > maxZ) maxZ = a[2];
  });
  histoneSpheres.forEach(hs => {
    const r = hs[3] || 6;
    if (hs[0] - r < minX) minX = hs[0] - r;
    if (hs[0] + r > maxX) maxX = hs[0] + r;
    if (hs[1] - r < minY) minY = hs[1] - r;
    if (hs[1] + r > maxY) maxY = hs[1] + r;
    if (hs[2] - r < minZ) minZ = hs[2] - r;
    if (hs[2] + r > maxZ) maxZ = hs[2] + r;
  });

  if (!isFinite(minX)) { minX = -20; maxX = 20; minY = -20; maxY = 20; minZ = -20; maxZ = 20; }
  const dnaCenterX = (minX + maxX) / 2;
  const dnaCenterY = (minY + maxY) / 2;
  const dnaCenterZ = (minZ + maxZ) / 2;
  const isLin = packagingMode.value === 'linear';

  lastDnaBounds = { minX, maxX, minY, maxY, minZ, maxZ, cx: dnaCenterX, cy: dnaCenterY, cz: dnaCenterZ };

  // Reservorio nuclear de p53 situado en el dominio izquierdo exterior del ADN (libre de solapamiento)
  const reservoirCenter = isLin
    ? [minX - 28.0, dnaCenterY, dnaCenterZ - 6.0]
    : [minX - 38.0, dnaCenterY - 2.0, dnaCenterZ + 4.0];

  p53UnitsList = [];

  for (let u = 0; u < p53Count; u++) {
    // 1. Tetrámero canónico de p53 (4 subunidades core en simetría D2 + dominio central de tetramerización)
    const unitGroup = new THREE.Group();
    unitGroup.name = 'p53_unit_' + u;
    unitGroup.scale.setScalar(1.45);

    const tetCore = new THREE.Mesh(geoP53TetAxis, matP53CoreLink);
    tetCore.rotation.z = Math.PI / 4;
    unitGroup.add(tetCore);

    const tetOffsets = [
      [ 1.15,  1.10,  0.45],
      [-1.15,  1.10, -0.45],
      [-1.15, -1.10,  0.45],
      [ 1.15, -1.10, -0.45]
    ];
    tetOffsets.forEach(([ox, oy, oz]) => {
      const sub = new THREE.Mesh(geoP53Sub, matP53Amber);
      sub.position.set(ox, oy, oz);
      unitGroup.add(sub);
    });

    // Halo estructural del dominio de unión al ADN (DBD)
    const dbdHalo = new THREE.Mesh(
      new THREE.TorusGeometry(2.0, 0.10, 10, 32),
      new THREE.MeshStandardMaterial({ color: 0xfbbf24, emissive: 0xf59e0b, emissiveIntensity: 0.65, transparent: true, opacity: 0.75 })
    );
    dbdHalo.rotation.x = Math.PI / 3;
    unitGroup.add(dbdHalo);

    // Fosfatos reguladores sobre N-terminal de p53: P-Ser15 (ATM/ATR), P-Ser20 (CHK1/2) y P-Ser46 (Apoptosis)
    {
      const matPhos = new THREE.MeshStandardMaterial({ color: 0xfacc15, emissive: 0xfacc15, emissiveIntensity: 0.95, roughness: 0.25 });
      const matSer46 = new THREE.MeshStandardMaterial({ color: 0xf97316, emissive: 0xf97316, emissiveIntensity: 0.95, roughness: 0.25 });
      const ph15 = new THREE.Mesh(new THREE.SphereGeometry(0.50, 14, 12), matPhos);
      ph15.position.set(1.6, 2.2, 0.55); ph15.name = 'pSer15';
      unitGroup.add(ph15);

      const ph20 = new THREE.Mesh(new THREE.SphereGeometry(0.50, 14, 12), matPhos);
      ph20.position.set(-1.6, 2.2, -0.55); ph20.name = 'pSer20';
      unitGroup.add(ph20);

      const ph46 = new THREE.Mesh(new THREE.SphereGeometry(0.48, 14, 12), matSer46);
      ph46.position.set(0, -2.3, 0.85); ph46.name = 'pSer46';
      unitGroup.add(ph46);
    }

    // 2. Complejo E3 Ubiquitina-Ligasa MDM2 (Dominio globular + Anillo RING + Cadena de Poli-Ubiquitina)
    const mdm2Group = new THREE.Group();
    mdm2Group.name = 'mdm2_complex_' + u;
    mdm2Group.scale.setScalar(1.35);

    const mdm2M = new THREE.Mesh(geoMdm2, matMdm2Purple);
    mdm2M.name = 'mdm2_sub_' + u;
    mdm2Group.add(mdm2M);

    const ringM = new THREE.Mesh(geoMdm2Ring, matMdm2Purple);
    ringM.position.set(0.9, 0.3, 0);
    ringM.rotation.y = Math.PI / 3;
    mdm2Group.add(ringM);

    const ubiG = new THREE.Group();
    ubiG.name = 'ubi_group_' + u;
    [[1.45, 1.15, 0.45], [0.55, 1.65, -0.35], [-0.45, 1.85, 0.25]].forEach(([ux, uy, uz]) => {
      const ub = new THREE.Mesh(geoUbi, matUbiWhite);
      ub.position.set(ux, uy, uz);
      ubiG.add(ub);
    });
    mdm2Group.add(ubiG);

    const phi = u * 2.39996;
    const cosTheta = 1 - (2 * (u + 0.5) / Math.max(1, p53Count));
    const sinTheta = Math.sqrt(Math.max(0, 1 - cosTheta * cosTheta));
    const rSpread = 6.0 + (u % 2) * 2.5;

    const anchor = [
      reservoirCenter[0] + sinTheta * Math.cos(phi) * rSpread,
      reservoirCenter[1] + cosTheta * rSpread * 0.9,
      reservoirCenter[2] + sinTheta * Math.sin(phi) * rSpread
    ];
    unitGroup.position.set(anchor[0], anchor[1], anchor[2]);
    mdm2Group.position.set(anchor[0], anchor[1] + 4.8, anchor[2]);

    // Posición desacoplada de MDM2 cuando p53 se fosforila en Ser15/Ser20
    const distantAnchor = isLin
      ? [minX - 30.0 - (u * 6.0), dnaCenterY + 14.0, maxZ + 16.0]
      : [minX - 28.0 + (u * 8.5), maxY + 22.0 + (u % 2) * 4.5, dnaCenterZ + 4.0];

    p53MeshGroup.add(unitGroup);
    p53MeshGroup.add(mdm2Group);

    p53UnitsList.push({
      group: unitGroup,
      mdm2Group: mdm2Group,
      floatingAnchor: anchor,
      distantAnchor: distantAnchor,
      currentBp: 0
    });
  }

  // 5b. Representación química de lesiones
  buildLesionDecorations(atoms, bonds, pairs, lesionTypeMap);

  mainHelixGroup.add(p53MeshGroup);

  lastLesionTypeMap = lesionTypeMap;
  p53Reservoir = reservoirCenter;
  buildSignaling();

  if (reframe) {
    const allPts = atoms.map(a => [a[0], a[1], a[2]]);
    p53UnitsList.forEach(u => {
      if (u.floatingAnchor) allPts.push(u.floatingAnchor);
    });
    Object.values(complexFocusCoords).forEach(pt => {
      if (Array.isArray(pt)) allPts.push(pt);
    });
    encuadrar(allPts);
  }
}


// ============================================================================
// RED DE SEÑALIZACIÓN Y CONTROL DEL CICLO G1/S (ALBERTS CAP. 5, 12 Y 17)
// ============================================================================
let signalingGroup = null;
let lastLesionTypeMap = new Map();
let p53Reservoir = [0, 0, 0];
let lastDnaBounds = { minX: -20, maxX: 20, minY: -20, maxY: 20, minZ: -20, maxZ: 20, cx: 0, cy: 0, cz: 0 };
let complexFocusCoords = {};
const activeFocusKey = ref('all');
let animClock = 0;

function addTether(parentGroup, fromVec, toVec, hex = 0x38bdf8, opacity = 0.55) {
  const pts = [fromVec.clone(), toVec.clone()];
  const geo = new THREE.BufferGeometry().setFromPoints(pts);
  const mat = new THREE.LineBasicMaterial({
    color: hex,
    transparent: true,
    opacity,
    depthTest: false
  });
  const line = new THREE.Line(geo, mat);
  line.renderOrder = 9990;
  parentGroup.add(line);
  return line;
}

function makeLabel(text, hex, scale = 1.0, subText = '') {
  const c = document.createElement('canvas');
  const ctx = c.getContext('2d');
  const titleFont = '700 28px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
  const subFont = '500 18px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';

  ctx.font = titleFont;
  const titleW = Math.ceil(ctx.measureText(text).width);
  let subW = 0;
  if (subText) {
    ctx.font = subFont;
    subW = Math.ceil(ctx.measureText(subText).width);
  }

  const w = Math.max(titleW, subW) + 84;
  const h = subText ? 82 : 56;
  c.width = w;
  c.height = h;

  const hexCol = '#' + hex.toString(16).padStart(6, '0');

  // Pastilla compacta estilizada de alto contraste
  ctx.fillStyle = 'rgba(5, 11, 26, 0.92)';
  ctx.beginPath();
  ctx.roundRect(3, 3, w - 6, h - 6, 18);
  ctx.fill();
  ctx.lineWidth = 2.4;
  ctx.strokeStyle = hexCol;
  ctx.stroke();

  // Indicador cromático del complejo
  ctx.fillStyle = hexCol;
  ctx.beginPath();
  ctx.arc(28, subText ? 28 : 28, 8, 0, Math.PI * 2);
  ctx.fill();

  // Título principal
  ctx.font = titleFont;
  ctx.fillStyle = '#f8fafc';
  ctx.textBaseline = 'middle';
  ctx.fillText(text, 48, subText ? 28 : 28);

  // Subtítulo bioquímico / estado
  if (subText) {
    ctx.font = subFont;
    ctx.fillStyle = '#94a3b8';
    ctx.fillText(subText, 48, 58);
  }

  const texture = new THREE.CanvasTexture(c);
  texture.colorSpace = THREE.SRGBColorSpace;
  const mat = new THREE.SpriteMaterial({ 
    map: texture, 
    depthTest: false, 
    transparent: true, 
    fog: false 
  });
  const sp = new THREE.Sprite(mat);
  const spriteH = (subText ? 3.0 : 2.1) * scale;
  sp.scale.set(spriteH * (w / h), spriteH, 1);
  sp.renderOrder = 9999;
  sp.userData.isLabel = true;
  return sp;
}

function clamp01(v) { return Math.max(0, Math.min(1, v)); }

function getKineticState() {
  const cs = props.cellState;
  if (cs && Object.keys(cs).length && (cs.p53 !== undefined || cs.ATM !== undefined)) {
    return {
      ATM: cs.ATM || 0,
      ATR: cs.ATR || 0,
      CHK2: cs.CHK2 || cs.ATM || 0,
      CHK1: cs.CHK1 || cs.ATR || 0,
      pSer15: cs.pSer15 || 0,
      pSer20: cs.pSer20 || 0,
      p53: cs.p53 || 0.05,
      p21: cs.p21 || 0.02,
      OGG1: cs.OGG1 || 0.35,
      ciclinaD: cs.ciclinaD || 0.65,
      ciclinaE: cs.ciclinaE || 0.50,
      RbP: cs.RbP || 0.50
    };
  }

  const types = [...lastLesionTypeMap.values()];
  const nDSB = types.filter(t => t === 'dsb').length;
  const nBase = types.filter(t => t !== 'dsb').length;

  const ATM = nDSB > 0 ? Math.min(1.0, 0.50 + 0.25 * nDSB) : 0.03;
  const ATR = nBase > 0 ? Math.min(1.0, 0.35 + 0.20 * nBase) : 0.02;
  const CHK2 = Math.min(1.0, ATM * 0.95);
  const CHK1 = Math.min(1.0, ATR * 0.92);

  const pSer15 = Math.min(1.0, Math.max(ATM, ATR) * 0.98);
  const pSer20 = Math.min(1.0, Math.max(CHK1, CHK2) * 0.90);
  const shield = Math.min(1.0, 0.6 * pSer15 + 0.4 * pSer20);

  const p53 = types.length > 0 ? Math.min(1.0, 0.05 + 0.88 * shield) : 0.05;
  const p21 = types.length > 0 ? Math.min(1.0, Math.pow(p53, 1.6) * 1.25) : 0.02;
  const OGG1 = Math.min(1.0, 0.30 + 0.65 * p53);

  const inh = p21 / (p21 + 0.25);
  const ciclinaD = 0.65;
  const ciclinaE = Math.max(0.04, 0.70 * (1 - inh));
  const actTotal = (ciclinaD * 0.4 + ciclinaE * 0.6) * (1 - inh);
  const RbP = clamp01(actTotal * 1.4);

  return { ATM, ATR, CHK2, CHK1, pSer15, pSer20, p53, p21, OGG1, ciclinaD, ciclinaE, RbP };
}

function disposeHierarchy(obj) {
  obj.traverse(node => {
    if (node.geometry) node.geometry.dispose();
    if (node.material) {
      if (Array.isArray(node.material)) node.material.forEach(m => { if (m.map) m.map.dispose(); m.dispose(); });
      else { if (node.material.map) node.material.map.dispose(); node.material.dispose(); }
    }
  });
}

function buildSignaling() {
  if (!mainHelixGroup) return;
  if (signalingGroup) {
    mainHelixGroup.remove(signalingGroup);
    disposeHierarchy(signalingGroup);
    signalingGroup = null;
  }

  const pairs = lastGeneratedPairs;
  const atoms = lastGeneratedAtoms;
  if (!pairs || !pairs.length) return;

  const st = getKineticState();
  const g = new THREE.Group();
  g.name = 'signaling_master_group';

  const isLin = packagingMode.value === 'linear';
  const UP = isLin ? new THREE.Vector3(0, 0, 1) : new THREE.Vector3(0, 1, 0);
  const pct = (v) => Math.round(clamp01(v || 0) * 100) + '%';
  const createMat = (hex, emissiveInt = 0.4, opacity = 1.0) => new THREE.MeshStandardMaterial({
    color: hex,
    emissive: hex,
    emissiveIntensity: emissiveInt,
    roughness: 0.32,
    metalness: 0.16,
    transparent: opacity < 1.0,
    opacity: opacity
  });
  const createSph = (r, hex, ei = 0.4, op = 1.0) => new THREE.Mesh(new THREE.SphereGeometry(r, 18, 14), createMat(hex, ei, op));

  const { minX, maxX, minY, maxY, minZ, maxZ, cx, cy, cz } = lastDnaBounds;
  const dnaCenter = new THREE.Vector3(cx, cy, cz);

  // Vector radial seguro hacia el exterior del volumen del ADN/histonas
  const safeOutwardDir = (pt) => {
    const v = new THREE.Vector3(pt.x - cx, isLin ? (pt.y - cy) : (pt.y - cy), isLin ? 0 : (pt.z - cz));
    if (v.lengthSq() < 0.01) return UP.clone();
    return v.normalize();
  };

  // --- 1. SENSORES FÍSICOS SOBRE EL ADN (MRN-ATM en DSB y RPA-ATR en Lesiones de Base) ---
  const sensorFluxNodes = [];
  const oxoGCoordinates = [];
  let dsbSensorRendered = false;
  let baseSensorRendered = false;
  let firstSensorFocusPos = null;

  lastLesionTypeMap.forEach((type, pairIndex) => {
    const pair = pairs[pairIndex];
    if (!pair) return;
    const center = new THREE.Vector3(...pair.centerPos);
    const b1 = baseCentroid(atoms, pair, 1) || center.clone().add(UP);
    const radialOut = safeOutwardDir(b1);
    const tangent = new THREE.Vector3(...(pair.tangent || [0, 0, 1])).normalize();

    if (type === 'dsb') {
      // Complejo MRN (Mre11₂·Rad50₂·Nbs1) + Quinasa ATM proyectado hacia el exterior del corte DSB
      const mrnGroup = new THREE.Group();
      mrnGroup.name = 'sensor_mrn_' + pairIndex;
      mrnGroup.scale.setScalar(1.35);
      const anchorPos = center.clone().addScaledVector(radialOut, 13.0);
      mrnGroup.position.copy(anchorPos);
      if (!firstSensorFocusPos) firstSensorFocusPos = anchorPos.toArray();

      // Conector al extremo roto del ADN
      addTether(g, center, anchorPos, 0xef4444, 0.75);

      // Dímero Mre11 (2 lóbulos nucleasa índigo)
      const mre11_A = createSph(1.25, 0x4f46e5, 0.55); mre11_A.position.set(-0.9, 0, 0);
      const mre11_B = createSph(1.25, 0x4338ca, 0.55); mre11_B.position.set(0.9, 0, 0);
      mrnGroup.add(mre11_A, mre11_B);

      // Brazos Coiled-Coil de Rad50 + Gancho de Zinc apical (Zn-hook)
      const rodGeo = new THREE.CylinderGeometry(0.24, 0.24, 6.8, 10);
      const rodMat = createMat(0x818cf8, 0.5);
      const rod1 = new THREE.Mesh(rodGeo, rodMat); rod1.position.set(-1.1, 3.4, 0.3); rod1.rotation.z = -0.16;
      const rod2 = new THREE.Mesh(rodGeo, rodMat); rod2.position.set(1.1, 3.4, -0.3); rod2.rotation.z = 0.16;
      const znHook = createSph(0.65, 0x22d3ee, 0.85); znHook.position.set(0, 6.9, 0);
      mrnGroup.add(rod1, rod2, znHook);

      // Subunidad adaptadora Nbs1
      const nbs1 = createSph(1.05, 0xa855f7, 0.6); nbs1.position.set(1.8, 1.4, 0.6);
      mrnGroup.add(nbs1);

      // Quinasa ATM bilobular activada (dominio FAT + dominio Quinasa + anillo P-Ser1981)
      const atmAct = clamp01(st.ATM);
      const atmLobe1 = createSph(1.55, 0xef4444, 0.35 + 0.75 * atmAct, 0.5 + 0.5 * atmAct);
      atmLobe1.position.set(3.2, 3.2, 0.8);
      const atmLobe2 = createSph(1.15, 0xdc2626, 0.35 + 0.75 * atmAct, 0.5 + 0.5 * atmAct);
      atmLobe2.position.set(4.5, 4.1, 0.8);
      const atmRing = new THREE.Mesh(new THREE.TorusGeometry(1.75, 0.16, 10, 28), createMat(0xfacc15, 0.85));
      atmRing.position.copy(atmLobe1.position);
      atmRing.rotation.x = Math.PI / 3;
      mrnGroup.add(atmLobe1, atmLobe2, atmRing);
      g.add(mrnGroup);

      if (!dsbSensorRendered) {
        const lblPos = anchorPos.clone().addScaledVector(UP, 10.5).addScaledVector(radialOut, 4.5);
        const lbl = makeLabel('Complejo MRN + Quinasa ATM', 0xef4444, 0.82, 'Sensor de Rotura DSB · Act: ' + pct(atmAct));
        lbl.position.copy(lblPos);
        g.add(lbl);
        addTether(g, anchorPos, lblPos, 0xef4444, 0.72);
        dsbSensorRendered = true;
      }

      sensorFluxNodes.push({
        worldPos: anchorPos.clone(),
        type: 'CHK2',
        level: st.CHK2
      });

    } else {
      // Trímero RPA (RPA70·RPA32·RPA14) recubriendo ssDNA + Complejo ATR-ATRIP
      const rpaGroup = new THREE.Group();
      rpaGroup.name = 'sensor_rpa_' + pairIndex;
      rpaGroup.scale.setScalar(1.35);
      const anchorPos = b1.clone().addScaledVector(radialOut, 11.0);
      rpaGroup.position.copy(anchorPos);
      if (!firstSensorFocusPos) firstSensorFocusPos = anchorPos.toArray();

      addTether(g, b1, anchorPos, 0x38bdf8, 0.75);

      // 3 subunidades OB-fold de RPA alineadas con la hebra
      const rpa70 = createSph(1.05, 0x94a3b8, 0.35); rpa70.position.copy(tangent.clone().multiplyScalar(-1.4));
      const rpa32 = createSph(0.90, 0x64748b, 0.35); rpa32.position.set(0, 0.2, 0);
      const rpa14 = createSph(0.75, 0x475569, 0.35); rpa14.position.copy(tangent.clone().multiplyScalar(1.3));
      rpaGroup.add(rpa70, rpa32, rpa14);

      // Adaptador ATRIP + Quinasa ATR bilobular
      const atrAct = clamp01(st.ATR);
      const atripAdapter = createSph(0.95, 0x38bdf8, 0.5);
      atripAdapter.position.set(0.8, 1.7, 0.4);
      const atrKinase = createSph(1.45, 0x0284c7, 0.35 + 0.75 * atrAct, 0.5 + 0.5 * atrAct);
      atrKinase.position.set(-0.4, 2.9, 0.8);
      const atrRing = new THREE.Mesh(new THREE.TorusGeometry(1.6, 0.15, 10, 26), createMat(0x38bdf8, 0.75));
      atrRing.position.copy(atrKinase.position);
      rpaGroup.add(atripAdapter, atrKinase, atrRing);
      g.add(rpaGroup);

      if (!baseSensorRendered) {
        const lblPos = anchorPos.clone().addScaledVector(UP, 8.5).addScaledVector(radialOut, 4.5);
        const lbl = makeLabel('Trímero RPA + ATR–ATRIP', 0x38bdf8, 0.82, 'Sensor ssDNA / Lesión · Act: ' + pct(atrAct));
        lbl.position.copy(lblPos);
        g.add(lbl);
        addTether(g, anchorPos, lblPos, 0x38bdf8, 0.72);
        baseSensorRendered = true;
      }

      sensorFluxNodes.push({
        worldPos: anchorPos.clone(),
        type: 'CHK1',
        level: st.CHK1
      });

      if (type === 'oxoG') oxoGCoordinates.push({ b1, radialOut });
    }
  });

  // --- 2. ESCISIÓN DE BASES (BER) POR GLICOSILASA OGG1 SOBRE 8-OXOGUANINA ---
  const ogg1Cap = Math.round(st.OGG1 * 4);
  oxoGCoordinates.forEach((ox, idx) => {
    const ogg1Pos = ox.b1.clone().addScaledVector(ox.radialOut, 6.0);
    if (idx < ogg1Cap) {
      const ogg1Group = new THREE.Group();
      ogg1Group.scale.setScalar(1.35);
      ogg1Group.position.copy(ogg1Pos);
      const clampArc = new THREE.Mesh(new THREE.TorusGeometry(1.15, 0.34, 12, 24, Math.PI * 1.45), createMat(0x10b981, 0.7));
      const catDomain = createSph(0.95, 0x059669, 0.6); catDomain.position.set(0.6, 0.5, 0);
      ogg1Group.add(clampArc, catDomain);
      g.add(ogg1Group);

      if (idx === 0) {
        const lblPos = ogg1Pos.clone().addScaledVector(UP, -5.5).addScaledVector(ox.radialOut, 5.0);
        const lbl = makeLabel('OGG1 Glicosilasa (Vía BER)', 0x10b981, 0.80, 'Escisión activa de 8-oxoG');
        lbl.position.copy(lblPos);
        g.add(lbl);
        addTether(g, ogg1Pos, lblPos, 0x10b981, 0.68);
      }
    } else {
      const lblPos = ogg1Pos.clone().addScaledVector(ox.radialOut, 5.0);
      const lbl = makeLabel('8-oxoG sin OGG1', 0xf97316, 0.76, 'Capacidad BER saturada');
      lbl.position.copy(lblPos);
      g.add(lbl);
    }
  });

  // --- 3. QUINASAS DIFUSIBLES CHK1 / CHK2 EN TRÁNSITO HACIA EL TETRÁMERO p53 ---
  const p53Target = new THREE.Vector3(...p53Reservoir);
  const labelsShown = {};
  sensorFluxNodes.forEach(node => {
    const hex = node.type === 'CHK1' ? 0x38bdf8 : 0xf472b6;
    // Línea guía tenue de la ruta de transducción hacia p53
    addTether(g, node.worldPos, p53Target, hex, 0.22);

    if (!labelsShown[node.type]) {
      labelsShown[node.type] = true;
      const midPoint = node.worldPos.clone().lerp(p53Target, 0.52).addScaledVector(UP, 3.5);
      const sub = node.type === 'CHK1' ? 'Activada por ATR · Fosforila Ser20' : 'Activada por ATM · Fosforila Ser20';
      const lbl = makeLabel(node.type + ' Quinasa Difusible (' + pct(node.level) + ')', hex, 0.76, sub);
      lbl.position.copy(midPoint);
      g.add(lbl);
    }
  });

  // --- 4. TETRÁMERO p53, CÓDIGO DE FOSFORILACIÓN (Ser15/Ser20/Ser46) Y LIGASA MDM2 ---
  const shieldFactor = Math.min(1.0, 0.6 * st.pSer15 + 0.4 * st.pSer20);
  const visibleP53Count = Math.max(1, Math.round(st.p53 * p53UnitsList.length / 0.6));
  const isSevere = props.isSevereDamage || lastLesionTypeMap.size >= 3;

  p53UnitsList.forEach((u, i) => {
    u.group.children.filter(c => c.userData.isLabel).forEach(c => { u.group.remove(c); disposeHierarchy(c); });
    u.mdm2Group.children.filter(c => c.userData.isLabel).forEach(c => { u.mdm2Group.remove(c); disposeHierarchy(c); });

    u.group.visible = i < visibleP53Count;

    const s15 = u.group.getObjectByName('pSer15');
    const s20 = u.group.getObjectByName('pSer20');
    const s46 = u.group.getObjectByName('pSer46');
    if (s15) s15.scale.setScalar(Math.max(0.001, st.pSer15));
    if (s20) s20.scale.setScalar(Math.max(0.001, st.pSer20));
    if (s46) s46.scale.setScalar(isSevere ? 1.15 : 0.001);

    const ubiGroup = u.mdm2Group.getObjectByName('ubi_group_' + i);
    if (ubiGroup) ubiGroup.scale.setScalar(Math.max(0.001, 1.0 - shieldFactor));

    if (i === 0) {
      const p53ModeTxt = isSevere
        ? 'Alto Sostenido + P-Ser46 → Activa BAX/PUMA'
        : (st.p53 > 0.25 ? 'Tetrámero Estabilizado → Induce p21 y BER' : 'Nivel Basal · Recambio rápido (~20 min)');
      const p53Lbl = makeLabel('Tetrámero p53 (' + pct(st.p53) + ')', 0xf59e0b, 0.78, p53ModeTxt);
      p53Lbl.position.set(0, -3.8, 0);
      u.group.add(p53Lbl);

      if (st.pSer15 > 0.05 || st.pSer20 > 0.05) {
        const phosTxt = isSevere ? 'P-Ser15 · P-Ser20 · P-Ser46 (Apoptosis)' : 'P-Ser15 (ATM/ATR) · P-Ser20 (CHK1/2)';
        const s15Lbl = makeLabel(phosTxt, 0xfacc15, 0.70, 'Bloquea unión de MDM2');
        s15Lbl.position.set(0, 3.8, 0);
        u.group.add(s15Lbl);
      }

      const mdm2Sub = shieldFactor > 0.5
        ? 'Desacoplada de p53 (Sin ubiquitinación)'
        : 'Acoplada a p53 · Ubiquitinación (' + pct(1 - shieldFactor) + ')';
      const mdm2Lbl = makeLabel('MDM2 Ligasa E3 + Ubiquitina', 0x8b5cf6, 0.78, mdm2Sub);
      mdm2Lbl.position.set(0, 3.6, 0);
      u.mdm2Group.add(mdm2Lbl);
    }
  });

  // --- 5. INTERRUPTOR DEL PUNTO R (DOMINIO DERECHO DESPEJADO): CICLINA D–CDK4/6, CICLINA E–CDK2 Y PINZA p21 ---
  const p21Level = clamp01(st.p21);
  const cdkInhibitionRatio = p21Level / (p21Level + 0.25);

  const rightDomainX = maxX + 32.0;

  // 5A. Complejo Ciclina D – CDK4/6 (Cuadrante Superior Derecho)
  const cdk46Group = new THREE.Group();
  cdk46Group.name = 'complex_cycD_cdk46';
  cdk46Group.scale.setScalar(1.45);
  const cdk46Pos = isLin
    ? new THREE.Vector3(rightDomainX, cy, cz + 16.0)
    : new THREE.Vector3(rightDomainX, cy + 18.0, cz + 4.0);
  cdk46Group.position.copy(cdk46Pos);
  cdk46Group.userData.brownian = { origin: cdk46Pos.clone(), phase: 0.0 };

  const actD = clamp01(st.ciclinaD * (1.0 - cdkInhibitionRatio));
  const cdk4Col = new THREE.Color(0x22c55e).lerp(new THREE.Color(0x475569), cdkInhibitionRatio * 0.7);
  // Quinasa CDK4/6 bilobular (lóbulo N + lóbulo C)
  const cdk4LobeN = new THREE.Mesh(new THREE.SphereGeometry(1.35, 18, 14), createMat(cdk4Col, 0.25 + 0.55 * actD));
  cdk4LobeN.position.set(-0.8, 0.45, 0);
  const cdk4LobeC = new THREE.Mesh(new THREE.SphereGeometry(1.55, 18, 14), createMat(cdk4Col, 0.25 + 0.55 * actD));
  cdk4LobeC.position.set(-0.6, -0.75, 0);
  // Ciclina D (dominio helicoidal cilíndrico dorado)
  const cycDCyl = new THREE.Mesh(new THREE.CylinderGeometry(1.15, 1.15, 2.7, 16), createMat(0xeab308, 0.5));
  cycDCyl.position.set(1.65, 0, 0);
  cycDCyl.rotation.z = 0.18;
  cdk46Group.add(cdk4LobeN, cdk4LobeC, cycDCyl);

  const cdk46Label = makeLabel('Ciclina D–CDK4/6 (' + pct(actD) + ')', 0x22c55e, 0.78, 'Sensor Mitogénico · Inicia fosforilación de Rb');
  cdk46Label.position.copy(UP.clone().multiplyScalar(3.6));
  cdk46Group.add(cdk46Label);
  addTether(cdk46Group, new THREE.Vector3(0.4, 1.2, 0), cdk46Label.position, 0x22c55e, 0.65);
  g.add(cdk46Group);

  // 5B. Complejo Ciclina E – CDK2 + Abrazadera Alostérica p21 (Cuadrante Inferior Derecho, separado 36 Å)
  const cdk2Group = new THREE.Group();
  cdk2Group.name = 'complex_cycE_cdk2';
  cdk2Group.scale.setScalar(1.45);
  const cdk2Pos = isLin
    ? new THREE.Vector3(rightDomainX, cy, cz - 16.0)
    : new THREE.Vector3(rightDomainX, cy - 18.0, cz - 2.0);
  cdk2Group.position.copy(cdk2Pos);
  cdk2Group.userData.brownian = { origin: cdk2Pos.clone(), phase: 1.8 };

  const actE = clamp01(st.ciclinaE * (1.0 - cdkInhibitionRatio));
  const cdk2Col = new THREE.Color(0x16a34a).lerp(new THREE.Color(0x334155), cdkInhibitionRatio * 0.9);
  const cdk2LobeN = new THREE.Mesh(new THREE.SphereGeometry(1.4, 18, 14), createMat(cdk2Col, 0.2 + 0.6 * actE));
  cdk2LobeN.position.set(-0.85, 0.45, 0);
  const cdk2LobeC = new THREE.Mesh(new THREE.SphereGeometry(1.6, 18, 14), createMat(cdk2Col, 0.2 + 0.6 * actE));
  cdk2LobeC.position.set(-0.65, -0.8, 0);
  const cycECyl = new THREE.Mesh(new THREE.CylinderGeometry(1.2, 1.2, 2.8, 16), createMat(0xf97316, 0.5));
  cycECyl.position.set(1.75, 0, 0);
  cycECyl.rotation.z = -0.15;
  cdk2Group.add(cdk2LobeN, cdk2LobeC, cycECyl);

  const cdk2Label = makeLabel('Ciclina E–CDK2 (' + pct(actE) + ')', 0x16a34a, 0.78, 'Bucle Biestable del Punto R (G1 → S)');
  cdk2Label.position.copy(UP.clone().multiplyScalar(3.6));
  cdk2Group.add(cdk2Label);
  addTether(cdk2Group, new THREE.Vector3(0.4, 1.2, 0), cdk2Label.position, 0x16a34a, 0.65);

  if (p21Level > 0.03) {
    // Abrazadera alostérica p21 (CIP1/WAF1) bloqueando la hendidura catalítica Ciclina-CDK
    const p21ClampMesh = new THREE.Mesh(
      new THREE.TorusGeometry(2.55, 0.36, 14, 48, Math.PI * 2 * Math.min(1.0, cdkInhibitionRatio * 1.25)),
      createMat(0x38bdf8, 0.92)
    );
    p21ClampMesh.position.set(0.45, 0, 0);
    p21ClampMesh.rotation.z = Math.PI * 0.5;
    p21ClampMesh.userData.isP21Clamp = true;
    cdk2Group.add(p21ClampMesh);

    const p21LabelPos = UP.clone().multiplyScalar(-3.8);
    const p21Label = makeLabel('Inhibidor p21 (CIP1/WAF1 · ' + pct(p21Level) + ')', 0x38bdf8, 0.76, 'Pinza alostérica que bloquea CDK2/CDK4');
    p21Label.position.copy(p21LabelPos);
    cdk2Group.add(p21Label);
    addTether(cdk2Group, new THREE.Vector3(0.45, -1.8, 0), p21LabelPos, 0x38bdf8, 0.7);
  }
  g.add(cdk2Group);

  // --- 6. LOCUS PROMOTOR EN LA CROMATINA: HETERODÍMERO E2F–DP1 Y PROTEÍNA Rb (p105) ---
  const promoterPairIdx = Math.min(pairs.length - 1, Math.max(0, Math.floor(pairs.length * 0.65)));
  const promoterPair = pairs[promoterPairIdx];
  const promoterBasePos = new THREE.Vector3(...promoterPair.centerPos);
  const promOut = safeOutwardDir(promoterBasePos);
  const promoterPos = promoterBasePos.clone().addScaledVector(promOut, 9.5);

  const promoterComplexGroup = new THREE.Group();
  promoterComplexGroup.name = 'promoter_e2f_rb_locus';
  promoterComplexGroup.scale.setScalar(1.40);
  promoterComplexGroup.position.copy(promoterPos);

  addTether(g, promoterBasePos, promoterPos, 0x06b6d4, 0.75);

  // Heterodímero E2F1 + DP1 asentado sobre el surco mayor del promotor
  const e2fSub = new THREE.Mesh(new THREE.CylinderGeometry(0.85, 0.85, 2.4, 14), createMat(0x06b6d4, 0.65));
  e2fSub.position.set(-0.7, 0, 0);
  e2fSub.rotation.z = 0.25;
  const dp1Sub = new THREE.Mesh(new THREE.CylinderGeometry(0.78, 0.78, 2.2, 14), createMat(0x0891b2, 0.55));
  dp1Sub.position.set(0.75, 0, 0);
  dp1Sub.rotation.z = -0.25;
  promoterComplexGroup.add(e2fSub, dp1Sub);

  // Proteína Rb (dominio de bolsillo A/B en herradura)
  const isHypoRb = cdkInhibitionRatio > 0.45;
  const rbGroup = new THREE.Group();
  rbGroup.name = 'rb_protein_subgroup';

  const rbColor = isHypoRb ? 0x94a3b8 : 0xec4899;
  const rbPocketArc = new THREE.Mesh(
    new THREE.TorusGeometry(1.75, 0.58, 14, 32, Math.PI * 1.45),
    createMat(rbColor, isHypoRb ? 0.3 : 0.8)
  );
  rbPocketArc.rotation.z = -Math.PI * 0.22;
  const rbLobeA = createSph(0.95, rbColor, isHypoRb ? 0.3 : 0.8); rbLobeA.position.set(-1.35, 0.8, 0);
  const rbLobeB = createSph(0.95, rbColor, isHypoRb ? 0.3 : 0.8); rbLobeB.position.set(1.35, 0.8, 0);
  rbGroup.add(rbPocketArc, rbLobeA, rbLobeB);

  if (isHypoRb) {
    // Rb hipofosforilado encajado sobre E2F secuestrándolo
    rbGroup.position.copy(promOut.clone().multiplyScalar(1.5));
    const rbLblPos = promOut.clone().multiplyScalar(4.5).addScaledVector(UP, -2.0);
    const rbStatusLabel = makeLabel('Rb Hipofosforilado + E2F Secuestrado', 0x94a3b8, 0.78, 'Promotor reprimido · Arresto en G1 (No cruza Punto R)');
    rbStatusLabel.position.copy(rbLblPos);
    promoterComplexGroup.add(rbStatusLabel);
    addTether(promoterComplexGroup, rbGroup.position, rbLblPos, 0x94a3b8, 0.65);
  } else {
    // Rb-P hiperfosforilado disociado en el nucleoplasma con sus 4 grupos fosfato
    const detachedOffset = promOut.clone().multiplyScalar(4.2).addScaledVector(UP, -1.8);
    rbGroup.position.copy(detachedOffset);

    [[0, 2.1, 0], [1.8, 1.1, 0.6], [-1.8, 1.1, -0.6], [0, -1.9, 0.7]].forEach(po => {
      const phos = createSph(0.48, 0xfacc15, 0.95);
      phos.position.set(po[0], po[1], po[2]);
      rbGroup.add(phos);
    });

    const detachedLabel = makeLabel('Rb-P Hiperfosforilado (Disociado)', 0xec4899, 0.76, 'Inactivado por CDK4/6 y CDK2 · Punto R Cruzado');
    detachedLabel.position.copy(UP.clone().multiplyScalar(-3.0));
    rbGroup.add(detachedLabel);

    const e2fLblPos = promOut.clone().multiplyScalar(2.0).addScaledVector(UP, 2.8);
    const e2fActiveLabel = makeLabel('Factor E2F–DP1 Libre en Promotor', 0x06b6d4, 0.78, 'Transcribiendo genes de Fase S (Ciclina E, Pol α)');
    e2fActiveLabel.position.copy(e2fLblPos);
    promoterComplexGroup.add(e2fActiveLabel);
    addTether(promoterComplexGroup, new THREE.Vector3(0, 0, 0), e2fLblPos, 0x06b6d4, 0.65);
  }
  promoterComplexGroup.add(rbGroup);
  g.add(promoterComplexGroup);

  // Guardar coordenadas de cada complejo para enfoque interactivo con 1 clic
  complexFocusCoords = {
    p53: p53Reservoir.slice(),
    cdk46: cdk46Pos.toArray(),
    cdk2: cdk2Pos.toArray(),
    rb_e2f: promoterPos.toArray(),
    sensor: firstSensorFocusPos || [cx, cy, cz]
  };

  signalingGroup = g;
  mainHelixGroup.add(g);
}

function toWorldCoords(localPt) {
  const v = new THREE.Vector3(localPt[0], localPt[1], localPt[2]);
  if (packagingMode.value === 'linear') {
    v.applyAxisAngle(new THREE.Vector3(1, 0, 0), -Math.PI / 2);
  }
  return v;
}

function focusOnComplex(key) {
  if (!camera || !controls) return;
  activeFocusKey.value = key;
  if (key === 'all' || !complexFocusCoords[key]) {
    resetCamera();
    return;
  }
  const targetWorld = toWorldCoords(complexFocusCoords[key]);
  const offsetDist = key === 'sensor' ? 46.0 : 54.0;
  controls.target.copy(targetWorld);
  camera.position.set(targetWorld.x, targetWorld.y + 4.0, targetWorld.z + offsetDist);
  controls.update();
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
  // Vista un poco más alejada y centrada para ver cómodamente el promotor Rb-E2F y el dock inferior sin cortes
  const dist = isLinear ? maxDim * 1.55 : maxDim * 1.48;
  const targetY = centro.y - (isLinear ? 1.0 : 1.5);

  camera.position.set(centro.x, targetY, dist);
  controls.target.set(centro.x, targetY, centro.z);
  camPos0.copy(camera.position);
  target0.copy(controls.target);
  activeFocusKey.value = 'all';
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
          const clicked3DPairIdx = obj.userData.atomPairMap[hit.instanceId];
          if (clicked3DPairIdx !== undefined && lastGeneratedPairs[clicked3DPairIdx]) {
            selected3DPairIdx.value = clicked3DPairIdx;
            const origSeqIdx = lastGeneratedPairs[clicked3DPairIdx].originalIndex ?? (clicked3DPairIdx % (cleanFullSequence.value.length || 1));
            internalSelectedPos.value = origSeqIdx;
            emit('selectBase', origSeqIdx);
            emit('update:selectedPosition', origSeqIdx);
            buildDNAHelix(false); // Redibuja de inmediato el anillo en el par 3D exacto clicado
          }
        }
      }
    }
  });

  animate();
}

function animate() {
  animId = requestAnimationFrame(animate);

  if (signalingGroup) {
    animClock += 0.016;
    const t = animClock;
    const tt = performance.now() * 0.00035;

    signalingGroup.children.forEach(child => {
      // 1. Quinasas CHK1 / CHK2 en tránsito direccional hacia p53
      if (child.userData && child.userData.fluxData) {
        const f = child.userData.fluxData;
        child.position.lerpVectors(f.from, f.to, (tt + f.phase) % 1.0);
      }

      // 2. Difusión browniana nucleoplásmica suave amortiguada
      if (child.userData && child.userData.brownian) {
        const b = child.userData.brownian;
        child.position.x = b.origin.x + Math.sin(t * 1.2 + b.phase) * 0.45;
        child.position.y = b.origin.y + Math.cos(t * 0.9 + b.phase) * 0.55;
        child.position.z = b.origin.z + Math.sin(t * 0.7 + b.phase) * 0.35;
        child.rotation.y = Math.sin(t * 0.6 + b.phase) * 0.08;
      }

      // 3. Respiración mecánica del anillo p21 en la hendidura catalítica
      if (child.children) {
        child.children.forEach(sub => {
          if (sub.userData && sub.userData.isP21Clamp) {
            const clampPulse = 1.0 + 0.05 * Math.sin(t * 2.8);
            sub.scale.set(clampPulse, clampPulse, 1.0);
          }
        });
      }
    });
  }

  const lesG = mainHelixGroup && mainHelixGroup.getObjectByName('lesion_decorations');
  if (lesG) {
    const sc = 1 + 0.25 * Math.sin(performance.now() * 0.006);
    lesG.children.forEach(m => { if (m.userData.pulse) m.scale.setScalar(sc); });
  }
  controls?.update();

  // Animación de complejos p53 / Mdm2 / Ubiquitina
  if (p53UnitsList.length > 0) {
    const totalUnits = p53UnitsList.length;

    if (!p53State.value.active) {
      // ESTADO DE REPOSO: Agrupadas en esfera no uniforme, moviéndose y fluctuando orgánicamente ("carritos locos")
      const t = Date.now() * 0.0022;
      p53UnitsList.forEach((u, i) => {
        if (u.floatingAnchor && u.group && u.mdm2Group) {
          const wobbleX = Math.sin(t * 2.0 + i * 1.8) * 1.6 + Math.cos(t * 1.1 + i * 2.7) * 1.0;
          const wobbleY = Math.cos(t * 1.8 + i * 2.2) * 1.5 + Math.sin(t * 1.4 + i * 1.3) * 0.9;
          const wobbleZ = Math.sin(t * 1.6 + i * 1.5) * 1.6 + Math.cos(t * 2.3 + i * 2.5) * 1.0;

          const posX = u.floatingAnchor[0] + wobbleX;
          const posY = u.floatingAnchor[1] + wobbleY;
          const posZ = u.floatingAnchor[2] + wobbleZ;

          u.group.position.x += (posX - u.group.position.x) * 0.16;
          u.group.position.y += (posY - u.group.position.y) * 0.16;
          u.group.position.z += (posZ - u.group.position.z) * 0.16;

          u.group.rotation.y += 0.016;
          u.group.rotation.x += 0.009;

          // MDM2 acoplado junto al trímero de p53 en reposo
          u.mdm2Group.position.x += (posX - u.mdm2Group.position.x) * 0.16;
          u.mdm2Group.position.y += (posY + 6.5 - u.mdm2Group.position.y) * 0.16;
          u.mdm2Group.position.z += (posZ - u.mdm2Group.position.z) * 0.16;

          u.mdm2Group.rotation.y += 0.012;
        }
      });
    } else {
      // ESTADO ACTIVO: p53 patrulla el ADN moviéndose JUNTAS como carritos locos agrupadas en círculo/esfera no uniforme
      const t = Date.now() * 0.0034;
      p53UnitsList.forEach((u, i) => {
        if (u.group) {
          // Distribución en esfera no uniforme dinámica (como enjambre / carritos locos)
          const phi = (i * 2.39996) + t * 1.6;
          const cosTheta = 1 - (2 * (i + 0.5) / Math.max(1, totalUnits));
          const sinTheta = Math.sqrt(Math.max(0, 1 - cosTheta * cosTheta));
          const clusterRadius = 3.8 + Math.sin(t * 2.4 + i * 2.1) * 1.3;

          // Fluctuaciones dinámicas caóticas ("carritos locos" esquivándose y revoloteando)
          const jitterX = Math.sin(t * 3.3 + i * 1.9) * 1.4 + Math.cos(t * 1.7 + i * 3.1) * 1.0;
          const jitterY = Math.cos(t * 2.9 + i * 2.3) * 1.4 + Math.sin(t * 1.5 + i * 1.7) * 0.9;
          const jitterZ = Math.sin(t * 2.6 + i * 1.4) * 1.5 + Math.cos(t * 3.7 + i * 2.7) * 1.0;

          const targetX = swarmCenter[0] + (sinTheta * Math.cos(phi) * clusterRadius) + jitterX;
          const targetY = swarmCenter[1] + (cosTheta * clusterRadius * 0.8) + jitterY;
          const targetZ = swarmCenter[2] + (sinTheta * Math.sin(phi) * clusterRadius) + jitterZ;

          // Movimiento reactivo a 60 FPS
          u.group.position.x += (targetX - u.group.position.x) * 0.22;
          u.group.position.y += (targetY - u.group.position.y) * 0.22;
          u.group.position.z += (targetZ - u.group.position.z) * 0.22;

          u.group.rotation.x += 0.024 * Math.sin(i + 1);
          u.group.rotation.y += 0.036 * Math.cos(i + 1);
          u.group.rotation.z += 0.02;
        }

        // MDM2 y ubiquitina flotando ARRIBA en el espacio libre del nucleoplasma (lejos del ADN y del tamaño de p53)
        if (u.mdm2Group && u.distantAnchor) {
          const floatX = Math.cos(t * 0.8 + i * 1.8) * 3.5;
          const floatY = Math.sin(t * 1.0 + i * 1.5) * 2.8;
          const floatZ = Math.sin(t * 0.7 + i * 2.1) * 2.0;

          u.mdm2Group.position.x += (u.distantAnchor[0] + floatX - u.mdm2Group.position.x) * 0.08;
          u.mdm2Group.position.y += (u.distantAnchor[1] + floatY - u.mdm2Group.position.y) * 0.08;
          u.mdm2Group.position.z += (u.distantAnchor[2] + floatZ - u.mdm2Group.position.z) * 0.08;

          u.mdm2Group.rotation.y += 0.008;
          u.mdm2Group.rotation.x += 0.004;
        }
      });
    }
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
  if (isExpanded.value) {
    if (document.documentElement && document.documentElement.requestFullscreen && !document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch(() => {});
    }
  } else {
    if (document.fullscreenElement && document.exitFullscreen) {
      document.exitFullscreen().catch(() => {});
    }
  }
  nextTick(() => {
    onWindowResize();
    setTimeout(onWindowResize, 80);
    setTimeout(onWindowResize, 250);
  });
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

let sigTimer = null;
watch(() => props.cellState, () => {
  if (sigTimer) return;
  sigTimer = setTimeout(() => { sigTimer = null; buildSignaling(); }, 1000);
}, { deep: true });

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
  if (typeof document !== 'undefined') document.removeEventListener('fullscreenchange', onFullscreenChange);
  if (controls) controls.dispose();
  if (renderer) renderer.dispose();
});
</script>

<style scoped>
/* Contenedor Principal de la Tarjeta (100% Edge-to-Edge Full Viewport) */
.dna-3d-card {
  position: relative;
  width: 100%;
  height: 100%;
  flex: 1 1 auto;
  background-color: #030b24;
  border-radius: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  border: none;
  box-shadow: none;
}

/* Header de la tarjeta integrado tipo HUD superior */
.card-header {
  padding: 0.55rem 1.25rem;
  background: linear-gradient(90deg, rgba(6, 12, 26, 0.96) 0%, rgba(11, 20, 42, 0.92) 50%, rgba(6, 12, 26, 0.96) 100%);
  border-bottom: 1px solid rgba(56, 189, 248, 0.22);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.75rem;
  flex-shrink: 0;
  z-index: 30;
}

.header-main {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.header-avatar {
  width: 36px;
  height: 36px;
  border-radius: var(--md-sys-shape-corner-small, 8px);
  background: linear-gradient(135deg, rgba(14, 165, 233, 0.25) 0%, rgba(2, 132, 199, 0.35) 100%);
  border: 1px solid rgba(56, 189, 248, 0.35);
  color: #38bdf8;
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-titles {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.title-text {
  font-size: 0.98rem;
  color: #f8fafc;
  font-weight: 700;
  letter-spacing: -0.2px;
  margin: 0;
}

.subhead-text {
  font-size: 0.74rem;
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
  min-height: 0;
}

/* Canvas Area */
.canvas-wrapper {
  position: relative;
  width: 100%;
  flex: 1 1 auto;
  height: 100%;
  min-height: 0;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: grab;
  background: radial-gradient(ellipse at 50% 46%, #0d1f3a 0%, #061121 62%, #030813 100%);
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

/* Estilos para los elementos HUD situados directamente en las esquinas */
.hud-corner-dropdown {
  position: absolute;
  top: 14px;
  z-index: 25;
}

.hud-corner-dropdown.corner-left {
  left: 18px;
}

.hud-corner-dropdown.corner-right {
  right: 18px;
}

.hud-corner-pill-btn {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 6px 14px;
  border-radius: 9999px;
  background: rgba(8, 15, 32, 0.90);
  border: 1px solid rgba(56, 189, 248, 0.35);
  color: #f1f5f9;
  font-size: 0.76rem;
  font-weight: 700;
  cursor: pointer;
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.55), 0 0 12px rgba(56, 189, 248, 0.15);
  transition: all 0.2s ease;
}

.hud-corner-pill-btn:hover {
  background: rgba(15, 23, 42, 0.98);
  border-color: #38bdf8;
  color: #ffffff;
  box-shadow: 0 0 16px rgba(56, 189, 248, 0.35);
}

.pill-icon {
  color: #38bdf8;
}

.pill-title {
  letter-spacing: 0.02em;
}

.pill-arrow {
  color: #94a3b8;
  transition: transform 0.2s ease;
}

.hud-dropdown-panel {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  width: 280px;
  background: rgba(7, 13, 28, 0.95);
  border: 1px solid rgba(56, 189, 248, 0.3);
  border-radius: 14px;
  padding: 10px 12px;
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.8), 0 0 20px rgba(56, 189, 248, 0.15);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  animation: fadeInDown 0.2s ease;
}

.hud-corner-pill-card {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 6px 14px;
  border-radius: 16px;
  background: rgba(8, 15, 32, 0.90);
  border: 1px solid rgba(56, 189, 248, 0.35);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.55), 0 0 12px rgba(56, 189, 248, 0.15);
}

.pair-display-row.compact-corner {
  margin: 0;
  gap: 0.55rem;
}

.corner-pair-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.65rem;
  color: #94a3b8;
  padding-top: 2px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.corner-pair-label .c-pos {
  color: #38bdf8;
  font-weight: 700;
}

.corner-pair-label .c-type {
  color: #64748b;
}

/* Floating HUDs */
.hud-card {
  position: absolute;
  background: rgba(7, 13, 28, 0.88);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border: 1px solid rgba(56, 189, 248, 0.28);
  border-radius: var(--md-sys-shape-corner-medium, 12px);
  padding: 0.75rem 0.95rem;
  box-shadow: 0 10px 32px rgba(0, 0, 0, 0.65);
  z-index: 15;
  pointer-events: auto;
}

.hud-top-left {
  top: 0.75rem;
  left: 214px;
  max-width: 320px;
}

.hud-top-right {
  top: 0.75rem;
  right: 214px;
  min-width: 245px;
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
@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translate(-50%, -12px);
  }
  to {
    opacity: 1;
    transform: translate(-50%, 0);
  }
}

.apoptosis-overlay-banner {
  position: absolute;
  top: 3.5rem;
  left: 50%;
  transform: translateX(-50%);
  z-index: 45;
  pointer-events: none;
  animation: fadeInDown 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
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
  top: 3.5rem;
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
  top: 3.5rem;
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


/* ═══════════════════════ BARRA FLOTANTE DE ENFOQUE A COMPLEJOS (ALBERTS) ═══════════════════════ */
.molecular-complex-focus-bar {
  position: absolute;
  top: 0.85rem;
  left: 50%;
  transform: translateX(-50%);
  z-index: 35;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.35rem 0.65rem;
  background: rgba(8, 15, 30, 0.88);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border: 1px solid rgba(56, 189, 248, 0.32);
  border-radius: 9999px;
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.65), 0 0 18px rgba(56, 189, 248, 0.14);
  pointer-events: auto;
  max-width: calc(100% - 620px);
  overflow-x: auto;
  scrollbar-width: none;
}

.molecular-complex-focus-bar::-webkit-scrollbar {
  display: none;
}

.complex-focus-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.38rem;
  padding: 0.3rem 0.72rem;
  border-radius: 9999px;
  background: rgba(15, 23, 42, 0.75);
  border: 1px solid rgba(148, 163, 184, 0.22);
  color: #cbd5e1;
  font-size: 0.71rem;
  font-weight: 600;
  white-space: nowrap;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.complex-focus-pill:hover {
  background: rgba(30, 41, 59, 0.95);
  border-color: rgba(56, 189, 248, 0.6);
  color: #f8fafc;
  transform: translateY(-1px);
}

.complex-focus-pill.active {
  background: linear-gradient(135deg, rgba(2, 132, 199, 0.38) 0%, rgba(15, 23, 42, 0.95) 100%);
  border-color: #38bdf8;
  color: #ffffff;
  box-shadow: 0 0 12px rgba(56, 189, 248, 0.35);
}

.complex-focus-pill.lesions-pill {
  border-color: rgba(244, 63, 94, 0.55);
  color: #fecdd3;
}

.cf-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}
.cf-dot.p53 { background: #34d399; box-shadow: 0 0 6px #34d399; }
.cf-dot.cdk4 { background: #fbbf24; box-shadow: 0 0 6px #fbbf24; }
.cf-dot.cdk2 { background: #f97316; box-shadow: 0 0 6px #f97316; }
.cf-dot.rb { background: #a855f7; box-shadow: 0 0 6px #a855f7; }
.cf-dot.lesion { background: #f43f5e; box-shadow: 0 0 6px #f43f5e; }

/* ═══════════════════════ CADENA DE NUCLEÓTIDOS DOCK COMPACTO EN LA ORILLA INFERIOR ═══════════════════════ */
.canvas-wrapper {
  flex: 1 1 auto !important;
  height: 100% !important;
  min-height: 0 !important;
}

.atomic-canvas-box {
  height: 100% !important;
  min-height: 0 !important;
}

.dna-3d-card.cinema-expanded,
.dna-3d-card:fullscreen {
  position: fixed !important;
  inset: 0 !important;
  width: 100vw !important;
  height: 100vh !important;
  max-height: 100vh !important;
  border-radius: 0 !important;
  z-index: 1200 !important;
  display: flex !important;
  flex-direction: column !important;
}

.dna-3d-card.cinema-expanded .canvas-wrapper,
.dna-3d-card:fullscreen .canvas-wrapper {
  flex: 1 1 auto !important;
  height: auto !important;
  min-height: 0 !important;
}

.dna-3d-card.cinema-expanded .atomic-canvas-box,
.dna-3d-card:fullscreen .atomic-canvas-box {
  min-height: 0 !important;
  height: 100% !important;
}

.header-nav-toolbar {
  display: flex;
  align-items: center;
  gap: 3px;
  background: rgba(15, 23, 42, 0.85);
  border: 1px solid rgba(56, 189, 248, 0.3);
  border-radius: 9999px;
  padding: 2px 6px;
  backdrop-filter: blur(10px);
}

.nav-mode-pill {
  display: flex;
  align-items: center;
  gap: 2px;
  background: rgba(2, 6, 23, 0.6);
  border-radius: 9999px;
  padding: 1px 2px;
}

.nav-tool-btn {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 1px solid transparent;
  background: transparent;
  color: #94a3b8;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.15s ease;
  padding: 0;
}

.nav-tool-btn:hover {
  background: rgba(56, 189, 248, 0.18);
  border-color: rgba(56, 189, 248, 0.4);
  color: #38bdf8;
}

.nav-tool-btn.active {
  background: rgba(14, 165, 233, 0.35);
  border-color: #38bdf8;
  color: #ffffff;
  box-shadow: 0 0 10px rgba(56, 189, 248, 0.4);
}

.nav-tools-divider {
  width: 1px;
  height: 16px;
  background: rgba(56, 189, 248, 0.22);
  margin: 0 2px;
}

.bottom-nucleotide-dock {
  position: absolute;
  bottom: 10px;
  left: 214px;
  right: 214px;
  margin-left: auto;
  margin-right: auto;
  width: max-content;
  max-width: calc(100vw - 428px);
  box-sizing: border-box;
  z-index: 20;
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(6, 12, 24, 0.94);
  border: 1px solid rgba(56, 189, 248, 0.32);
  border-radius: 12px;
  padding: 5px 12px;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.78), 0 0 18px rgba(56, 189, 248, 0.14);
}

.dock-polarity-col {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  height: 84px;
  padding: 1px 0;
  flex-shrink: 0;
  user-select: none;
}

.dock-polarity-tag {
  padding: 2px 5px;
  border-radius: 4px;
  font-size: 0.65rem;
  font-weight: 800;
  font-family: var(--md-ref-typeface-mono, monospace);
  border: 1px solid;
  letter-spacing: 0.5px;
}

.dock-polarity-tag.p5 {
  background: rgba(51, 115, 230, 0.25);
  color: #70d6ff;
  border-color: rgba(56, 189, 248, 0.45);
}

.dock-polarity-tag.p3 {
  background: rgba(115, 140, 191, 0.25);
  color: #b0c4de;
  border-color: rgba(115, 140, 191, 0.45);
}

.dock-polarity-stem {
  width: 1px;
  flex: 1;
  background: rgba(56, 189, 248, 0.2);
  margin: 3px 0;
}

.nucleotide-scroll-track {
  display: flex;
  align-items: center;
  gap: 5px;
  overflow-x: auto;
  overflow-y: hidden;
  scroll-behavior: smooth;
  flex: 1 1 auto;
  min-width: 0;
  max-width: 100%;
  padding: 2px 4px;
  scrollbar-width: thin;
  scrollbar-color: rgba(56, 189, 248, 0.6) rgba(8, 15, 28, 0.7);
}

/* Scrollbar ultra sutil y estilizado */
.nucleotide-scroll-track::-webkit-scrollbar {
  height: 4px;
}
.nucleotide-scroll-track::-webkit-scrollbar-track {
  background: rgba(8, 15, 28, 0.7);
  border-radius: 999px;
}
.nucleotide-scroll-track::-webkit-scrollbar-thumb {
  background: linear-gradient(90deg, rgba(56, 189, 248, 0.4), rgba(14, 165, 233, 0.9));
  border-radius: 999px;
  box-shadow: 0 0 6px rgba(56, 189, 248, 0.5);
}

.dock-base-column {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 32px;
  padding: 2px 2px;
  border-radius: 6px;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.16s cubic-bezier(0.4, 0, 0.2, 1);
  user-select: none;
  flex-shrink: 0;
  position: relative;
}

.dock-base-column:hover {
  background: rgba(56, 189, 248, 0.1);
  border-color: rgba(56, 189, 248, 0.35);
  transform: translateY(-2px);
}

.dock-base-column.active {
  background: rgba(0, 77, 105, 0.45);
  border: 1.5px solid var(--md-sys-color-primary, #70d6ff);
  box-shadow: 0 0 14px rgba(112, 214, 255, 0.55);
  transform: translateY(-2px);
}

.dock-base-column.damaged {
  border-color: #f43f5e;
  box-shadow: 0 0 10px rgba(244, 63, 94, 0.55);
}

.dock-pos-idx {
  font-size: 0.58rem;
  color: #64748b;
  line-height: 1;
  margin-bottom: 2px;
}

.dock-bb-monomer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1px;
  position: relative;
  width: 100%;
}

.dock-bb-monomer.top {
  margin-bottom: 3px;
}

.dock-bb-monomer.bottom {
  margin-top: 3px;
}

.dock-bb-dot {
  font-family: var(--md-ref-typeface-mono, monospace);
  font-size: 0.52rem;
  font-weight: 800;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

.dock-bb-dot.phosphate {
  background: #3373e6;
  color: #ffffff;
  box-shadow: 0 0 5px rgba(51, 115, 230, 0.6);
}

.dock-bb-dot.sugar {
  background: #738cbf;
  color: #ffffff;
  border-radius: 2px;
  box-shadow: 0 0 5px rgba(115, 140, 191, 0.6);
}

.dock-bb-hyphen {
  font-size: 0.5rem;
  font-weight: 700;
  color: rgba(148, 163, 184, 0.5);
  margin: 0 1px;
}

.dock-bb-stem-down {
  position: absolute;
  bottom: -3px;
  left: 50%;
  width: 1px;
  height: 3px;
  background: rgba(148, 163, 184, 0.35);
}

.dock-bb-stem-up {
  position: absolute;
  top: -3px;
  left: 50%;
  width: 1px;
  height: 3px;
  background: rgba(148, 163, 184, 0.35);
}

.dock-base-capsule {
  width: 24px;
  height: 22px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 0.78rem;
  transition: transform 0.15s ease;
}

/* Colores canónicos de bases concordantes con la paleta 3D del proyecto */
.dock-base-column.a .dock-base-capsule.primary {
  background: linear-gradient(135deg, rgba(140, 204, 255, 0.22) 0%, rgba(140, 204, 255, 0.35) 100%);
  color: #8cccff;
  border: 1px solid rgba(140, 204, 255, 0.6);
  box-shadow: 0 0 8px rgba(140, 204, 255, 0.3);
}

.dock-base-column.t .dock-base-capsule.primary {
  background: linear-gradient(135deg, rgba(64, 128, 242, 0.22) 0%, rgba(64, 128, 242, 0.35) 100%);
  color: #4080f2;
  border: 1px solid rgba(64, 128, 242, 0.6);
  box-shadow: 0 0 8px rgba(64, 128, 242, 0.3);
}

.dock-base-column.c .dock-base-capsule.primary {
  background: linear-gradient(135deg, rgba(38, 89, 217, 0.22) 0%, rgba(38, 89, 217, 0.35) 100%);
  color: #2659d9;
  border: 1px solid rgba(38, 89, 217, 0.6);
  box-shadow: 0 0 8px rgba(38, 89, 217, 0.3);
}

.dock-base-column.g .dock-base-capsule.primary {
  background: linear-gradient(135deg, rgba(191, 224, 255, 0.22) 0%, rgba(191, 224, 255, 0.35) 100%);
  color: #bfe0ff;
  border: 1px solid rgba(191, 224, 255, 0.6);
  box-shadow: 0 0 8px rgba(191, 224, 255, 0.3);
}

.dock-base-capsule.comp {
  background: rgba(15, 23, 42, 0.75);
  border: 1px solid rgba(148, 163, 184, 0.25);
  color: #94a3b8;
}

.dock-base-column:hover .dock-base-capsule {
  transform: scale(1.08);
}

.dock-hydrogen-bonds {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  height: 10px;
  margin: 1px 0;
}

.dock-h-line {
  width: 10px;
  height: 1.5px;
  border-radius: 1px;
  background-color: #8fb4e0;
  box-shadow: 0 0 3px rgba(143, 180, 224, 0.7);
}

.dock-damage-beacon {
  position: absolute;
  top: -2px;
  right: -2px;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #f43f5e;
  box-shadow: 0 0 6px #f43f5e;
}


.hud-top-left.collapsed {
  max-width: 170px;
}

.hud-card-header.clickable {
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  user-select: none;
}

.hud-header-left {
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.hud-toggle-btn {
  background: transparent;
  border: none;
  color: #38bdf8;
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: 0.65rem;
  font-family: var(--md-ref-typeface-mono, monospace);
  cursor: pointer;
  padding: 0;
}

.dock-polarity-col {
  height: 84px;
}

</style>
