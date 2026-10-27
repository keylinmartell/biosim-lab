<template>
  <div class="md3-lab-shell">
    <!-- MD3 Laboratory Top App Bar -->
    <header class="md3-app-bar">
      <div class="app-bar-left">
        <div class="lab-logo-container">
          <Icon name="science" size="22" />
        </div>
        <div class="lab-identity">
          <div class="lab-title-row">
            <h1 class="lab-title">BioSIM <span class="accent-text">Lab</span></h1>
          </div>
          <span class="lab-subtext">Plataforma de Simulación y Análisis Biológico Computacional</span>
        </div>
      </div>

      <!-- MD3 Navigation Tabs -->
      <nav class="md3-nav-tabs" aria-label="Navegación principal de laboratorio">
        <button 
          :class="['md3-tab-item', { active: currentTab === '3d' }]" 
          @click="currentTab = '3d'"
        >
          <Icon name="biotech" size="20" class="tab-icon" />
          <span class="tab-label">Microscopía 3D</span>
          <div class="active-indicator"></div>
        </button>

        <button 
          :class="['md3-tab-item', { active: currentTab === 'dna' }]" 
          @click="currentTab = 'dna'"
        >
          <Icon name="dna" size="20" class="tab-icon" />
          <span class="tab-label">Laboratorio de ADN</span>
          <div class="active-indicator"></div>
        </button>

        <button 
          :class="['md3-tab-item', { active: currentTab === 'db' }]" 
          @click="currentTab = 'db'"
        >
          <Icon name="dataset" size="20" class="tab-icon" />
          <span class="tab-label">Cepas en PostgreSQL</span>
          <div class="active-indicator"></div>
        </button>

        <!-- <button 
          :class="['md3-tab-item', { active: currentTab === 'experimental' }]" 
          @click="currentTab = 'experimental'"
        >
          <Icon name="science" size="20" class="tab-icon" />
          <span class="tab-label">Modelo Experimental</span>
          <div class="active-indicator"></div>
        </button> -->
      </nav>

      <!-- Instrumentation & Telemetry Status -->
      <div class="app-bar-telemetry">
        <div class="telemetry-chip online">
          <span class="live-dot"></span>
          <span class="chip-label">BD: biosim (OK)</span>
        </div>
        <div class="telemetry-chip server">
          <Icon name="server" size="14" class="micro-icon" />
          <span class="chip-label">FastAPI v1.0</span>
        </div>
      </div>
    </header>

    <!-- Sub-header HUD Bar (Scientific Context & Quick Telemetry) -->
    <div class="hud-bar">
      <div class="hud-container">
        <div class="hud-breadcrumb">
          <Icon name="terminal" size="14" class="icon" />
          <span class="path">ESTACIÓN DE TRABAJO &gt;</span>
          <span class="current-module">{{ moduleName }}</span>
        </div>
        <div class="hud-stats">
          <span class="stat-item"><span class="k">TASA REPLICACIÓN:</span> <span class="v">99.8% FIDELIDAD</span></span>
          <span class="stat-divider">|</span>
          <span class="stat-item"><span class="k">MODO GLSL:</span> <span class="v">CONFOCAL PROCEDURAL</span></span>
          <span class="stat-divider">|</span>
          <span class="stat-item"><span class="k">SESIÓN:</span> <span class="v">LOCAL DEV (5173)</span></span>
        </div>
      </div>
    </div>

    <!-- Main Scientific Workstation Canvas -->
    <main class="md3-main-container">
      <transition name="md3-fade" mode="out-in">
        <div v-if="currentTab === '3d'" key="3d" class="view-wrapper">
          <CellViewer3D :cellState="selectedCellState" @update:cellState="selectedCellState = $event" />
        </div>
        <div v-else-if="currentTab === 'dna'" key="dna" class="view-wrapper">
          <DNALab />
        </div>
        <div v-else-if="currentTab === 'db'" key="db" class="view-wrapper">
          <CellManager @selectCell="handleCellSelected" />
        </div>
        <div v-else-if="currentTab === 'experimental'" key="experimental" class="view-wrapper">
          <ExperimentalLab />
        </div>
      </transition>
    </main>

    <!-- MD3 Laboratory System Footer -->
    <footer class="md3-lab-footer">
      <div class="footer-left">
        <Icon name="shield" size="16" class="footer-icon" />
        <span>BioSIM Lab Workstation · Modelo Abstracto Inicial v1.0 · Trazabilidad Científica Estricta</span>
      </div>
      <div class="footer-specs">
        <span class="spec-pill">FastAPI 3.11+</span>
        <span class="spec-pill">PostgreSQL 16</span>
        <span class="spec-pill">Vue 3.5</span>
        <span class="spec-pill">Three.js WebGL</span>
        <span class="spec-pill">Material 3</span>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import Icon from './components/Icon.vue';
import CellViewer3D from './components/CellViewer3D.vue';
import DNALab from './components/DNALab.vue';
import CellManager from './components/CellManager.vue';
import ExperimentalLab from './components/ExperimentalLab.vue';

const currentTab = ref('3d');
const selectedCellState = ref('G1');

const moduleName = computed(() => {
  switch (currentTab.value) {
    case '3d': return 'MICROSCOPÍA CONFOCAL 3D (FLUORESCENCIA DAPI/CIAN)';
    case 'dna': return 'SECUENCIADOR, COMPLEMENTARIEDAD & MUTAGÉNESIS IN SILICO';
    case 'db': return 'BIOBANCO Y REGISTRO RELACIONAL DE CÉLULAS VIRTUALES (POSTGRESQL)';
    case 'experimental': return 'MODELO EXPERIMENTAL DINÁMICO & CÉLULA PLURIPOTENCIAL (GEMINI + ENGINE)';
    default: return 'LABORATORIO BIO-COMPUTACIONAL';
  }
});

function handleCellSelected(cell) {
  selectedCellState.value = cell.cell_cycle_phase || cell.cell_state || 'G1';
  currentTab.value = '3d';
}
</script>

<style scoped>
.md3-lab-shell {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: var(--md-sys-color-surface);
}

/* MD3 Laboratory Top App Bar */
.md3-app-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
  padding: 0 1.5rem;
  background-color: var(--md-sys-color-surface-container-low);
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(12px);
}

.app-bar-left {
  display: flex;
  align-items: center;
  gap: 0.9rem;
}

.lab-logo-container {
  width: 38px;
  height: 38px;
  border-radius: var(--md-sys-shape-corner-medium);
  background: linear-gradient(135deg, var(--md-sys-color-primary-container), var(--md-sys-color-surface-container-highest));
  border: 1px solid rgba(112, 214, 255, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--md-sys-color-primary);
  box-shadow: 0 0 14px rgba(112, 214, 255, 0.2);
}

.lab-identity {
  display: flex;
  flex-direction: column;
}

.lab-title-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.lab-title {
  font-size: 1.15rem;
  font-weight: 700;
  letter-spacing: -0.3px;
  color: var(--md-sys-color-on-surface);
  line-height: 1.2;
}

.accent-text {
  color: var(--md-sys-color-primary);
}

.system-chip {
  font-size: 0.65rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 0.1rem 0.45rem;
  border-radius: var(--md-sys-shape-corner-extra-small);
  background-color: var(--md-sys-color-surface-container-highest);
  color: var(--md-sys-color-primary);
  border: 1px solid rgba(112, 214, 255, 0.25);
}

.lab-subtext {
  font-size: 0.68rem;
  color: var(--md-sys-color-on-surface-variant);
}

/* MD3 Navigation Tabs */
.md3-nav-tabs {
  display: flex;
  height: 100%;
  gap: 0.25rem;
}

.md3-tab-item {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  height: 100%;
  padding: 0 1.2rem;
  background: transparent;
  border: none;
  color: var(--md-sys-color-on-surface-variant);
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  position: relative;
  transition: all var(--md-sys-motion-duration-short) ease;
}

.md3-tab-item:hover {
  color: var(--md-sys-color-on-surface);
  background-color: rgba(255, 255, 255, 0.03);
}

.md3-tab-item.active {
  color: var(--md-sys-color-primary);
  font-weight: 600;
}

.tab-icon {
  color: inherit;
}

.active-indicator {
  position: absolute;
  bottom: 0;
  left: 0.8rem;
  right: 0.8rem;
  height: 3px;
  border-radius: 3px 3px 0 0;
  background-color: transparent;
  transition: all var(--md-sys-motion-duration-short) var(--md-sys-motion-easing-emphasized);
}

.md3-tab-item.active .active-indicator {
  background-color: var(--md-sys-color-primary);
  box-shadow: 0 0 10px var(--md-sys-color-primary);
}

/* Telemetry Section */
.app-bar-telemetry {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.telemetry-chip {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.28rem 0.65rem;
  border-radius: var(--md-sys-shape-corner-full);
  background-color: var(--md-sys-color-surface-container);
  border: 1px solid var(--md-sys-color-outline-variant);
  font-size: 0.72rem;
  color: var(--md-sys-color-on-surface-variant);
}

.telemetry-chip.online {
  border-color: rgba(122, 229, 130, 0.3);
  color: var(--md-sys-color-tertiary);
}

.live-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background-color: var(--md-sys-color-tertiary);
  box-shadow: 0 0 8px var(--md-sys-color-tertiary);
  animation: pulse-ring 2.5s infinite;
}

@keyframes pulse-ring {
  0% { transform: scale(0.95); opacity: 0.8; }
  50% { transform: scale(1.15); opacity: 1; }
  100% { transform: scale(0.95); opacity: 0.8; }
}

.micro-icon {
  color: var(--md-sys-color-primary);
}

/* HUD Bar */
.hud-bar {
  background-color: var(--md-sys-color-surface-container-lowest);
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
  padding: 0.35rem 1.5rem;
  font-family: var(--md-ref-typeface-mono);
  font-size: 0.7rem;
}

.hud-container {
  max-width: 1360px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.hud-breadcrumb {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  color: var(--md-sys-color-on-surface-variant);
}

.hud-breadcrumb .icon {
  color: var(--md-sys-color-primary);
}

.hud-breadcrumb .current-module {
  color: var(--md-sys-color-primary);
  font-weight: 600;
}

.hud-stats {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  color: var(--md-sys-color-on-surface-variant);
}

.stat-item .k {
  color: #64748b;
  margin-right: 0.25rem;
}

.stat-item .v {
  color: #cbd5e1;
  font-weight: 500;
}

.stat-divider {
  color: #334155;
}

/* Main Container */
.md3-main-container {
  flex: 1;
  max-width: 1360px;
  width: 100%;
  margin: 0 auto;
  padding: 1.5rem 1.5rem 2rem;
}

.view-wrapper {
  width: 100%;
}

/* Footer */
.md3-lab-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.85rem 1.5rem;
  background-color: var(--md-sys-color-surface-container-lowest);
  border-top: 1px solid var(--md-sys-color-outline-variant);
  font-size: 0.72rem;
  color: var(--md-sys-color-on-surface-variant);
  flex-wrap: wrap;
  gap: 0.8rem;
}

.footer-left {
  display: flex;
  align-items: center;
  gap: 0.45rem;
}

.footer-icon {
  color: var(--md-sys-color-primary);
}

.footer-specs {
  display: flex;
  gap: 0.4rem;
  flex-wrap: wrap;
}

.spec-pill {
  padding: 0.15rem 0.45rem;
  border-radius: var(--md-sys-shape-corner-extra-small);
  background-color: var(--md-sys-color-surface-container);
  border: 1px solid var(--md-sys-color-outline-variant);
  color: #94a3b8;
  font-family: var(--md-ref-typeface-mono);
  font-size: 0.68rem;
}

/* Transitions */
.md3-fade-enter-active,
.md3-fade-leave-active {
  transition: opacity var(--md-sys-motion-duration-short) ease,
              transform var(--md-sys-motion-duration-short) var(--md-sys-motion-easing-decelerate);
}

.md3-fade-enter-from {
  opacity: 0;
  transform: translateY(6px);
}

.md3-fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

@media (max-width: 900px) {
  .md3-app-bar {
    height: auto;
    padding: 0.75rem 1rem;
    flex-wrap: wrap;
    gap: 0.8rem;
  }
  .md3-nav-tabs {
    order: 3;
    width: 100%;
    justify-content: space-around;
    border-top: 1px solid var(--md-sys-color-outline-variant);
    padding-top: 0.5rem;
  }
  .hud-stats {
    display: none;
  }
}

@media (max-width: 640px) {
  .md3-main-container {
    padding: 0.85rem 0.65rem 1.5rem;
  }
  .lab-subtext {
    display: none;
  }
  .app-bar-telemetry {
    display: none;
  }
  .md3-tab-item {
    padding: 0.4rem 0.5rem;
    font-size: 0.76rem;
    gap: 0.35rem;
  }
  .tab-icon {
    width: 16px;
    height: 16px;
  }
  .hud-bar {
    padding: 0.3rem 0.75rem;
  }
  .md3-lab-footer {
    padding: 0.75rem 0.85rem;
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
