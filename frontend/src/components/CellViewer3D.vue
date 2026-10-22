<template>
  <div class="confocal-workstation md3-card-outlined">
    <!-- Workstation Header / Control de Canales y Modos Ópticos -->
    <div class="workstation-header">
      <div class="header-left">
        <div class="header-icon-box">
          <Icon name="biotech" size="24" />
        </div>
        <div>
          <h2>Microscopía Confocal 3D — Ultra-Estructura Celular Proporcional</h2>
          <span class="subtext">Simulación biomecánica basada en dimensiones citológicas reales (1 µm = 0.28 unidades 3D)</span>
        </div>
      </div>

      <!-- Segmented Fluorophore Channels & Optical Controls -->
      <div class="header-controls-row">
        <div class="channels-legend">
          <button 
            :class="['channel-chip dapi', { active: channels.dapi }]"
            @click="toggleChannel('dapi')"
            title="Fluorescencia 405nm (Núcleo y Cromatina)"
          >
            <span class="pip"></span>
            <span class="ch-name">DAPI (405nm)</span>
            <span class="ch-target">ADN</span>
          </button>
          <button 
            :class="['channel-chip mito', { active: channels.mito }]"
            @click="toggleChannel('mito')"
            title="MitoTracker Red 561nm (Mitocondrias activas)"
          >
            <span class="pip"></span>
            <span class="ch-name">MitoTracker (561nm)</span>
            <span class="ch-target">ATP</span>
          </button>
          <button 
            :class="['channel-chip gfp', { active: channels.gfp }]"
            @click="toggleChannel('gfp')"
            title="GFP 488nm (Centrosomas, Citoesqueleto y Peroxisomas)"
          >
            <span class="pip"></span>
            <span class="ch-name">GFP (488nm)</span>
            <span class="ch-target">Tubulina</span>
          </button>
          <button 
            :class="['channel-chip cy5', { active: channels.cy5 }]"
            @click="toggleChannel('cy5')"
            title="Cy5 / Alexa Fluor 640nm (Membrana y Endomembranas)"
          >
            <span class="pip"></span>
            <span class="ch-name">Cy5 (640nm)</span>
            <span class="ch-target">Membranas</span>
          </button>
        </div>

        <div class="optical-toggles">
          <button 
            :class="['tool-btn', { active: !isAutoRotating }]" 
            @click="toggleAutoRotate" 
            :title="isAutoRotating ? 'Pausar rotación 3D' : 'Reanudar rotación 3D'"
          >
            <Icon :name="isAutoRotating ? 'pause' : '3d_rotation'" size="16" />
            <span>{{ isAutoRotating ? 'Pausar Rotación 3D' : 'Reanudar Rotación' }}</span>
          </button>
          <button 
            :class="['tool-btn', { active: crossSection }]" 
            @click="toggleCrossSection" 
            title="Corte Sagital 50% para ver el interior del citosol sin oclusión"
          >
            <Icon name="tune" size="16" />
            <span>Corte Sagital (50%)</span>
          </button>
          <button 
            :class="['tool-btn', { active: showScaleTable }]" 
            @click="showScaleTable = !showScaleTable" 
            title="Ver tabla de proporciones y escala citométrica"
          >
            <Icon name="analytics" size="16" />
            <span>Escala Citométrica</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Barra Superior de Fases Celulares (G0, G1, S, G2, M) -->
    <div class="phase-selector-bar">
      <button 
        v-for="p in mainPhases" 
        :key="p.code"
        :class="['phase-nav-item', { active: activeMainPhase === p.code }]"
        @click="selectMainPhase(p.code)"
        type="button"
      >
        <span class="phase-badge">{{ p.code }}</span>
        <div class="phase-info">
          <span class="phase-name">{{ p.shortName }}</span>
          <span class="phase-sub">{{ p.captionShort }}</span>
        </div>
        <div class="active-indicator"></div>
      </button>
    </div>

    <!-- Sub-barra Dinámica de Mitosis con Timeline y Reproductor Continuo a 60 FPS -->
    <div class="subphase-selector-bar" v-if="activeMainPhase === 'M'">
      <div class="mitosis-top-row">
        <div class="subphase-label">
          <Icon name="cell_merge" size="18" class="pulse-icon" />
          <span>Cinética de Mitosis (Fase M):</span>
        </div>
        <div class="subphase-buttons">
          <button 
            v-for="sub in mitosisSubphases" 
            :key="sub.id"
            :class="['subphase-chip', { active: activeMitosisSubphase === sub.id }]"
            @click="jumpToMitosisSubphase(sub.id)"
          >
            <span class="num">{{ sub.step }}.</span>
            <span class="sub-name">{{ sub.name }}</span>
          </button>
        </div>

        <div class="mitosis-controls">
          <button class="icon-tool-btn" @click="stepMitosisPrev" title="Etapa anterior">
            <Icon name="skip_previous" size="16" />
          </button>
          <button 
            class="play-mitosis-btn" 
            @click="toggleMitosisPlayback" 
            :title="isPlayingMitosis ? 'Pausar simulación continua' : 'Reproducir mitosis continua a 60 FPS'"
          >
            <Icon :name="isPlayingMitosis ? 'pause' : 'play_arrow'" size="16" />
            <span>{{ isPlayingMitosis ? 'Pausar' : 'Reproducir' }}</span>
          </button>
          <button class="icon-tool-btn" @click="stepMitosisNext" title="Siguiente etapa">
            <Icon name="skip_next" size="16" />
          </button>

          <div class="speed-selector" title="Velocidad de reproducción">
            <button 
              v-for="s in [0.5, 1.0, 2.0]" 
              :key="s" 
              :class="['speed-btn', { active: mitosisSpeed === s }]"
              @click="mitosisSpeed = s"
            >
              {{ s }}x
            </button>
          </div>
        </div>
      </div>

      <!-- Scrubber Slider Continuo 0% a 100% -->
      <div class="mitosis-scrubber-row">
        <div class="scrubber-track-container">
          <input 
            type="range" 
            min="0" 
            max="100" 
            step="0.2"
            v-model.number="mitosisProgressPercent" 
            @input="onScrubberInput"
            class="mitosis-scrubber-slider"
          />
          <div class="stage-ticks">
            <span 
              v-for="sub in mitosisSubphases" 
              :key="sub.id" 
              class="stage-tick"
              :style="{ left: (sub.center * 100) + '%' }"
              :class="{ current: activeMitosisSubphase === sub.id }"
              @click="jumpToMitosisSubphase(sub.id)"
            >
              {{ sub.name }}
            </span>
          </div>
        </div>
        <div class="scrubber-metric-badge">
          <span class="badge-label">{{ currentMitosisData?.name }}</span>
          <span class="badge-pct">{{ Math.round(mitosisProgress * 100) }}%</span>
        </div>
      </div>
    </div>

    <!-- Visor Central 3D + Inspector Anatómico Lateral -->
    <div class="viewer-main-area">
      <!-- Visor Central WebGL -->
      <div class="single-viewer-container">
        <div class="canvas-box" ref="canvasContainer">
          <!-- Overlay HUD Superior Izquierdo: Telemetría y Fase Activa -->
          <div class="viewer-hud-top-left">
            <div class="active-code-pill">
              {{ activeMainPhase }}
              <span v-if="activeMainPhase === 'M'">: {{ currentMitosisData?.name }}</span>
            </div>
            <div class="hud-phase-meta">
              <span class="phase-title">{{ activePhaseTitle }}</span>
              <div class="hud-sub-tags">
                <span class="tag">OBJETIVO: 100x INMERSIÓN EN ACEITE</span>
                <span class="tag">RESOLUCIÓN: CONFOCAL PROCEDURAL</span>
                <span class="tag" v-if="isolatedOrganelle">AISLADO: {{ isolatedOrganelle.name }}</span>
              </div>
            </div>
          </div>

          <!-- Overlay HUD Superior Derecho: Controles de Cámara y Navegación -->
          <div class="viewer-hud-top-right">
            <!-- Botón Pausar/Reanudar Rotación 3D visible en cada fase celular -->
            <button 
              :class="['rotation-hud-btn', { paused: !isAutoRotating }]" 
              @click.stop="toggleAutoRotate" 
              :title="isAutoRotating ? 'Pausar rotación automática 3D de la célula' : 'Reanudar rotación automática 3D'"
            >
              <Icon :name="isAutoRotating ? 'pause' : '3d_rotation'" size="15" class="rot-icon" />
              <span>{{ isAutoRotating ? 'Pausar Rotación 3D' : 'Reanudar Rotación' }}</span>
            </button>

            <div class="telemetry-box">
              <span class="hud-cue"><Icon name="3d_rotation" size="14" class="cue-icon" /> Rotar 360°</span>
              <span class="hud-cue"><Icon name="zoom_in" size="14" class="cue-icon" /> Zoom continuo</span>
            </div>
            <div class="nav-controls">
              <button class="nav-btn" @click.stop="prevPhase" title="Fase anterior">
                <Icon name="chevron_left" size="18" />
              </button>
              <button class="nav-btn" @click.stop="nextPhase" title="Fase siguiente">
                <Icon name="chevron_right" size="18" />
              </button>
            </div>
          </div>

          <!-- Overlay HUD Inferior: Micro-descripción Biomecánica -->
          <div class="viewer-hud-bottom">
            <div class="caption-dock">
              <Icon name="info" size="16" class="dock-icon" />
              <span class="caption-code">{{ activeMainPhase }}</span>
              <span class="divider">/</span>
              <span class="caption-desc">{{ activePhaseCaption }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Panel Lateral: Catálogo e Inspector Anatómico de Orgánulos -->
      <div class="organelle-inspector-sidebar">
        <div class="sidebar-header">
          <div class="sidebar-title-row">
            <div class="title-with-icon">
              <Icon name="layers" size="18" class="header-icon" />
              <div>
                <h3>Orgánulos & Estructura</h3>
                <span class="sub-dim">Explorador Citológico Ultra-Pro</span>
              </div>
            </div>
            <span class="badge">{{ filteredOrganelles.length }} / {{ organellesList.length }}</span>
          </div>

          <!-- Barra de Búsqueda Rápida -->
          <div class="search-input-wrap">
            <Icon name="search" size="14" class="search-icon" />
            <input 
              type="text" 
              v-model="organelleSearchQuery" 
              placeholder="Buscar por nombre o función..." 
              class="organelle-search-input"
            />
            <button v-if="organelleSearchQuery" @click="organelleSearchQuery = ''" class="clear-search-btn" title="Limpiar búsqueda">✕</button>
          </div>

          <!-- Chips de Filtro por Categoría -->
          <div class="category-filter-chips">
            <button 
              v-for="cat in organelleCategories" 
              :key="cat.id"
              :class="['cat-chip', { active: organelleCategoryFilter === cat.id }]"
              @click="organelleCategoryFilter = cat.id"
            >
              {{ cat.name }}
            </button>
          </div>
        </div>

        <div class="organelle-chips-scroll">
          <!-- Botón de Vista Celular Completa -->
          <button 
            :class="['organelle-btn full-cell-btn', { active: selectedOrganelleId === 'all' && !isolatedOrganelleId }]"
            @click="selectOrganelle('all')"
          >
            <span class="org-dot all"></span>
            <div class="org-texts">
              <div class="org-name-row">
                <span class="org-name">Vista Celular Completa</span>
                <span class="cat-pill all">Completa</span>
              </div>
              <span class="org-dim">Todos los 15 componentes anatómicos</span>
            </div>
            <button 
              v-if="isolatedOrganelleId" 
              class="restore-quick-pill" 
              @click.stop="toggleIsolate(null)" 
              title="Restablecer vista a todos los orgánulos"
            >
              Restaurar
            </button>
          </button>

          <!-- Lista de Orgánulos Filtrados -->
          <div 
            v-for="org in filteredOrganelles" 
            :key="org.id"
            :class="['organelle-card-item', { 
              active: selectedOrganelleId === org.id,
              isolated: isolatedOrganelleId === org.id 
            }]"
            @click="selectOrganelle(org.id)"
          >
            <div class="item-left">
              <span class="org-dot" :style="{ backgroundColor: org.color, boxShadow: `0 0 8px ${org.color}aa` }"></span>
              <div class="org-texts">
                <div class="org-name-row">
                  <span class="org-name">{{ org.name }}</span>
                  <span class="cat-pill" :class="org.category">{{ getCategoryLabel(org.category) }}</span>
                </div>
                <span class="org-dim font-mono">{{ org.realSize }} &bull; {{ org.scale3d }}</span>
              </div>
            </div>

            <!-- Botones de Acción Rápida en la Fila -->
            <div class="item-quick-actions" @click.stop>
              <button 
                class="quick-action-btn focus-btn"
                @click="focusCameraOnOrganelle(org.id)"
                title="Enfocar cámara en este orgánulo"
              >
                <Icon name="center_focus_strong" size="13" />
              </button>
              <button 
                :class="['quick-action-btn solo-btn', { active: isolatedOrganelleId === org.id }]"
                @click="toggleIsolate(org.id)"
                :title="isolatedOrganelleId === org.id ? 'Restaurar vista completa' : 'Aislar este componente en 3D'"
              >
                <span v-if="isolatedOrganelleId === org.id">SOLO</span>
                <span v-else>Aislar</span>
              </button>
            </div>
          </div>

          <div v-if="filteredOrganelles.length === 0" class="empty-search-state">
            <Icon name="search_off" size="24" />
            <p>No se encontraron componentes citológicos con ese criterio.</p>
          </div>
        </div>

        <!-- Ficha de Telemetría Anatómica del Orgánulo Seleccionado -->
        <div class="organelle-spec-card md3-card-elevated" v-if="selectedOrganelleData">
          <div class="spec-card-head">
            <div class="spec-dot" :style="{ backgroundColor: selectedOrganelleData.color, boxShadow: `0 0 10px ${selectedOrganelleData.color}` }"></div>
            <div class="spec-titles">
              <h4>{{ selectedOrganelleData.name }}</h4>
              <div class="spec-badge-row">
                <span class="dim-tag font-mono">Real: {{ selectedOrganelleData.realSize }}</span>
                <span class="ratio-tag font-mono">3D: {{ selectedOrganelleData.scale3d }}</span>
              </div>
            </div>
          </div>

          <div class="spec-body-content">
            <div class="spec-info-block">
              <span class="block-label">Estructura & Ultra-morfología:</span>
              <p class="block-text">{{ selectedOrganelleData.structure }}</p>
            </div>

            <div class="spec-info-block">
              <span class="block-label">Función Bioquímica:</span>
              <p class="block-text">{{ selectedOrganelleData.function }}</p>
            </div>

            <div class="spec-phase-state">
              <span class="label">Estado en Fase {{ activeMainPhase }}:</span>
              <span class="value">{{ getOrganellePhaseBehavior(selectedOrganelleData.id) }}</span>
            </div>
          </div>

          <div class="spec-actions">
            <button 
              class="isolate-btn" 
              :class="{ active: isolatedOrganelleId === selectedOrganelleData.id }"
              @click="toggleIsolate(selectedOrganelleData.id)"
            >
              <Icon :name="isolatedOrganelleId === selectedOrganelleData.id ? 'visibility_off' : 'visibility'" size="15" />
              <span>{{ isolatedOrganelleId === selectedOrganelleData.id ? 'Restaurar Vista Completa' : 'Aislar en 3D (Solo)' }}</span>
            </button>
            <button 
              class="focus-camera-btn" 
              @click="focusCameraOnOrganelle(selectedOrganelleData.id)"
              title="Centrar y aproximar cámara a este orgánulo"
            >
              <Icon name="center_focus_strong" size="15" />
              <span>Enfocar Cámara</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal / Drawer: Tabla Comparativa de Escala Proporcional Científica -->
    <div class="scale-table-modal" v-if="showScaleTable" @click.self="showScaleTable = false">
      <div class="scale-modal-content md3-card-elevated">
        <div class="modal-header">
          <div class="header-left">
            <Icon name="analytics" size="20" />
            <h3>Tabla Citométrica de Proporciones Reales vs Modelo 3D</h3>
          </div>
          <button class="close-btn" @click="showScaleTable = false">✕</button>
        </div>
        <p class="modal-intro">
          Factor de escala matemática normalizado: <strong>1 µm ≈ 0.28 unidades 3D</strong>. 
          Asegura la fidelidad biológica estricta de volúmenes intracelulares:
        </p>

        <div class="table-wrapper">
          <table class="cytometry-table">
            <thead>
              <tr>
                <th>Orgánulo / Estructura</th>
                <th>Dimensión Citológica Real</th>
                <th>Dimensión Proporcional en 3D</th>
                <th>Proporción Relativa / Función</th>
                <th>Comportamiento en Mitosis (M)</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="org in organellesList" :key="org.id">
                <td class="org-cell">
                  <span class="pip" :style="{ backgroundColor: org.color }"></span>
                  <strong>{{ org.name }}</strong>
                </td>
                <td class="font-mono">{{ org.realSize }}</td>
                <td class="font-mono highlight">{{ org.scale3d }}</td>
                <td>{{ org.structure }}</td>
                <td class="phase-behavior">{{ getOrganelleMitosisBehavior(org.id) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Panel de Inspección Científica Inferior y Persistencia -->
    <div class="inspection-panel">
      <div class="panel-card">
        <div class="card-left">
          <div class="code-badge">{{ activeMainPhase }}</div>
          <div class="card-headings">
            <h3>{{ activePhaseTitle }}</h3>
            <span class="sub-text">Microscopía confocal en tiempo real · {{ activePhaseMorphology }}</span>
          </div>
        </div>

        <div class="card-specs">
          <div class="spec-cell">
            <span class="spec-label">Volumen Celular</span>
            <span class="spec-val font-mono">{{ currentVolumeText }}</span>
          </div>
          <div class="spec-cell">
            <span class="spec-label">Contenido ADN</span>
            <span class="spec-val highlight font-mono">{{ activePhaseDna }}</span>
          </div>
          <div class="spec-cell">
            <span class="spec-label">Mitocondrias Activas</span>
            <span class="spec-val font-mono">{{ activeMitoCount }} unidades</span>
          </div>
          <div class="spec-cell">
            <span class="spec-label">Centrosomas</span>
            <span class="spec-val font-mono">{{ activeCentrosomeText }}</span>
          </div>
        </div>

        <button class="md3-button-filled" @click="syncWithPostgres">
          <Icon name="save" size="18" />
          <span>Fijar Estado en PostgreSQL</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue';
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import Icon from './Icon.vue';

const props = defineProps({
  cellState: {
    type: String,
    default: 'G1'
  }
});

const emit = defineEmits(['update:cellState']);

// Canales ópticos de fluorescencia
const channels = ref({
  dapi: true,
  mito: true,
  gfp: true,
  cy5: true
});

const crossSection = ref(true); // Iniciado en true para ver el interior celular espectacular
const showScaleTable = ref(false);
const isAutoRotating = ref(true);
const isPlayingMitosis = ref(false);
const mitosisSpeed = ref(1.0);
const mitosisProgress = ref(0.41); // Inicia centrado en Metafase (placa ecuatorial visible)

function toggleAutoRotate() {
  isAutoRotating.value = !isAutoRotating.value;
}

// Subfases de Mitosis con límites temporales normalizados [0.0, 1.0]
const mitosisSubphases = [
  {
    id: 'prophase',
    step: 1,
    name: 'Profase',
    start: 0.0,
    end: 0.16,
    center: 0.08,
    desc: 'Condensación de cromatina en cromosomas visibles en X. El nucléolo se desvanece y los dos centrosomas inician su migración hacia polos opuestos emitiendo rayos de áster.'
  },
  {
    id: 'prometaphase',
    step: 2,
    name: 'Prometafase',
    start: 0.16,
    end: 0.33,
    center: 0.24,
    desc: 'Disolución total de la envoltura nuclear. Los microtúbulos del huso invaden el núcleo y capturan los cinetocoros de los cromosomas mediante inestabilidad dinámica.'
  },
  {
    id: 'metaphase',
    step: 3,
    name: 'Metafase',
    start: 0.33,
    end: 0.50,
    center: 0.41,
    desc: 'Alineación ecuatorial de máxima precisión en la placa metafásica (x = 0). Tensión bilateral de fibras cinetocóricas comprobada por el punto de control SAC.'
  },
  {
    id: 'anaphase',
    step: 4,
    name: 'Anafase',
    start: 0.50,
    end: 0.68,
    center: 0.59,
    desc: 'Degradación de cohesinas por la separasa. Las cromátidas hermanas se segregan a polos opuestos con resistencia hidrodinámica (morfología en V) mientras la célula se elonga.'
  },
  {
    id: 'telophase',
    step: 5,
    name: 'Telofase',
    start: 0.68,
    end: 0.84,
    center: 0.76,
    desc: 'Reconstitución de las dos nuevas envolturas nucleares en cada polo alrededor de la cromatina descondensada. Reaparecen los nucléolos y el huso central forma el cuerpo intermedio.'
  },
  {
    id: 'cytokinesis',
    step: 6,
    name: 'Citocinesis',
    start: 0.84,
    end: 1.0,
    center: 0.92,
    desc: 'Contracción progresiva del anillo de actina y miosina II en el ecuador, estrangulando el surco de escisión hasta separar la célula en dos células hijas autónomas con reparto 50/50.'
  }
];

const activeMitosisSubphase = computed(() => {
  const p = mitosisProgress.value;
  const match = mitosisSubphases.find(s => p >= s.start && p < s.end);
  return match ? match.id : (p >= 0.84 ? 'cytokinesis' : 'prophase');
});

const mitosisProgressPercent = computed({
  get: () => Math.round(mitosisProgress.value * 1000) / 10,
  set: (val) => {
    mitosisProgress.value = Math.max(0, Math.min(1, val / 100));
    updateContinuousMitosis(mitosisProgress.value);
  }
});

// Fases Principales
const activeMainPhase = ref(props.cellState?.startsWith('M') ? 'M' : (props.cellState || 'G1'));

watch(() => props.cellState, (val) => {
  if (val) {
    if (val.startsWith('M')) {
      activeMainPhase.value = 'M';
      const sub = val.split('_')[1];
      const match = mitosisSubphases.find(s => s.id === sub);
      if (match) {
        mitosisProgress.value = match.center;
      }
    } else if (mainPhases.some(p => p.code === val)) {
      activeMainPhase.value = val;
    }
    update3DState();
  }
});

// Fases Principales
const mainPhases = [
  {
    code: 'G0',
    shortName: 'G0 — Reposo',
    captionShort: 'Quiescencia basal / Mantenimiento',
    title: 'G0 — Célula en Reposo (Quiescencia Basal)',
    caption: 'G0: Célula metabólicamente estable sin proliferación. Tamaño basal mínimo, nucléolo compacto, 1 centrosoma y metabolismo respiratorio basal.',
    morphology: 'Célula ovoide basal (diámetro ~14 µm). Cromatina laxa con baja transcripción, ribosomas y endomembranas en nivel de reposo.',
    dna: '2C (Diploide basal)',
    radius: 2.0,
    mitoCount: 8,
    centrosomes: 1
  },
  {
    code: 'G1',
    shortName: 'G1 — Crecimiento',
    captionShort: 'Síntesis de ARNm y proteínas',
    title: 'G1 — Crecimiento Activo y Síntesis de ARN',
    caption: 'G1: La célula despierta y se expande activamente. El nucléolo se agranda, aumentan los ribosomas, RER y Golgi; las mitocondrias se alargan y dividen.',
    morphology: 'Célula en expansión continua (~16.5 µm). Núcleo activo con nucléolo agrandado. Red de RER y túbulos de Golgi ramificados.',
    dna: '2C (Pre-replicativo)',
    radius: 2.3,
    mitoCount: 14,
    centrosomes: 1
  },
  {
    code: 'S',
    shortName: 'S — Replicación',
    captionShort: 'Duplicación de ADN y Centríolos',
    title: 'S — Replicación del ADN y Duplicación Centrosomal',
    caption: 'S: Replicación activa del genoma en múltiples horquillas simultáneas. El centrosoma se duplica formando procentríolos. Mitocondrias aumentan para ATP.',
    morphology: 'Célula hiperactiva (~18.5 µm). Núcleo brillante poblado por focos de replicación. Duplicación de diplosomas centríolares.',
    dna: '2C ➔ 4C (En duplicación activa)',
    radius: 2.6,
    mitoCount: 20,
    centrosomes: 2
  },
  {
    code: 'G2',
    shortName: 'G2 — Preparación',
    captionShort: 'Volumen máximo y dos centrosomas',
    title: 'G2 — Preparación Avanzada para la División',
    caption: 'G2: Fase de mayor volumen y carga celular (~21 µm). Cromatina compactándose, 2 centrosomas maduros separados en polos superiores con áster radiante.',
    morphology: 'Célula hipertrofiada al máximo (~21 µm). Dos centrosomas maduros polares con microtúbulos dinámicos. Máxima dotación de mitocondrias y endomembranas.',
    dna: '4C (Genoma duplicado)',
    radius: 2.9,
    mitoCount: 28,
    centrosomes: 2
  },
  {
    code: 'M',
    shortName: 'M — Mitosis',
    captionShort: 'División nuclear y citocinesis',
    title: 'M — Mitosis y Citocinesis Celular',
    caption: 'M: Gran reordenamiento macromolecular. Cromosomas condensados en X, disolución de envoltura nuclear, huso mitótico bipolar y estrangulamiento por actomiosina.',
    morphology: 'Dinámica mitótica coordinada: de placa ecuatorial a surco de escisión de citocinesis en dos células hijas.',
    dna: '4C ➔ 2x(2C) (Segregación equitativa)',
    radius: 2.8,
    mitoCount: 28,
    centrosomes: 2
  }
];



// Lista de los 15 Componentes Anatómicos con dimensiones científicas exactas
const organellesList = [
  {
    id: 'nucleus',
    name: 'Núcleo Celular',
    category: 'genetic',
    realSize: '5 - 10 µm',
    scale3d: 'R = 0.85 - 1.30 u',
    color: '#3b82f6',
    target: [0, 0, 0],
    camDist: 3.8,
    structure: 'El orgánulo más grande. Doble membrana nuclear con poros de 100 nm, matriz con cromatina (ADN + histonas) y nucléolo.',
    function: 'Almacena y custodia el genoma completo. Centro de control de la transcripción de ARN y la replicación del ADN.'
  },
  {
    id: 'nucleolus',
    name: 'Nucléolo',
    category: 'genetic',
    realSize: '1 - 3 µm',
    scale3d: 'R = 0.22 - 0.42 u',
    color: '#60a5fa',
    target: [0.02, 0.02, -0.08],
    camDist: 2.2,
    structure: 'Subcompartimento denso y esférico dentro del núcleo, no delimitado por membrana, rico en ARNr y ribonucleoproteínas.',
    function: 'Síntesis de ARN ribosómico (ARNr) y ensamblaje de las subunidades ribosómicas 40S y 60S.'
  },
  {
    id: 'envelope',
    name: 'Envoltura Nuclear & Poros',
    category: 'genetic',
    realSize: 'Poros ~100 nm',
    scale3d: 'Shell doble + anillos NPC',
    color: '#2563eb',
    target: [0, 0, 0],
    camDist: 3.2,
    structure: 'Doble bicapa lipídica concéntrica perforada por complejos de poro nuclear (NPC) octagonales de ~100 nm.',
    function: 'Regula selectivamente el tráfico bidireccional macromolecular de ARN, factores de transcripción y proteínas entre núcleo y citosol.'
  },
  {
    id: 'mitochondria',
    name: 'Mitocondrias (MitoTracker)',
    category: 'energy',
    realSize: '0.5-1 x 1-2 µm',
    scale3d: '0.16 x 0.36 u',
    color: '#f97316',
    target: [-0.6, -0.5, 0.0],
    camDist: 3.2,
    structure: 'Orgánulo cilíndrico/arriñonado de doble membrana con crestas mitocondriales internas invaginadas y matriz con ADNmt.',
    function: 'Respiración celular y síntesis aeróbica masiva de ATP mediante fosforilación oxidativa. Regula apoptosis.'
  },
  {
    id: 'rer',
    name: 'Retículo Endopl. Rugoso (RER)',
    category: 'endomembrane',
    realSize: 'Cisternas 40-50 nm',
    scale3d: 'Láminas curvadas',
    color: '#06b6d4',
    target: [-0.08, 0.04, 0.01],
    camDist: 3.0,
    structure: 'Red de sacos aplanados y cisternas membranosas interconectadas, densamente tapizadas de ribosomas en su cara citosólica.',
    function: 'Síntesis, plegamiento con chaperonas y N-glicosilación inicial de proteínas de secreción, lisosomales y transmembrana.'
  },
  {
    id: 'rel',
    name: 'Retículo Endopl. Liso (REL)',
    category: 'endomembrane',
    realSize: 'Túbulos 30-60 nm',
    scale3d: 'Malla tubular',
    color: '#f43f5e',
    target: [-1.42, -0.72, -0.2],
    camDist: 2.6,
    structure: 'Red anastomosada de túbulos membranosos lisos, continuos con el RER pero carentes de ribosomas adheridos.',
    function: 'Biosíntesis de lípidos y esteroides, detoxificación de xenobióticos/fármacos y reservorio intracelular de calcio (Ca2+).'
  },
  {
    id: 'golgi',
    name: 'Aparato de Golgi & Vesículas',
    category: 'endomembrane',
    realSize: 'Dictiosoma 1 - 3 µm',
    scale3d: 'Pilas de 5 cisternas',
    color: '#eab308',
    target: [0.98, -0.68, 0.28],
    camDist: 2.6,
    structure: 'Pila de 4-6 cisternas membranosas curvas con polaridad bioquímica estricta (cara cis receptora y cara trans de secreción).',
    function: 'Modificación postraduccional, clasificación y empaquetamiento de proteínas y lípidos en vesículas de transporte específico.'
  },
  {
    id: 'centrosome',
    name: 'Centrosoma con Centríolos',
    category: 'structure',
    realSize: '0.2 x 0.4 µm',
    scale3d: 'Cilindros L 0.05 x 0.12 u',
    color: '#a3e635',
    target: [0.72, 1.05, 0.22],
    camDist: 1.8,
    structure: 'Par de centríolos ortogonales en ángulo de 90° formados por 9 tripletes de microtúbulos, inmersos en material pericentriolar (PCM).',
    function: 'Centro organizador de microtúbulos (MTOC). Nuclea el citoesqueleto y construye el huso mitótico bipolar en la división celular.'
  },
  {
    id: 'lysosome',
    name: 'Lisosomas',
    category: 'endomembrane',
    realSize: '0.2 - 0.5 µm',
    scale3d: 'R = 0.09 u',
    color: '#fbbf24',
    target: [-0.6, -0.8, 0.2],
    camDist: 2.8,
    structure: 'Vesículas esféricas delimitadas por membrana única provistas de bombas de protones vacuolares (V-ATPasa, pH 4.5 - 5.0).',
    function: 'Digestión celular de macromoléculas, degradación de desechos celulares, autofagia y destrucción de partículas fagocitadas.'
  },
  {
    id: 'peroxisome',
    name: 'Peroxisomas',
    category: 'energy',
    realSize: '0.2 - 0.5 µm',
    scale3d: 'R = 0.08 u',
    color: '#10b981',
    target: [0.8, 0.6, -0.2],
    camDist: 2.8,
    structure: 'Vesículas metabólicas esféricas con núcleo cristalino conteniendo altas concentraciones de catalasa y oxidasas flavínicas.',
    function: 'Beta-oxidación de ácidos grasos de cadena muy larga y descomposición inmediata del tóxico peróxido de hidrógeno (H2O2) en agua.'
  },
  {
    id: 'vacuole',
    name: 'Vacuolas Animales',
    category: 'endomembrane',
    realSize: '0.3 - 0.8 µm',
    scale3d: 'R = 0.13 u',
    color: '#38bdf8',
    target: [-0.5, 0.8, 0.1],
    camDist: 2.8,
    structure: 'Vesículas acuosas de almacenamiento rodeadas por membrana simple semipermeable.',
    function: 'Almacenamiento transitorio de agua, solutos, iones y secuestro de sustancias osmóticas secundarias.'
  },
  {
    id: 'ribosome',
    name: 'Ribosomas Libres',
    category: 'structure',
    realSize: '20 - 30 nm',
    scale3d: 'Nube micro-partículas',
    color: '#c084fc',
    target: [0, 0, 0],
    camDist: 3.5,
    structure: 'Complejos ribonucleoproteicos multiméricos de 80S constituidos por subunidad menor 40S y mayor 60S dispersos en citosol.',
    function: 'Traducción de ARN mensajero en proteínas citosólicas solubles (enzimas de la glucólisis, tubulina, actina).'
  },
  {
    id: 'cytoskeleton',
    name: 'Citoesqueleto & Huso',
    category: 'structure',
    realSize: '7 - 25 nm',
    scale3d: 'Red filamentos & huso',
    color: '#2dd4bf',
    target: [0, 0, 0],
    camDist: 4.0,
    structure: 'Red tridimensional dinámica de microtúbulos de tubulina (25 nm), filamentos intermedios (10 nm) y microfilamentos de actina (7 nm).',
    function: 'Soporte mecánico, transporte vesicular axonal/intracelular, ciclosis y formación del huso acromático y anillo contráctil.'
  },
  {
    id: 'cytosol',
    name: 'Citosol (Matriz Celular)',
    category: 'structure',
    realSize: 'Fase coloidal acuosa',
    scale3d: 'Volumen difuso',
    color: '#0284c7',
    target: [0, 0, 0],
    camDist: 4.8,
    structure: 'Gel coloidal acuoso rico en agua (70%), iones disueltos, aminoácidos, nucleótidos y metabolitos intermedios.',
    function: 'Medio fluido en el que flotan los orgánulos; sede de reacciones metabólicas basales como glucólisis y biosíntesis de monómeros.'
  },
  {
    id: 'membrane',
    name: 'Membrana Plasmática',
    category: 'structure',
    realSize: '7 - 10 nm grosor',
    scale3d: 'Bicapa R = 2.0 - 2.9 u',
    color: '#70d6ff',
    target: [0, 0, 0],
    camDist: 5.6,
    structure: 'Bicapa lipídica fluida (fosfolípidos, colesterol y esfingolípidos) con proteínas integrales y periféricas incrustadas.',
    function: 'Mantiene la homeostasis intracelular, barrera de permeabilidad selectiva, transducción de señales y comunicación celular.'
  }
];

const selectedOrganelleId = ref('all');
const isolatedOrganelleId = ref(null);
const organelleCategoryFilter = ref('all');
const organelleSearchQuery = ref('');

const organelleCategories = [
  { id: 'all', name: 'Todos' },
  { id: 'genetic', name: 'Genético' },
  { id: 'endomembrane', name: 'Endomembrana' },
  { id: 'energy', name: 'Metabolismo' },
  { id: 'structure', name: 'Estructura' }
];

const filteredOrganelles = computed(() => {
  return organellesList.filter(org => {
    const matchesCat = (organelleCategoryFilter.value === 'all') || (org.category === organelleCategoryFilter.value);
    const matchesQuery = !organelleSearchQuery.value || 
      org.name.toLowerCase().includes(organelleSearchQuery.value.toLowerCase()) ||
      org.structure.toLowerCase().includes(organelleSearchQuery.value.toLowerCase()) ||
      org.function.toLowerCase().includes(organelleSearchQuery.value.toLowerCase());
    return matchesCat && matchesQuery;
  });
});

const selectedOrganelleData = computed(() => {
  return organellesList.find(o => o.id === selectedOrganelleId.value);
});

const isolatedOrganelle = computed(() => {
  return organellesList.find(o => o.id === isolatedOrganelleId.value);
});

function getCategoryLabel(category) {
  if (category === 'genetic') return 'Genético';
  if (category === 'endomembrane') return 'Endomembrana';
  if (category === 'energy') return 'Metabolismo';
  if (category === 'structure') return 'Estructura';
  return 'Orgánulo';
}

function focusCameraOnOrganelle(id) {
  if (!camera || !controls) return;
  if (id === 'all' || !id) {
    smoothFocusOn(new THREE.Vector3(0, 0, 0), 8.2);
    return;
  }
  const org = organellesList.find(o => o.id === id);
  if (!org) return;
  const tgt = org.target || [0, 0, 0];
  const dist = org.camDist || 3.8;
  smoothFocusOn(new THREE.Vector3(tgt[0], tgt[1], tgt[2]), dist);
}

function smoothFocusOn(targetVec, distance = 4.0, duration = 800) {
  if (!camera || !controls) return;
  
  const currentDir = new THREE.Vector3().subVectors(camera.position, controls.target).normalize();
  if (currentDir.lengthSq() < 0.001) currentDir.set(0, 0.2, 1);
  
  const endPos = new THREE.Vector3().copy(targetVec).addScaledVector(currentDir, distance);
  
  cameraTransition = {
    startPos: camera.position.clone(),
    endPos: endPos,
    startTarget: controls.target.clone(),
    endTarget: targetVec.clone(),
    startTime: performance.now(),
    duration: duration
  };
}

function selectOrganelle(id) {
  selectedOrganelleId.value = id;
  if (id === 'all') {
    isolatedOrganelleId.value = null;
    focusCameraOnOrganelle('all');
  } else {
    focusCameraOnOrganelle(id);
  }
  updateVisibilityLayers();
}

function toggleIsolate(id) {
  if (!id || isolatedOrganelleId.value === id) {
    isolatedOrganelleId.value = null;
    focusCameraOnOrganelle('all');
  } else {
    isolatedOrganelleId.value = id;
    selectedOrganelleId.value = id;
    focusCameraOnOrganelle(id);
  }
  updateVisibilityLayers();
}

function toggleCrossSection() {
  crossSection.value = !crossSection.value;
  updateCrossSectionState();
}

function toggleChannel(ch) {
  channels.value[ch] = !channels.value[ch];
  updateChannelColors();
}

// Comportamiento de cada orgánulo en cada fase
function getOrganellePhaseBehavior(orgId) {
  const p = activeMainPhase.value;
  if (p === 'G0') {
    if (orgId === 'nucleus') return 'Cromatina laxa, baja tasa de transcripción génica.';
    if (orgId === 'nucleolus') return 'Tamaño mínimo (1.5 µm), baja síntesis de ARNr.';
    if (orgId === 'mitochondria') return 'Cantidad basal mínima (8 uds), producción estable de ATP.';
    if (orgId === 'centrosome') return '1 solo centrosoma con 2 centríolos juntos en reposo.';
    if (orgId === 'rer' || orgId === 'golgi') return 'Volumen compacto para mantenimiento basal.';
    return 'Actividad y tamaño mínimos de reposo metabólico.';
  }
  if (p === 'G1') {
    if (orgId === 'nucleus') return 'Aumenta de volumen, transcripción activa de ARNm.';
    if (orgId === 'nucleolus') return 'Se agranda y activa intensamente para fabricar ribosomas.';
    if (orgId === 'mitochondria') return 'Mitocondrias se alargan y sufren fisión (suben a 14 uds).';
    if (orgId === 'centrosome') return '1 centrosoma; al final de G1 los centríolos se separan ligeramente.';
    if (orgId === 'rer' || orgId === 'golgi') return 'Expansión continua para biosíntesis de proteínas y lípidos.';
    return 'Crecimiento generalizado y preparación metabólica.';
  }
  if (p === 'S') {
    if (orgId === 'nucleus') return 'Replicación activa del ADN en horquillas simultáneas.';
    if (orgId === 'centrosome') return 'Duplicación activa: nacen dos procentríolos perpendiculares.';
    if (orgId === 'mitochondria') return 'Aumentan a 20 uds para satisfacer alta demanda energética.';
    if (orgId === 'rer') return 'Alta síntesis de histonas requeridas para empaquetar ADN nuevo.';
    return 'Duplicación sincrónica de genoma y diplosomas.';
  }
  if (p === 'G2') {
    if (orgId === 'nucleus') return 'Volumen nuclear máximo, cromatina condensándose.';
    if (orgId === 'centrosome') return '2 centrosomas maduros separados en polo superior con áster.';
    if (orgId === 'mitochondria') return 'Máxima dotación celular (28 uds) listas para segregarse.';
    if (orgId === 'rer' || orgId === 'golgi') return 'Masa celular totalmente duplicada para repartir.';
    return 'Preparación final con citoesqueleto altamente dinámico.';
  }
  if (p === 'M') {
    const sub = activeMitosisSubphase.value;
    if (sub === 'prophase') return 'Cromatina condensada en cromosomas en X; nucléolo disuelto; centrosomas viajan a polos opuestos.';
    if (sub === 'prometaphase') return 'Envoltura nuclear fragmentada en vesículas; microtúbulos capturan cinetocoros; Golgi/RE fragmentados.';
    if (sub === 'metaphase') return 'Cromosomas alineados perfectamente en el plano ecuatorial con fibras en tensión.';
    if (sub === 'anaphase') return 'Cromátidas hermanas separadas desplazándose a polos opuestos; célula alargada.';
    if (sub === 'telophase') return 'Envoltura nuclear reensamblada en ambos polos; cromosomas se descondensan; nucléolo reaparece.';
    if (sub === 'cytokinesis') return 'Surco de escisión estrangulado por anillo de actina; dos células hijas con dotación completa.';
  }
  return 'Estado fisiológico activo coordinado.';
}

function getOrganelleMitosisBehavior(orgId) {
  if (orgId === 'nucleus' || orgId === 'envelope') return 'Desensamblaje en prometafase y reconstitución en telofase';
  if (orgId === 'nucleolus') return 'Se disuelve en profase y reaparece en telofase';
  if (orgId === 'centrosome') return 'Polos opuestos nucleando el huso bipolar';
  if (orgId === 'cytoskeleton') return 'Construye el huso acromático y anillo de citocinesis';
  if (orgId === 'rer' || orgId === 'golgi') return 'Fragmentación en vesículas y reconstitución en células hijas';
  if (orgId === 'mitochondria' || orgId === 'lysosome' || orgId === 'peroxisome') return 'Partición y segregación equitativa 50/50 entre ambas células hijas';
  if (orgId === 'membrane') return 'Invaginación y estrangulamiento ecuatorial';
  return 'Repartición citoplásmica pasiva';
}

const currentMitosisData = computed(() => {
  return mitosisSubphases.find(s => s.id === activeMitosisSubphase.value) || mitosisSubphases[2];
});

const activePhaseTitle = computed(() => {
  if (activeMainPhase.value === 'M') {
    return `Mitosis (M) — ${currentMitosisData.value?.name}`;
  }
  return mainPhases.find(p => p.code === activeMainPhase.value)?.title || '';
});

const activePhaseCaption = computed(() => {
  if (activeMainPhase.value === 'M') {
    return currentMitosisData.value?.desc || '';
  }
  return mainPhases.find(p => p.code === activeMainPhase.value)?.caption || '';
});

const activePhaseMorphology = computed(() => {
  if (activeMainPhase.value === 'M') {
    return `Etapa ${currentMitosisData.value?.step}/6: ${currentMitosisData.value?.desc}`;
  }
  return mainPhases.find(p => p.code === activeMainPhase.value)?.morphology || '';
});

const activePhaseDna = computed(() => {
  if (activeMainPhase.value === 'M') {
    const sub = activeMitosisSubphase.value;
    if (sub === 'anaphase' || sub === 'telophase' || sub === 'cytokinesis') {
      return '4C ➔ 2x (2C Diploide)';
    }
    return '4C (Cromosomas dobles)';
  }
  return mainPhases.find(p => p.code === activeMainPhase.value)?.dna || '2C';
});

const activeMitoCount = computed(() => {
  const p = mainPhases.find(m => m.code === activeMainPhase.value);
  return p ? p.mitoCount : 14;
});

const activeCentrosomeText = computed(() => {
  if (activeMainPhase.value === 'G0') return '1 centrosoma (2 centríolos juntos)';
  if (activeMainPhase.value === 'G1') return '1 centrosoma (centríolos en separación)';
  if (activeMainPhase.value === 'S') return '2 pares (duplicación en curso)';
  if (activeMainPhase.value === 'G2') return '2 centrosomas maduros separados';
  if (activeMainPhase.value === 'M') return '2 centrosomas en polos opuestos (Huso)';
  return '1';
});

const currentVolumeText = computed(() => {
  const p = mainPhases.find(m => m.code === activeMainPhase.value);
  if (p) return `Radio 3D: ${p.radius.toFixed(2)} u (~${(p.radius / 0.28).toFixed(1)} µm)`;
  return '';
});

function selectMainPhase(code) {
  activeMainPhase.value = code;
  if (code !== 'M') {
    emit('update:cellState', code);
  } else {
    emit('update:cellState', `M_${activeMitosisSubphase.value}`);
  }
  update3DState();
}

function jumpToMitosisSubphase(subId) {
  const sub = mitosisSubphases.find(s => s.id === subId);
  if (sub) {
    mitosisProgress.value = sub.center;
    activeMainPhase.value = 'M';
    updateContinuousMitosis(mitosisProgress.value);
    emit('update:cellState', `M_${subId}`);
  }
}

function selectMitosisSubphase(subId) {
  jumpToMitosisSubphase(subId);
}

function onScrubberInput() {
  activeMainPhase.value = 'M';
  updateContinuousMitosis(mitosisProgress.value);
  emit('update:cellState', `M_${activeMitosisSubphase.value}`);
}

function stepMitosisPrev() {
  const idx = mitosisSubphases.findIndex(s => s.id === activeMitosisSubphase.value);
  if (idx > 0) {
    jumpToMitosisSubphase(mitosisSubphases[idx - 1].id);
  } else {
    jumpToMitosisSubphase(mitosisSubphases[0].id);
  }
}

function stepMitosisNext() {
  const idx = mitosisSubphases.findIndex(s => s.id === activeMitosisSubphase.value);
  if (idx < mitosisSubphases.length - 1) {
    jumpToMitosisSubphase(mitosisSubphases[idx + 1].id);
  } else {
    jumpToMitosisSubphase(mitosisSubphases[mitosisSubphases.length - 1].id);
  }
}

function toggleMitosisPlayback() {
  isPlayingMitosis.value = !isPlayingMitosis.value;
  if (isPlayingMitosis.value) {
    activeMainPhase.value = 'M';
  }
}

function prevPhase() {
  if (activeMainPhase.value === 'M') {
    const idx = mitosisSubphases.findIndex(s => s.id === activeMitosisSubphase.value);
    if (idx > 0) {
      jumpToMitosisSubphase(mitosisSubphases[idx - 1].id);
    } else {
      selectMainPhase('G2');
    }
  } else {
    const idx = mainPhases.findIndex(p => p.code === activeMainPhase.value);
    const prevIdx = (idx - 1 + mainPhases.length) % mainPhases.length;
    selectMainPhase(mainPhases[prevIdx].code);
  }
}

function nextPhase() {
  if (activeMainPhase.value === 'M') {
    const idx = mitosisSubphases.findIndex(s => s.id === activeMitosisSubphase.value);
    if (idx < mitosisSubphases.length - 1) {
      jumpToMitosisSubphase(mitosisSubphases[idx + 1].id);
    } else {
      selectMainPhase('G0');
    }
  } else {
    const idx = mainPhases.findIndex(p => p.code === activeMainPhase.value);
    if (mainPhases[idx].code === 'G2') {
      selectMainPhase('M');
      jumpToMitosisSubphase('prophase');
    } else {
      selectMainPhase(mainPhases[(idx + 1) % mainPhases.length].code);
    }
  }
}

function syncWithPostgres() {
  const code = activeMainPhase.value === 'M' ? `M_${activeMitosisSubphase.value}` : activeMainPhase.value;
  emit('update:cellState', code);
  alert(`Fase '${code}' vinculada con PostgreSQL en el registro de células virtuales.`);
}

// =========================================================================
// 3D THREE.JS PROCEDURAL SCIENTIFIC GRAPHICS ENGINE
// Ultra-pro biological eukaryotic cell renderer matching confocal / cryo-EM standards
// =========================================================================
const canvasContainer = ref(null);
let renderer = null;
let scene = null;
let camera = null;
let controls = null;
let mainCellGroup = null;
let animId = null;
const startTime = performance.now();

// Grupos de orgánulos para control individual de visibilidad y shaders
const organelleGroups = {
  nucleus: null,
  nucleolus: null,
  envelope: null,
  mitochondria: null,
  rer: null,
  rel: null,
  golgi: null,
  centrosome: null,
  lysosome: null,
  peroxisome: null,
  vacuole: null,
  ribosome: null,
  cytoskeleton: null,
  cytosol: null,
  membrane: null
};

// Shaders GLSL para Membrana Celular con Corte Sagital y Fresnel
const noiseGLSL = `
vec3 mod289(vec3 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
vec4 mod289(vec4 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
vec4 permute(vec4 x) { return mod289(((x*34.0)+1.0)*x); }
vec4 taylorInvSqrt(vec4 r) { return 1.79284291400159 - 0.85373472095314 * r; }
float snoise(vec3 v) {
  const vec2 C = vec2(1.0/6.0, 1.0/3.0);
  const vec4 D = vec4(0.0, 0.5, 1.0, 2.0);
  vec3 i  = floor(v + dot(v, C.yyy) );
  vec3 x0 = v - i + dot(i, C.xxx) ;
  vec3 g = step(x0.yzx, x0.xyz);
  vec3 l = 1.0 - g;
  vec3 i1 = min( g.xyz, l.zxy );
  vec3 i2 = max( g.xyz, l.zxy );
  vec3 x1 = x0 - i1 + C.xxx;
  vec3 x2 = x0 - i2 + C.yyy;
  vec3 x3 = x0 - D.yyy;
  i = mod289(i);
  vec4 p = permute( permute( permute(
              i.z + vec4(0.0, i1.z, i2.z, 1.0 ))
            + i.y + vec4(0.0, i1.y, i2.y, 1.0 ))
            + i.x + vec4(0.0, i1.x, i2.x, 1.0 ));
  float n_ = 0.142857142857;
  vec3  ns = n_ * D.wyz - D.xzx;
  vec4 j = p - 49.0 * floor(p * ns.z * ns.z);
  vec4 x_ = floor(j * ns.z);
  vec4 y_ = floor(j - 7.0 * x_ );
  vec4 x = x_ *ns.x + ns.yyyy;
  vec4 y = y_ *ns.x + ns.yyyy;
  vec4 h = 1.0 - abs(x) - abs(y);
  vec4 b0 = vec4( x.xy, y.xy );
  vec4 b1 = vec4( x.zw, y.zw );
  vec4 s0 = floor(b0)*2.0 + 1.0;
  vec4 s1 = floor(b1)*2.0 + 1.0;
  vec4 sh = -step(h, vec4(0.0));
  vec4 a0 = b0.xzyw + s0.xzyw*sh.xxyy ;
  vec4 a1 = b1.xzyw + s1.xzyw*sh.zzww ;
  vec3 p0 = vec3(a0.xy,h.x);
  vec3 p1 = vec3(a0.zw,h.y);
  vec3 p2 = vec3(a1.xy,h.z);
  vec3 p3 = vec3(a1.zw,h.w);
  vec4 norm = taylorInvSqrt(vec4(dot(p0,p0), dot(p1,p1), dot(p2, p2), dot(p3,p3)));
  p0 *= norm.x; p1 *= norm.y; p2 *= norm.z; p3 *= norm.w;
  vec4 m = max(0.6 - vec4(dot(x0,x0), dot(x1,x1), dot(x2,x2), dot(x3,x3)), 0.0);
  m = m * m;
  return 42.0 * dot( m*m, vec4( dot(p0,x0), dot(p1,x1), dot(p2,x2), dot(p3,x3) ) );
}
`;

let membraneMaterial = null;
let nucleusMaterial = null;
let replicationFociPoints = null;
let mitoticSpindleLines = null;
let spindleGeo = null;
let spindlePositions = null;
const NUM_K_FIBERS = 16;
const NUM_INTERPOLAR = 24;
const NUM_ASTRAL_PER_POLE = 16;
const TOTAL_SPINDLE_LINES = NUM_K_FIBERS + NUM_INTERPOLAR + (NUM_ASTRAL_PER_POLE * 2);

let chromosomesGroup = null;
const chromatidsList = [];
let contractileRingMesh = null;
let daughterNucleusLeft = null;
let daughterNucleusRight = null;
let daughterCellLeftGroup = null;
let daughterCellRightGroup = null;
let daughterMembraneLeftMat = null;
let daughterMembraneRightMat = null;
let daughterRimLeftMesh = null;
let daughterRimRightMesh = null;
let intercellularBridgeMesh = null;
let bridgeMaterial = null;
let cutawayRimMesh = null;
let ghostCellSilhouetteMesh = null;
let cytoskeletonMaterial = null;
let cameraTransition = null;

// Shader para la Membrana Plasmática con translucidez, fresnel, corte sagital y surco de escisión de mitosis
function createMembraneShader() {
  return new THREE.ShaderMaterial({
    uniforms: {
      uTime: { value: 0 },
      uColor: { value: new THREE.Color(0x0284c7) },
      uInnerColor: { value: new THREE.Color(0x032142) },
      uGlowColor: { value: new THREE.Color(0x70d6ff) },
      uCrossSection: { value: 1.0 },
      uOpacity: { value: 0.55 },
      uElongation: { value: 1.0 },
      uCleavagePinch: { value: 0.0 }
    },
    vertexShader: `
      varying vec3 vNormal;
      varying vec3 vViewPos;
      varying vec3 vWorldPos;
      uniform float uTime;
      uniform float uElongation;
      uniform float uCleavagePinch;
      ${noiseGLSL}
      void main() {
        vec3 pos = position;
        // Elongación en eje de división X
        pos.x *= uElongation;

        // Estrangulamiento gaussiano del surco de escisión ecuatorial (x = 0)
        float pinch = uCleavagePinch * exp(- (pos.x * pos.x) / 0.55);
        pos.yz *= (1.0 - pinch);

        // Ondulación orgánica confocal
        float noise = snoise(pos * 1.6 + vec3(uTime * 0.1)) * 0.055;
        vec3 displaced = pos + normal * noise;

        vec4 mvPosition = modelViewMatrix * vec4(displaced, 1.0);
        vViewPos = -mvPosition.xyz;
        vWorldPos = (modelMatrix * vec4(displaced, 1.0)).xyz;
        vNormal = normalize(normalMatrix * normal);
        gl_Position = projectionMatrix * mvPosition;
      }
    `,
    fragmentShader: `
      uniform vec3 uColor;
      uniform vec3 uInnerColor;
      uniform vec3 uGlowColor;
      uniform float uCrossSection;
      uniform float uOpacity;
      uniform float uTime;
      varying vec3 vNormal;
      varying vec3 vViewPos;
      varying vec3 vWorldPos;
      ${noiseGLSL}
      void main() {
        // Corte Sagital / Cross Section con apertura limpia
        if (uCrossSection > 0.5 && vWorldPos.z > 0.08) {
          discard;
        }

        vec3 n = normalize(vNormal);
        vec3 v = normalize(vViewPos);
        bool isFront = gl_FrontFacing;

        float fresnel = pow(1.0 - abs(dot(n, v)), 2.0);
        float bioNoise = snoise(vWorldPos * 3.5 + vec3(uTime * 0.06)) * 0.15;
        float intensity = clamp(fresnel + bioNoise, 0.0, 1.0);

        vec3 baseCol = isFront ? uColor : uInnerColor;
        vec3 col = mix(baseCol * 0.7, uGlowColor, intensity);

        // Resaltar borde de corte con bioluminiscencia
        if (uCrossSection > 0.5 && abs(vWorldPos.z - 0.08) < 0.045) {
          col += vec3(0.3, 0.7, 1.0) * 0.85;
        }

        float alpha = clamp((fresnel * 0.75 + 0.22) * uOpacity, 0.0, 0.96);
        gl_FragColor = vec4(col, alpha);
      }
    `,
    transparent: true,
    side: THREE.DoubleSide,
    depthWrite: false
  });
}

// Shader para el Núcleo Celular con Doble Envoltura y Poros Nucleares
function createNucleusShader() {
  return new THREE.ShaderMaterial({
    uniforms: {
      uTime: { value: 0 },
      uDeepBlue: { value: new THREE.Color(0x0f2b5c) },
      uLightBlue: { value: new THREE.Color(0x38bdf8) },
      uCrossSection: { value: 1.0 },
      uPores: { value: 1.0 }
    },
    vertexShader: `
      varying vec3 vNormal;
      varying vec3 vViewPos;
      varying vec3 vWorldPos;
      uniform float uTime;
      ${noiseGLSL}
      void main() {
        vNormal = normalize(normalMatrix * normal);
        float n = snoise(position * 2.8 + vec3(uTime * 0.08)) * 0.035;
        vec3 displaced = position + normal * n;
        vec4 mvPosition = modelViewMatrix * vec4(displaced, 1.0);
        vViewPos = -mvPosition.xyz;
        vWorldPos = (modelMatrix * vec4(displaced, 1.0)).xyz;
        gl_Position = projectionMatrix * mvPosition;
      }
    `,
    fragmentShader: `
      uniform vec3 uDeepBlue;
      uniform vec3 uLightBlue;
      uniform float uCrossSection;
      uniform float uPores;
      uniform float uTime;
      varying vec3 vNormal;
      varying vec3 vViewPos;
      varying vec3 vWorldPos;
      ${noiseGLSL}
      void main() {
        if (uCrossSection > 0.5 && vWorldPos.z > -0.02) {
          discard;
        }

        vec3 n = normalize(vNormal);
        vec3 v = normalize(vViewPos);
        float chromatin = snoise(vWorldPos * 6.0) * 0.35 + 0.65;
        
        // Complejos de Poro Nuclear (NPC) octagonales de ~100 nm
        float poreFactor = 1.0;
        if (uPores > 0.5) {
          float pGrid = sin(vWorldPos.x * 26.0) * sin(vWorldPos.y * 26.0) * sin(vWorldPos.z * 26.0);
          if (pGrid > 0.68) {
            poreFactor = 0.25; // Canal central del poro
          } else if (pGrid > 0.55) {
            poreFactor = 1.45; // Anillo octagonal fluorescente
          }
        }

        float depth = pow(max(0.0, dot(n, v)), 1.4);
        vec3 col = mix(uLightBlue * poreFactor, uDeepBlue, depth * chromatin);

        // Resalte de corte de la doble envoltura
        if (uCrossSection > 0.5 && abs(vWorldPos.z - (-0.02)) < 0.035) {
          col = vec3(0.35, 0.85, 1.0);
        }

        float edgeAlpha = smoothstep(0.0, 0.15, dot(n, v));
        gl_FragColor = vec4(col, 0.92 * edgeAlpha);
      }
    `,
    transparent: true,
    side: THREE.DoubleSide
  });
}

// Textura procedural ultra-detallada para el Nucléolo (núcleo granular cálido/bronce idéntico a la imagen de referencia)
function createNucleolusTexture() {
  const canvas = document.createElement('canvas');
  canvas.width = 512;
  canvas.height = 512;
  const ctx = canvas.getContext('2d');

  // Gradiente base cálido terracota / bronce / ámbar
  const grad = ctx.createRadialGradient(256, 256, 25, 256, 256, 255);
  grad.addColorStop(0, '#fbbf24');
  grad.addColorStop(0.25, '#f59e0b');
  grad.addColorStop(0.55, '#c25e2e');
  grad.addColorStop(0.8, '#9a3412');
  grad.addColorStop(1, '#5c1d06');
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, 512, 512);

  // Micro-gránulos de ribonucleoproteínas (Componente Granular del nucléolo en tonos dorados/bronce)
  for (let i = 0; i < 4800; i++) {
    const x = Math.random() * 512;
    const y = Math.random() * 512;
    const r = Math.random() * 2.4 + 0.6;
    const p = Math.random();
    if (p > 0.72) ctx.fillStyle = 'rgba(254, 240, 138, 0.85)'; // Brillo dorado
    else if (p > 0.40) ctx.fillStyle = 'rgba(245, 158, 11, 0.75)'; // Ámbar medio
    else if (p > 0.20) ctx.fillStyle = 'rgba(194, 94, 46, 0.65)'; // Terracota
    else ctx.fillStyle = 'rgba(92, 29, 6, 0.60)'; // Sombra de poro
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.fill();
  }

  // Centros fibrilares (lagunas porosas características)
  for (let j = 0; j < 45; j++) {
    const cx = 80 + Math.random() * 352;
    const cy = 80 + Math.random() * 352;
    const rad = 5 + Math.random() * 14;
    const spotGrad = ctx.createRadialGradient(cx, cy, 1, cx, cy, rad);
    spotGrad.addColorStop(0, 'rgba(67, 20, 7, 0.9)');
    spotGrad.addColorStop(0.5, 'rgba(180, 83, 9, 0.45)');
    spotGrad.addColorStop(1, 'rgba(180, 83, 9, 0)');
    ctx.fillStyle = spotGrad;
    ctx.beginPath();
    ctx.arc(cx, cy, rad, 0, Math.PI * 2);
    ctx.fill();
  }

  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.RepeatWrapping;
  return texture;
}

// Textura bioluminiscente para centrómeros y focos
function createGlowDotTexture() {
  const canvas = document.createElement('canvas');
  canvas.width = 64;
  canvas.height = 64;
  const ctx = canvas.getContext('2d');
  const grad = ctx.createRadialGradient(32, 32, 2, 32, 32, 30);
  grad.addColorStop(0, '#ffffff');
  grad.addColorStop(0.3, '#38bdf8');
  grad.addColorStop(0.7, 'rgba(14, 165, 233, 0.45)');
  grad.addColorStop(1, 'rgba(0, 0, 0, 0)');
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, 64, 64);
  return new THREE.CanvasTexture(canvas);
}

// Inicialización de la Escena 3D
function initScene() {
  const container = canvasContainer.value;
  if (!container) return;

  const width = container.clientWidth || 800;
  const height = container.clientHeight || 560;

  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x06111e);
  scene.fog = new THREE.FogExp2(0x06111e, 0.045);

  camera = new THREE.PerspectiveCamera(40, width / height, 0.1, 1000);
  camera.position.set(0, 0.3, 8.2);

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
  renderer.setSize(width, height);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.35;
  container.appendChild(renderer.domElement);

  // OrbitControls suaves con damping
  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.minDistance = 1.0;
  controls.maxDistance = 14.0;
  controls.autoRotate = false;
  controls.target.set(0, 0, 0);

  // Iluminación biológica de tres puntos (Studio + Rim + Core glow)
  const ambient = new THREE.AmbientLight(0x0c4a6e, 1.5);
  scene.add(ambient);

  // Luz principal (Key Light) desde arriba derecha
  const keyLight = new THREE.DirectionalLight(0xe0f2fe, 2.6);
  keyLight.position.set(6, 9, 7);
  scene.add(keyLight);

  // Luz de relleno fría (Fill Light) desde abajo izquierda
  const fillLight = new THREE.DirectionalLight(0x0369a1, 1.8);
  fillLight.position.set(-7, -4, -4);
  scene.add(fillLight);

  // Luz de contraluz / Rim Light para silueta traslúcida
  const rimLight = new THREE.DirectionalLight(0x38bdf8, 2.4);
  rimLight.position.set(0, -6, -8);
  scene.add(rimLight);

  // Nube de partículas de fondo microscópico confocal
  const bgGeo = new THREE.BufferGeometry();
  const bgPos = new Float32Array(300 * 3);
  for (let i = 0; i < 300 * 3; i += 3) {
    bgPos[i] = (Math.random() - 0.5) * 26;
    bgPos[i + 1] = (Math.random() - 0.5) * 26;
    bgPos[i + 2] = (Math.random() - 0.5) * 16 - 2;
  }
  bgGeo.setAttribute('position', new THREE.BufferAttribute(bgPos, 3));
  const bgMat = new THREE.PointsMaterial({
    color: 0x0284c7,
    size: 0.045,
    transparent: true,
    opacity: 0.35,
    blending: THREE.AdditiveBlending
  });
  scene.add(new THREE.Points(bgGeo, bgMat));

  // Grupo Maestro de la Célula
  mainCellGroup = new THREE.Group();
  scene.add(mainCellGroup);

  // Construcción de todos los orgánulos
  buildAllOrganelles();

  // Actualizar estado visual inicial
  update3DState();

  // Bucle de animación 60fps
  animate();
}

// Constructor maestro de los 15 orgánulos
function buildAllOrganelles() {
  const glowTex = createGlowDotTexture();

  // 1. MEMBRANA PLASMÁTICA CON MICROVELLOSIDADES & CORTE SAGITAL
  organelleGroups.membrane = new THREE.Group();
  membraneMaterial = createMembraneShader();
  const memGeo = new THREE.SphereGeometry(2.32, 80, 80);
  const memMesh = new THREE.Mesh(memGeo, membraneMaterial);
  organelleGroups.membrane.add(memMesh);

  // Microvellosidades / Espículas Receptoras superficiales en la cara externa no cortada
  const microvilliCount = 240;
  const viliMat = new THREE.MeshStandardMaterial({
    color: 0x7dd3fc,
    roughness: 0.3,
    metalness: 0.1,
    transparent: true,
    opacity: 0.85
  });
  const viliGeo = new THREE.ConeGeometry(0.018, 0.15, 5);
  viliGeo.translate(0, 0.075, 0);

  for (let i = 0; i < microvilliCount; i++) {
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.acos(2 * Math.random() - 1);
    const zDir = Math.cos(phi);

    // Solo colocamos microvellosidades en el hemisferio no cortado
    if (zDir < 0.08) {
      const viliMesh = new THREE.Mesh(viliGeo, viliMat);
      const x = Math.sin(phi) * Math.cos(theta);
      const y = Math.sin(phi) * Math.sin(theta);
      const z = zDir;
      const normal = new THREE.Vector3(x, y, z).normalize();
      
      viliMesh.position.copy(normal.clone().multiplyScalar(2.31));
      viliMesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), normal);
      organelleGroups.membrane.add(viliMesh);
    }
  }

  // Anillo de corte sagital / lipid bilayer rim (resalta el grosor de la bicapa)
  const rimGeo = new THREE.TorusGeometry(2.32, 0.022, 16, 96);
  const rimMat = new THREE.MeshBasicMaterial({
    color: 0x38bdf8,
    transparent: true,
    opacity: 0.8
  });
  cutawayRimMesh = new THREE.Mesh(rimGeo, rimMat);
  cutawayRimMesh.position.set(0, 0, 0.08);
  organelleGroups.membrane.add(cutawayRimMesh);

  // 1.1 ANILLO CONTRÁCTIL Y PUENTE INTERCELULAR (Surco de escisión de citocinesis)
  const ringGeo = new THREE.TorusGeometry(1.68, 0.046, 16, 80);
  const ringMat = new THREE.MeshStandardMaterial({
    color: 0xf43f5e,
    emissive: 0xe11d48,
    emissiveIntensity: 1.45,
    roughness: 0.25
  });
  contractileRingMesh = new THREE.Mesh(ringGeo, ringMat);
  contractileRingMesh.rotation.y = Math.PI / 2; // Orientado en el plano ecuatorial YZ (x = 0)
  contractileRingMesh.visible = false;
  mainCellGroup.add(contractileRingMesh);

  // Puente lipídico intercelular / tallo de citocinesis (conecta ambas células antes de la abscisión)
  const bridgeGeo = new THREE.CylinderGeometry(0.35, 0.35, 1.4, 32, 8, true);
  bridgeGeo.rotateZ(Math.PI / 2);
  bridgeMaterial = createMembraneShader();
  intercellularBridgeMesh = new THREE.Mesh(bridgeGeo, bridgeMaterial);
  intercellularBridgeMesh.visible = false;
  mainCellGroup.add(intercellularBridgeMesh);

  // 1.2 CÉLULAS HIJAS INDEPENDIENTES PARA TELOFASE Y CITOCINESIS (División celular real)
  const dMemGeo = new THREE.SphereGeometry(1.65, 64, 64);
  const dRimGeo = new THREE.TorusGeometry(1.65, 0.02, 16, 80);

  // Material y texturas de los núcleos hijos
  const dNucMat = new THREE.MeshStandardMaterial({
    color: 0x1d4ed8,
    emissive: 0x0f2b5c,
    emissiveIntensity: 0.85,
    roughness: 0.35,
    transparent: true,
    opacity: 0.85
  });
  const dNucGeo = new THREE.SphereGeometry(0.70, 32, 32);

  const dNuTex = createNucleolusTexture();
  const dNuMat = new THREE.MeshStandardMaterial({
    map: dNuTex,
    bumpMap: dNuTex,
    bumpScale: 0.04,
    roughness: 0.35,
    metalness: 0.2,
    emissive: 0xc25e2e,
    emissiveIntensity: 0.52
  });
  const dNuGeo = new THREE.SphereGeometry(0.32, 28, 28);

  // A) CÉLULA HIJA IZQUIERDA
  daughterCellLeftGroup = new THREE.Group();
  daughterMembraneLeftMat = createMembraneShader();
  const dMemLeftMesh = new THREE.Mesh(dMemGeo, daughterMembraneLeftMat);
  daughterCellLeftGroup.add(dMemLeftMesh);

  daughterRimLeftMesh = new THREE.Mesh(dRimGeo, rimMat.clone());
  daughterRimLeftMesh.position.set(0, 0, 0.08);
  daughterCellLeftGroup.add(daughterRimLeftMesh);

  // Microvellosidades de la célula hija izquierda
  for (let i = 0; i < 90; i++) {
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.acos(2 * Math.random() - 1);
    const zDir = Math.cos(phi);
    if (zDir < 0.08) {
      const vMesh = new THREE.Mesh(viliGeo, viliMat);
      const x = Math.sin(phi) * Math.cos(theta);
      const y = Math.sin(phi) * Math.sin(theta);
      const normal = new THREE.Vector3(x, y, zDir).normalize();
      vMesh.position.copy(normal.clone().multiplyScalar(1.64));
      vMesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), normal);
      daughterCellLeftGroup.add(vMesh);
    }
  }

  // Núcleo hijo izquierdo
  daughterNucleusLeft = new THREE.Group();
  const leftNucMesh = new THREE.Mesh(dNucGeo, dNucMat);
  const leftNu = new THREE.Mesh(dNuGeo, dNuMat);
  leftNu.position.set(0, 0, -0.05);
  daughterNucleusLeft.add(leftNucMesh);
  daughterNucleusLeft.add(leftNu);
  const leftLight = new THREE.PointLight(0xf59e0b, 1.2, 2.5);
  leftLight.position.set(0, 0, 0.1);
  daughterNucleusLeft.add(leftLight);
  daughterCellLeftGroup.add(daughterNucleusLeft);

  daughterCellLeftGroup.position.set(-1.42, 0, 0);
  daughterCellLeftGroup.visible = false;
  mainCellGroup.add(daughterCellLeftGroup);

  // B) CÉLULA HIJA DERECHA
  daughterCellRightGroup = new THREE.Group();
  daughterMembraneRightMat = createMembraneShader();
  const dMemRightMesh = new THREE.Mesh(dMemGeo, daughterMembraneRightMat);
  daughterCellRightGroup.add(dMemRightMesh);

  daughterRimRightMesh = new THREE.Mesh(dRimGeo, rimMat.clone());
  daughterRimRightMesh.position.set(0, 0, 0.08);
  daughterCellRightGroup.add(daughterRimRightMesh);

  // Microvellosidades de la célula hija derecha
  for (let i = 0; i < 90; i++) {
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.acos(2 * Math.random() - 1);
    const zDir = Math.cos(phi);
    if (zDir < 0.08) {
      const vMesh = new THREE.Mesh(viliGeo, viliMat);
      const x = Math.sin(phi) * Math.cos(theta);
      const y = Math.sin(phi) * Math.sin(theta);
      const normal = new THREE.Vector3(x, y, zDir).normalize();
      vMesh.position.copy(normal.clone().multiplyScalar(1.64));
      vMesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), normal);
      daughterCellRightGroup.add(vMesh);
    }
  }

  // Núcleo hijo derecho
  daughterNucleusRight = new THREE.Group();
  const rightNucMesh = new THREE.Mesh(dNucGeo, dNucMat.clone());
  const rightNu = new THREE.Mesh(dNuGeo, dNuMat.clone());
  rightNu.position.set(0, 0, -0.05);
  daughterNucleusRight.add(rightNucMesh);
  daughterNucleusRight.add(rightNu);
  const rightLight = new THREE.PointLight(0xf59e0b, 1.2, 2.5);
  rightLight.position.set(0, 0, 0.1);
  daughterNucleusRight.add(rightLight);
  daughterCellRightGroup.add(daughterNucleusRight);

  daughterCellRightGroup.position.set(1.42, 0, 0);
  daughterCellRightGroup.visible = false;
  mainCellGroup.add(daughterCellRightGroup);

  mainCellGroup.add(organelleGroups.membrane);

  // 2. NÚCLEO (Matriz nuclear, cromatina laxa y focos de replicación)
  organelleGroups.nucleus = new THREE.Group();
  nucleusMaterial = createNucleusShader();
  const nucGeo = new THREE.SphereGeometry(0.98, 54, 54);
  const nucMesh = new THREE.Mesh(nucGeo, nucleusMaterial);
  organelleGroups.nucleus.add(nucMesh);

  // Red de cromatina laxa interna (filamentos sutiles de ADN en torno al nucléolo)
  const chromatinPoints = [];
  for (let k = 0; k < 75; k++) {
    const a1 = Math.random() * Math.PI * 2;
    const a2 = Math.random() * Math.PI * 2;
    const r1 = 0.48 + Math.random() * 0.08;
    const r2 = 0.82 + Math.random() * 0.14;
    chromatinPoints.push(new THREE.Vector3(
      0.02 + Math.cos(a1) * r1,
      0.02 + Math.sin(a1) * r1,
      -0.08 + (Math.random() - 0.5) * 0.2
    ));
    chromatinPoints.push(new THREE.Vector3(
      Math.cos(a2) * r2,
      Math.sin(a2) * r2,
      (Math.random() - 0.5) * 0.35
    ));
  }
  const chromatinGeo = new THREE.BufferGeometry().setFromPoints(chromatinPoints);
  const chromatinMat = new THREE.LineBasicMaterial({
    color: 0x60a5fa,
    transparent: true,
    opacity: 0.5,
    blending: THREE.AdditiveBlending
  });
  organelleGroups.nucleus.add(new THREE.LineSegments(chromatinGeo, chromatinMat));

  // Focos de replicación para fase S (Fluorescencia EdU/PCNA)
  const fociCount = 420;
  const fociGeo = new THREE.BufferGeometry();
  const fociPos = new Float32Array(fociCount * 3);
  for (let i = 0; i < fociCount * 3; i += 3) {
    const r = 0.28 + Math.random() * 0.62;
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.acos(2 * Math.random() - 1);
    fociPos[i] = r * Math.sin(phi) * Math.cos(theta);
    fociPos[i + 1] = r * Math.sin(phi) * Math.sin(theta);
    fociPos[i + 2] = r * Math.cos(phi) * 0.7;
  }
  fociGeo.setAttribute('position', new THREE.BufferAttribute(fociPos, 3));
  const fociMat = new THREE.PointsMaterial({
    color: 0xa3e635,
    size: 0.075,
    map: glowTex,
    transparent: true,
    opacity: 0.95,
    blending: THREE.AdditiveBlending
  });
  replicationFociPoints = new THREE.Points(fociGeo, fociMat);
  replicationFociPoints.visible = false;
  organelleGroups.nucleus.add(replicationFociPoints);
  mainCellGroup.add(organelleGroups.nucleus);

  // 2.1 ENVOLTURA NUCLEAR & COMPLEJOS DE PORO NUCLEAR (NPC) INDEPENDIENTES
  organelleGroups.envelope = new THREE.Group();
  const envMat = new THREE.ShaderMaterial({
    uniforms: {
      uCrossSection: { value: 1.0 },
      uColor: { value: new THREE.Color(0x2563eb) }
    },
    vertexShader: `
      varying vec3 vWorldPos;
      void main() {
        vWorldPos = (modelMatrix * vec4(position, 1.0)).xyz;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      uniform float uCrossSection;
      uniform vec3 uColor;
      varying vec3 vWorldPos;
      void main() {
        if (uCrossSection > 0.5 && vWorldPos.z > -0.02) discard;
        gl_FragColor = vec4(uColor, 0.45);
      }
    `,
    transparent: true,
    wireframe: true
  });
  const envGeo = new THREE.SphereGeometry(1.02, 42, 42);
  const envMesh = new THREE.Mesh(envGeo, envMat);
  organelleGroups.envelope.add(envMesh);

  // 48 Anillos de Poros Nucleares NPC fosforescentes
  const npcMat = new THREE.MeshStandardMaterial({
    color: 0x38bdf8,
    emissive: 0x0284c7,
    emissiveIntensity: 0.95,
    roughness: 0.25
  });
  const npcGeo = new THREE.TorusGeometry(0.038, 0.010, 8, 16);
  for (let n = 0; n < 48; n++) {
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.acos(2 * Math.random() - 1);
    const zDir = Math.cos(phi);
    if (zDir < 0.04) {
      const npcMesh = new THREE.Mesh(npcGeo, npcMat);
      const nx = Math.sin(phi) * Math.cos(theta);
      const ny = Math.sin(phi) * Math.sin(theta);
      const norm = new THREE.Vector3(nx, ny, zDir).normalize();
      npcMesh.position.copy(norm.clone().multiplyScalar(1.02));
      npcMesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 0, 1), norm);
      organelleGroups.envelope.add(npcMesh);
    }
  }
  mainCellGroup.add(organelleGroups.envelope);

  // 3. NUCLÉOLO INDEPENDIENTE (Subcompartimento de ARNr con luz cálida y textura HD)
  organelleGroups.nucleolus = new THREE.Group();
  const nuTex = createNucleolusTexture();
  const nuGeo = new THREE.SphereGeometry(0.48, 48, 48);
  const nuMat = new THREE.MeshStandardMaterial({
    map: nuTex,
    bumpMap: nuTex,
    bumpScale: 0.06,
    roughness: 0.30,
    metalness: 0.20,
    emissive: 0xc25e2e,
    emissiveIntensity: 0.65
  });
  const nucleolusMesh = new THREE.Mesh(nuGeo, nuMat);
  nucleolusMesh.position.set(0.02, 0.02, -0.08);
  organelleGroups.nucleolus.add(nucleolusMesh);

  // Luz biológica puntual cálida que emana del nucléolo iluminando el nucleoplasma
  const nucleolusLight = new THREE.PointLight(0xf59e0b, 2.8, 4.0);
  nucleolusLight.position.set(0.02, 0.02, 0.15);
  organelleGroups.nucleolus.add(nucleolusLight);
  mainCellGroup.add(organelleGroups.nucleolus);

  // 3.1 CITOSOL (Matriz Celular Coloidal)
  organelleGroups.cytosol = new THREE.Group();
  buildColloidalCytosol(organelleGroups.cytosol);
  organelleGroups.cytosol.visible = false;
  mainCellGroup.add(organelleGroups.cytosol);

  // 3.2 SILUETA HOLOGRÁFICA FANTASMA (Referencia espacial visible al aislar cualquier orgánulo)
  const ghostGeo = new THREE.SphereGeometry(2.32, 48, 48);
  const ghostMat = new THREE.MeshBasicMaterial({
    color: 0x38bdf8,
    wireframe: true,
    transparent: true,
    opacity: 0.10
  });
  ghostCellSilhouetteMesh = new THREE.Mesh(ghostGeo, ghostMat);
  ghostCellSilhouetteMesh.visible = false;
  mainCellGroup.add(ghostCellSilhouetteMesh);

  // 4. CROMOSOMAS EN X (Para Mitosis)
  chromosomesGroup = new THREE.Group();
  chromosomesGroup.visible = false;
  buildChromosomesModel(chromosomesGroup);
  mainCellGroup.add(chromosomesGroup);

  // 5. MITOCONDRIAS ULTRA-PRO (Cápsula translúcida + Crestas internas en estantes plegados)
  organelleGroups.mitochondria = new THREE.Group();
  buildDetailedMitochondriaCollection(organelleGroups.mitochondria);
  mainCellGroup.add(organelleGroups.mitochondria);

  // 6. RETÍCULO ENDOPLASMÁTICO RUGOSO (RER) — COLLAR CONCÉNTRICO DE LÁMINAS ONDULADAS
  organelleGroups.rer = new THREE.Group();
  buildUndulatingRoughEndoplasmicReticulum(organelleGroups.rer);
  mainCellGroup.add(organelleGroups.rer);

  // 7. RETÍCULO ENDOPLASMÁTICO LISO (REL) — RED TUBULAR RAMIFICADA
  organelleGroups.rel = new THREE.Group();
  buildSmoothEndoplasmicReticulum(organelleGroups.rel);
  mainCellGroup.add(organelleGroups.rel);

  // 8. APARATO DE GOLGI & VESÍCULAS DE SECRECIÓN
  organelleGroups.golgi = new THREE.Group();
  buildGolgiApparatus(organelleGroups.golgi);
  mainCellGroup.add(organelleGroups.golgi);

  // 9. CENTROSOMA CON CENTRÍOLOS (Cilindros de 9 tripletes de microtúbulos + satélite naranja)
  organelleGroups.centrosome = new THREE.Group();
  buildDetailedCentrosomes(organelleGroups.centrosome, glowTex);
  mainCellGroup.add(organelleGroups.centrosome);

  // 10. HUSO MITÓTICO (Microtúbulos polares y cinetocóricos para M)
  mitoticSpindleLines = new THREE.Group();
  buildMitoticSpindle(mitoticSpindleLines);
  mitoticSpindleLines.visible = false;
  mainCellGroup.add(mitoticSpindleLines);

  // 11. LISOSOMAS (Esferas ácidas con contenido granular denso ámbar)
  organelleGroups.lysosome = new THREE.Group();
  buildVesicleCluster(organelleGroups.lysosome, 14, 0.10, 0xf59e0b, 0.88);
  mainCellGroup.add(organelleGroups.lysosome);

  // 12. PEROXISOMAS (Esferas verde esmeralda cristalino con núcleo de catalasa)
  organelleGroups.peroxisome = new THREE.Group();
  buildVesicleCluster(organelleGroups.peroxisome, 12, 0.085, 0x10b981, 0.92);
  mainCellGroup.add(organelleGroups.peroxisome);

  // 13. VACUOLAS ANIMALES (Esferas acuosas translúcidas)
  organelleGroups.vacuole = new THREE.Group();
  buildVesicleCluster(organelleGroups.vacuole, 7, 0.14, 0x38bdf8, 0.45);
  mainCellGroup.add(organelleGroups.vacuole);

  // 14. RIBOSOMAS LIBRES & VESÍCULAS DE TRANSPORTE ÁMBAR (Gotas cálidas que contrastan en azul)
  organelleGroups.ribosome = new THREE.Group();
  buildFreeRibosomesAndGranules(organelleGroups.ribosome);
  mainCellGroup.add(organelleGroups.ribosome);

  // 15. CITOESQUELETO (Malla 3D densa que atraviesa el citosol conectando orgánulos)
  organelleGroups.cytoskeleton = new THREE.Group();
  buildCytoskeletalMesh(organelleGroups.cytoskeleton);
  mainCellGroup.add(organelleGroups.cytoskeleton);
}

// Fabricador de Citosol / Matriz Citoplásmica Coloidal
function buildColloidalCytosol(parentGroup) {
  const cytGeo = new THREE.SphereGeometry(2.28, 48, 48);
  const cytMat = new THREE.MeshStandardMaterial({
    color: 0x0284c7,
    roughness: 0.25,
    metalness: 0.08,
    transparent: true,
    opacity: 0.28,
    side: THREE.DoubleSide,
    depthWrite: false
  });
  const cytMesh = new THREE.Mesh(cytGeo, cytMat);
  parentGroup.add(cytMesh);

  // Micropartículas coloidales en suspensión citosólica (enzimas, sustratos y ATP)
  const pCount = 650;
  const pGeo = new THREE.BufferGeometry();
  const pPos = new Float32Array(pCount * 3);
  for (let i = 0; i < pCount * 3; i += 3) {
    const r = 0.98 + Math.random() * 1.25;
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.acos(2 * Math.random() - 1);
    pPos[i] = r * Math.sin(phi) * Math.cos(theta);
    pPos[i + 1] = r * Math.sin(phi) * Math.sin(theta);
    pPos[i + 2] = r * Math.cos(phi) * 0.85;
  }
  pGeo.setAttribute('position', new THREE.BufferAttribute(pPos, 3));
  const pMat = new THREE.PointsMaterial({
    color: 0x38bdf8,
    size: 0.035,
    transparent: true,
    opacity: 0.85,
    blending: THREE.AdditiveBlending
  });
  parentGroup.add(new THREE.Points(pGeo, pMat));
}

// Fabricador de Mitocondrias Ultra-Pro (Cápsula translúcida + Crestas internas visibles)
function buildDetailedMitochondriaCollection(parentGroup) {
  // Material de la membrana externa (cápsula translúcida cian-azul oscuro)
  const outerMat = new THREE.MeshStandardMaterial({
    color: 0x062840,
    roughness: 0.18,
    metalness: 0.1,
    transparent: true,
    opacity: 0.58,
    side: THREE.DoubleSide,
    depthWrite: false
  });

  // Material de las crestas mitocondriales internas (anillos y placas onduladas ámbar/naranja bioluminiscentes)
  const cristaMat = new THREE.MeshStandardMaterial({
    color: 0xf97316,
    emissive: 0xea580c,
    emissiveIntensity: 1.15,
    roughness: 0.25,
    side: THREE.DoubleSide
  });

  // Posiciones biológicas armoniosas (4 mitocondrias grandes en primer plano del corte sagital como en la referencia)
  const mitoLayouts = [
    // Mitocondrias prominentes en el corte anterior (visibles inmediatamente como en la foto)
    { pos: [-1.45, -0.92, 0.08], rot: [0.35, 0.55, 0.65], scale: 1.25 },
    { pos: [1.42, -0.38, 0.08], rot: [-0.45, 0.75, -0.32], scale: 1.28 },
    { pos: [-1.62, 0.42, 0.06], rot: [0.55, -0.45, 0.85], scale: 1.2 },
    { pos: [0.32, -1.62, 0.08], rot: [-0.25, 0.65, 1.15], scale: 1.25 },
    // Mitocondrias distribuidas en el citosol posterior y ecuatorial
    { pos: [-1.3, 1.2, -0.5], rot: [0.5, 0.2, -0.6], scale: 1.05 },
    { pos: [1.5, -1.1, -0.4], rot: [-0.3, 0.9, 0.4], scale: 1.1 },
    { pos: [-0.9, -1.4, -0.6], rot: [0.8, -0.2, 0.3], scale: 1.05 },
    { pos: [0.9, 1.4, -0.5], rot: [-0.6, 0.4, -0.8], scale: 1.1 },
    { pos: [-1.75, -0.2, -0.7], rot: [0.4, 0.5, -0.2], scale: 1.0 },
    { pos: [1.65, 0.2, -0.7], rot: [-0.5, 0.3, 0.7], scale: 1.0 },
    { pos: [0.0, 1.7, -0.6], rot: [0.1, 0.9, -0.4], scale: 1.05 },
    { pos: [-0.6, 1.5, -0.8], rot: [0.7, -0.4, 0.2], scale: 1.0 },
    { pos: [0.7, -1.6, -0.7], rot: [-0.4, 0.6, 0.8], scale: 1.05 },
    { pos: [-0.3, -1.2, -0.8], rot: [0.3, -0.5, 0.6], scale: 1.0 }
  ];

  for (let i = 14; i < 28; i++) {
    const angle = (i / 14) * Math.PI * 2;
    const r = 1.35 + (i % 3) * 0.25;
    mitoLayouts.push({
      pos: [Math.cos(angle) * r, Math.sin(angle) * r, -0.4 - (i % 4) * 0.25],
      rot: [Math.random() * Math.PI, Math.random() * Math.PI, Math.random() * Math.PI],
      scale: 0.95 + Math.random() * 0.2
    });
  }

  mitoLayouts.forEach((item, index) => {
    const singleMito = new THREE.Group();

    // 1. Cápsula exterior translúcida (0.13 radio x 0.36 altura)
    const bodyGeo = new THREE.CapsuleGeometry(0.13, 0.36, 16, 24);
    const bodyMesh = new THREE.Mesh(bodyGeo, outerMat);
    singleMito.add(bodyMesh);

    // 2. Sistema de crestas mitocondriales transversales plegadas (estantes internos)
    const cristaCount = 9;
    for (let c = 0; c < cristaCount; c++) {
      const yOffset = ((c / (cristaCount - 1)) - 0.5) * 0.32;
      const widthFactor = 1.0 - Math.pow(yOffset / 0.22, 2) * 0.32;
      
      const discGeo = new THREE.CylinderGeometry(0.106 * Math.max(0.4, widthFactor), 0.106 * Math.max(0.4, widthFactor), 0.016, 16);
      const discMesh = new THREE.Mesh(discGeo, cristaMat);
      discMesh.position.set((c % 2 === 0 ? 0.014 : -0.014), yOffset, 0);
      discMesh.rotation.set(0.12 * (c % 2 === 0 ? 1 : -1), 0, 0.16);
      singleMito.add(discMesh);
    }

    // 3. Matriz mitocondrial central con resplandor cálido
    const matrixLight = new THREE.PointLight(0xf97316, 0.45, 0.85);
    singleMito.add(matrixLight);

    singleMito.position.set(item.pos[0], item.pos[1], item.pos[2]);
    singleMito.rotation.set(item.rot[0], item.rot[1], item.rot[2]);
    singleMito.scale.set(item.scale, item.scale, item.scale);
    singleMito.userData = { defaultPos: singleMito.position.clone(), mitoIndex: index };

    parentGroup.add(singleMito);
  });
}

// Fabricador de Retículo Endoplasmático Rugoso (RER)
// Collar concéntrico de 6 láminas onduladas con pliegues orgánicos y miles de ribosomas adheridos
function buildUndulatingRoughEndoplasmicReticulum(parentGroup) {
  const rerMat = new THREE.MeshStandardMaterial({
    color: 0x0284c7,
    roughness: 0.30,
    metalness: 0.1,
    side: THREE.DoubleSide,
    transparent: true,
    opacity: 0.90
  });

  const rerRibosomesGroup = new THREE.Group();

  const layers = 6;
  const riboPosList = [];

  for (let l = 0; l < layers; l++) {
    const baseR = 1.15 + l * 0.15;
    const height = 0.82 - l * 0.07;
    const uSegments = 54;
    const vSegments = 18;
    
    const sheetGeo = new THREE.BufferGeometry();
    const positions = [];
    const indices = [];

    // Envolver alrededor del núcleo en forma de collar amplio
    const angleStart = -0.15 * Math.PI;
    const angleEnd = 1.95 * Math.PI;

    for (let v = 0; v <= vSegments; v++) {
      const vNorm = v / vSegments;
      const y = (vNorm - 0.5) * height;

      for (let u = 0; u <= uSegments; u++) {
        const uNorm = u / uSegments;
        const theta = angleStart + uNorm * (angleEnd - angleStart);

        // Ondulación orgánica del pliegue (convoluciones del RER como en la imagen)
        const wave = Math.sin(theta * 6.0 + l * 1.35) * (0.12 + l * 0.02) * Math.cos(vNorm * Math.PI)
                   + Math.cos(theta * 10.0) * 0.05
                   + Math.sin(theta * 3.0) * 0.06;
        const r = baseR + wave;

        const x = r * Math.cos(theta);
        // Desplazamiento hacia atrás en el corte frontal para no ocluir el núcleo
        let z = r * Math.sin(theta) * 0.72;
        if (z > 0.06) z = 0.06 - Math.pow(z - 0.06, 1.4) * 0.5;

        positions.push(x, y, z);

        // Sembrar ribosomas sobre la superficie de la lámina del RER
        if (Math.random() > 0.58) {
          riboPosList.push(
            x + (Math.random() - 0.5) * 0.02,
            y + (Math.random() - 0.5) * 0.02,
            z + (Math.random() - 0.5) * 0.02
          );
        }
      }
    }

    for (let v = 0; v < vSegments; v++) {
      for (let u = 0; u < uSegments; u++) {
        const p1 = v * (uSegments + 1) + u;
        const p2 = p1 + 1;
        const p3 = (v + 1) * (uSegments + 1) + u;
        const p4 = p3 + 1;

        indices.push(p1, p2, p3);
        indices.push(p2, p4, p3);
      }
    }

    sheetGeo.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    sheetGeo.setIndex(indices);
    sheetGeo.computeVertexNormals();

    const sheetMesh = new THREE.Mesh(sheetGeo, rerMat);
    sheetMesh.rotation.set(0.15 + l * 0.05, 0.2 + l * 0.06, -0.08);
    sheetMesh.position.set(-0.08, 0.04, 0.01);
    parentGroup.add(sheetMesh);
  }

  // Ribosomas fosforescentes adheridos a las membranas del RER
  const riboCount = riboPosList.length / 3;
  const riboGeo = new THREE.BufferGeometry();
  riboGeo.setAttribute('position', new THREE.Float32BufferAttribute(riboPosList, 3));
  
  const riboMat = new THREE.PointsMaterial({
    color: 0x67e8f9,
    size: 0.038,
    transparent: true,
    opacity: 0.95
  });
  rerRibosomesGroup.add(new THREE.Points(riboGeo, riboMat));
  parentGroup.add(rerRibosomesGroup);
}

// Fabricador de Retículo Endoplasmático Liso (REL)
function buildSmoothEndoplasmicReticulum(parentGroup) {
  const relMat = new THREE.MeshStandardMaterial({
    color: 0xf43f5e,
    roughness: 0.28,
    metalness: 0.1,
    transparent: true,
    opacity: 0.86
  });

  // Red de túbulos anastomosados curvados (malla tubular)
  for (let i = 0; i < 7; i++) {
    const tubeGeo = new THREE.TorusGeometry(0.22 + (i % 3) * 0.07, 0.034, 12, 28, Math.PI * 1.6);
    const tubeMesh = new THREE.Mesh(tubeGeo, relMat);
    tubeMesh.position.set(-1.42 + (i * 0.13), -0.72 + (i * 0.18), -0.25 + (i * 0.08));
    tubeMesh.rotation.set(i * 0.85, i * 0.55, i * 0.4);
    parentGroup.add(tubeMesh);
  }
}

// Fabricador de Aparato de Golgi
function buildGolgiApparatus(parentGroup) {
  const golgiMat = new THREE.MeshStandardMaterial({
    color: 0xeab308,
    roughness: 0.28,
    side: THREE.DoubleSide
  });

  // 6 Cisternas curvas apiladas con extremos hinchados
  for (let i = 0; i < 6; i++) {
    const r = 0.48 - i * 0.035;
    const cisternaGeo = new THREE.TorusGeometry(r, 0.040, 14, 36, Math.PI * 0.9);
    const cisternaMesh = new THREE.Mesh(cisternaGeo, golgiMat);
    cisternaMesh.position.set(0.98, -0.68 + i * 0.075, 0.28);
    cisternaMesh.rotation.set(0.42, 0.28, 0.18 + i * 0.05);
    parentGroup.add(cisternaMesh);
  }

  // Vesículas de secreción desprendiéndose en los bordes
  const vMat = new THREE.MeshStandardMaterial({
    color: 0xfde047,
    roughness: 0.3,
    emissive: 0xd97706,
    emissiveIntensity: 0.35
  });
  for (let j = 0; j < 22; j++) {
    const vGeo = new THREE.SphereGeometry(0.042 + Math.random() * 0.022, 14, 14);
    const vMesh = new THREE.Mesh(vGeo, vMat);
    vMesh.position.set(
      1.18 + (Math.random() - 0.5) * 0.52,
      -0.58 + (Math.random() - 0.5) * 0.52,
      0.30 + (Math.random() - 0.5) * 0.42
    );
    parentGroup.add(vMesh);
  }
}

// Fabricador de Centrosoma con Centríolos (9 tripletes de microtúbulos ortogonales en L + satélite naranja)
let centrosome1Group = null;
let centrosome2Group = null;

function buildDetailedCentrosomes(parentGroup, glowTex) {
  const tubuleMat = new THREE.MeshStandardMaterial({
    color: 0xe2e8f0,
    roughness: 0.22,
    metalness: 0.75
  });

  const hubMat = new THREE.MeshStandardMaterial({
    color: 0xf97316,
    emissive: 0xea580c,
    emissiveIntensity: 0.95,
    roughness: 0.25
  });

  const asterSpriteMat = new THREE.SpriteMaterial({
    map: glowTex,
    color: 0x38bdf8,
    transparent: true,
    opacity: 0.9,
    blending: THREE.AdditiveBlending
  });

  function createCentrioleBarrel() {
    const barrel = new THREE.Group();
    const numTriplets = 9;
    const barrelRadius = 0.045;
    const length = 0.24;
    const tubGeo = new THREE.CylinderGeometry(0.011, 0.011, length, 8);

    for (let t = 0; t < numTriplets; t++) {
      const angle = (t / numTriplets) * Math.PI * 2;
      const tubMesh = new THREE.Mesh(tubGeo, tubuleMat);
      tubMesh.position.set(Math.cos(angle) * barrelRadius, 0, Math.sin(angle) * barrelRadius);
      barrel.add(tubMesh);
    }
    return barrel;
  }

  // Centrosoma 1 ubicado en cuadrante superior derecho cerca del RER
  centrosome1Group = new THREE.Group();

  const b1 = createCentrioleBarrel();
  centrosome1Group.add(b1);

  const b2 = createCentrioleBarrel();
  b2.rotation.z = Math.PI / 2;
  b2.position.set(0.12, 0.08, 0);
  centrosome1Group.add(b2);

  // Satélite pericentriolar esférico naranja brillante (idéntico al de la imagen del usuario)
  const hubSphere = new THREE.Mesh(new THREE.SphereGeometry(0.068, 16, 16), hubMat);
  hubSphere.position.set(0.05, -0.06, 0.08);
  centrosome1Group.add(hubSphere);

  // Nube de Material Pericentriolar (PCM) con condensación de tubulina
  const pcmMat = new THREE.MeshStandardMaterial({
    color: 0x38bdf8,
    roughness: 0.3,
    transparent: true,
    opacity: 0.35,
    emissive: 0x0284c7,
    emissiveIntensity: 0.45
  });
  const pcmMesh = new THREE.Mesh(new THREE.SphereGeometry(0.19, 16, 16), pcmMat);
  pcmMesh.position.set(0.06, 0.04, 0);
  centrosome1Group.add(pcmMesh);

  // Rayos de microtúbulos del Áster radial
  const asterPoints = [];
  for (let r = 0; r < 28; r++) {
    const th = Math.random() * Math.PI * 2;
    const ph = Math.acos(2 * Math.random() - 1);
    asterPoints.push(new THREE.Vector3(0.06, 0.04, 0));
    asterPoints.push(new THREE.Vector3(
      0.06 + Math.sin(ph) * Math.cos(th) * 0.48,
      0.04 + Math.sin(ph) * Math.sin(th) * 0.48,
      Math.cos(ph) * 0.35
    ));
  }
  const asterGeo = new THREE.BufferGeometry().setFromPoints(asterPoints);
  const asterLineMat = new THREE.LineBasicMaterial({
    color: 0x7dd3fc,
    transparent: true,
    opacity: 0.75,
    blending: THREE.AdditiveBlending
  });
  centrosome1Group.add(new THREE.LineSegments(asterGeo, asterLineMat));

  const aster1 = new THREE.Sprite(asterSpriteMat);
  aster1.scale.set(0.7, 0.7, 1);
  centrosome1Group.add(aster1);

  centrosome1Group.position.set(0.72, 1.05, 0.22);
  parentGroup.add(centrosome1Group);

  // Centrosoma 2 (Para G2 y Mitosis)
  centrosome2Group = new THREE.Group();
  const b3 = createCentrioleBarrel();
  centrosome2Group.add(b3);

  const b4 = createCentrioleBarrel();
  b4.rotation.z = Math.PI / 2;
  b4.position.set(0.12, 0.08, 0);
  centrosome2Group.add(b4);

  const hubSphere2 = new THREE.Mesh(new THREE.SphereGeometry(0.068, 16, 16), hubMat);
  hubSphere2.position.set(0.05, -0.06, 0.08);
  centrosome2Group.add(hubSphere2);

  const pcmMesh2 = new THREE.Mesh(new THREE.SphereGeometry(0.19, 16, 16), pcmMat.clone());
  pcmMesh2.position.set(0.06, 0.04, 0);
  centrosome2Group.add(pcmMesh2);

  const asterGeo2 = new THREE.BufferGeometry().setFromPoints(asterPoints);
  centrosome2Group.add(new THREE.LineSegments(asterGeo2, asterLineMat.clone()));

  const aster2 = new THREE.Sprite(asterSpriteMat.clone());
  aster2.scale.set(0.7, 0.7, 1);
  centrosome2Group.add(aster2);

  centrosome2Group.position.set(1.22, 1.25, 0.12);
  centrosome2Group.visible = false;
  parentGroup.add(centrosome2Group);
}

// Fabricador de 16 Cromátidas Hermanas (8 Pares de Cromosomas en Mitosis)
function buildChromosomesModel(parentGroup) {
  const chromoMat = new THREE.MeshStandardMaterial({
    color: 0x38bdf8,
    roughness: 0.24,
    metalness: 0.15,
    emissive: 0x1d4ed8,
    emissiveIntensity: 0.95
  });

  const kinetochoreMat = new THREE.MeshStandardMaterial({
    color: 0xfacc15,
    emissive: 0xeab308,
    emissiveIntensity: 1.35,
    roughness: 0.2
  });

  chromatidsList.length = 0;

  for (let i = 0; i < 16; i++) {
    const ch = new THREE.Group();
    const isLeft = (i < 8);
    const pairIndex = i % 8;

    // Brazo cilíndrico/capsular denso de la cromátida condensada
    const armGeo = new THREE.CapsuleGeometry(0.054, 0.38, 12, 16);
    const armMesh = new THREE.Mesh(armGeo, chromoMat);
    ch.add(armMesh);

    // Cinetocoro centromérico de anclaje de microtúbulos (botón esférico fluorescente amarillo dorado)
    const kGeo = new THREE.SphereGeometry(0.044, 12, 12);
    const kMesh = new THREE.Mesh(kGeo, kinetochoreMat);
    // El cinetocoro apunta hacia el polo respectivo (izquierdo o derecho)
    kMesh.position.set(isLeft ? -0.055 : 0.055, 0, 0);
    ch.add(kMesh);

    ch.userData = {
      isLeft,
      pairIndex,
      kinetochoreMesh: kMesh
    };

    chromatidsList.push(ch);
    parentGroup.add(ch);
  }
}

// Fabricador de Huso Mitótico Dinámico (Microtúbulos Cinetocóricos, Interpolares y Rayos de Áster)
function buildMitoticSpindle(parentGroup) {
  const spindleMat = new THREE.LineBasicMaterial({
    color: 0x67e8f9,
    transparent: true,
    opacity: 0.85,
    blending: THREE.AdditiveBlending
  });

  spindlePositions = new Float32Array(TOTAL_SPINDLE_LINES * 2 * 3);
  spindleGeo = new THREE.BufferGeometry();
  spindleGeo.setAttribute('position', new THREE.BufferAttribute(spindlePositions, 3));

  const spindleMesh = new THREE.LineSegments(spindleGeo, spindleMat);
  parentGroup.add(spindleMesh);
}

// Fabricador de Vesículas (Lisosomas, Peroxisomas, Vacuolas)
function buildVesicleCluster(parentGroup, count, radius, colorHex, opacity) {
  const isVacuole = (colorHex === 0x38bdf8);
  const isPeroxisome = (colorHex === 0x10b981);
  const isLysosome = (colorHex === 0xf59e0b || colorHex === 0xfbbf24);

  const mat = new THREE.MeshStandardMaterial({
    color: colorHex,
    roughness: isVacuole ? 0.15 : 0.25,
    metalness: 0.1,
    transparent: true,
    opacity: isVacuole ? 0.72 : opacity,
    emissive: colorHex,
    emissiveIntensity: isLysosome ? 0.65 : (isPeroxisome ? 0.55 : 0.40)
  });

  for (let i = 0; i < count; i++) {
    const r = radius * (0.85 + Math.random() * 0.3);
    const geo = new THREE.SphereGeometry(r, 18, 18);
    const mesh = new THREE.Mesh(geo, mat);

    // Núcleo cristalino denso para peroxisomas (urato oxidasa)
    if (isPeroxisome) {
      const coreGeo = new THREE.OctahedronGeometry(r * 0.48);
      const coreMat = new THREE.MeshStandardMaterial({
        color: 0x34d399,
        emissive: 0x059669,
        emissiveIntensity: 0.95,
        roughness: 0.2
      });
      mesh.add(new THREE.Mesh(coreGeo, coreMat));
    }

    // Granulaciones hidrolíticas densas para lisosomas
    if (isLysosome) {
      const coreGeo = new THREE.SphereGeometry(r * 0.45, 12, 12);
      const coreMat = new THREE.MeshStandardMaterial({
        color: 0xd97706,
        emissive: 0xb45309,
        emissiveIntensity: 0.85
      });
      mesh.add(new THREE.Mesh(coreGeo, coreMat));
    }

    // Núcleo acuoso límpido para vacuolas
    if (isVacuole) {
      const coreGeo = new THREE.SphereGeometry(r * 0.65, 14, 14);
      const coreMat = new THREE.MeshBasicMaterial({
        color: 0x7dd3fc,
        transparent: true,
        opacity: 0.45
      });
      mesh.add(new THREE.Mesh(coreGeo, coreMat));
    }

    const angle = Math.random() * Math.PI * 2;
    const dist = 1.15 + Math.random() * 0.95;
    mesh.position.set(
      Math.cos(angle) * dist,
      (Math.random() - 0.5) * 1.9,
      (Math.random() - 0.5) * 1.5
    );
    parentGroup.add(mesh);
  }
}

// Ribosomas Libres y Vesículas de Transporte Ámbar (gotas de contraste cálido idénticas a la imagen)
function buildFreeRibosomesAndGranules(parentGroup) {
  // 1. Ribosomas Libres (micropartículas azul claro/violeta)
  const riboCount = 750;
  const riboGeo = new THREE.BufferGeometry();
  const riboPos = new Float32Array(riboCount * 3);
  for (let i = 0; i < riboCount * 3; i += 3) {
    const r = 1.05 + Math.random() * 1.15;
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.acos(2 * Math.random() - 1);
    riboPos[i] = r * Math.sin(phi) * Math.cos(theta);
    riboPos[i + 1] = r * Math.sin(phi) * Math.sin(theta);
    riboPos[i + 2] = r * Math.cos(phi);
  }
  riboGeo.setAttribute('position', new THREE.BufferAttribute(riboPos, 3));
  const riboMat = new THREE.PointsMaterial({
    color: 0xc084fc,
    size: 0.038,
    transparent: true,
    opacity: 0.88
  });
  parentGroup.add(new THREE.Points(riboGeo, riboMat));

  // 2. Gránulos y Vesículas de Transporte Ámbar/Naranja (esferas flotantes visibles como en la imagen)
  const granuleMat = new THREE.MeshStandardMaterial({
    color: 0xf97316,
    emissive: 0xea580c,
    emissiveIntensity: 0.85,
    roughness: 0.25
  });
  for (let g = 0; g < 18; g++) {
    const gGeo = new THREE.SphereGeometry(0.055 + Math.random() * 0.025, 14, 14);
    const gMesh = new THREE.Mesh(gGeo, granuleMat);
    const ang = Math.random() * Math.PI * 2;
    const dist = 1.1 + Math.random() * 0.9;
    gMesh.position.set(
      Math.cos(ang) * dist,
      (Math.random() - 0.5) * 1.8,
      (Math.random() - 0.5) * 1.4
    );
    parentGroup.add(gMesh);
  }
}

// Fabricador de Citoesqueleto (Red 3D biológica cristalina de microtúbulos y filamentos interconectados)
function buildCytoskeletalMesh(parentGroup) {
  cytoskeletonMaterial = new THREE.LineBasicMaterial({
    color: 0x7dd3fc,
    transparent: true,
    opacity: 0.38,
    blending: THREE.AdditiveBlending
  });
  const cytoLinesMat = cytoskeletonMaterial;

  const nodes = [];
  // 65 nodos estructurales distribuidos orgánicamente en el citosol
  for (let i = 0; i < 65; i++) {
    const r = 0.95 + Math.random() * 1.25;
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.acos(2 * Math.random() - 1);
    nodes.push(new THREE.Vector3(
      r * Math.sin(phi) * Math.cos(theta),
      r * Math.sin(phi) * Math.sin(theta),
      Math.min(0.06, r * Math.cos(phi))
    ));
  }

  const points = [];
  // Conectar cada nodo con sus vecinos más cercanos (distancia biológica < 0.65)
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      const dist = nodes[i].distanceTo(nodes[j]);
      if (dist < 0.62) {
        points.push(nodes[i]);
        points.push(nodes[j]);
      }
    }
  }

  // Filamentos corticales desde los nodos hacia la membrana interna
  for (let k = 0; k < 30; k++) {
    const n = nodes[Math.floor(Math.random() * nodes.length)];
    const corticalAnchor = n.clone().normalize().multiplyScalar(2.28);
    if (corticalAnchor.z < 0.08) {
      points.push(n);
      points.push(corticalAnchor);
    }
  }

  const cytoGeo = new THREE.BufferGeometry().setFromPoints(points);
  parentGroup.add(new THREE.LineSegments(cytoGeo, cytoLinesMat));

  // Pequeños micro-nodos fluorescentes en las intersecciones del citoesqueleto
  const nodeGeo = new THREE.BufferGeometry().setFromPoints(nodes);
  const nodeMat = new THREE.PointsMaterial({
    color: 0xa5f3fc,
    size: 0.024,
    transparent: true,
    opacity: 0.65,
    blending: THREE.AdditiveBlending
  });
  parentGroup.add(new THREE.Points(nodeGeo, nodeMat));
}

// =========================================================================
// ACTUALIZADOR DEL ESTADO FÍSICO 3D SEGÚN LA FASE Y MITOSIS CONTINUA
// =========================================================================
function update3DState() {
  if (!mainCellGroup) return;

  const phase = activeMainPhase.value;
  const isM = (phase === 'M');

  if (isM) {
    updateContinuousMitosis(mitosisProgress.value);
    updateVisibilityLayers();
    updateChannelColors();
    return;
  }

  // Restaurar estado interfásico basal (G0, G1, S, G2)
  if (membraneMaterial) {
    if (membraneMaterial.uniforms.uElongation) membraneMaterial.uniforms.uElongation.value = 1.0;
    if (membraneMaterial.uniforms.uCleavagePinch) membraneMaterial.uniforms.uCleavagePinch.value = 0.0;
    membraneMaterial.uniforms.uOpacity.value = 0.55;
  }
  if (organelleGroups.membrane) {
    organelleGroups.membrane.visible = channels.value.cy5;
  }
  if (daughterCellLeftGroup) daughterCellLeftGroup.visible = false;
  if (daughterCellRightGroup) daughterCellRightGroup.visible = false;
  if (intercellularBridgeMesh) intercellularBridgeMesh.visible = false;
  if (contractileRingMesh) contractileRingMesh.visible = false;
  if (chromosomesGroup) chromosomesGroup.visible = false;
  if (mitoticSpindleLines) mitoticSpindleLines.visible = false;
  if (cutawayRimMesh) cutawayRimMesh.visible = crossSection.value;

  // 1. Escala Celular
  let cellScale = 1.0;
  if (phase === 'G0') cellScale = 0.88;
  else if (phase === 'G1') cellScale = 1.0;
  else if (phase === 'S') cellScale = 1.14;
  else if (phase === 'G2') cellScale = 1.28;

  if (organelleGroups.membrane) {
    organelleGroups.membrane.scale.set(cellScale, cellScale, cellScale);
  }

  // 2. Estado del Núcleo
  if (organelleGroups.nucleus) {
    organelleGroups.nucleus.visible = channels.value.dapi;
    if (nucleusMaterial) nucleusMaterial.opacity = 1.0;
    if (organelleGroups.nucleolus) {
      organelleGroups.nucleolus.visible = channels.value.dapi;
      let nucScale = 1.0;
      if (phase === 'G0') nucScale = 0.68;
      else if (phase === 'G1') nucScale = 1.0;
      else if (phase === 'S') nucScale = 1.18;
      else if (phase === 'G2') nucScale = 1.35;
      organelleGroups.nucleolus.scale.set(nucScale, nucScale, nucScale);
    }
  }

  // Focos de replicación en S
  if (replicationFociPoints) {
    replicationFociPoints.visible = (phase === 'S');
  }

  // 3. Centrosomas
  if (centrosome1Group && centrosome2Group) {
    if (phase === 'G0' || phase === 'G1') {
      centrosome1Group.position.set(0.55, 1.35, 0.15);
      centrosome2Group.visible = false;
    } else if (phase === 'S') {
      centrosome1Group.position.set(0.55, 1.35, 0.15);
      centrosome2Group.visible = true;
      centrosome2Group.position.set(0.78, 1.32, 0.15);
    } else if (phase === 'G2') {
      centrosome1Group.position.set(0.42, 1.55, 0.15);
      centrosome2Group.visible = true;
      centrosome2Group.position.set(1.22, 1.35, 0.1);
    }
  }

  // 4. Mitocondrias
  if (organelleGroups.mitochondria) {
    const activeLimit = activeMitoCount.value;
    organelleGroups.mitochondria.children.forEach((mito, idx) => {
      mito.visible = (idx < activeLimit);
      if (mito.userData?.defaultPos) {
        mito.position.copy(mito.userData.defaultPos);
      }
    });
  }

  // 5. RER y Golgi
  if (organelleGroups.rer && organelleGroups.golgi) {
    organelleGroups.rer.scale.set(1, 1, 1);
    organelleGroups.golgi.scale.set(1, 1, 1);
  }

  updateVisibilityLayers();
  updateChannelColors();
}

// =========================================================================
// CINÉTICA CONTINUA PROCEDURAL DE MITOSIS A 60 FPS (Fórmula Biofísica)
// =========================================================================
function updateContinuousMitosis(p) {
  if (!mainCellGroup) return;

  // Parámetro de transición de división en dos células hijas
  // Telofase: 0.68 -> 0.84 (transición y estrangulamiento profundo)
  // Citocinesis: 0.84 -> 1.00 (dos células hijas separadas con abscisión final)
  const isDividingInTwo = (p >= 0.72);
  const isFullCytokinesis = (p >= 0.84);

  // Distancia del centro de cada célula hija según el avance
  let daughterDist = 1.35;
  if (p >= 0.72 && p < 0.84) {
    const a = (p - 0.72) / 0.12;
    daughterDist = THREE.MathUtils.lerp(1.22, 1.45, a);
  } else if (p >= 0.84) {
    const a = (p - 0.84) / 0.16;
    daughterDist = THREE.MathUtils.lerp(1.45, 1.68, a);
  }

  // 1. Visibilidad y Deformación de la Membrana Materna vs Células Hijas
  if (organelleGroups.membrane && membraneMaterial) {
    if (isFullCytokinesis) {
      organelleGroups.membrane.visible = false;
    } else {
      organelleGroups.membrane.visible = channels.value.cy5;
      let elong = 1.0;
      let pinch = 0.0;

      if (p < 0.33) {
        elong = 1.0 + (p / 0.33) * 0.12;
        pinch = 0.0;
      } else if (p < 0.50) {
        elong = 1.12;
        pinch = 0.0;
      } else if (p < 0.68) {
        const a = (p - 0.50) / 0.18;
        elong = 1.12 + a * 0.35;
        pinch = a * 0.32;
      } else {
        const a = (p - 0.68) / 0.16;
        elong = 1.47 + a * 0.12;
        pinch = 0.32 + a * 0.55;
      }

      if (membraneMaterial.uniforms.uElongation) {
        membraneMaterial.uniforms.uElongation.value = elong;
      }
      if (membraneMaterial.uniforms.uCleavagePinch) {
        membraneMaterial.uniforms.uCleavagePinch.value = pinch;
      }

      // Desvanecimiento suave en la transición a 2 células (0.72 -> 0.84)
      if (p >= 0.72) {
        const fade = (p - 0.72) / 0.12;
        membraneMaterial.uniforms.uOpacity.value = THREE.MathUtils.lerp(0.55, 0.0, fade);
      } else {
        membraneMaterial.uniforms.uOpacity.value = 0.55;
      }
    }
  }

  // 2. Control de las Dos Células Hijas (Telofase a Citocinesis)
  if (daughterCellLeftGroup && daughterCellRightGroup) {
    if (isDividingInTwo) {
      daughterCellLeftGroup.visible = channels.value.cy5;
      daughterCellRightGroup.visible = channels.value.cy5;

      daughterCellLeftGroup.position.set(-daughterDist, 0, 0);
      daughterCellRightGroup.position.set(daughterDist, 0, 0);

      let dOpacity = 0.55;
      if (p < 0.84) {
        const a = (p - 0.72) / 0.12;
        dOpacity = THREE.MathUtils.lerp(0.0, 0.55, a);
      }
      if (daughterMembraneLeftMat) daughterMembraneLeftMat.uniforms.uOpacity.value = dOpacity;
      if (daughterMembraneRightMat) daughterMembraneRightMat.uniforms.uOpacity.value = dOpacity;

      // Escala celular de cada célula hija (crecen de 0.90 a 1.0)
      let dScale = 0.90;
      if (p >= 0.84) {
        const a = (p - 0.84) / 0.16;
        dScale = THREE.MathUtils.lerp(0.90, 1.0, a);
      }
      daughterCellLeftGroup.scale.set(dScale, dScale, dScale);
      daughterCellRightGroup.scale.set(dScale, dScale, dScale);
    } else {
      daughterCellLeftGroup.visible = false;
      daughterCellRightGroup.visible = false;
    }
  }

  // 3. Puente Intercelular y Anillo Contráctil de Actomiosina
  if (contractileRingMesh && intercellularBridgeMesh) {
    if (p >= 0.52 && p < 0.94) {
      contractileRingMesh.visible = true;
      intercellularBridgeMesh.visible = (p >= 0.72);

      let bridgeRadius = 0.35;
      let ringScale = 1.0;

      if (p < 0.72) {
        const a = (p - 0.52) / 0.20;
        ringScale = THREE.MathUtils.lerp(1.35, 0.75, a);
      } else if (p < 0.84) {
        const a = (p - 0.72) / 0.12;
        ringScale = THREE.MathUtils.lerp(0.75, 0.32, a);
        bridgeRadius = THREE.MathUtils.lerp(0.35, 0.18, a);
      } else {
        const a = (p - 0.84) / 0.10;
        ringScale = THREE.MathUtils.lerp(0.32, 0.08, a);
        bridgeRadius = THREE.MathUtils.lerp(0.18, 0.035, a);
      }

      contractileRingMesh.scale.set(ringScale, ringScale, ringScale);
      contractileRingMesh.position.set(0, 0, 0);

      intercellularBridgeMesh.scale.set(1.0, bridgeRadius, bridgeRadius);
      intercellularBridgeMesh.position.set(0, 0, 0);
      if (bridgeMaterial) {
        bridgeMaterial.uniforms.uOpacity.value = 0.75;
      }
    } else {
      // Abscisión Celular Completa a partir de p >= 0.94
      contractileRingMesh.visible = false;
      intercellularBridgeMesh.visible = false;
    }
  }

  // Ocultar borde estático durante la división
  if (cutawayRimMesh) {
    cutawayRimMesh.visible = crossSection.value && (p < 0.72);
  }

  // 4. Centrosomas y Polos del Huso Mitótico
  let poleX = 1.55;
  if (p < 0.16) {
    const a = p / 0.16;
    if (centrosome1Group) {
      centrosome1Group.position.set(
        THREE.MathUtils.lerp(0.42, -1.3, a),
        THREE.MathUtils.lerp(1.45, 0.0, a),
        THREE.MathUtils.lerp(0.15, 0.0, a)
      );
    }
    if (centrosome2Group) {
      centrosome2Group.visible = true;
      centrosome2Group.position.set(
        THREE.MathUtils.lerp(1.22, 1.3, a),
        THREE.MathUtils.lerp(1.35, 0.0, a),
        THREE.MathUtils.lerp(0.1, 0.0, a)
      );
    }
    poleX = THREE.MathUtils.lerp(1.0, 1.3, a);
  } else if (p < 0.50) {
    poleX = 1.55;
    if (centrosome1Group) centrosome1Group.position.set(-poleX, 0, 0);
    if (centrosome2Group) {
      centrosome2Group.visible = true;
      centrosome2Group.position.set(poleX, 0, 0);
    }
  } else if (p < 0.68) {
    const a = (p - 0.50) / 0.18;
    poleX = 1.55 + a * 0.35;
    if (centrosome1Group) centrosome1Group.position.set(-poleX, 0, 0);
    if (centrosome2Group) {
      centrosome2Group.visible = true;
      centrosome2Group.position.set(poleX, 0, 0);
    }
  } else {
    poleX = daughterDist + 0.65;
    if (centrosome1Group) centrosome1Group.position.set(-poleX, 0.35, 0.12);
    if (centrosome2Group) {
      centrosome2Group.visible = true;
      centrosome2Group.position.set(poleX, 0.35, 0.12);
    }
  }

  const pole1 = new THREE.Vector3(-poleX, 0, 0);
  const pole2 = new THREE.Vector3(poleX, 0, 0);

  // 5. Segregación de las 16 cromátidas hermanas
  if (chromosomesGroup) {
    chromosomesGroup.visible = (p < 0.88);

    for (let i = 0; i < 16; i++) {
      const ch = chromatidsList[i];
      if (!ch) continue;
      const isLeft = (i < 8);
      const k = i % 8;

      const yk = ((k % 4) - 1.5) * 0.36;
      const zk = ((Math.floor(k / 4)) - 0.5) * 0.42;

      if (p < 0.16) {
        // Profase: cromatina condensada en territorio nuclear
        const angle = (k / 8) * Math.PI * 2;
        const rad = 0.52;
        const xScat = Math.cos(angle) * rad;
        const yScat = Math.sin(angle) * rad;
        const zScat = (k - 3.5) * 0.08;
        ch.position.set(xScat + (isLeft ? -0.04 : 0.04), yScat, zScat);
        ch.rotation.set(0.2 * k, 0.3 * k, isLeft ? 0.35 : -0.35);
        ch.scale.set(0.9, 0.9, 0.9);
      } else if (p < 0.33) {
        // Prometafase: migración de captura hacia la placa ecuatorial
        const a = (p - 0.16) / 0.17;
        const angle = (k / 8) * Math.PI * 2;
        const xInit = Math.cos(angle) * 0.52;
        const yInit = Math.sin(angle) * 0.52;
        const zInit = (k - 3.5) * 0.08;

        const targetX = isLeft ? -0.065 : 0.065;
        const curX = THREE.MathUtils.lerp(xInit, targetX, a);
        const curY = THREE.MathUtils.lerp(yInit, yk, a);
        const curZ = THREE.MathUtils.lerp(zInit, zk, a);

        ch.position.set(curX, curY, curZ);
        ch.rotation.set(0.1, 0, isLeft ? 0.3 : -0.3);
        ch.scale.set(1.0, 1.0, 1.0);
      } else if (p < 0.50) {
        // Metafase: alineación estricta en placa metafásica con micro-tensión
        const jitter = Math.sin(performance.now() * 0.003 + k) * 0.012;
        const curX = (isLeft ? -0.065 : 0.065) + jitter;
        ch.position.set(curX, yk, zk);
        ch.rotation.set(0, 0, isLeft ? 0.32 : -0.32);
        ch.scale.set(1.05, 1.05, 1.05);
      } else if (p < 0.68) {
        // Anafase: separación rápida hacia polos con morfología hidrodinámica en V
        const a = (p - 0.50) / 0.18;
        const easeA = a * a * (3 - 2 * a);
        const targetDist = 1.18;
        const startX = isLeft ? -0.065 : 0.065;
        const endX = isLeft ? -targetDist : targetDist;
        const curX = THREE.MathUtils.lerp(startX, endX, easeA);

        const curY = THREE.MathUtils.lerp(yk, yk * 0.65, easeA);
        const curZ = THREE.MathUtils.lerp(zk, zk * 0.65, easeA);

        ch.position.set(curX, curY, curZ);
        const dragAngle = Math.sin(easeA * Math.PI) * 0.75;
        ch.rotation.set(0, 0, isLeft ? (0.32 + dragAngle) : (-0.32 - dragAngle));
        ch.scale.set(1.0, 1.0, 1.0);
      } else if (p < 0.84) {
        // Telofase: empaquetamiento dentro del núcleo hijo
        const a = (p - 0.68) / 0.16;
        const targetX = isLeft ? -daughterDist : daughterDist;
        const curX = targetX + (k % 2 === 0 ? 0.04 : -0.04) * (1.0 - a);
        const curY = yk * THREE.MathUtils.lerp(0.65, 0.35, a);
        const curZ = zk * THREE.MathUtils.lerp(0.65, 0.35, a);

        ch.position.set(curX, curY, curZ);
        ch.rotation.set(0.1, 0.1, isLeft ? 0.15 : -0.15);
        const decondenseScale = THREE.MathUtils.lerp(1.0, 0.45, a);
        ch.scale.set(decondenseScale, decondenseScale, decondenseScale);
      } else {
        // Citocinesis: cromatina descondensada dentro del núcleo hijo
        const a = (p - 0.84) / 0.16;
        const curX = isLeft ? -daughterDist : daughterDist;
        ch.position.set(curX, yk * 0.3, zk * 0.3);
        ch.rotation.set(0, 0, 0);
        const decondenseScale = THREE.MathUtils.lerp(0.45, 0.25, a);
        ch.scale.set(decondenseScale, decondenseScale, decondenseScale);
      }
    }
  }

  // 6. Huso Mitótico Dinámico a 60 FPS
  if (mitoticSpindleLines && spindlePositions && spindleGeo) {
    if (p >= 0.16 && p < 0.84) {
      mitoticSpindleLines.visible = true;
      let ptr = 0;

      // Fibras cinetocóricas (16 fibras)
      for (let i = 0; i < 16; i++) {
        const ch = chromatidsList[i];
        const isLeft = (i < 8);
        const pole = isLeft ? pole1 : pole2;

        spindlePositions[ptr++] = pole.x;
        spindlePositions[ptr++] = pole.y;
        spindlePositions[ptr++] = pole.z;

        if (ch) {
          spindlePositions[ptr++] = ch.position.x + (isLeft ? -0.05 : 0.05);
          spindlePositions[ptr++] = ch.position.y;
          spindlePositions[ptr++] = ch.position.z;
        } else {
          spindlePositions[ptr++] = 0;
          spindlePositions[ptr++] = 0;
          spindlePositions[ptr++] = 0;
        }
      }

      // Fibras interpolares solapadas (24 fibras)
      for (let j = 0; j < NUM_INTERPOLAR; j++) {
        const theta = (j / NUM_INTERPOLAR) * Math.PI * 2;
        const midY = Math.sin(theta) * (p < 0.68 ? 0.72 : (1.0 - (p - 0.68) / 0.16 * 0.82) * 0.72);
        const midZ = Math.cos(theta) * (p < 0.68 ? 0.72 : (1.0 - (p - 0.68) / 0.16 * 0.82) * 0.72);
        const midX = 0;

        const usePole = (j % 2 === 0) ? pole1 : pole2;
        spindlePositions[ptr++] = usePole.x;
        spindlePositions[ptr++] = usePole.y;
        spindlePositions[ptr++] = usePole.z;

        spindlePositions[ptr++] = midX;
        spindlePositions[ptr++] = midY;
        spindlePositions[ptr++] = midZ;
      }

      // Rayos de áster (16 por polo = 32 rayos)
      for (let ap = 0; ap < NUM_ASTRAL_PER_POLE; ap++) {
        const phi = (ap / NUM_ASTRAL_PER_POLE) * Math.PI * 2;
        spindlePositions[ptr++] = pole1.x;
        spindlePositions[ptr++] = pole1.y;
        spindlePositions[ptr++] = pole1.z;
        spindlePositions[ptr++] = pole1.x - 0.55;
        spindlePositions[ptr++] = pole1.y + Math.sin(phi) * 0.65;
        spindlePositions[ptr++] = pole1.z + Math.cos(phi) * 0.65;

        spindlePositions[ptr++] = pole2.x;
        spindlePositions[ptr++] = pole2.y;
        spindlePositions[ptr++] = pole2.z;
        spindlePositions[ptr++] = pole2.x + 0.55;
        spindlePositions[ptr++] = pole2.y + Math.sin(phi) * 0.65;
        spindlePositions[ptr++] = pole2.z + Math.cos(phi) * 0.65;
      }

      spindleGeo.attributes.position.needsUpdate = true;
    } else {
      mitoticSpindleLines.visible = false;
    }
  }

  // 7. Núcleo principal de la célula madre
  if (organelleGroups.nucleus) {
    const isolated = isolatedOrganelleId.value;
    if (isolated && (isolated === 'nucleus' || isolated === 'nucleolus' || isolated === 'envelope')) {
      organelleGroups.nucleus.visible = true;
      if (nucleusMaterial) nucleusMaterial.opacity = 0.95;
      if (organelleGroups.nucleolus) {
        organelleGroups.nucleolus.visible = true;
        organelleGroups.nucleolus.scale.set(1, 1, 1);
      }
    } else if (p < 0.16) {
      organelleGroups.nucleus.visible = true;
      if (nucleusMaterial) nucleusMaterial.opacity = 1.0 - (p / 0.16) * 0.6;
      if (organelleGroups.nucleolus) {
        organelleGroups.nucleolus.visible = true;
        const nScale = Math.max(0.1, 1.0 - (p / 0.16));
        organelleGroups.nucleolus.scale.set(nScale, nScale, nScale);
      }
    } else {
      organelleGroups.nucleus.visible = false;
      if (organelleGroups.nucleolus && !isolated) {
        organelleGroups.nucleolus.visible = false;
      }
    }
  }

  // 8. Partición Equitativa 50/50 de Mitocondrias
  if (organelleGroups.mitochondria) {
    const activeLimit = activeMitoCount.value;
    organelleGroups.mitochondria.children.forEach((mito, idx) => {
      mito.visible = (idx < activeLimit);
      if (p >= 0.48) {
        const toLeft = (idx < 14);
        const defPos = mito.userData?.defaultPos || mito.position;

        if (isDividingInTwo) {
          const dCenter = toLeft ? -daughterDist : daughterDist;
          const angle = (idx / 14) * Math.PI * 2;
          const rLocal = 0.55 + (idx % 3) * 0.28;
          const localX = Math.cos(angle) * rLocal * 0.65;
          const localY = Math.sin(angle) * rLocal * 0.75;
          const localZ = -0.15 - (idx % 4) * 0.18;

          mito.position.set(dCenter + localX, localY, localZ);
          mito.scale.set(0.95, 0.95, 0.95);
        } else {
          const segA = (p - 0.48) / 0.24;
          const shiftX = toLeft ? (-0.75 * segA) : (+0.75 * segA);
          let posX = defPos.x + shiftX;
          if (toLeft && posX > -0.32) posX = -0.35;
          if (!toLeft && posX < 0.32) posX = 0.35;

          const squeeze = 1.0 - segA * 0.2;
          mito.position.set(posX, defPos.y * squeeze, defPos.z * squeeze);
        }
      } else if (mito.userData?.defaultPos) {
        mito.position.copy(mito.userData.defaultPos);
      }
    });
  }

  // 9. Fragmentación de RER y Golgi
  if (organelleGroups.rer && organelleGroups.golgi) {
    const isolated = isolatedOrganelleId.value;
    if (isolated && (isolated === 'rer' || isolated === 'golgi')) {
      organelleGroups.rer.scale.set(1, 1, 1);
      organelleGroups.golgi.scale.set(1, 1, 1);
    } else if (p >= 0.16 && p < 0.75) {
      organelleGroups.rer.scale.set(0.48, 0.48, 0.48);
      organelleGroups.golgi.scale.set(0.48, 0.48, 0.48);
    } else if (p >= 0.75 && p < 0.88) {
      const a = (p - 0.75) / 0.13;
      const s = THREE.MathUtils.lerp(0.48, 0.75, a);
      organelleGroups.rer.scale.set(s, s, s);
      organelleGroups.golgi.scale.set(s, s, s);
    } else if (p >= 0.88) {
      organelleGroups.rer.scale.set(0.01, 0.01, 0.01);
      organelleGroups.golgi.scale.set(0.01, 0.01, 0.01);
    } else {
      organelleGroups.rer.scale.set(1, 1, 1);
      organelleGroups.golgi.scale.set(1, 1, 1);
    }
  }
}

// Control de Aislamiento y Capas de Visibilidad
function updateVisibilityLayers() {
  const isolated = isolatedOrganelleId.value;

  Object.keys(organelleGroups).forEach((k) => {
    const grp = organelleGroups[k];
    if (!grp) return;

    if (isolated) {
      if (isolated === 'nucleus') {
        // Al aislar el núcleo, mostramos el núcleo, nucléolo y envoltura juntos para máxima fidelidad
        grp.visible = (k === 'nucleus' || k === 'nucleolus' || k === 'envelope');
      } else {
        grp.visible = (k === isolated);
      }
    } else {
      if (k === 'membrane') grp.visible = channels.value.cy5;
      else if (k === 'cytosol') grp.visible = false; // El citosol se activa especialmente al aislarlo o al seleccionarlo
      else if (k === 'nucleus' || k === 'nucleolus' || k === 'envelope') grp.visible = channels.value.dapi;
      else if (k === 'mitochondria') grp.visible = channels.value.mito;
      else if (k === 'centrosome' || k === 'cytoskeleton' || k === 'peroxisome') grp.visible = channels.value.gfp;
      else grp.visible = true;
    }
  });

  // Mostrar silueta celular translúcida holográfica como referencia anatómica al aislar
  if (ghostCellSilhouetteMesh) {
    ghostCellSilhouetteMesh.visible = !!(isolated && isolated !== 'membrane');
  }

  // Refuerzo de brillo en citoesqueleto al aislar
  if (cytoskeletonMaterial) {
    cytoskeletonMaterial.opacity = (isolated === 'cytoskeleton') ? 0.88 : 0.38;
  }

  if (daughterCellLeftGroup && daughterCellRightGroup) {
    const isM = (activeMainPhase.value === 'M');
    const isDividing = isM && (mitosisProgress.value >= 0.72);
    if (isDividing && !isolated) {
      daughterCellLeftGroup.visible = channels.value.cy5;
      daughterCellRightGroup.visible = channels.value.cy5;
    } else if (isDividing && isolated) {
      daughterCellLeftGroup.visible = (isolated === 'membrane' || isolated === 'nucleus');
      daughterCellRightGroup.visible = (isolated === 'membrane' || isolated === 'nucleus');
    } else {
      daughterCellLeftGroup.visible = false;
      daughterCellRightGroup.visible = false;
    }
  }

  if (isolated === 'membrane' && membraneMaterial) {
    membraneMaterial.uniforms.uOpacity.value = 0.95;
  } else if (membraneMaterial) {
    membraneMaterial.uniforms.uOpacity.value = 0.55;
  }
}

function updateCrossSectionState() {
  const val = crossSection.value ? 1.0 : 0.0;
  if (membraneMaterial && membraneMaterial.uniforms.uCrossSection) {
    membraneMaterial.uniforms.uCrossSection.value = val;
  }
  if (daughterMembraneLeftMat && daughterMembraneLeftMat.uniforms.uCrossSection) {
    daughterMembraneLeftMat.uniforms.uCrossSection.value = val;
  }
  if (daughterMembraneRightMat && daughterMembraneRightMat.uniforms.uCrossSection) {
    daughterMembraneRightMat.uniforms.uCrossSection.value = val;
  }
  if (bridgeMaterial && bridgeMaterial.uniforms.uCrossSection) {
    bridgeMaterial.uniforms.uCrossSection.value = val;
  }
  if (nucleusMaterial && nucleusMaterial.uniforms.uCrossSection) {
    nucleusMaterial.uniforms.uCrossSection.value = val;
  }
  if (cutawayRimMesh) {
    cutawayRimMesh.visible = crossSection.value;
  }
  if (daughterRimLeftMesh) {
    daughterRimLeftMesh.visible = crossSection.value;
  }
  if (daughterRimRightMesh) {
    daughterRimRightMesh.visible = crossSection.value;
  }
}

function updateChannelColors() {
  updateVisibilityLayers();
}

function highlightOrganelle(id) {
  if (id === 'all') {
    isolatedOrganelleId.value = null;
    updateVisibilityLayers();
    return;
  }
}

// Bucle de Renderizado y Animación a 60 FPS
function animate() {
  animId = requestAnimationFrame(animate);
  const t = (performance.now() - startTime) * 0.001;

  if (membraneMaterial && membraneMaterial.uniforms.uTime) {
    membraneMaterial.uniforms.uTime.value = t;
  }
  if (daughterMembraneLeftMat && daughterMembraneLeftMat.uniforms.uTime) {
    daughterMembraneLeftMat.uniforms.uTime.value = t;
  }
  if (daughterMembraneRightMat && daughterMembraneRightMat.uniforms.uTime) {
    daughterMembraneRightMat.uniforms.uTime.value = t;
  }
  if (bridgeMaterial && bridgeMaterial.uniforms.uTime) {
    bridgeMaterial.uniforms.uTime.value = t;
  }
  if (nucleusMaterial && nucleusMaterial.uniforms.uTime) {
    nucleusMaterial.uniforms.uTime.value = t;
  }

  // Reproducción continua fluida de la cinética de mitosis a 60 FPS
  if (activeMainPhase.value === 'M' && isPlayingMitosis.value) {
    mitosisProgress.value += 0.00105 * mitosisSpeed.value;
    if (mitosisProgress.value > 1.0) {
      mitosisProgress.value = 0.0;
    }
    updateContinuousMitosis(mitosisProgress.value);
  }

  // Transición cinemática suave de cámara hacia orgánulos
  if (cameraTransition) {
    const elapsed = (performance.now() - cameraTransition.startTime) / cameraTransition.duration;
    if (elapsed >= 1.0) {
      camera.position.copy(cameraTransition.endPos);
      controls.target.copy(cameraTransition.endTarget);
      cameraTransition = null;
    } else {
      const tEase = 1 - Math.pow(1 - elapsed, 3);
      camera.position.lerpVectors(cameraTransition.startPos, cameraTransition.endPos, tEase);
      controls.target.lerpVectors(cameraTransition.startTarget, cameraTransition.endTarget, tEase);
    }
  }

  // Rotación orgánica suave de la célula (se pausa si hay un orgánulo aislado o si el usuario pausó la rotación 3D)
  if (mainCellGroup && !isolatedOrganelleId.value && isAutoRotating.value) {
    mainCellGroup.rotation.y += 0.0018;
  }

  // Damping interactivo de OrbitControls
  if (controls) {
    controls.update();
  }

  // Dinámica de los focos de replicación en fase S
  if (replicationFociPoints && replicationFociPoints.visible) {
    replicationFociPoints.rotation.y = t * 0.28;
    replicationFociPoints.rotation.z = Math.sin(t * 1.2) * 0.12;
  }

  // Ciclosis y movimiento suave de las mitocondrias
  if (organelleGroups.mitochondria && organelleGroups.mitochondria.visible) {
    organelleGroups.mitochondria.children.forEach((m, idx) => {
      m.rotation.x += 0.002 * (idx % 2 === 0 ? 1 : -1);
      m.rotation.y += 0.0015;
    });
  }

  if (renderer && scene && camera) {
    renderer.render(scene, camera);
  }
}

function onResize() {
  if (!canvasContainer.value || !camera || !renderer) return;
  const w = canvasContainer.value.clientWidth;
  const h = canvasContainer.value.clientHeight || 560;
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
  renderer.setSize(w, h);
}

onMounted(() => {
  setTimeout(() => {
    initScene();
  }, 60);
  window.addEventListener('resize', onResize);
});

onUnmounted(() => {
  if (animId) cancelAnimationFrame(animId);
  window.removeEventListener('resize', onResize);
  if (controls) controls.dispose();
  if (renderer && renderer.domElement) {
    renderer.dispose();
  }
});
</script>

<style scoped>
.confocal-workstation {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-color: var(--md-sys-color-surface-container-low);
  border: 1px solid var(--md-sys-color-outline-variant);
  border-radius: var(--md-sys-shape-corner-medium);
}

/* Header */
.workstation-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.4rem;
  background-color: var(--md-sys-color-surface-container);
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
  flex-wrap: wrap;
  gap: 1rem;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.header-icon-box {
  width: 40px;
  height: 40px;
  border-radius: var(--md-sys-shape-corner-small);
  background-color: var(--md-sys-color-surface-container-highest);
  color: var(--md-sys-color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-left h2 {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
}

.subtext {
  font-size: 0.8rem;
  color: var(--md-sys-color-on-surface-variant);
}

.header-controls-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

/* Channels Legend & Toggles */
.channels-legend {
  display: flex;
  gap: 0.45rem;
  background-color: var(--md-sys-color-surface-dim);
  padding: 0.25rem 0.45rem;
  border-radius: var(--md-sys-shape-corner-full);
  border: 1px solid var(--md-sys-color-outline-variant);
}

.channel-chip {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0.25rem 0.65rem;
  border-radius: var(--md-sys-shape-corner-full);
  font-size: 0.72rem;
  color: var(--md-sys-color-on-surface-variant);
  opacity: 0.55;
  transition: all 0.2s ease;
}

.channel-chip.active {
  opacity: 1;
  background-color: var(--md-sys-color-surface-container-high);
  color: var(--md-sys-color-on-surface);
}

.channel-chip .pip {
  width: 7px;
  height: 7px;
  border-radius: 50%;
}

.channel-chip.dapi .pip { background-color: #3b82f6; box-shadow: 0 0 6px #3b82f6; }
.channel-chip.mito .pip { background-color: #f97316; box-shadow: 0 0 6px #f97316; }
.channel-chip.gfp .pip { background-color: #a3e635; box-shadow: 0 0 6px #a3e635; }
.channel-chip.cy5 .pip { background-color: #06b6d4; box-shadow: 0 0 6px #06b6d4; }

.ch-target {
  font-family: var(--md-ref-typeface-mono);
  font-size: 0.68rem;
  opacity: 0.75;
}

.optical-toggles {
  display: flex;
  gap: 0.5rem;
}

.tool-btn {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  background-color: var(--md-sys-color-surface-container-high);
  border: 1px solid var(--md-sys-color-outline-variant);
  color: var(--md-sys-color-on-surface);
  border-radius: var(--md-sys-shape-corner-small);
  padding: 0.35rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tool-btn.active {
  background-color: var(--md-sys-color-primary-container);
  color: var(--md-sys-color-on-primary-container);
  border-color: var(--md-sys-color-primary);
}

/* Phase Selector Bar */
.phase-selector-bar {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  background-color: var(--md-sys-color-surface-container-low);
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
}

.phase-nav-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: transparent;
  border: none;
  border-right: 1px solid var(--md-sys-color-outline-variant);
  text-align: left;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.phase-nav-item:last-child {
  border-right: none;
}

.phase-nav-item:hover {
  background-color: var(--md-sys-color-surface-container);
}

.phase-nav-item.active {
  background-color: var(--md-sys-color-surface-container-high);
}

.phase-badge {
  font-family: var(--md-ref-typeface-mono);
  font-weight: 700;
  font-size: 0.95rem;
  padding: 0.2rem 0.5rem;
  background-color: var(--md-sys-color-surface-dim);
  border: 1px solid var(--md-sys-color-outline-variant);
  border-radius: var(--md-sys-shape-corner-extra-small);
  color: var(--md-sys-color-primary);
}

.phase-info {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.phase-name {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
}

.phase-sub {
  font-size: 0.68rem;
  color: var(--md-sys-color-on-surface-variant);
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
}

.active-indicator {
  display: none;
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background-color: var(--md-sys-color-primary);
}

.phase-nav-item.active .active-indicator {
  display: block;
}

/* Sub-barra de Mitosis */
.subphase-selector-bar {
  display: flex;
  flex-direction: column;
  padding: 0.65rem 1.4rem;
  background: linear-gradient(180deg, #121a28 0%, #0d131f 100%);
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
  gap: 0.65rem;
}

.mitosis-top-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.subphase-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--md-sys-color-secondary);
}

.pulse-icon {
  color: #38bdf8;
  animation: pulseIcon 2s infinite ease-in-out;
}

@keyframes pulseIcon {
  0%, 100% { transform: scale(1); opacity: 0.85; }
  50% { transform: scale(1.22); opacity: 1; filter: drop-shadow(0 0 6px rgba(56, 189, 248, 0.6)); }
}

.subphase-buttons {
  display: flex;
  gap: 0.35rem;
  flex-wrap: wrap;
}

.subphase-chip {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.3rem 0.65rem;
  background-color: var(--md-sys-color-surface-dim);
  border: 1px solid var(--md-sys-color-outline-variant);
  border-radius: var(--md-sys-shape-corner-full);
  color: var(--md-sys-color-on-surface-variant);
  font-size: 0.74rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.subphase-chip:hover {
  background-color: var(--md-sys-color-surface-container);
  color: var(--md-sys-color-on-surface);
  border-color: #38bdf8;
}

.subphase-chip.active {
  background: linear-gradient(135deg, rgba(56, 189, 248, 0.25) 0%, rgba(14, 165, 233, 0.35) 100%);
  color: #7dd3fc;
  border-color: #38bdf8;
  box-shadow: 0 0 10px rgba(56, 189, 248, 0.25);
  font-weight: 600;
}

.subphase-chip .num {
  font-family: var(--md-ref-typeface-mono);
  opacity: 0.75;
}

.mitosis-controls {
  display: flex;
  align-items: center;
  gap: 0.45rem;
}

.icon-tool-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  background-color: var(--md-sys-color-surface-container);
  border: 1px solid var(--md-sys-color-outline-variant);
  border-radius: var(--md-sys-shape-corner-small);
  color: var(--md-sys-color-on-surface);
  cursor: pointer;
  transition: all 0.15s ease;
}

.icon-tool-btn:hover {
  background-color: var(--md-sys-color-surface-container-high);
  color: #38bdf8;
  border-color: #38bdf8;
}

.play-mitosis-btn {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.35rem 0.85rem;
  background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
  color: #ffffff;
  border: 1px solid #38bdf8;
  border-radius: var(--md-sys-shape-corner-small);
  font-size: 0.76rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 6px rgba(2, 132, 199, 0.35);
}

.play-mitosis-btn:hover {
  filter: brightness(1.15);
  box-shadow: 0 0 12px rgba(56, 189, 248, 0.5);
}

.speed-selector {
  display: flex;
  background-color: var(--md-sys-color-surface-dim);
  border: 1px solid var(--md-sys-color-outline-variant);
  border-radius: var(--md-sys-shape-corner-small);
  overflow: hidden;
}

.speed-btn {
  padding: 0.25rem 0.45rem;
  background: transparent;
  border: none;
  font-size: 0.7rem;
  font-family: var(--md-ref-typeface-mono);
  color: var(--md-sys-color-on-surface-variant);
  cursor: pointer;
  transition: all 0.15s ease;
}

.speed-btn:hover {
  color: var(--md-sys-color-on-surface);
}

.speed-btn.active {
  background-color: var(--md-sys-color-primary-container);
  color: var(--md-sys-color-on-primary-container);
  font-weight: 700;
}

/* Scrubber Slider Continuo */
.mitosis-scrubber-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.2rem 0;
}

.scrubber-track-container {
  position: relative;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.mitosis-scrubber-slider {
  width: 100%;
  height: 6px;
  -webkit-appearance: none;
  appearance: none;
  background: linear-gradient(90deg, #1e3a5f 0%, #0284c7 50%, #38bdf8 100%);
  border-radius: 4px;
  outline: none;
  cursor: pointer;
  transition: height 0.15s ease;
  z-index: 2;
}

.mitosis-scrubber-slider:hover {
  height: 8px;
}

.mitosis-scrubber-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #38bdf8;
  border: 2px solid #ffffff;
  box-shadow: 0 0 10px rgba(56, 189, 248, 0.8);
  cursor: pointer;
  transition: transform 0.15s ease;
}

.mitosis-scrubber-slider::-webkit-slider-thumb:hover {
  transform: scale(1.25);
}

.stage-ticks {
  position: relative;
  width: 100%;
  height: 18px;
  margin-top: 4px;
}

.stage-tick {
  position: absolute;
  transform: translateX(-50%);
  font-size: 0.65rem;
  font-weight: 500;
  color: var(--md-sys-color-on-surface-variant);
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
  user-select: none;
}

.stage-tick:hover {
  color: #38bdf8;
}

.stage-tick.current {
  color: #38bdf8;
  font-weight: 700;
  text-shadow: 0 0 6px rgba(56, 189, 248, 0.6);
}

.scrubber-metric-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.3rem 0.75rem;
  background: rgba(14, 165, 233, 0.15);
  border: 1px solid rgba(56, 189, 248, 0.35);
  border-radius: var(--md-sys-shape-corner-small);
  white-space: nowrap;
}

.scrubber-metric-badge .badge-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #7dd3fc;
}

.scrubber-metric-badge .badge-pct {
  font-family: var(--md-ref-typeface-mono);
  font-size: 0.75rem;
  font-weight: 700;
  color: #38bdf8;
  min-width: 32px;
  text-align: right;
}

/* Área Principal: Visor 3D + Sidebar */
.viewer-main-area {
  display: grid;
  grid-template-columns: 1fr 390px;
  min-height: 580px;
  background-color: #04070c;
}

@media (max-width: 1024px) {
  .viewer-main-area {
    grid-template-columns: 1fr;
  }
}

.single-viewer-container {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 560px;
  background-color: #04070c;
}

.canvas-box {
  width: 100%;
  height: 100%;
  min-height: 560px;
  position: relative;
}

/* HUD Overlays */
.viewer-hud-top-left {
  position: absolute;
  top: 1rem;
  left: 1.2rem;
  display: flex;
  align-items: center;
  gap: 0.85rem;
  pointer-events: none;
  z-index: 5;
}

.active-code-pill {
  font-family: var(--md-ref-typeface-mono);
  font-size: 1.25rem;
  font-weight: 700;
  padding: 0.4rem 0.9rem;
  background: rgba(11, 15, 23, 0.85);
  border: 1px solid var(--md-sys-color-primary);
  color: var(--md-sys-color-primary);
  border-radius: var(--md-sys-shape-corner-small);
  backdrop-filter: blur(8px);
}

.hud-phase-meta {
  display: flex;
  flex-direction: column;
}

.phase-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: #ffffff;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);
}

.hud-sub-tags {
  display: flex;
  gap: 0.4rem;
  margin-top: 0.15rem;
  flex-wrap: wrap;
}

.hud-sub-tags .tag {
  font-size: 0.62rem;
  font-family: var(--md-ref-typeface-mono);
  color: var(--md-sys-color-on-surface-variant);
  background: rgba(15, 23, 42, 0.65);
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
}

.viewer-hud-top-right {
  position: absolute;
  top: 1rem;
  right: 1.2rem;
  display: flex;
  align-items: center;
  gap: 0.8rem;
  z-index: 5;
}

.telemetry-box {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  background: rgba(11, 15, 23, 0.8);
  padding: 0.4rem 0.75rem;
  border-radius: var(--md-sys-shape-corner-small);
  border: 1px solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(8px);
  pointer-events: none;
}

.hud-cue {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.68rem;
  color: var(--md-sys-color-on-surface-variant);
}

.cue-icon {
  color: var(--md-sys-color-primary);
}

.nav-controls {
  display: flex;
  gap: 0.35rem;
}

.rotation-hud-btn {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.45rem 0.85rem;
  background: rgba(11, 15, 23, 0.88);
  border: 1px solid rgba(56, 189, 248, 0.35);
  border-radius: var(--md-sys-shape-corner-small);
  color: #7dd3fc;
  font-family: var(--md-ref-typeface-plain);
  font-size: 0.72rem;
  font-weight: 600;
  cursor: pointer;
  backdrop-filter: blur(8px);
  transition: all 0.2s ease;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.35);
}

.rotation-hud-btn:hover {
  background: rgba(14, 165, 233, 0.2);
  border-color: #38bdf8;
  color: #e0f2fe;
  transform: translateY(-1px);
}

.rotation-hud-btn.paused {
  background: rgba(245, 158, 11, 0.15);
  border-color: rgba(245, 158, 11, 0.45);
  color: #fbbf24;
}

.rotation-hud-btn.paused:hover {
  background: rgba(245, 158, 11, 0.25);
  border-color: #f59e0b;
}

.rot-icon {
  flex-shrink: 0;
}

.nav-btn {
  width: 32px;
  height: 32px;
  background: rgba(11, 15, 23, 0.85);
  border: 1px solid var(--md-sys-color-outline-variant);
  color: var(--md-sys-color-on-surface);
  border-radius: var(--md-sys-shape-corner-small);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  backdrop-filter: blur(8px);
}

.nav-btn:hover {
  background-color: var(--md-sys-color-primary-container);
  color: var(--md-sys-color-on-primary-container);
  border-color: var(--md-sys-color-primary);
}

.viewer-hud-bottom {
  position: absolute;
  bottom: 1rem;
  left: 1.2rem;
  right: 1.2rem;
  pointer-events: none;
  z-index: 5;
}

.caption-dock {
  display: inline-flex;
  align-items: center;
  gap: 0.6rem;
  background: rgba(11, 15, 23, 0.85);
  padding: 0.5rem 1rem;
  border-radius: var(--md-sys-shape-corner-medium);
  border: 1px solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(8px);
  max-width: 90%;
}

.dock-icon {
  color: var(--md-sys-color-primary);
}

.caption-code {
  font-family: var(--md-ref-typeface-mono);
  font-weight: 700;
  color: var(--md-sys-color-primary);
}

.divider {
  color: var(--md-sys-color-outline);
}

.caption-desc {
  font-size: 0.78rem;
  color: var(--md-sys-color-on-surface);
}

/* Sidebar: Inspector Anatómico */
/* Sidebar: Inspector Anatómico Ultra-Pro */
.organelle-inspector-sidebar {
  display: flex;
  flex-direction: column;
  background-color: #070c14;
  border-left: 1px solid rgba(255, 255, 255, 0.08);
  overflow: hidden;
  height: 100%;
  max-height: 720px;
}

.sidebar-header {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  padding: 0.85rem 1rem 0.65rem 1rem;
  background: rgba(11, 19, 32, 0.95);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.sidebar-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.title-with-icon {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.header-icon {
  color: #38bdf8;
}

.sidebar-header h3 {
  font-size: 0.88rem;
  font-weight: 600;
  color: #f1f5f9;
  line-height: 1.15;
}

.sidebar-header .sub-dim {
  font-size: 0.62rem;
  color: #64748b;
  display: block;
}

.sidebar-header .badge {
  font-size: 0.65rem;
  font-family: var(--md-ref-typeface-mono);
  font-weight: 600;
  padding: 0.15rem 0.45rem;
  background-color: rgba(56, 189, 248, 0.12);
  border: 1px solid rgba(56, 189, 248, 0.28);
  border-radius: var(--md-sys-shape-corner-full);
  color: #38bdf8;
}

/* Barra de Búsqueda */
.search-input-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 0.65rem;
  color: #64748b;
  pointer-events: none;
}

.organelle-search-input {
  width: 100%;
  padding: 0.35rem 1.8rem 0.35rem 2rem;
  background: rgba(15, 23, 42, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: #f8fafc;
  font-size: 0.72rem;
  outline: none;
  transition: all 0.2s ease;
}

.organelle-search-input:focus {
  border-color: #38bdf8;
  background: rgba(15, 23, 42, 1);
  box-shadow: 0 0 8px rgba(56, 189, 248, 0.25);
}

.clear-search-btn {
  position: absolute;
  right: 0.5rem;
  background: transparent;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  font-size: 0.7rem;
}

/* Chips de Filtro por Categoría */
.category-filter-chips {
  display: flex;
  gap: 0.35rem;
  overflow-x: auto;
  padding-bottom: 0.1rem;
}

.cat-chip {
  padding: 0.2rem 0.55rem;
  background: rgba(30, 41, 59, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  color: #94a3b8;
  font-size: 0.64rem;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s ease;
}

.cat-chip:hover {
  background: rgba(51, 65, 85, 0.8);
  color: #e2e8f0;
}

.cat-chip.active {
  background: rgba(14, 165, 233, 0.22);
  border-color: #38bdf8;
  color: #38bdf8;
  font-weight: 600;
}

/* Contenedor de Scroll de Orgánulos */
.organelle-chips-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 0.55rem;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.full-cell-btn {
  background: rgba(15, 23, 42, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s ease;
}

.full-cell-btn:hover {
  background: rgba(30, 41, 59, 0.85);
  border-color: rgba(56, 189, 248, 0.4);
}

.full-cell-btn.active {
  background: rgba(14, 165, 233, 0.15);
  border-color: #38bdf8;
}

.restore-quick-pill {
  padding: 0.2rem 0.5rem;
  background: #facc15;
  color: #000000;
  border: none;
  border-radius: 4px;
  font-size: 0.65rem;
  font-weight: 700;
  cursor: pointer;
}

.restore-quick-pill:hover {
  filter: brightness(1.1);
}

/* Tarjeta individual de Orgánulo */
.organelle-card-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.6rem;
  padding: 0.45rem 0.65rem;
  background: rgba(11, 19, 32, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.organelle-card-item:hover {
  background: rgba(19, 31, 50, 0.85);
  border-color: rgba(56, 189, 248, 0.35);
  transform: translateX(2px);
}

.organelle-card-item.active {
  background: rgba(14, 165, 233, 0.12);
  border-color: #38bdf8;
  box-shadow: 0 0 10px rgba(56, 189, 248, 0.15);
}

.organelle-card-item.isolated {
  border-color: #facc15;
  background: rgba(250, 204, 21, 0.08);
  box-shadow: 0 0 10px rgba(250, 204, 21, 0.2);
}

.item-left {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  overflow: hidden;
  flex: 1;
}

.org-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.org-dot.all {
  background: conic-gradient(#3b82f6, #f97316, #a3e635, #06b6d4, #c084fc, #3b82f6);
}

.org-texts {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  flex: 1;
}

.org-name-row {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.org-name {
  font-size: 0.75rem;
  font-weight: 600;
  color: #f1f5f9;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
}

.cat-pill {
  font-size: 0.58rem;
  padding: 0.05rem 0.35rem;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.08);
  color: #94a3b8;
  font-weight: 500;
}

.cat-pill.genetic { color: #93c5fd; background: rgba(59, 130, 246, 0.15); }
.cat-pill.endomembrane { color: #67e8f9; background: rgba(6, 182, 212, 0.15); }
.cat-pill.energy { color: #fdba74; background: rgba(249, 115, 22, 0.15); }
.cat-pill.structure { color: #5eead4; background: rgba(20, 184, 166, 0.15); }

.org-dim {
  font-size: 0.63rem;
  color: #94a3b8;
  margin-top: 1px;
}

/* Acciones Rápidas en la Fila */
.item-quick-actions {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  flex-shrink: 0;
}

.quick-action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.25rem 0.45rem;
  border-radius: 4px;
  font-size: 0.64rem;
  cursor: pointer;
  transition: all 0.15s ease;
}

.focus-btn {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #94a3b8;
}

.focus-btn:hover {
  background: rgba(56, 189, 248, 0.2);
  color: #38bdf8;
  border-color: #38bdf8;
}

.solo-btn {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #cbd5e1;
  font-weight: 500;
}

.solo-btn:hover {
  background: rgba(250, 204, 21, 0.18);
  color: #facc15;
  border-color: #facc15;
}

.solo-btn.active {
  background: #facc15;
  color: #000000;
  border-color: #facc15;
  font-weight: 700;
}

.empty-search-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 2rem 1rem;
  color: #64748b;
  gap: 0.5rem;
  font-size: 0.72rem;
}

/* Ficha de Telemetría Anatómica */
.organelle-spec-card {
  padding: 0.85rem;
  margin: 0.4rem 0.55rem 0.55rem 0.55rem;
  border-radius: 10px;
  background: rgba(15, 23, 42, 0.95);
  border: 1px solid rgba(56, 189, 248, 0.25);
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  font-size: 0.73rem;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(10px);
}

.spec-card-head {
  display: flex;
  align-items: center;
  gap: 0.55rem;
}

.spec-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  flex-shrink: 0;
}

.spec-titles h4 {
  font-size: 0.84rem;
  font-weight: 700;
  color: #f8fafc;
}

.spec-badge-row {
  display: flex;
  gap: 0.5rem;
  margin-top: 1px;
}

.dim-tag {
  font-size: 0.64rem;
  color: #38bdf8;
}

.ratio-tag {
  font-size: 0.64rem;
  color: #94a3b8;
}

.spec-body-content {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.spec-info-block .block-label {
  font-size: 0.64rem;
  font-weight: 600;
  color: #38bdf8;
  display: block;
}

.spec-info-block .block-text {
  color: #cbd5e1;
  line-height: 1.35;
  font-size: 0.71rem;
}

.spec-phase-state {
  background: rgba(2, 132, 199, 0.12);
  padding: 0.4rem 0.6rem;
  border-radius: 6px;
  border-left: 3px solid #38bdf8;
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.spec-phase-state .label {
  font-size: 0.64rem;
  font-weight: 700;
  color: #7dd3fc;
}

.spec-phase-state .value {
  font-size: 0.71rem;
  color: #f1f5f9;
  line-height: 1.35;
}

.spec-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.45rem;
  margin-top: 0.25rem;
}

.isolate-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  padding: 0.45rem;
  background: rgba(30, 41, 59, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #f8fafc;
  border-radius: 6px;
  font-size: 0.72rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.isolate-btn:hover {
  background: rgba(250, 204, 21, 0.15);
  border-color: #facc15;
  color: #facc15;
}

.isolate-btn.active {
  background: #facc15;
  color: #000000;
  border-color: #facc15;
  font-weight: 700;
  box-shadow: 0 0 10px rgba(250, 204, 21, 0.35);
}

.focus-camera-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  padding: 0.45rem;
  background: rgba(14, 165, 233, 0.18);
  border: 1px solid #38bdf8;
  color: #38bdf8;
  border-radius: 6px;
  font-size: 0.72rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.focus-camera-btn:hover {
  background: #0284c7;
  color: #ffffff;
  box-shadow: 0 0 10px rgba(56, 189, 248, 0.4);
}

/* Modal de Tabla Citométrica */
.scale-table-modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1.5rem;
}

.scale-modal-content {
  background-color: var(--md-sys-color-surface-container);
  border: 1px solid var(--md-sys-color-outline-variant);
  border-radius: var(--md-sys-shape-corner-large);
  width: 100%;
  max-width: 920px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  padding: 1.5rem;
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}

.modal-header .header-left {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  color: var(--md-sys-color-primary);
}

.modal-header h3 {
  font-size: 1.15rem;
  color: var(--md-sys-color-on-surface);
}

.close-btn {
  background: transparent;
  border: none;
  color: var(--md-sys-color-on-surface-variant);
  font-size: 1.25rem;
  cursor: pointer;
}

.modal-intro {
  font-size: 0.85rem;
  color: var(--md-sys-color-on-surface-variant);
  margin-bottom: 1rem;
}

.table-wrapper {
  overflow-y: auto;
  border: 1px solid var(--md-sys-color-outline-variant);
  border-radius: var(--md-sys-shape-corner-small);
}

.cytometry-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.78rem;
  text-align: left;
}

.cytometry-table th {
  background-color: var(--md-sys-color-surface-container-high);
  padding: 0.65rem 0.85rem;
  color: var(--md-sys-color-primary);
  font-weight: 600;
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
  position: sticky;
  top: 0;
}

.cytometry-table td {
  padding: 0.6rem 0.85rem;
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
  color: var(--md-sys-color-on-surface-variant);
}

.cytometry-table tr:hover {
  background-color: var(--md-sys-color-surface-container-highest);
}

.org-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--md-sys-color-on-surface);
}

.highlight {
  color: var(--md-sys-color-primary);
  font-weight: 600;
}

.phase-behavior {
  font-size: 0.72rem;
  color: var(--md-sys-color-secondary);
}

/* Inspection Panel */
.inspection-panel {
  padding: 1.25rem 1.5rem;
  background-color: var(--md-sys-color-surface-container);
  border-top: 1px solid var(--md-sys-color-outline-variant);
}

.panel-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.card-left {
  display: flex;
  align-items: center;
  gap: 1.1rem;
}

.code-badge {
  font-family: var(--md-ref-typeface-mono);
  font-size: 1.5rem;
  font-weight: 700;
  width: 52px;
  height: 52px;
  border-radius: var(--md-sys-shape-corner-medium);
  background-color: var(--md-sys-color-primary-container);
  color: var(--md-sys-color-on-primary-container);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--md-sys-color-primary);
}

.card-headings h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
}

.card-headings .sub-text {
  font-size: 0.8rem;
  color: var(--md-sys-color-on-surface-variant);
}

.card-specs {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.spec-cell {
  display: flex;
  flex-direction: column;
}

.spec-label {
  font-size: 0.7rem;
  color: var(--md-sys-color-on-surface-variant);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.spec-val {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--md-sys-color-on-surface);
}

.spec-val.highlight {
  color: var(--md-sys-color-primary);
}

.md3-button-filled {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background-color: var(--md-sys-color-primary);
  color: var(--md-sys-color-on-primary);
  border: none;
  padding: 0.65rem 1.25rem;
  border-radius: var(--md-sys-shape-corner-full);
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.md3-button-filled:hover {
  filter: brightness(1.1);
  box-shadow: 0 4px 12px rgba(112, 214, 255, 0.35);
}

/* Reglas Responsivas para Dispositivos Móviles y Tablets */
@media (max-width: 1024px) {
  .viewer-main-area {
    grid-template-columns: 1fr;
  }
  .single-viewer-container {
    min-height: 460px;
    height: 52vh;
  }
  .canvas-box {
    min-height: 460px;
    height: 100%;
  }
  .organelle-inspector-sidebar {
    border-left: none;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
    max-height: 480px;
  }
}

@media (max-width: 860px) {
  .workstation-header {
    flex-direction: column;
    align-items: flex-start;
    padding: 0.85rem 1rem;
    gap: 0.75rem;
  }
  .header-controls-row {
    width: 100%;
    flex-direction: column;
    align-items: flex-start;
    gap: 0.65rem;
  }
  .channels-legend {
    width: 100%;
    overflow-x: auto;
    flex-wrap: nowrap;
    -webkit-overflow-scrolling: touch;
    padding: 0.3rem;
  }
  .optical-toggles {
    width: 100%;
    overflow-x: auto;
    flex-wrap: nowrap;
    padding-bottom: 0.2rem;
  }
  .phase-selector-bar {
    display: flex;
    overflow-x: auto;
    scroll-snap-type: x mandatory;
    -webkit-overflow-scrolling: touch;
  }
  .phase-nav-item {
    flex: 0 0 auto;
    min-width: 125px;
    scroll-snap-align: start;
    padding: 0.6rem 0.8rem;
  }
  .mitosis-top-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.6rem;
  }
  .subphase-buttons {
    width: 100%;
    overflow-x: auto;
    flex-wrap: nowrap;
    -webkit-overflow-scrolling: touch;
    padding-bottom: 0.2rem;
  }
}

@media (max-width: 640px) {
  .single-viewer-container {
    min-height: 380px;
    height: 48vh;
  }
  .canvas-box {
    min-height: 380px;
  }
  .viewer-hud-top-left {
    top: 0.65rem;
    left: 0.65rem;
    gap: 0.5rem;
  }
  .active-code-pill {
    font-size: 0.95rem;
    padding: 0.25rem 0.55rem;
  }
  .hud-sub-tags {
    display: none;
  }
  .phase-title {
    font-size: 0.8rem;
  }
  .viewer-hud-top-right {
    top: 0.65rem;
    right: 0.65rem;
    gap: 0.4rem;
  }
  .telemetry-box {
    display: none;
  }
  .rotation-hud-btn span {
    display: none;
  }
  .rotation-hud-btn {
    padding: 0.4rem;
  }
  .viewer-hud-bottom {
    left: 0.65rem;
    right: 0.65rem;
    bottom: 0.65rem;
  }
  .caption-dock {
    max-width: 100%;
    padding: 0.35rem 0.65rem;
    font-size: 0.68rem;
  }
  .caption-desc {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    font-size: 0.65rem;
  }
  .scrubber-metric-badge {
    display: none;
  }
}
</style>
