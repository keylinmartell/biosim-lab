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
            <h3>ADN-B · Modelo Atómico Real</h3>
            <span class="locus-pill" :class="'locus-' + activeGeneId">
              Locus: {{ activeGeneId }} ({{ activeGeneProduct }}) · Hebra {{ currentLocus?.gene.strand }}
            </span>
            <span class="atomic-badge">{{ activeLocusSeq.length }} pb · Modelo Paramétrico</span>
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
      </div>
    </div>

    <!-- Barra de Estado Biológico del Locus -->
    <div class="watermark-status-bar">
      <span class="status-chip" :class="{ transcribing: isTranscribing }">
        <Icon name="biotech" size="14" />
        {{ isTranscribing ? 'ARN Polimerasa II Transcribiendo Hebra Molde (R19)' : 'Cromatina en Reposo' }}
      </span>
      <span v-if="p53Bound" class="status-chip p53-active">
        <Icon name="shield" size="14" />
        ✦ p53 unido al Surco Mayor (R28)
      </span>
      <span v-if="hasDsb" class="status-chip dsb-chip">
        <Icon name="warning" size="14" />
        ⚠ Rotura Doble Cadena (DSB) en Locus (R30)
      </span>
    </div>

    <!-- Visor Atómico Tridimensional (Componente DNAHelix3D) -->
    <div class="adn-viewer-container">
      <DNAHelix3D 
        :sequence="activeLocusSeq" 
        :selectedPosition="selectedPosition" 
        @selectBase="selectedPosition = $event" 
      />
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
import { ref, computed } from 'vue';
import Icon from './Icon.vue';
import DNAHelix3D from './DNAHelix3D.vue';
import { buildLocus, express, pickActiveGene, AA3 } from '../sim/dnaEngine';

const props = defineProps({
  kb: { type: Object, default: () => ({}) },
  cellFate: { type: String, default: 'pluripotente' },
  cellPhase: { type: String, default: 'G1' },
  cellState: { type: Object, default: () => ({}) },
  alive: { type: Boolean, default: true }
});

const selectedLocusKey = ref('AUTO');
const selectedPosition = ref(0);

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

// Secuencia activa para el modelo 3D
const activeLocusSeq = computed(() => {
  if (!currentLocus.value?.forward) return 'ATCGATCGATCGATCGATCGAT';
  return currentLocus.value.forward;
});

// Expresión génica (Transcripción, Splicing y Traducción)
const expressionResult = computed(() => {
  if (!currentLocus.value) return null;
  return express(currentLocus.value);
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
.watermark-status-bar {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-wrap: wrap;
  padding: 0.5rem 0.85rem;
  background: rgba(15, 23, 42, 0.65);
  border-radius: var(--md-sys-shape-corner-small);
  border: 1px solid rgba(56, 189, 248, 0.2);
}

.adn-viewer-container {
  position: relative;
  width: 100%;
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
