<template>
  <div class="dna-lab-layout">
    <!-- Header Científico del Secuenciador -->
    <div class="dna-header-card md3-card-outlined">
      <div class="header-main">
        <div class="header-icon-box">
          <Icon name="dna" size="24" />
        </div>
        <div class="header-text">
          <h2>Secuenciador, Complementariedad & Mutagénesis in Silico</h2>
          <span class="subtext">Motor de recombinación estocástica, edición dirigida y modelado tridimensional reactivo</span>
        </div>
      </div>

      <!-- Muestras de Referencia y Gestión de Experimentos -->
      <div class="header-actions-row">
        <div class="sample-chips-row">
          <span class="chips-label">Muestras Estándar:</span>
          <button class="md3-chip" @click="loadSample('ATCGATCGATCG')">
            <Icon name="tag" size="14" class="chip-icon" />
            <span>Control Corto (12bp)</span>
          </button>
          <button class="md3-chip" @click="loadSample('ATGCGATCGATCGATCGATC')">
            <Icon name="dna" size="14" class="chip-icon" />
            <span>Gen Sintético (20bp)</span>
          </button>
          <button class="md3-chip" @click="loadSample('ATGCCCCCGGGGTTTAA')">
            <Icon name="water_drop" size="14" class="chip-icon" />
            <span>Rica en GC (64.7%)</span>
          </button>
        </div>

        <div class="exp-management-buttons">
          <button class="md3-button-filled save-exp-btn" @click="saveCurrentExperiment" :disabled="loading" title="Guardar todo el proceso del experimento">
            <Icon name="save" size="18" />
            <span>Guardar Experimento</span>
          </button>
          <button class="md3-button-tonal load-exp-btn" @click="openLoadDialog" :disabled="loading" title="Cargar un experimento guardado para restaurar secuencias y modelo 3D">
            <Icon name="history" size="18" />
            <span>Cargar Experimento ({{ savedExperimentsList.length }})</span>
          </button>
          <button class="md3-button-outlined manual-exp-btn" @click="showManualDialog = true" title="Abrir Manual de Laboratorio interactivo con la guía paso a paso">
            <Icon name="menu_book" size="18" />
            <span>Manual del Lab</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Banner Toast de Notificación de Experimento Guardado / Cargado -->
    <div class="exp-toast-banner" v-if="experimentNotification">
      <Icon name="check_circle" size="20" class="toast-icon" />
      <div class="toast-text">
        <strong>{{ experimentNotification.title }}</strong>
        <span>{{ experimentNotification.message }}</span>
      </div>
      <button class="toast-close-btn" @click="experimentNotification = null" title="Cerrar">✕</button>
    </div>

    <!-- Panel de Entrada de Cadena y Citometría de Bases -->
    <div class="dna-input-section md3-card-outlined">
      <div class="input-primary-row">
        <div class="md3-textfield flex-grow">
          <label for="dna-seq-input">Hebra Codificante de Entrada (5' &rarr; 3'):</label>
          <div class="input-action-bar">
            <input 
              id="dna-seq-input"
              type="text" 
              v-model="sequenceInput" 
              placeholder="Introduce bases A, T, C, G (ej: ATCGTAGC)..."
              class="font-mono sequence-field"
              @input="handleInput"
            />
            <button class="md3-button-filled" @click="validateAndProcess" :disabled="loading">
              <Icon name="analytics" size="18" />
              <span>Validar Molde</span>
            </button>
            <button class="md3-button-tonal" @click="handleCopyDNA" :disabled="loading || !validationData?.is_valid" title="Crear Copia de Trabajo sin errores">
              <Icon name="content_copy" size="18" />
              <span>Generar Copia de Trabajo</span>
            </button>
            <button class="md3-chip" v-if="initialMoldSequence && initialMoldSequence !== sequenceInput" @click="resetToInitialMold" title="Restaurar a la secuencia original intacta">
              <Icon name="restart_alt" size="14" />
              <span>Restaurar a Molde</span>
            </button>
          </div>
          <div class="copy-feedback-banner" v-if="copyNotification">
            <Icon name="check_circle" size="16" class="copy-icon" />
            <span>{{ copyNotification }}</span>
          </div>
        </div>
      </div>

      <!-- Barra de Parámetros Biofísicos y Validación -->
      <div class="metrics-grid" v-if="validationData">
        <div class="metric-tile">
          <span class="m-k">Longitud Total</span>
          <span class="m-v font-mono">{{ validationData.length }} <small>pares de bases (bp)</small></span>
        </div>
        <div class="metric-tile">
          <span class="m-k">Contenido GC (%)</span>
          <div class="gc-progress-wrapper">
            <span class="m-v font-mono highlight">{{ validationData.gc_content }}%</span>
            <div class="gc-bar">
              <div class="gc-fill" :style="{ width: validationData.gc_content + '%' }"></div>
            </div>
          </div>
        </div>
        <div class="metric-tile">
          <span class="m-k">Distribución de Nucleótidos</span>
          <div class="nucleotide-badges">
            <span class="n-badge a"><span class="pip"></span>A: {{ validationData.base_counts?.A || 0 }}</span>
            <span class="n-badge t"><span class="pip"></span>T: {{ validationData.base_counts?.T || 0 }}</span>
            <span class="n-badge c"><span class="pip"></span>C: {{ validationData.base_counts?.C || 0 }}</span>
            <span class="n-badge g"><span class="pip"></span>G: {{ validationData.base_counts?.G || 0 }}</span>
          </div>
        </div>
        <div class="metric-tile">
          <span class="m-k">Estado de Calidad</span>
          <span :class="['status-chip', validationData.is_valid ? 'valid' : 'invalid']">
            <Icon :name="validationData.is_valid ? 'check_circle' : 'warning'" size="16" />
            <span>{{ validationData.is_valid ? 'Secuencia Válida' : (validationData.invalid_chars?.length ? `Bases No Válidas (${validationData.invalid_chars.join(', ')})` : 'Secuencia No Válida') }}</span>
          </span>
        </div>
      </div>

      <!-- Banner de Error si la secuencia contiene símbolos no válidos -->
      <div class="validation-error-alert" v-if="validationData && !validationData.is_valid">
        <Icon name="warning" size="20" class="err-icon" />
        <div class="err-text">
          <strong>Secuencia no válida para el motor genético:</strong>
          <span>{{ validationData.error_message || 'Contiene caracteres no canónicos. Solo se aceptan A, T, C, G.' }}</span>
        </div>
      </div>
    </div>

    <!-- Barra de Flujo Experimental Guiado (Paso 1 -> Paso 2 -> Paso 3 -> Paso 4 -> Paso 5) -->
    <div class="pipeline-stepper-card md3-card-outlined" v-if="validationData?.is_valid">
      <div class="stepper-header">
        <div class="stepper-title-box">
          <Icon name="science" size="18" class="stepper-icon" />
          <span class="stepper-tag">Flujo Científico Experimental (Fase 1):</span>
        </div>
        <span class="stepper-status font-mono">Paso {{ currentStep }} de 5: <strong>{{ currentStepName }}</strong></span>
      </div>
      <div class="stepper-track">
        <div :class="['step-pill', { active: currentStep === 1, done: currentStep > 1 }]">
          <span class="step-num">1</span>
          <span class="step-label">Molde Inicial</span>
        </div>
        <div class="step-line"></div>
        <div :class="['step-pill', { active: currentStep === 2, done: currentStep > 2 }]">
          <span class="step-num">2</span>
          <span class="step-label">Copia de Trabajo</span>
        </div>
        <div class="step-line"></div>
        <div :class="['step-pill', { active: currentStep === 3, done: currentStep > 3 }]">
          <span class="step-num">3</span>
          <span class="step-label">Inducción de Daño</span>
        </div>
        <div class="step-line"></div>
        <div :class="['step-pill', { active: currentStep === 4, done: currentStep > 4 }]">
          <span class="step-num">4</span>
          <span class="step-label">Detección (MMR)</span>
        </div>
        <div class="step-line"></div>
        <div :class="['step-pill', { active: currentStep === 5, done: isFullyRepaired }]">
          <span class="step-num">5</span>
          <span class="step-label">Reparación Homóloga</span>
        </div>
      </div>
    </div>

    <!-- Aviso si la secuencia actual no es válida -->
    <div class="invalid-sequence-placeholder md3-card-outlined" v-if="validationData && !validationData.is_valid">
      <div class="placeholder-content">
        <Icon name="warning" size="36" class="placeholder-icon" />
        <div>
          <h3>Secuencia con Símbolos No Permitidos</h3>
          <p>La cadena ingresada contiene caracteres no canónicos <strong>({{ (validationData.invalid_chars || []).join(', ') }})</strong>. Corrige la secuencia eliminando los símbolos no válidos para restaurar la doble hélice 3D y habilitar las operaciones de recombinación.</p>
        </div>
      </div>
    </div>

    <!-- Estación Molecular: Alineamiento 2D & Modelo 3D Reactivo de Doble Hélice -->
    <div class="molecular-workbench-grid" v-if="cleanSequence && validationData?.is_valid">
      <!-- Columna Izquierda: Track Interactivo de Nucleótidos y Telemetría -->
      <div class="sequence-track-card md3-card-outlined">
        <div class="track-header">
          <div class="track-title-group">
            <Icon name="dna" size="22" class="title-icon" />
            <div>
              <h3>Mapa de Alineamiento de Nucleótidos</h3>
              <span class="hint">Haz clic en cualquier base para posicionar el editor de mutación quirúrgica</span>
            </div>
          </div>

          <div class="spectral-legend">
            <span class="leg-item a"><span class="square"></span> A (Adenina)</span>
            <span class="leg-item t"><span class="square"></span> T (Timina)</span>
            <span class="leg-item c"><span class="square"></span> C (Citosina)</span>
            <span class="leg-item g"><span class="square"></span> G (Guanina)</span>
          </div>
        </div>

        <!-- Segmento Gráfico de Bases (5' a 3' y complementaria 3' a 5') -->
        <div class="track-viewport">
          <div class="track-strand-label">5'</div>
          <div class="bases-filmstrip">
            <div 
              v-for="(base, idx) in cleanSequence" 
              :key="idx"
              :class="['base-column', base.toLowerCase(), { selected: selectedPosition === idx }]"
              @click="selectBaseForMutation(idx, base)"
            >
              <span class="pos-index font-mono">{{ idx }}</span>
              <div class="base-capsule primary-strand">
                <span class="letter font-mono">{{ base }}</span>
              </div>
              <div class="hydrogen-bond">
                <span class="h-line"></span>
                <span class="h-line"></span>
                <span class="h-line" v-if="base === 'C' || base === 'G'"></span>
              </div>
              <div class="base-capsule comp-strand">
                <span class="letter font-mono">{{ complementMap[base] }}</span>
              </div>
            </div>
          </div>
          <div class="track-strand-label">3'</div>
        </div>

        <!-- Telemetría de Codificación y Hebra Antisentido -->
        <div class="encoded-data-row" v-if="complementStrand">
          <div class="encoded-field">
            <span class="field-label">Hebra Complementaria Antisentido (3' &rarr; 5'):</span>
            <code class="font-mono strand-box">{{ complementStrand }}</code>
          </div>
          <div class="encoded-field">
            <span class="field-label">Representación Binaria Biocontrolada (2 bits/base):</span>
            <code class="font-mono strand-box binary">{{ binaryStrand }}</code>
          </div>
        </div>
      </div>

      <!-- Columna Derecha: Modelo Tridimensional Reactivo de la Doble Hélice (B-DNA) -->
      <DNAHelix3D 
        :sequence="cleanSequence" 
        :selectedPosition="selectedPosition" 
        @selectBase="handleHelixBaseSelect"
      />
    </div>

    <!-- Panel de Operaciones Genéticas (Modo 1 Replicación vs Modo 2 Mutación Controlada) -->
    <div class="operations-container" v-if="cleanSequence">
      <!-- MODO 2: Mutación Controlada (Precisión CRISPR / Sustitución) -->
      <div class="op-panel md3-card-outlined mode-controlled">
        <div class="op-panel-header">
          <div class="header-icon-mini">
            <Icon name="content_cut" size="18" />
          </div>
          <div>
            <h4>Modo 2: Edición Dirigida (Intervención CRISPR)</h4>
            <span class="op-sub">Alteración puntual precisa en coordenadas específicas de la cadena</span>
          </div>
        </div>

        <div class="op-form-grid">
          <div class="md3-textfield">
            <label>Posición Cero-Indexada:</label>
            <input type="number" v-model.number="controlledForm.position" :min="0" :max="cleanSequence.length" class="font-mono" />
          </div>

          <div class="md3-textfield">
            <label>Tipo de Evento:</label>
            <select v-model="controlledForm.type">
              <option value="substitution">Sustitución (Puntual)</option>
              <option value="insertion">Inserción (+1 Base)</option>
              <option value="deletion">Deleción (-1 Base)</option>
            </select>
          </div>

          <div class="md3-textfield full-span" v-if="controlledForm.type !== 'deletion'">
            <label>Base a Incorporar:</label>
            <div class="base-segmented-selector">
              <button 
                v-for="b in ['A', 'T', 'C', 'G']" 
                :key="b"
                :class="['seg-btn', b.toLowerCase(), { active: controlledForm.newBase === b }]"
                @click="controlledForm.newBase = b"
                type="button"
              >
                {{ b }}
              </button>
            </div>
          </div>
        </div>

        <button class="md3-button-filled" @click="applyControlledMutation" :disabled="loading">
          <Icon name="content_cut" size="18" />
          <span>Aplicar Mutación Dirigida</span>
        </button>
      </div>

      <!-- MODO 1: Replicación Estocástica (Polimerasa con Tasa de Error) -->
      <div class="op-panel md3-card-outlined mode-stochastic">
        <div class="op-panel-header">
          <div class="header-icon-mini">
            <Icon name="shuffle" size="18" />
          </div>
          <div>
            <h4>Modo 1: Replicación Celular Estocástica</h4>
            <span class="op-sub">Simulación de duplicación con probabilidad estocástica de error de polimerasa</span>
          </div>
        </div>

        <div class="slider-module">
          <div class="slider-telemetry">
            <span class="slider-title">Tasa de Error por Base:</span>
            <span class="slider-rate font-mono">{{ (mutationRate * 100).toFixed(1) }}%</span>
          </div>
          <input 
            type="range" 
            v-model.number="mutationRate" 
            min="0" 
            max="0.20" 
            step="0.005" 
            class="md3-range-slider"
          />
          <div class="slider-marks">
            <span>0.0% (Alta Fidelidad)</span>
            <span>10.0% (Hipermutación)</span>
            <span>20.0% (Umbral Letal)</span>
          </div>
        </div>

        <button class="md3-button-tonal" @click="replicateWithProbabilities" :disabled="loading">
          <Icon name="restart_alt" size="18" />
          <span>Simular Duplicación Estocástica</span>
        </button>
      </div>
    </div>

    <!-- Inspector Comparativo de Mutaciones (Diff Inspector Estilo NCBI BLAST) -->
    <div class="diff-inspector-card md3-card-outlined" v-if="diffResult">
      <div class="diff-header">
        <div class="diff-title-row">
          <Icon name="compare_arrows" size="24" class="diff-icon" />
          <div>
            <h3>Reporte de Mutagénesis y Diferencias de Secuencia</h3>
            <span class="diff-meta">Alineamiento de extremos apareados (Referencia vs Copia Sintetizada)</span>
          </div>
        </div>

        <div :class="['diff-badge-pill', { alert: diffResult.difference_count > 0 }]">
          <Icon :name="diffResult.difference_count > 0 ? 'warning' : 'check_circle'" size="16" class="pill-icon" />
          <span>{{ diffResult.difference_count }} mutaciones detectadas</span>
        </div>
      </div>

      <!-- Comparador Visual Alineado -->
      <div class="diff-alignment-table">
        <div class="alignment-row">
          <span class="row-tag">REFERENCIA:</span>
          <code class="font-mono strand-stream">{{ diffResult.reference }}</code>
        </div>
        <div class="alignment-row">
          <span class="row-tag modified">SINTETIZADA:</span>
          <code class="font-mono strand-stream mod-stream">{{ diffResult.modified }}</code>
        </div>
      </div>

      <!-- Lista Detallada de Eventos de Mutación -->
      <div class="mutation-events-grid" v-if="diffResult.differences.length > 0">
        <div v-for="(d, i) in diffResult.differences" :key="i" class="mutation-card">
          <div class="m-top">
            <span class="m-coord font-mono">Posición {{ d.position }}</span>
            <span :class="['m-type-chip', d.status]">{{ d.status }}</span>
          </div>
          <div class="m-transition">
            <span class="base-old font-mono">{{ d.reference_base || '∅' }}</span>
            <Icon name="arrow_forward" size="14" class="arrow" />
            <span class="base-new font-mono">{{ d.modified_base || '∅' }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 3.1 & 3.2: Detección de Apareamientos Incorrectos & Reparación Guiada por Referencia -->
    <div class="mismatch-repair-card md3-card-outlined" v-if="cleanSequence">
      <div class="section-header">
        <div class="section-title-group">
          <Icon name="build" size="22" class="section-icon" />
          <div>
            <h3>3. Mecanismos de Reparación: Apareamientos Dúplex & Referencia Homóloga</h3>
            <span class="subtext">Control de calidad de pares canónicos Watson-Crick (A–T, C–G) y corrección asistida por plantilla</span>
          </div>
        </div>
      </div>

      <div class="duplex-work-grid">
        <!-- Columna 1: Detección de Desapareamientos -->
        <div class="duplex-card">
          <div class="card-subtitle">
            <Icon name="science" size="18" />
            <span>3.1 Detección de Apareamientos Incorrectos (Dúplex)</span>
          </div>
          <p class="desc-text">
            Compara la hebra codificante con una segunda cadena apareada para identificar pares no canónicos.
          </p>

          <div class="md3-textfield">
            <label>Cadena Apareada a Comprobar:</label>
            <div class="input-with-actions">
              <input 
                type="text" 
                v-model="duplexStrand" 
                placeholder="Cadena apareada (A, T, C, G)..." 
                class="font-mono sequence-field"
              />
              <button class="md3-chip" type="button" @click="fillDuplexWithCanonical" title="Usar complementaria estándar">
                <span>Complementaria</span>
              </button>
              <button class="md3-chip" type="button" @click="insertDuplexMismatch" title="Introducir un apareamiento erróneo">
                <Icon name="shuffle" size="14" />
                <span>Inducir Error</span>
              </button>
            </div>
          </div>

          <button class="md3-button-filled" @click="runMismatchDetection" :disabled="loading">
            <Icon name="analytics" size="18" />
            <span>Escanear Apareamientos Dúplex</span>
          </button>

          <!-- Resultados de Apareamientos -->
          <div class="mismatch-feedback" v-if="mismatchResult">
            <div :class="['status-banner', mismatchResult.is_fully_canonical ? 'success' : 'warning']">
              <Icon :name="mismatchResult.is_fully_canonical ? 'check_circle' : 'warning'" size="18" />
              <span>
                {{ mismatchResult.is_fully_canonical 
                  ? 'Apareamiento 100% canónico Watson-Crick.' 
                  : `${mismatchResult.mismatch_count} apareamiento(s) no canónico(s) detectado(s).` }}
              </span>
            </div>

            <div class="pairs-visual-strip">
              <div 
                v-for="(pair, idx) in duplexPairsDisplay" 
                :key="idx" 
                :class="['pair-pill', pair.is_canonical ? 'canonical' : 'non-canonical']"
                :title="pair.note"
              >
                <span class="p-idx font-mono">{{ idx }}</span>
                <span class="p-b1 font-mono">{{ pair.b1 }}</span>
                <span class="p-conn">:</span>
                <span class="p-b2 font-mono">{{ pair.b2 }}</span>
              </div>
            </div>

            <div class="scientific-disclaimer-mini" v-if="mismatchResult.mismatch_count > 0">
              <Icon name="info" size="14" />
              <span>Regla del modelo: El sistema marca el error sin conjeturar automáticamente la base original en ausencia de plantilla fiable.</span>
            </div>
          </div>
        </div>

        <!-- Columna 2: Reparación Guiada por Referencia -->
        <div class="duplex-card">
          <div class="card-subtitle">
            <Icon name="shield" size="18" />
            <span>3.2 Reparación Guiada por Referencia Fiable</span>
          </div>
          <p class="desc-text">
            Reemplaza las posiciones alteradas únicamente cuando están autorizadas y respaldadas por una plantilla fiable.
          </p>

          <div class="md3-textfield">
            <label>Secuencia de Referencia Homóloga Fiable:</label>
            <input 
              type="text" 
              v-model="referenceStrand" 
              placeholder="Secuencia homóloga de referencia..." 
              class="font-mono sequence-field"
            />
          </div>

          <div class="action-buttons-row">
            <button class="md3-button-tonal" @click="useCurrentAsReference">
              <Icon name="tag" size="16" />
              <span>Usar Inicial</span>
            </button>
            <button class="md3-button-filled" @click="runReferenceRepair" :disabled="loading">
              <Icon name="build" size="18" />
              <span>Reparar con Referencia</span>
            </button>
          </div>

          <!-- Resultado de Reparación -->
          <div class="repair-feedback" v-if="repairResult">
            <div :class="['status-banner', repairResult.matches_reference ? 'success' : 'info']">
              <Icon :name="repairResult.matches_reference ? 'check_circle' : 'info'" size="18" />
              <div>
                <strong>Estado: {{ repairResult.status }}</strong>
                <p>
                  {{ repairResult.matches_reference 
                    ? 'Secuencia completamente restaurada conforme a la plantilla de referencia.' 
                    : `Reparadas ${repairResult.repaired_positions?.length || 0} posiciones autorizadas.` }}
                </p>
              </div>
            </div>

            <div class="repaired-seq-preview">
              <span class="tag">Secuencia Resultante:</span>
              <code class="font-mono">{{ repairResult.repaired_sequence }}</code>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 3.3: Modelo Conceptual de Roturas de ADN (DSB) & Unión de Extremos -->
    <div class="dsb-card md3-card-outlined" v-if="cleanSequence">
      <div class="section-header">
        <div class="section-title-group">
          <Icon name="content_cut" size="22" class="section-icon alert" />
          <div>
            <h3>3.3 Extensión Conceptual: Roturas Bicatenarias (DSB) y Vías de Reparación</h3>
            <span class="subtext">Comparación abstracta entre Homología (HDR) y Unión de Extremos No Homólogos (NHEJ)</span>
          </div>
        </div>
      </div>

      <div class="dsb-controls-row">
        <div class="md3-textfield break-pos-field">
          <label>Posición del Punto de Rotura (1 a {{ Math.max(1, cleanSequence.length - 1) }}):</label>
          <input 
            type="number" 
            v-model.number="breakPosition" 
            :min="1" 
            :max="Math.max(1, cleanSequence.length - 1)" 
            class="font-mono"
          />
        </div>

        <div class="dsb-action-buttons">
          <button class="md3-button-filled hdr-btn" @click="runBreakSimulation('homology_directed')" :disabled="loading">
            <Icon name="shield" size="18" />
            <span>Reparar vía HDR (Homología)</span>
          </button>
          <button class="md3-button-tonal nhej-btn" @click="runBreakSimulation('end_joining')" :disabled="loading">
            <Icon name="build" size="18" />
            <span>Reparar vía NHEJ (Unión Extremos)</span>
          </button>
        </div>
      </div>

      <!-- Visualización de Rotura y Fragmentación -->
      <div class="dsb-result-panel" v-if="breakResult">
        <div class="fragments-display">
          <div class="frag-box">
            <span class="frag-label">Extremo 5' (Fragmento Izq):</span>
            <code class="font-mono">{{ breakResult.fragments[0] }}</code>
          </div>
          <div class="cut-marker">
            <Icon name="content_cut" size="18" />
            <span>ROTURA</span>
          </div>
          <div class="frag-box">
            <span class="frag-label">Extremo 3' (Fragmento Der):</span>
            <code class="font-mono">{{ breakResult.fragments[1] }}</code>
          </div>
        </div>

        <div class="recombined-box">
          <div class="rec-header">
            <span class="rec-title">Secuencia Recombinada ({{ breakResult.repair_method?.toUpperCase() }}):</span>
            <span :class="['scar-badge', breakResult.scar?.includes('deletion') ? 'scarred' : 'clean']">
              Cicatriz: {{ breakResult.scar }}
            </span>
          </div>
          <code class="font-mono rec-seq">{{ breakResult.repaired_sequence }}</code>
          <p class="rec-desc">{{ breakResult.description }}</p>
        </div>
      </div>
    </div>

    <!-- 7 & 10: Cuaderno de Bitácora / Registro de Experimentos & Marco Científico -->
    <div class="audit-log-card md3-card-outlined">
      <div class="section-header">
        <div class="section-title-group">
          <Icon name="history" size="22" class="section-icon" />
          <div>
            <h3>7. Registro de Experimentos & Trazabilidad de Operaciones</h3>
            <span class="subtext">Auditoría inmutable de secuencias, mutaciones, métodos y resoluciones</span>
          </div>
        </div>
        <button class="md3-chip" type="button" @click="fetchLogs">
          <Icon name="restart_alt" size="14" />
          <span>Refrescar Registro ({{ experimentLogs.length }})</span>
        </button>
      </div>

      <!-- Banner Rigor Científico Sección 10 -->
      <div class="scientific-notice-banner">
        <div class="notice-icon">
          <Icon name="science" size="24" />
        </div>
        <div class="notice-content">
          <h4>Nota Científica y Suposiciones del Modelo (Sección 10)</h4>
          <p>
            La reparación real del ADN implica complejos proteicos dinámicos (MutS/MutL, ATM/ATR, RAD51, DNA-PKcs, Ligasa IV), señales de fosforilación y topología de la cromatina. Este módulo representa <strong>únicamente reglas didácticas computacionales seleccionadas</strong>. La presencia de una secuencia de referencia permite la corrección computacional, pero no implica que una célula real siempre identifique o repare con éxito dicha alteración. Los resultados del programa constituyen <strong>simulaciones didácticas in silico</strong> y no evidencia experimental molecular directa.
          </p>
        </div>
      </div>

      <!-- Tabla de Eventos -->
      <div class="events-table-wrapper" v-if="experimentLogs.length > 0">
        <table class="events-table">
          <thead>
            <tr>
              <th>ID Experimento</th>
              <th>Operación</th>
              <th>Secuencia Inicial</th>
              <th>Secuencia Final</th>
              <th>Referencia</th>
              <th>Resultado</th>
              <th>Acción</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="ev in experimentLogs" :key="ev.experiment_id">
              <td><code class="font-mono exp-id">{{ ev.experiment_id }}</code></td>
              <td><span class="op-chip">{{ ev.operation_type }}</span></td>
              <td><code class="font-mono seq-cell">{{ ev.initial_sequence }}</code></td>
              <td><code class="font-mono seq-cell">{{ ev.final_sequence }}</code></td>
              <td>
                <span v-if="ev.reference_used" class="font-mono ref-text">{{ ev.reference_used }}</span>
                <span v-else class="no-ref">Sin plantilla</span>
              </td>
              <td>
                <span :class="['res-status', ev.repair_result?.status || 'ok']">
                  {{ ev.repair_result?.status || 'registrado' }}
                </span>
              </td>
              <td>
                <button class="md3-chip load-row-chip" @click="loadEventOrExperiment(ev)" title="Cargar este estado en el laboratorio">
                  <Icon name="arrow_forward" size="12" />
                  <span>Cargar</span>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Diálogo Modal: Cargar Experimento Guardado -->
    <div class="md3-dialog-backdrop" v-if="showLoadDialog" @click.self="showLoadDialog = false">
      <div class="md3-dialog-surface md3-card-outlined">
        <div class="dialog-header">
          <div class="dialog-title-group">
            <Icon name="history" size="24" class="dialog-icon" />
            <div>
              <h3>Cargar Experimento Guardado</h3>
              <span class="dialog-sub">Selecciona un experimento previo para restaurar secuencias, mutaciones y el modelo 3D</span>
            </div>
          </div>
          <button class="dialog-close-btn" @click="showLoadDialog = false" title="Cerrar">✕</button>
        </div>

        <div class="dialog-body">
          <div class="empty-experiments-notice" v-if="savedExperimentsList.length === 0">
            <Icon name="info" size="32" class="empty-icon" />
            <h4>No hay experimentos guardados</h4>
            <p>Realiza mutaciones o reparaciones en el laboratorio y pulsa <strong>"Guardar Experimento"</strong> para conservarlos aquí.</p>
          </div>

          <div class="saved-experiments-list" v-else>
            <div 
              v-for="exp in savedExperimentsList" 
              :key="exp.experiment_id" 
              class="saved-exp-card"
            >
              <div class="card-main-info">
                <div class="exp-id-row">
                  <span class="exp-badge font-mono">{{ exp.experiment_id }}</span>
                  <span class="exp-date">{{ formatDate(exp.created_at) }}</span>
                  <span :class="['exp-status-chip', exp.status]">{{ exp.status }}</span>
                </div>
                <h4 class="exp-title">{{ exp.name }}</h4>

                <div class="exp-sequences-summary">
                  <div class="summary-line">
                    <span class="label">Inicial (Molde):</span>
                    <code class="font-mono">{{ exp.initial_sequence }}</code>
                  </div>
                  <div class="summary-line" v-if="exp.mutation_applied?.type">
                    <span class="label">Alteración:</span>
                    <span class="val">{{ formatMutationLabel(exp.mutation_applied) }}</span>
                  </div>
                  <div class="summary-line" v-if="exp.final_sequence">
                    <span class="label">Final:</span>
                    <code class="font-mono">{{ exp.final_sequence }}</code>
                  </div>
                </div>
              </div>

              <div class="card-action-box">
                <button class="md3-button-filled load-btn" @click="loadExperiment(exp)">
                  <Icon name="arrow_forward" size="16" />
                  <span>Cargar en Lab</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Diálogo Modal: Manual de Laboratorio Interactivo -->
    <div class="md3-dialog-backdrop" v-if="showManualDialog" @click.self="showManualDialog = false">
      <div class="md3-dialog-surface manual-dialog-surface md3-card-outlined">
        <div class="dialog-header">
          <div class="dialog-title-group">
            <Icon name="menu_book" size="24" class="dialog-icon highlight" />
            <div>
              <h3>Manual Técnico y Guía Operativa del Laboratorio</h3>
              <span class="dialog-sub">Explicación paso a paso de cada proceso biológico in silico y función de cada botón</span>
            </div>
          </div>
          <button class="dialog-close-btn" @click="showManualDialog = false" title="Cerrar Manual">✕</button>
        </div>

        <div class="manual-tabs-bar">
          <button 
            :class="['manual-tab-btn', { active: manualActiveTab === 'flow' }]" 
            @click="manualActiveTab = 'flow'"
          >
            <Icon name="science" size="16" />
            <span>1. Flujo Paso a Paso (1 a 5)</span>
          </button>
          <button 
            :class="['manual-tab-btn', { active: manualActiveTab === 'buttons' }]" 
            @click="manualActiveTab = 'buttons'"
          >
            <Icon name="build" size="16" />
            <span>2. Guía de Cada Botón ("Pa' qué")</span>
          </button>
          <button 
            :class="['manual-tab-btn', { active: manualActiveTab === 'protocols' }]" 
            @click="manualActiveTab = 'protocols'"
          >
            <Icon name="biotech" size="16" />
            <span>3. Protocolos de Ensayo</span>
          </button>
        </div>

        <div class="dialog-body manual-dialog-body">
          <!-- Pestaña 1: Flujo Experimental Paso a Paso -->
          <div v-if="manualActiveTab === 'flow'" class="manual-section-content">
            <div class="manual-hero-banner">
              <Icon name="science" size="22" />
              <div>
                <h4>Filosofía del Flujo Científico In Silico</h4>
                <p>En la biología y en este software, un error de apareamiento (ej: A–G) marca una discordancia pero no revela por sí solo cuál es la base correcta original. La corrección requiere obligatoriamente una <strong>hebra molde parental o referencia homóloga</strong>.</p>
              </div>
            </div>

            <div class="flow-steps-accordion">
              <div class="flow-step-item">
                <div class="step-badge step-1">Paso 1</div>
                <div class="step-info">
                  <h5>Molde Inicial Validado (Hebra Parental)</h5>
                  <p>La cadena de entrada que escribes o seleccionas se fija como el <strong>molde de referencia inmutable</strong>. El sistema valida las bases (A, T, C, G) en tiempo real, bloqueando el render 3D si hay caracteres espurios (ej: 'O' o 'X') para garantizar la integridad estequiométrica.</p>
                </div>
              </div>

              <div class="flow-step-item">
                <div class="step-badge step-2">Paso 2</div>
                <div class="step-info">
                  <h5>Generación de Copia de Trabajo</h5>
                  <p>Al pulsar <em>"Copiar Secuencia"</em>, la maquinaria celular clona la hebra asegurando una identidad del 100%. Las mutaciones posteriores se realizan sobre esta copia de trabajo, protegiendo el molde original.</p>
                </div>
              </div>

              <div class="flow-step-item">
                <div class="step-badge step-3">Paso 3</div>
                <div class="step-info">
                  <h5>Inducción de Daño Molecular</h5>
                  <p>Se induce una lesión o alteración sobre la copia de trabajo mediante 3 vías: mutación dirigida CRISPR (sustitución, inserción, deleción), replicación estocástica celular con tasa de error de polimerasa, o rotura bicatenaria (DSB).</p>
                </div>
              </div>

              <div class="flow-step-item">
                <div class="step-badge step-4">Paso 4</div>
                <div class="step-info">
                  <h5>Detección Automática de Daño (MMR & Diff)</h5>
                  <p>Al ocurrir cualquier mutación, el motor compara instantáneamente la cadena mutada contra la <strong>complementaria canónica del molde inicial</strong>. Detecta apareamientos erróneos no canónicos (A-G, C-T) y calcula el reporte Diff sin intervención manual.</p>
                </div>
              </div>

              <div class="flow-step-item">
                <div class="step-badge step-5">Paso 5</div>
                <div class="step-info">
                  <h5>Reparación Guiada por Homología / Resolución de Cicatriz</h5>
                  <p>Se utiliza la referencia homóloga para restaurar las bases alteradas bajo verificación estricta de fidelidad. En roturas DSB, se compara la vía HDR (alta fidelidad, sin cicatriz) con la vía NHEJ (unión directa propensa a microdeleciones).</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Pestaña 2: Diccionario de Cada Botón -->
          <div v-if="manualActiveTab === 'buttons'" class="manual-section-content">
            <div class="button-guide-grid">
              <!-- Header y Sesión -->
              <div class="button-guide-card">
                <div class="card-tag">Cabecera & Sesión</div>
                <div class="btn-entry">
                  <span class="btn-name filled"><Icon name="save" size="14" /> Guardar Experimento</span>
                  <p>Guarda en memoria y disco (<code>saved_experiments.json</code>) el ensayo completo: molde inicial, copia, mutaciones, resultado MMR, reparación, secuencia final y diffs.</p>
                </div>
                <div class="btn-entry">
                  <span class="btn-name tonal"><Icon name="history" size="14" /> Cargar Experimento</span>
                  <p>Abre el catálogo de experimentos guardados para restaurar con un solo clic el estado exacto en el visor 3D, mapas y campos de edición.</p>
                </div>
                <div class="btn-entry">
                  <span class="btn-name chip"><Icon name="restart_alt" size="14" /> Restaurar a Molde</span>
                  <p>Descarta mutaciones y roturas acumuladas en la sesión y regresa de inmediato al molde parental de partida.</p>
                </div>
              </div>

              <!-- Entrada y Métricas -->
              <div class="button-guide-card">
                <div class="card-tag">Entrada & Secuenciador</div>
                <div class="btn-entry">
                  <span class="btn-name filled"><Icon name="analytics" size="14" /> Procesar Secuencia</span>
                  <p>Re-calcula en el backend las métricas biofísicas (longitud, %GC, distribución), actualiza la hebra antisentido y el modelo 3D.</p>
                </div>
                <div class="btn-entry">
                  <span class="btn-name tonal"><Icon name="content_copy" size="14" /> Copiar Secuencia</span>
                  <p>Genera la copia fidedigna de trabajo con verificación de identidad al 100%, avanzando el flujo al Paso 2.</p>
                </div>
                <div class="btn-entry">
                  <span class="btn-name chip"><Icon name="tag" size="14" /> Muestras Estándar</span>
                  <p>Carga instantáneamente secuencias calibradas: Control Corto (12bp), Gen Sintético (20bp) o Rica en GC (64.7%).</p>
                </div>
              </div>

              <!-- Visor 3D -->
              <div class="button-guide-card">
                <div class="card-tag">Visor 3D (B-DNA)</div>
                <div class="btn-entry">
                  <span class="btn-name chip"><Icon name="dna" size="14" /> Modo Curva / Lineal</span>
                  <p>Alterna la forma espacial entre la ondulación orgánica natural <em>in vivo</em> o un eje rectilíneo de difracción cristalográfica.</p>
                </div>
                <div class="btn-entry">
                  <span class="btn-name icon-btn"><Icon name="rotate" size="14" /> Giro 360°</span>
                  <p>Pausa o reanuda la rotación orbital continua de la macromolécula para inspección estática de enlaces.</p>
                </div>
                <div class="btn-entry">
                  <span class="btn-name icon-btn"><Icon name="zoom" size="14" /> Zoom + / -</span>
                  <p>Acerca o aleja la cámara virtual respecto al centro de masa de la molécula.</p>
                </div>
                <div class="btn-entry">
                  <span class="btn-name icon-btn"><Icon name="restart_alt" size="14" /> Perspectiva Cenital</span>
                  <p>Restablece el encuadre, inclinación y orientación inicial de la cámara 3D.</p>
                </div>
              </div>

              <!-- Mutación y Recombinación -->
              <div class="button-guide-card">
                <div class="card-tag">Mutagénesis</div>
                <div class="btn-entry">
                  <span class="btn-name filled"><Icon name="content_cut" size="14" /> Aplicar Mutación Dirigida</span>
                  <p>Ejecuta una edición quirúrgica (sustitución, inserción o deleción) en la coordenada seleccionada mediante tecnología conceptual CRISPR.</p>
                </div>
                <div class="btn-entry">
                  <span class="btn-name tonal"><Icon name="shuffle" size="14" /> Simular Duplicación Estocástica</span>
                  <p>Sintetiza una nueva generación replicando la hebra con una probabilidad de error por base configurable del 0% al 20%.</p>
                </div>
              </div>

              <!-- Reparación y Roturas -->
              <div class="button-guide-card">
                <div class="card-tag">Reparación & Roturas (DSB)</div>
                <div class="btn-entry">
                  <span class="btn-name filled"><Icon name="analytics" size="14" /> Escanear Apareamientos Dúplex</span>
                  <p>Comprueba cada par de bases en la doble cadena dúplex para identificar desajustes no canónicos (MMR).</p>
                </div>
                <div class="btn-entry">
                  <span class="btn-name chip"><Icon name="shuffle" size="14" /> Inducir Error</span>
                  <p>Introduce a propósito un apareamiento erróneo en el centro del dúplex para poner a prueba el sistema de detección.</p>
                </div>
                <div class="btn-entry">
                  <span class="btn-name filled"><Icon name="build" size="14" /> Reparar con Referencia</span>
                  <p>Sustituye únicamente las bases erróneas autorizadas y respaldadas por la secuencia de referencia homóloga.</p>
                </div>
                <div class="btn-entry">
                  <span class="btn-name filled hdr-color"><Icon name="shield" size="14" /> Reparar vía HDR</span>
                  <p>Reconstruye la rotura de doble cadena con alta fidelidad asistida por plantilla homóloga (sin cicatriz).</p>
                </div>
                <div class="btn-entry">
                  <span class="btn-name tonal nhej-color"><Icon name="build" size="14" /> Reparar vía NHEJ</span>
                  <p>Une directamente los extremos rotos sin plantilla, introduciendo cicatrices mutacionales o microdeleciones.</p>
                </div>
              </div>

              <!-- Auditoría y Bitácora -->
              <div class="button-guide-card">
                <div class="card-tag">Auditoría & Trazabilidad</div>
                <div class="btn-entry">
                  <span class="btn-name chip"><Icon name="restart_alt" size="14" /> Refrescar Registro</span>
                  <p>Actualiza la bitácora con los eventos moleculares procesados más recientes por el servidor.</p>
                </div>
                <div class="btn-entry">
                  <span class="btn-name chip"><Icon name="arrow_forward" size="14" /> Cargar (en fila)</span>
                  <p>Restaura al instante en el laboratorio la secuencia y parámetros exactos del evento seleccionado.</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Pestaña 3: Protocolos de Ensayo -->
          <div v-if="manualActiveTab === 'protocols'" class="manual-section-content">
            <div class="protocol-card">
              <h4>Protocolo A: Ensayo de Mutación Quirúrgica y Reparación por Homología</h4>
              <ol class="protocol-steps-list">
                <li>Verifica que la secuencia inicial esté validada (Paso 1).</li>
                <li>Pulsa <strong>"Copiar Secuencia"</strong> para fijar la copia de trabajo (Paso 2).</li>
                <li>Haz clic en la base 4 del Mapa 2D o de la hélice 3D.</li>
                <li>Selecciona el tipo <em>"Sustitución"</em> y la base <em>"G"</em> en el panel CRISPR.</li>
                <li>Pulsa <strong>"Aplicar Mutación Dirigida"</strong> (el sistema detecta el error en el Paso 4 automáticamente).</li>
                <li>Baja al panel <em>3.2 Reparación Guiada por Referencia</em> y pulsa <strong>"Usar Inicial"</strong> y luego <strong>"Reparar con Referencia"</strong>.</li>
                <li>La secuencia vuelve a quedar restaurada al 100% (Paso 5). Pulsa <strong>"Guardar Experimento"</strong> para conservarlo.</li>
              </ol>
            </div>

            <div class="protocol-card">
              <h4>Protocolo B: Roturas Bicatenarias (DSB) y Comparación HDR vs NHEJ</h4>
              <ol class="protocol-steps-list">
                <li>Carga la muestra <em>"Gen Sintético (20bp)"</em> y pulsa <em>"Copiar Secuencia"</em>.</li>
                <li>En la sección 3.3, fija la rotura en la posición 8.</li>
                <li>Pulsa <strong>"Reparar vía NHEJ"</strong>: observa la escisión de fragmentos y la cicatriz molecular resultante.</li>
                <li>Pulsa <strong>"Restaurar a Molde"</strong> en la cabecera para restablecer el gen intacto.</li>
                <li>Ahora pulsa <strong>"Reparar vía HDR"</strong>: observa la reconstitución limpia y perfecta asistida por la referencia homóloga.</li>
              </ol>
            </div>
          </div>
        </div>

        <div class="dialog-footer">
          <span class="doc-file-hint font-mono">Documento completo persistido en: MANUAL_LABORATORIO_ADN.txt</span>
          <button class="md3-button-filled" @click="showManualDialog = false">
            <span>Entendido, Volver al Laboratorio</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { api } from '../api/client';
import Icon from './Icon.vue';
import DNAHelix3D from './DNAHelix3D.vue';

const sequenceInput = ref('ATCGATCGATCG');
const initialMoldSequence = ref('ATCGATCGATCG');
const cleanSequence = computed(() => {
  return validationData.value?.is_valid ? sequenceInput.value.trim().toUpperCase() : '';
});
const validationData = ref(null);
const complementStrand = ref('');
const binaryStrand = ref('');
const selectedPosition = ref(0);
const loading = ref(false);

const complementMap = { A: 'T', T: 'A', C: 'G', G: 'C' };

const controlledForm = ref({
  position: 0,
  type: 'substitution',
  newBase: 'G'
});

const mutationRate = ref(0.02);
const diffResult = ref(null);

// Fase 1: Copia y validación
const copyNotification = ref('');

// Fase 1: Apareamientos Dúplex y Reparación Guiada
const duplexStrand = ref('');
const mismatchResult = ref(null);
const referenceStrand = ref('');
const repairResult = ref(null);

// Fase 1: Roturas Bicatenarias (DSB)
const breakPosition = ref(4);
const breakResult = ref(null);

// Fase 1: Bitácora de Experimentos (Trazabilidad) y Persistencia
const experimentLogs = ref([]);
const savedExperimentsList = ref([]);
const showLoadDialog = ref(false);
const showManualDialog = ref(false);
const manualActiveTab = ref('flow');
const experimentNotification = ref(null);
const lastMutationApplied = ref(null);

const isFullyRepaired = computed(() => {
  return repairResult.value?.matches_reference === true || (breakResult.value?.matches_initial === true && diffResult.value?.difference_count === 0);
});

const currentStep = computed(() => {
  if (repairResult.value || (breakResult.value && breakResult.value.status.includes('repaired'))) return 5;
  if ((diffResult.value && diffResult.value.difference_count > 0) || (mismatchResult.value && mismatchResult.value.mismatch_count > 0)) return 4;
  if (lastMutationApplied.value) return 3;
  if (copyNotification.value) return 2;
  return 1;
});

const currentStepName = computed(() => {
  switch (currentStep.value) {
    case 1: return 'Molde Inicial Validado';
    case 2: return 'Copia de Trabajo Activa';
    case 3: return 'Daño Molecular Inducido';
    case 4: return 'Detección de Daño (MMR/Diff)';
    case 5: return isFullyRepaired.value ? 'Restaurado por Homología' : 'Reparación / Cicatriz';
    default: return 'Inicio';
  }
});

function formatDate(isoStr) {
  if (!isoStr) return '';
  try {
    const d = new Date(isoStr);
    return d.toLocaleString('es-ES', { 
      day: '2-digit', month: '2-digit', year: 'numeric',
      hour: '2-digit', minute: '2-digit', second: '2-digit'
    });
  } catch (e) {
    return isoStr;
  }
}

function formatMutationLabel(mut) {
  if (!mut) return 'Sin mutación';
  if (mut.type === 'substitution') {
    return `Sustitución en pos ${mut.position}: ${mut.original_base || '∅'} → ${mut.new_base}`;
  }
  if (mut.type === 'insertion') {
    return `Inserción en pos ${mut.position}: +${mut.new_base}`;
  }
  if (mut.type === 'deletion') {
    return `Deleción en pos ${mut.position} (-1 base)`;
  }
  if (mut.type === 'stochastic_replication') {
    return `Replicación estocástica (${(mut.rate * 100).toFixed(1)}% tasa de error)`;
  }
  if (mut.type === 'double_strand_break') {
    return `Rotura de ADN (DSB) en pos ${mut.break_position}`;
  }
  return mut.type || 'Alteración puntual';
}

async function fetchSavedExperiments() {
  try {
    const res = await api.listDNAExperiments();
    savedExperimentsList.value = res.experiments || [];
  } catch (err) {
    console.error('Error al listar experimentos guardados:', err);
  }
}

function openLoadDialog() {
  showLoadDialog.value = true;
  fetchSavedExperiments();
}

async function saveCurrentExperiment() {
  const current = sequenceInput.value.trim().toUpperCase();
  if (!current) {
    alert("Introduce primero una secuencia válida para poder guardar un experimento.");
    return;
  }

  try {
    loading.value = true;
    const initial = initialMoldSequence.value || referenceStrand.value || current;

    let mutationInfo = lastMutationApplied.value;
    if (!mutationInfo && diffResult.value && diffResult.value.difference_count > 0) {
      mutationInfo = {
        type: controlledForm.value.type,
        position: controlledForm.value.position,
        new_base: controlledForm.value.newBase,
        diff_count: diffResult.value.difference_count
      };
    } else if (!mutationInfo && breakResult.value) {
      mutationInfo = {
        type: 'double_strand_break',
        break_position: breakResult.value.break_position,
        method: breakResult.value.repair_method
      };
    }

    const payload = {
      name: `Ensayo ${current.slice(0, 10)} (${mutationInfo ? mutationInfo.type : 'control'})`,
      initial_sequence: initial,
      working_copy: current,
      mutation_applied: mutationInfo,
      altered_sequence: current,
      detection_result: mismatchResult.value,
      repair_applied: repairResult.value || breakResult.value,
      final_sequence: current,
      diff_result: diffResult.value,
      status: repairResult.value?.status || breakResult.value?.status || (diffResult.value?.difference_count ? 'mutated' : 'intact')
    };

    const saved = await api.saveDNAExperiment(payload);
    await fetchSavedExperiments();
    await fetchLogs();

    experimentNotification.value = {
      title: `Experimento guardado [${saved.experiment_id}]`,
      message: `El proceso completo ha quedado registrado con éxito en el sistema.`
    };
    setTimeout(() => {
      experimentNotification.value = null;
    }, 4500);
  } catch (err) {
    alert(err.message || 'Error al guardar experimento');
  } finally {
    loading.value = false;
  }
}

function loadExperiment(exp) {
  if (!exp) return;
  const seqToLoad = exp.final_sequence || exp.altered_sequence || exp.initial_sequence;
  sequenceInput.value = seqToLoad;

  if (exp.initial_sequence) {
    initialMoldSequence.value = exp.initial_sequence;
    referenceStrand.value = exp.initial_sequence;
  }

  if (exp.mutation_applied) {
    lastMutationApplied.value = exp.mutation_applied;
    if (exp.mutation_applied.position !== undefined) {
      controlledForm.value.position = exp.mutation_applied.position;
      selectedPosition.value = exp.mutation_applied.position;
    }
    if (exp.mutation_applied.type) {
      controlledForm.value.type = exp.mutation_applied.type;
    }
    if (exp.mutation_applied.new_base) {
      controlledForm.value.newBase = exp.mutation_applied.new_base;
    }
  }

  if (exp.detection_result) {
    mismatchResult.value = exp.detection_result;
  }
  if (exp.repair_applied) {
    repairResult.value = exp.repair_applied;
  }
  if (exp.diff_result) {
    diffResult.value = exp.diff_result;
  }

  validateAndProcess();
  showLoadDialog.value = false;

  experimentNotification.value = {
    title: `Experimento ${exp.experiment_id} cargado`,
    message: `Se restauró la secuencia (${seqToLoad.length} bp), mutaciones asociadas y la hélice 3D.`
  };
  setTimeout(() => {
    experimentNotification.value = null;
  }, 4500);
}

function loadEventOrExperiment(ev) {
  if (!ev) return;
  const seqToLoad = ev.final_sequence || ev.initial_sequence;
  sequenceInput.value = seqToLoad;

  if (ev.initial_sequence) {
    initialMoldSequence.value = ev.initial_sequence;
  }

  if (ev.reference_used) {
    referenceStrand.value = ev.reference_used;
  } else if (ev.initial_sequence) {
    referenceStrand.value = ev.initial_sequence;
  }

  if (ev.repair_result) {
    repairResult.value = ev.repair_result;
  }
  if (ev.detection_result) {
    mismatchResult.value = ev.detection_result;
  }

  validateAndProcess();

  experimentNotification.value = {
    title: `Evento ${ev.experiment_id} cargado`,
    message: `Secuencia restaurada en el laboratorio (${seqToLoad.length} bp).`
  };
  setTimeout(() => {
    experimentNotification.value = null;
  }, 4500);
}


const duplexPairsDisplay = computed(() => {
  const s1 = cleanSequence.value || sequenceInput.value.trim().toUpperCase();
  const s2 = duplexStrand.value.trim().toUpperCase() || complementStrand.value;
  const maxLen = Math.max(s1.length, s2.length);
  const pairs = [];
  for (let i = 0; i < maxLen; i++) {
    const b1 = s1[i] || '∅';
    const b2 = s2[i] || '∅';
    const isCanon = (b1 !== '∅' && b2 !== '∅' && complementMap[b1] === b2);
    pairs.push({
      b1,
      b2,
      is_canonical: isCanon,
      note: isCanon ? 'Apareamiento Canónico Watson-Crick' : `Apareamiento No Canónico (${b1}-${b2})`
    });
  }
  return pairs;
});

let debounceTimer = null;
function handleInput() {
  sequenceInput.value = sequenceInput.value.toUpperCase();
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    validateAndProcess();
  }, 100);
}

function loadSample(seq) {
  sequenceInput.value = seq;
  initialMoldSequence.value = seq;
  referenceStrand.value = seq;
  lastMutationApplied.value = null;
  repairResult.value = null;
  breakResult.value = null;
  diffResult.value = null;
  mismatchResult.value = null;
  copyNotification.value = '';
  validateAndProcess();
}

function resetToInitialMold() {
  if (!initialMoldSequence.value) return;
  sequenceInput.value = initialMoldSequence.value;
  lastMutationApplied.value = null;
  repairResult.value = null;
  breakResult.value = null;
  diffResult.value = null;
  mismatchResult.value = null;
  copyNotification.value = '';
  validateAndProcess();
  experimentNotification.value = {
    title: 'Molde Inicial Restaurado',
    message: `Se restableció la hebra molde de partida (${initialMoldSequence.value.length} bp) para un nuevo ensayo.`
  };
  setTimeout(() => {
    experimentNotification.value = null;
  }, 3500);
}

async function validateAndProcess() {
  const raw = sequenceInput.value.trim().toUpperCase();
  if (!raw) {
    validationData.value = {
      sequence: '',
      is_valid: false,
      length: 0,
      gc_content: 0,
      base_counts: {},
      invalid_chars: [],
      error_message: 'Secuencia vacía. Introduce nucleótidos A, T, C o G.'
    };
    complementStrand.value = '';
    binaryStrand.value = '';
    return;
  }

  try {
    loading.value = true;
    const valRes = await api.validateDNA(raw);
    validationData.value = valRes;

    if (valRes.is_valid) {
      if (!initialMoldSequence.value) {
        initialMoldSequence.value = raw;
      }
      const compRes = await api.complementDNA(raw);
      complementStrand.value = compRes.complement;
      binaryStrand.value = compRes.binary_repr;

      if (!duplexStrand.value) {
        duplexStrand.value = compRes.complement;
      }
      if (!referenceStrand.value) {
        referenceStrand.value = initialMoldSequence.value || raw;
      }
      breakPosition.value = Math.max(1, Math.floor(raw.length / 2));
    } else {
      complementStrand.value = '';
      binaryStrand.value = '';
    }
  } catch (err) {
    console.error(err);
  } finally {
    loading.value = false;
  }
}

async function handleCopyDNA() {
  if (!cleanSequence.value) return;
  try {
    loading.value = true;
    const res = await api.copyDNA(cleanSequence.value);
    copyNotification.value = `Copia generada con éxito (${res.length} bp). Identidad original: 100% [${res.event_id}]`;
    if (!initialMoldSequence.value) {
      initialMoldSequence.value = cleanSequence.value;
    }
    referenceStrand.value = initialMoldSequence.value;
    await fetchLogs();
    setTimeout(() => {
      copyNotification.value = '';
    }, 4500);
  } catch (err) {
    alert(err.message || 'Error al copiar secuencia');
  } finally {
    loading.value = false;
  }
}

function fillDuplexWithCanonical() {
  duplexStrand.value = complementStrand.value;
}

function insertDuplexMismatch() {
  if (!duplexStrand.value) duplexStrand.value = complementStrand.value;
  if (duplexStrand.value.length > 0) {
    const arr = duplexStrand.value.split('');
    const targetPos = Math.floor(arr.length / 2);
    const cur = arr[targetPos];
    const other = ['A', 'T', 'C', 'G'].find(b => b !== cur) || 'A';
    arr[targetPos] = other;
    duplexStrand.value = arr.join('');
  }
}

async function runMismatchDetection() {
  if (!cleanSequence.value) return;
  try {
    loading.value = true;
    const strand2 = duplexStrand.value.trim().toUpperCase() || complementStrand.value;
    const res = await api.detectMismatches(cleanSequence.value, strand2);
    mismatchResult.value = res;
    await fetchLogs();
  } catch (err) {
    alert(err.message || 'Error en detección de apareamientos');
  } finally {
    loading.value = false;
  }
}

function useCurrentAsReference() {
  referenceStrand.value = initialMoldSequence.value || cleanSequence.value;
}

async function runReferenceRepair() {
  const current = sequenceInput.value.trim().toUpperCase();
  const moldRef = initialMoldSequence.value || referenceStrand.value || current;
  try {
    loading.value = true;
    const res = await api.repairWithReference(current, moldRef);
    repairResult.value = res;
    if (res.matches_reference) {
      sequenceInput.value = res.repaired_sequence;
      await validateAndProcess();
      diffResult.value = await api.compareDNA(moldRef, res.repaired_sequence);
      const compMold = await api.complementDNA(moldRef);
      mismatchResult.value = await api.detectMismatches(res.repaired_sequence, compMold.complement);
      duplexStrand.value = compMold.complement;
    }
    await fetchLogs();
  } catch (err) {
    alert(err.message || 'Error en reparación guiada');
  } finally {
    loading.value = false;
  }
}

async function runBreakSimulation(method) {
  const currentWorking = cleanSequence.value || sequenceInput.value.trim().toUpperCase();
  if (!initialMoldSequence.value) {
    initialMoldSequence.value = currentWorking;
  }
  const moldRef = initialMoldSequence.value;

  try {
    loading.value = true;
    const pos = Math.min(Math.max(1, breakPosition.value), currentWorking.length - 1);
    const refSeq = method === 'homology_directed' ? moldRef : null;
    const res = await api.simulateBreakRepair(currentWorking, pos, method, refSeq);
    breakResult.value = res;
    lastMutationApplied.value = {
      type: 'double_strand_break',
      break_position: pos,
      method: method,
      scar: res.scar
    };

    sequenceInput.value = res.repaired_sequence;
    await validateAndProcess();
    diffResult.value = await api.compareDNA(moldRef, res.repaired_sequence);
    await fetchLogs();
  } catch (err) {
    alert(err.message || 'Error en simulación de rotura');
  } finally {
    loading.value = false;
  }
}

async function fetchLogs() {
  try {
    const res = await api.getDNAEvents(25);
    experimentLogs.value = res.events || [];
  } catch (err) {
    console.error('Error fetching logs:', err);
  }
}

function selectBaseForMutation(index, base) {
  selectedPosition.value = index;
  controlledForm.value.position = index;
  const diffs = ['A', 'T', 'C', 'G'].filter(b => b !== base);
  controlledForm.value.newBase = diffs[0];
}

function handleHelixBaseSelect(index) {
  if (index >= 0 && index < cleanSequence.value.length) {
    selectBaseForMutation(index, cleanSequence.value[index]);
  }
}

async function applyControlledMutation() {
  const currentWorking = cleanSequence.value;
  if (!initialMoldSequence.value) {
    initialMoldSequence.value = currentWorking;
  }
  const moldRef = initialMoldSequence.value;

  try {
    loading.value = true;
    const res = await api.mutateControlled(
      currentWorking,
      controlledForm.value.type,
      controlledForm.value.position,
      controlledForm.value.newBase
    );

    sequenceInput.value = res.modified_sequence;
    lastMutationApplied.value = res.mutation;
    repairResult.value = null;
    await validateAndProcess();

    // 1. Detección automática de mutaciones frente al molde inicial
    diffResult.value = await api.compareDNA(moldRef, res.modified_sequence);

    // 2. Detección automática de apareamientos erróneos frente a la complementaria del molde
    const compMold = await api.complementDNA(moldRef);
    duplexStrand.value = compMold.complement;
    mismatchResult.value = await api.detectMismatches(res.modified_sequence, compMold.complement);

    await fetchLogs();
  } catch (err) {
    alert(err.message || 'Error al aplicar mutación controlada');
  } finally {
    loading.value = false;
  }
}

async function replicateWithProbabilities() {
  const currentWorking = cleanSequence.value;
  if (!initialMoldSequence.value) {
    initialMoldSequence.value = currentWorking;
  }
  const moldRef = initialMoldSequence.value;

  try {
    loading.value = true;
    const res = await api.replicateStochastic(currentWorking, mutationRate.value);
    sequenceInput.value = res.replicated_sequence;
    lastMutationApplied.value = {
      type: 'stochastic_replication',
      rate: mutationRate.value,
      count: res.mutation_count,
      mutations: res.mutations
    };
    repairResult.value = null;
    await validateAndProcess();

    // Detección automática
    diffResult.value = await api.compareDNA(moldRef, res.replicated_sequence);
    const compMold = await api.complementDNA(moldRef);
    duplexStrand.value = compMold.complement;
    mismatchResult.value = await api.detectMismatches(res.replicated_sequence, compMold.complement);

    await fetchLogs();
  } catch (err) {
    alert(err.message || 'Error en la replicación');
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  validateAndProcess();
  fetchLogs();
  fetchSavedExperiments();
});
</script>

<style scoped>
.dna-lab-layout {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

/* Header Científico */
.dna-header-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.2rem 1.6rem;
  background-color: var(--md-sys-color-surface-container);
  flex-wrap: wrap;
  gap: 1.2rem;
}

.header-main {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-icon-box {
  width: 44px;
  height: 44px;
  border-radius: var(--md-sys-shape-corner-medium);
  background-color: var(--md-sys-color-surface-container-high);
  border: 1px solid var(--md-sys-color-outline-variant);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--md-sys-color-primary);
}

.header-text h2 {
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
  letter-spacing: -0.2px;
}

.header-text .subtext {
  font-size: 0.74rem;
  color: var(--md-sys-color-on-surface-variant);
}

.sample-chips-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-wrap: wrap;
}

.chips-label {
  font-size: 0.74rem;
  color: var(--md-sys-color-on-surface-variant);
}

.sample-chips-row .md3-chip {
  cursor: pointer;
}

.sample-chips-row .md3-chip:hover {
  border-color: var(--md-sys-color-primary);
  color: var(--md-sys-color-on-surface);
}

.chip-icon {
  color: var(--md-sys-color-primary);
}

/* Entrada de Secuencia & Métricas */
.dna-input-section {
  padding: 1.4rem 1.6rem;
  background-color: var(--md-sys-color-surface-container-low);
}

.input-primary-row {
  display: flex;
  gap: 1rem;
}

.flex-grow {
  flex: 1;
}

.input-action-bar {
  display: flex;
  gap: 0.8rem;
  margin-top: 0.35rem;
}

.sequence-field {
  flex: 1;
  font-size: 1.05rem;
  letter-spacing: 2.5px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.2rem;
  margin-top: 1.4rem;
  padding-top: 1.2rem;
  border-top: 1px solid var(--md-sys-color-outline-variant);
}

.metric-tile {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.m-k {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--md-sys-color-on-surface-variant);
}

.m-v {
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
}

.m-v small {
  font-size: 0.72rem;
  color: var(--md-sys-color-on-surface-variant);
  font-weight: 400;
}

.gc-progress-wrapper {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}

.gc-bar {
  flex: 1;
  height: 6px;
  border-radius: var(--md-sys-shape-corner-full);
  background-color: var(--md-sys-color-surface-container-highest);
  overflow: hidden;
}

.gc-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--md-sys-color-primary), var(--md-sys-color-tertiary));
  border-radius: var(--md-sys-shape-corner-full);
  transition: width var(--md-sys-motion-duration-medium) ease;
}

.nucleotide-badges {
  display: flex;
  gap: 0.4rem;
}

.n-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.2rem 0.5rem;
  border-radius: var(--md-sys-shape-corner-extra-small);
  font-size: 0.74rem;
  font-family: var(--md-ref-typeface-mono);
  font-weight: 600;
}

.n-badge .pip {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.n-badge.a { background: rgba(239, 68, 68, 0.15); color: var(--bio-base-a); }
.n-badge.a .pip { background: var(--bio-base-a); }

.n-badge.t { background: rgba(16, 185, 129, 0.15); color: var(--bio-base-t); }
.n-badge.t .pip { background: var(--bio-base-t); }

.n-badge.c { background: rgba(6, 182, 212, 0.15); color: var(--bio-base-c); }
.n-badge.c .pip { background: var(--bio-base-c); }

.n-badge.g { background: rgba(245, 158, 11, 0.15); color: var(--bio-base-g); }
.n-badge.g .pip { background: var(--bio-base-g); }

.status-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.3rem 0.7rem;
  border-radius: var(--md-sys-shape-corner-small);
  font-size: 0.75rem;
  font-weight: 500;
  width: fit-content;
}

.status-chip.valid {
  background: rgba(122, 229, 130, 0.15);
  color: var(--md-sys-color-tertiary);
  border: 1px solid rgba(122, 229, 130, 0.3);
}

.status-chip.invalid {
  background: rgba(255, 180, 171, 0.15);
  color: var(--md-sys-color-error);
  border: 1px solid rgba(255, 180, 171, 0.3);
}

/* Workbench Grid (Alineamiento 2D + Doble Hélice 3D) */
.molecular-workbench-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 1.25rem;
  align-items: stretch;
  min-width: 0;
}

/* Track Molecular Interactivo */
.sequence-track-card {
  padding: 1.4rem 1.6rem;
  background-color: var(--md-sys-color-surface-container);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-width: 0;
  overflow: hidden;
}

.track-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.2rem;
  flex-wrap: wrap;
  gap: 0.8rem;
}

.track-title-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.title-icon {
  color: var(--md-sys-color-primary);
}

.track-title-group h3 {
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
}

.track-title-group .hint {
  font-size: 0.72rem;
  color: var(--md-sys-color-on-surface-variant);
}

.spectral-legend {
  display: flex;
  gap: 0.8rem;
}

.leg-item {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.72rem;
  color: var(--md-sys-color-on-surface-variant);
}

.leg-item .square {
  width: 8px;
  height: 8px;
  border-radius: 2px;
}

.leg-item.a .square { background: var(--bio-base-a); }
.leg-item.t .square { background: var(--bio-base-t); }
.leg-item.c .square { background: var(--bio-base-c); }
.leg-item.g .square { background: var(--bio-base-g); }

.track-viewport {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  background-color: var(--md-sys-color-surface-container-lowest);
  border: 1px solid var(--md-sys-color-outline-variant);
  border-radius: var(--md-sys-shape-corner-medium);
  padding: 1rem 0.8rem;
  overflow-x: auto;
}

.track-strand-label {
  font-family: var(--md-ref-typeface-mono);
  font-weight: 700;
  font-size: 0.9rem;
  color: var(--md-sys-color-primary);
  padding: 0 0.4rem;
}

.bases-filmstrip {
  display: flex;
  gap: 0.45rem;
}

.base-column {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 44px;
  cursor: pointer;
  padding: 0.35rem 0.2rem;
  border-radius: var(--md-sys-shape-corner-small);
  transition: all var(--md-sys-motion-duration-short);
}

.base-column:hover {
  background-color: var(--md-sys-color-surface-container-high);
  transform: translateY(-2px);
}

.base-column.selected {
  background-color: var(--md-sys-color-surface-container-highest);
  box-shadow: 0 0 0 2px var(--md-sys-color-primary);
}

.pos-index {
  font-size: 0.65rem;
  color: var(--md-sys-color-on-surface-variant);
  margin-bottom: 0.3rem;
}

.base-capsule {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1rem;
}

.base-column.a .primary-strand { background: rgba(239, 68, 68, 0.2); color: var(--bio-base-a); border: 1px solid var(--bio-base-a); }
.base-column.t .primary-strand { background: rgba(16, 185, 129, 0.2); color: var(--bio-base-t); border: 1px solid var(--bio-base-t); }
.base-column.c .primary-strand { background: rgba(6, 182, 212, 0.2); color: var(--bio-base-c); border: 1px solid var(--bio-base-c); }
.base-column.g .primary-strand { background: rgba(245, 158, 11, 0.2); color: var(--bio-base-g); border: 1px solid var(--bio-base-g); }

.hydrogen-bond {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  height: 14px;
  margin: 3px 0;
}

.h-line {
  width: 2px;
  height: 2px;
  border-radius: 50%;
  background-color: var(--md-sys-color-outline);
}

.comp-strand {
  background-color: var(--md-sys-color-surface-container-high);
  border: 1px solid var(--md-sys-color-outline-variant);
  color: var(--md-sys-color-on-surface-variant);
}

.encoded-data-row {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  margin-top: 1.2rem;
  padding-top: 1rem;
  border-top: 1px solid var(--md-sys-color-outline-variant);
}

.encoded-field {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  flex-wrap: wrap;
  min-width: 0;
  max-width: 100%;
}

.field-label {
  font-size: 0.75rem;
  color: var(--md-sys-color-on-surface-variant);
  min-width: 240px;
}

.strand-box {
  padding: 0.3rem 0.7rem;
  border-radius: var(--md-sys-shape-corner-small);
  background-color: var(--md-sys-color-surface-container-lowest);
  border: 1px solid var(--md-sys-color-outline-variant);
  color: var(--md-sys-color-primary);
  font-size: 0.85rem;
  letter-spacing: 1.5px;
  max-width: 100%;
  overflow-x: auto;
  word-break: break-all;
}

.strand-box.binary {
  color: var(--md-sys-color-secondary);
}

/* Operaciones Genéticas */
.operations-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
  gap: 1.25rem;
}

.op-panel {
  padding: 1.4rem 1.6rem;
  background-color: var(--md-sys-color-surface-container-low);
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

.op-panel-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.header-icon-mini {
  width: 36px;
  height: 36px;
  border-radius: var(--md-sys-shape-corner-small);
  background-color: var(--md-sys-color-surface-container-highest);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--md-sys-color-primary);
}

.op-panel-header h4 {
  font-size: 0.98rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
}

.op-sub {
  font-size: 0.7rem;
  color: var(--md-sys-color-on-surface-variant);
}

.op-form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.9rem;
}

.full-span {
  grid-column: span 2;
}

.base-segmented-selector {
  display: flex;
  gap: 0.4rem;
}

.seg-btn {
  flex: 1;
  height: 38px;
  border-radius: var(--md-sys-shape-corner-small);
  background-color: var(--md-sys-color-surface-container-highest);
  border: 1px solid var(--md-sys-color-outline-variant);
  font-family: var(--md-ref-typeface-mono);
  font-weight: 700;
  font-size: 1rem;
  cursor: pointer;
  transition: all var(--md-sys-motion-duration-short);
}

.seg-btn.a { color: var(--bio-base-a); }
.seg-btn.t { color: var(--bio-base-t); }
.seg-btn.c { color: var(--bio-base-c); }
.seg-btn.g { color: var(--bio-base-g); }

.seg-btn.active {
  background-color: var(--md-sys-color-primary-container);
  border-color: var(--md-sys-color-primary);
  box-shadow: 0 0 10px rgba(112, 214, 255, 0.4);
}

.slider-module {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  background-color: var(--md-sys-color-surface-container);
  padding: 1rem;
  border-radius: var(--md-sys-shape-corner-small);
  border: 1px solid var(--md-sys-color-outline-variant);
}

.slider-telemetry {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.slider-title {
  font-size: 0.78rem;
  color: var(--md-sys-color-on-surface);
}

.slider-rate {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--md-sys-color-primary);
}

.md3-range-slider {
  accent-color: var(--md-sys-color-primary);
  cursor: pointer;
}

.slider-marks {
  display: flex;
  justify-content: space-between;
  font-size: 0.65rem;
  color: var(--md-sys-color-on-surface-variant);
  font-family: var(--md-ref-typeface-mono);
}

/* Diff Inspector */
.diff-inspector-card {
  padding: 1.4rem 1.6rem;
  background-color: var(--md-sys-color-surface-container);
}

.diff-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.2rem;
  flex-wrap: wrap;
  gap: 0.8rem;
}

.diff-title-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.diff-icon {
  color: var(--md-sys-color-primary);
}

.diff-title-row h3 {
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
}

.diff-meta {
  font-size: 0.72rem;
  color: var(--md-sys-color-on-surface-variant);
}

.diff-badge-pill {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.35rem 0.85rem;
  border-radius: var(--md-sys-shape-corner-full);
  background-color: var(--md-sys-color-surface-container-high);
  border: 1px solid var(--md-sys-color-outline-variant);
  font-size: 0.78rem;
  color: var(--md-sys-color-on-surface);
}

.diff-badge-pill.alert {
  background: rgba(245, 158, 11, 0.15);
  border-color: rgba(245, 158, 11, 0.4);
  color: var(--bio-base-g);
}

.diff-alignment-table {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  background-color: var(--md-sys-color-surface-container-lowest);
  border: 1px solid var(--md-sys-color-outline-variant);
  border-radius: var(--md-sys-shape-corner-medium);
  padding: 1rem 1.2rem;
  margin-bottom: 1rem;
}

.alignment-row {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.row-tag {
  font-family: var(--md-ref-typeface-mono);
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface-variant);
  width: 95px;
}

.row-tag.modified {
  color: var(--bio-base-g);
}

.strand-stream {
  font-size: 0.95rem;
  letter-spacing: 2px;
  color: var(--md-sys-color-on-surface);
}

.mod-stream {
  color: var(--bio-base-g);
}

.mutation-events-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(210px, 1fr));
  gap: 0.75rem;
}

.mutation-card {
  padding: 0.75rem 0.9rem;
  border-radius: var(--md-sys-shape-corner-small);
  background-color: var(--md-sys-color-surface-container-high);
  border: 1px solid var(--md-sys-color-outline-variant);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.m-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.m-coord {
  font-size: 0.72rem;
  color: var(--md-sys-color-on-surface-variant);
}

.m-type-chip {
  font-size: 0.65rem;
  padding: 0.12rem 0.45rem;
  border-radius: 4px;
  text-transform: uppercase;
  font-weight: 600;
}

.m-type-chip.changed { background: rgba(245, 158, 11, 0.2); color: var(--bio-base-g); }
.m-type-chip.deleted { background: rgba(239, 68, 68, 0.2); color: var(--bio-base-a); }
.m-type-chip.inserted { background: rgba(16, 185, 129, 0.2); color: var(--bio-base-t); }

.m-transition {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.15rem;
  font-weight: 700;
}

.base-old { color: var(--md-sys-color-on-surface-variant); }
.arrow { color: var(--md-sys-color-outline); }
.base-new { color: var(--md-sys-color-primary); }

/* Feedback Copia */
.copy-feedback-banner {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.8rem;
  background: rgba(16, 185, 129, 0.12);
  border: 1px solid rgba(16, 185, 129, 0.35);
  border-radius: var(--md-sys-shape-corner-small);
  color: #10b981;
  font-size: 0.82rem;
  font-weight: 600;
  margin-top: 0.4rem;
}

/* 3.1 & 3.2: Apareamientos y Reparación */
.mismatch-repair-card,
.dsb-card,
.audit-log-card {
  padding: 1.4rem 1.6rem;
  background-color: var(--md-sys-color-surface-container);
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.section-title-group {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.section-icon {
  color: var(--md-sys-color-primary);
}

.section-icon.alert {
  color: var(--bio-base-a);
}

.duplex-work-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
  gap: 1.25rem;
}

.duplex-card {
  background: var(--md-sys-color-surface-container-high);
  border: 1px solid var(--md-sys-color-outline-variant);
  border-radius: var(--md-sys-shape-corner-medium);
  padding: 1.2rem 1.4rem;
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
}

.card-subtitle {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-weight: 700;
  font-size: 0.95rem;
  color: var(--md-sys-color-on-surface);
}

.desc-text {
  font-size: 0.82rem;
  color: var(--md-sys-color-on-surface-variant);
  margin: 0;
  line-height: 1.4;
}

.input-with-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.input-with-actions .sequence-field {
  flex: 1;
  min-width: 180px;
}

.action-buttons-row {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
}

.status-banner {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.65rem 0.9rem;
  border-radius: var(--md-sys-shape-corner-small);
  font-size: 0.84rem;
}

.status-banner.success {
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.35);
  color: #10b981;
}

.status-banner.warning {
  background: rgba(245, 158, 11, 0.15);
  border: 1px solid rgba(245, 158, 11, 0.35);
  color: #f59e0b;
}

.status-banner.info {
  background: rgba(59, 130, 246, 0.15);
  border: 1px solid rgba(59, 130, 246, 0.35);
  color: #60a5fa;
}

.pairs-visual-strip {
  display: flex;
  gap: 0.4rem;
  overflow-x: auto;
  padding: 0.4rem 0;
}

.pair-pill {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.35rem 0.5rem;
  border-radius: 4px;
  min-width: 32px;
  font-size: 0.78rem;
  border: 1px solid transparent;
}

.pair-pill .p-idx {
  font-size: 0.6rem;
  opacity: 0.7;
}

.pair-pill .p-conn {
  line-height: 0.5;
  font-weight: bold;
}

.pair-pill.canonical {
  background: rgba(16, 185, 129, 0.12);
  border-color: rgba(16, 185, 129, 0.3);
  color: #10b981;
}

.pair-pill.non-canonical {
  background: rgba(239, 68, 68, 0.18);
  border-color: rgba(239, 68, 68, 0.5);
  color: #ef4444;
  animation: pulse-border 1.5s infinite alternate;
}

@keyframes pulse-border {
  from { border-color: rgba(239, 68, 68, 0.4); }
  to { border-color: rgba(239, 68, 68, 0.9); }
}

.scientific-disclaimer-mini {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  font-size: 0.74rem;
  color: var(--md-sys-color-outline);
  background: var(--md-sys-color-surface-container-lowest);
  padding: 0.45rem 0.7rem;
  border-radius: 4px;
}

.repaired-seq-preview {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-size: 0.85rem;
  padding: 0.6rem 0.8rem;
  background: var(--md-sys-color-surface-container-lowest);
  border-radius: var(--md-sys-shape-corner-small);
}

/* 3.3: DSB Simulator */
.dsb-controls-row {
  display: flex;
  align-items: flex-end;
  gap: 1.2rem;
  flex-wrap: wrap;
}

.break-pos-field {
  max-width: 280px;
}

.dsb-action-buttons {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.hdr-btn {
  background-color: #059669;
  color: #ffffff;
}

.nhej-btn {
  border-color: #d97706;
  color: #f59e0b;
}

.dsb-result-panel {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  background: var(--md-sys-color-surface-container-high);
  border: 1px solid var(--md-sys-color-outline-variant);
  border-radius: var(--md-sys-shape-corner-medium);
  padding: 1.2rem 1.4rem;
}

.fragments-display {
  display: flex;
  align-items: center;
  gap: 0.9rem;
  flex-wrap: wrap;
}

.frag-box {
  background: var(--md-sys-color-surface-container-lowest);
  border: 1px solid var(--md-sys-color-outline-variant);
  padding: 0.6rem 0.9rem;
  border-radius: var(--md-sys-shape-corner-small);
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.frag-label {
  font-size: 0.7rem;
  color: var(--md-sys-color-on-surface-variant);
}

.cut-marker {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: var(--bio-base-a);
  font-size: 0.65rem;
  font-weight: 700;
  gap: 0.2rem;
}

.recombined-box {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0.8rem 1rem;
  background: var(--md-sys-color-surface-container-lowest);
  border-radius: var(--md-sys-shape-corner-small);
}

.rec-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.scar-badge {
  font-size: 0.68rem;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  font-weight: 700;
  text-transform: uppercase;
}

.scar-badge.clean {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
}

.scar-badge.scarred {
  background: rgba(245, 158, 11, 0.2);
  color: #f59e0b;
}

.rec-seq {
  font-size: 1.05rem;
  letter-spacing: 2px;
  color: var(--md-sys-color-primary);
}

.rec-desc {
  font-size: 0.8rem;
  color: var(--md-sys-color-on-surface-variant);
  margin: 0;
}

/* 7 & 10: Auditoría y Nota Científica */
.scientific-notice-banner {
  display: flex;
  gap: 1rem;
  background: rgba(59, 130, 246, 0.08);
  border: 1px solid rgba(59, 130, 246, 0.25);
  border-radius: var(--md-sys-shape-corner-medium);
  padding: 1rem 1.3rem;
  align-items: flex-start;
}

.notice-icon {
  color: #3b82f6;
  flex-shrink: 0;
  margin-top: 0.2rem;
}

.notice-content h4 {
  margin: 0 0 0.35rem 0;
  font-size: 0.92rem;
  color: #60a5fa;
}

.notice-content p {
  margin: 0;
  font-size: 0.8rem;
  line-height: 1.45;
  color: var(--md-sys-color-on-surface-variant);
}

.events-table-wrapper {
  overflow-x: auto;
  border: 1px solid var(--md-sys-color-outline-variant);
  border-radius: var(--md-sys-shape-corner-small);
}

.events-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8rem;
}

.events-table th,
.events-table td {
  padding: 0.65rem 0.9rem;
  text-align: left;
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
}

.events-table th {
  background: var(--md-sys-color-surface-container-high);
  font-weight: 600;
  color: var(--md-sys-color-on-surface-variant);
  font-size: 0.74rem;
  text-transform: uppercase;
}

.exp-id {
  color: var(--md-sys-color-primary);
  font-weight: 600;
}

.op-chip {
  font-size: 0.68rem;
  padding: 0.15rem 0.45rem;
  background: var(--md-sys-color-surface-container-highest);
  border-radius: 4px;
}

.seq-cell {
  letter-spacing: 1px;
}

.no-ref {
  color: var(--md-sys-color-outline);
  font-style: italic;
  font-size: 0.74rem;
}

.res-status {
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
}

.res-status.fully_repaired,
.res-status.repaired_high_fidelity,
.res-status.copied_exact {
  color: #10b981;
}

.res-status.partially_repaired,
.res-status.repaired_prone_to_scar {
  color: #f59e0b;
}

/* Alerta de Validación de Símbolos No Permitidos */
.validation-error-alert {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.8rem 1.2rem;
  margin-top: 1rem;
  background: rgba(239, 68, 68, 0.12);
  border: 1px solid rgba(239, 68, 68, 0.4);
  border-radius: var(--md-sys-shape-corner-small);
  color: #f87171;
}

.validation-error-alert .err-icon {
  color: #ef4444;
  flex-shrink: 0;
}

.validation-error-alert .err-text {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  font-size: 0.85rem;
}

.invalid-sequence-placeholder {
  padding: 2rem;
  background: var(--md-sys-color-surface-container);
  border: 1px dashed rgba(239, 68, 68, 0.5);
  border-radius: var(--md-sys-shape-corner-medium);
  margin-top: 0.5rem;
}

.placeholder-content {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.placeholder-icon {
  color: #ef4444;
  flex-shrink: 0;
}

.placeholder-content h3 {
  margin: 0 0 0.35rem 0;
  color: #f87171;
  font-size: 1.1rem;
}

.placeholder-content p {
  margin: 0;
  color: var(--md-sys-color-on-surface-variant);
  font-size: 0.88rem;
  line-height: 1.5;
}

/* Acciones de Gestión de Experimentos en Header */
.header-actions-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  gap: 1rem;
  flex-wrap: wrap;
}

.exp-management-buttons {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.save-exp-btn {
  background-color: var(--md-sys-color-primary);
  color: var(--md-sys-color-on-primary);
}

.load-exp-btn {
  background-color: var(--md-sys-color-surface-container-highest);
  color: var(--md-sys-color-on-surface);
  border: 1px solid var(--md-sys-color-outline-variant);
}

/* Toast Banner */
.exp-toast-banner {
  display: flex;
  align-items: center;
  gap: 0.9rem;
  padding: 0.85rem 1.25rem;
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.45);
  border-radius: var(--md-sys-shape-corner-medium);
  color: #10b981;
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from { opacity: 0; transform: translateY(-8px); }
  to { opacity: 1; transform: translateY(0); }
}

.toast-icon {
  flex-shrink: 0;
}

.toast-text {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  flex: 1;
}

.toast-text strong {
  font-size: 0.88rem;
  color: #10b981;
}

.toast-text span {
  font-size: 0.78rem;
  color: var(--md-sys-color-on-surface);
}

.toast-close-btn {
  background: none;
  border: none;
  color: var(--md-sys-color-outline);
  cursor: pointer;
  font-size: 1rem;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
}

.toast-close-btn:hover {
  color: var(--md-sys-color-on-surface);
  background: rgba(255, 255, 255, 0.08);
}

/* Botón Cargar en fila de tabla */
.load-row-chip {
  background: rgba(59, 130, 246, 0.12);
  border-color: rgba(59, 130, 246, 0.35);
  color: #60a5fa;
  cursor: pointer;
  padding: 0.2rem 0.6rem;
  font-size: 0.72rem;
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
}

.load-row-chip:hover {
  background: rgba(59, 130, 246, 0.25);
  border-color: #3b82f6;
  color: #ffffff;
}

/* Modal Dialog de Cargar Experimentos */
.md3-dialog-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.72);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 1.5rem;
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.md3-dialog-surface {
  background: var(--md-sys-color-surface-container);
  border-radius: var(--md-sys-shape-corner-large);
  width: 100%;
  max-width: 780px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6);
  border: 1px solid var(--md-sys-color-outline-variant);
  overflow: hidden;
}

.dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.3rem 1.6rem;
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
  background: var(--md-sys-color-surface-container-high);
}

.dialog-title-group {
  display: flex;
  align-items: center;
  gap: 0.9rem;
}

.dialog-icon {
  color: var(--md-sys-color-primary);
}

.dialog-header h3 {
  margin: 0 0 0.2rem 0;
  font-size: 1.15rem;
  color: var(--md-sys-color-on-surface);
}

.dialog-sub {
  font-size: 0.78rem;
  color: var(--md-sys-color-on-surface-variant);
}

.dialog-close-btn {
  background: none;
  border: none;
  color: var(--md-sys-color-outline);
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0.3rem 0.6rem;
  border-radius: 4px;
}

.dialog-close-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--md-sys-color-on-surface);
}

.dialog-body {
  padding: 1.3rem 1.6rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.empty-experiments-notice {
  text-align: center;
  padding: 3rem 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  color: var(--md-sys-color-on-surface-variant);
}

.empty-icon {
  color: var(--md-sys-color-outline);
}

.empty-experiments-notice h4 {
  margin: 0;
  color: var(--md-sys-color-on-surface);
  font-size: 1.05rem;
}

.empty-experiments-notice p {
  margin: 0;
  max-width: 420px;
  font-size: 0.85rem;
  line-height: 1.4;
}

.saved-experiments-list {
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
}

.saved-exp-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.25rem;
  padding: 1.1rem 1.3rem;
  background: var(--md-sys-color-surface-container-high);
  border: 1px solid var(--md-sys-color-outline-variant);
  border-radius: var(--md-sys-shape-corner-medium);
  transition: border-color 0.2s, background-color 0.2s;
}

.saved-exp-card:hover {
  border-color: var(--md-sys-color-primary);
  background: var(--md-sys-color-surface-container-highest);
}

.card-main-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  flex: 1;
}

.exp-id-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.exp-badge {
  color: var(--md-sys-color-primary);
  font-weight: 700;
  font-size: 0.85rem;
}

.exp-date {
  color: var(--md-sys-color-outline);
  font-size: 0.74rem;
}

.exp-status-chip {
  font-size: 0.65rem;
  padding: 0.12rem 0.45rem;
  border-radius: 4px;
  font-weight: 600;
  text-transform: uppercase;
}

.exp-status-chip.fully_repaired,
.exp-status-chip.repaired_high_fidelity,
.exp-status-chip.intact {
  background: rgba(16, 185, 129, 0.18);
  color: #10b981;
}

.exp-status-chip.partially_repaired,
.exp-status-chip.repaired_prone_to_scar,
.exp-status-chip.mutated {
  background: rgba(245, 158, 11, 0.18);
  color: #f59e0b;
}

.exp-title {
  margin: 0;
  font-size: 0.95rem;
  color: var(--md-sys-color-on-surface);
}

.exp-sequences-summary {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.78rem;
}

.summary-line {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.summary-line .label {
  color: var(--md-sys-color-on-surface-variant);
  width: 95px;
  font-size: 0.72rem;
}

.summary-line code {
  color: var(--md-sys-color-on-surface);
  letter-spacing: 1px;
}

.summary-line .val {
  color: var(--bio-base-g);
  font-weight: 600;
}

.card-action-box .load-btn {
  white-space: nowrap;
}

/* Pipeline Stepper */
.pipeline-stepper-card {
  padding: 1rem 1.4rem;
  background-color: var(--md-sys-color-surface-container);
  border-radius: var(--md-sys-shape-corner-medium);
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  border-color: rgba(99, 102, 241, 0.2);
}

.stepper-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.8rem;
}

.stepper-title-box {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--md-sys-color-primary);
}

.stepper-icon {
  color: var(--md-sys-color-primary);
}

.stepper-tag {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stepper-status {
  font-size: 0.82rem;
  color: var(--md-sys-color-on-surface-variant);
  background: var(--md-sys-color-surface-container-high);
  padding: 0.25rem 0.65rem;
  border-radius: 999px;
  border: 1px solid var(--md-sys-color-outline-variant);
}

.stepper-status strong {
  color: var(--md-sys-color-primary);
}

.stepper-track {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  position: relative;
  overflow-x: auto;
  padding: 0.4rem 0.2rem;
}

.step-pill {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.45rem 0.9rem;
  border-radius: 999px;
  background: var(--md-sys-color-surface-container-low);
  border: 1px solid var(--md-sys-color-outline-variant);
  transition: all 0.25s ease;
  white-space: nowrap;
}

.step-num {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 700;
  background: var(--md-sys-color-surface-container-highest);
  color: var(--md-sys-color-on-surface-variant);
}

.step-label {
  font-size: 0.8rem;
  color: var(--md-sys-color-on-surface-variant);
}

.step-pill.active {
  background: rgba(99, 102, 241, 0.15);
  border-color: var(--md-sys-color-primary);
  box-shadow: 0 0 12px rgba(99, 102, 241, 0.25);
}

.step-pill.active .step-num {
  background: var(--md-sys-color-primary);
  color: var(--md-sys-color-on-primary);
}

.step-pill.active .step-label {
  color: var(--md-sys-color-on-surface);
  font-weight: 600;
}

.step-pill.done {
  background: rgba(16, 185, 129, 0.12);
  border-color: rgba(16, 185, 129, 0.4);
}

.step-pill.done .step-num {
  background: #10b981;
  color: #000;
}

.step-pill.done .step-label {
  color: #10b981;
}

.step-line {
  flex: 1;
  height: 2px;
  background: var(--md-sys-color-outline-variant);
  min-width: 12px;
}

/* Manual de Laboratorio Modal Styles */
.manual-dialog-surface {
  max-width: 920px;
  width: 95vw;
  max-height: 88vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-color: var(--md-sys-color-surface-container);
}

.dialog-icon.highlight {
  color: #38bdf8;
}

.manual-tabs-bar {
  display: flex;
  background: var(--md-sys-color-surface-container-low);
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
  padding: 0 1.2rem;
  gap: 0.5rem;
  overflow-x: auto;
}

.manual-tab-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.1rem;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  color: var(--md-sys-color-on-surface-variant);
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.manual-tab-btn:hover {
  color: var(--md-sys-color-on-surface);
  background: rgba(255, 255, 255, 0.03);
}

.manual-tab-btn.active {
  color: #38bdf8;
  border-bottom-color: #38bdf8;
  font-weight: 600;
}

.manual-dialog-body {
  flex: 1;
  overflow-y: auto;
  padding: 1.4rem;
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

.manual-hero-banner {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem 1.25rem;
  background: rgba(56, 189, 248, 0.08);
  border: 1px solid rgba(56, 189, 248, 0.25);
  border-radius: var(--md-sys-shape-corner-medium);
  color: var(--md-sys-color-on-surface);
}

.manual-hero-banner h4 {
  margin: 0 0 0.3rem 0;
  color: #38bdf8;
  font-size: 0.95rem;
}

.manual-hero-banner p {
  margin: 0;
  font-size: 0.83rem;
  line-height: 1.45;
  color: var(--md-sys-color-on-surface-variant);
}

.flow-steps-accordion {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.flow-step-item {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
  padding: 0.9rem 1.1rem;
  background: var(--md-sys-color-surface-container-low);
  border: 1px solid var(--md-sys-color-outline-variant);
  border-radius: var(--md-sys-shape-corner-medium);
}

.step-badge {
  padding: 0.3rem 0.65rem;
  border-radius: 999px;
  font-size: 0.74rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

.step-badge.step-1 { background: rgba(99, 102, 241, 0.2); color: #818cf8; }
.step-badge.step-2 { background: rgba(56, 189, 248, 0.2); color: #38bdf8; }
.step-badge.step-3 { background: rgba(245, 158, 11, 0.2); color: #f59e0b; }
.step-badge.step-4 { background: rgba(239, 68, 68, 0.2); color: #ef4444; }
.step-badge.step-5 { background: rgba(16, 185, 129, 0.2); color: #10b981; }

.step-info h5 {
  margin: 0 0 0.25rem 0;
  font-size: 0.92rem;
  color: var(--md-sys-color-on-surface);
}

.step-info p {
  margin: 0;
  font-size: 0.82rem;
  line-height: 1.45;
  color: var(--md-sys-color-on-surface-variant);
}

/* Button Guide Grid */
.button-guide-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
}

.button-guide-card {
  background: var(--md-sys-color-surface-container-low);
  border: 1px solid var(--md-sys-color-outline-variant);
  border-radius: var(--md-sys-shape-corner-medium);
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.card-tag {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #38bdf8;
  letter-spacing: 0.5px;
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
  padding-bottom: 0.4rem;
}

.btn-entry {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.btn-name {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.78rem;
  font-weight: 600;
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
  width: fit-content;
}

.btn-name.filled { background: var(--md-sys-color-primary); color: var(--md-sys-color-on-primary); }
.btn-name.tonal { background: var(--md-sys-color-surface-container-highest); color: var(--md-sys-color-on-surface); }
.btn-name.chip { background: var(--md-sys-color-surface-container-high); border: 1px solid var(--md-sys-color-outline-variant); color: var(--md-sys-color-on-surface); }
.btn-name.icon-btn { background: rgba(56, 189, 248, 0.15); color: #38bdf8; }
.btn-name.hdr-color { background: #059669; color: #fff; }
.btn-name.nhej-color { background: rgba(245, 158, 11, 0.2); color: #f59e0b; }

.btn-entry p {
  margin: 0;
  font-size: 0.8rem;
  color: var(--md-sys-color-on-surface-variant);
  line-height: 1.4;
}

/* Protocols */
.protocol-card {
  background: var(--md-sys-color-surface-container-low);
  border: 1px solid var(--md-sys-color-outline-variant);
  border-radius: var(--md-sys-shape-corner-medium);
  padding: 1.2rem;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.protocol-card h4 {
  margin: 0;
  color: #38bdf8;
  font-size: 0.95rem;
}

.protocol-steps-list {
  margin: 0;
  padding-left: 1.3rem;
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  font-size: 0.82rem;
  color: var(--md-sys-color-on-surface);
  line-height: 1.45;
}

.dialog-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.4rem;
  border-top: 1px solid var(--md-sys-color-outline-variant);
  background: var(--md-sys-color-surface-container-low);
  flex-wrap: wrap;
  gap: 0.8rem;
}

.doc-file-hint {
  font-size: 0.74rem;
  color: var(--md-sys-color-on-surface-variant);
}

@media (max-width: 1024px) {
  .molecular-workbench-grid {
    grid-template-columns: 1fr;
  }
}
</style>
