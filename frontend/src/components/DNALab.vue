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

      <!-- Gestión de Experimentos -->
      <div class="exp-management-buttons">
        <button class="md3-button-filled save-exp-btn" @click="openSaveDialog" :disabled="loading" title="Guardar todo el proceso del experimento con nombre y notas">
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
        <button class="md3-button-outlined dna-test-btn" @click="showDnaTestDialog = true" title="Abrir modelos 3D reales de ADN Prueba (Atómico y Fotorrealista)">
          <Icon name="dna" size="18" />
          <span>ADN Prueba</span>
        </button>
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

    <!-- ═══════════════════════ BARRA DE NAVEGACIÓN POR FASES (TABS) ═══════════════════════ -->
    <nav class="phase-tabs-nav">
      <button
        :class="['phase-tab-btn', { active: activePhaseTab === 'phase1' }]"
        @click="activePhaseTab = 'phase1'"
      >
        <Icon name="biotech" size="18" />
        <span class="tab-label">Fase 1: Integridad y Reparación del Molde (ADN)</span>
        <span class="tab-badge" v-if="cleanSequence">{{ cleanSequence.length }} bp</span>
      </button>
      <button
        :class="['phase-tab-btn', { active: activePhaseTab === 'phase2' }]"
        @click="activePhaseTab = 'phase2'"
      >
        <Icon name="genetics" size="18" />
        <span class="tab-label">Fase 2: Expresión Génica &amp; Proteínas (Dogma Central)</span>
        <span class="tab-badge phase2-badge" v-if="selectedGene">{{ selectedGene.name }}</span>
      </button>
      <div class="tab-indicator" :class="activePhaseTab"></div>
    </nav>

    <!-- ═══════════════════════ CABECERA GENERAL COMPARTIDA: SELECTOR DE GENES ═══════════════════════ -->
    <div class="shared-gene-selector-card md3-card-outlined">
      <div class="shared-selector-header">
        <div class="shared-selector-title">
          <div class="selector-badge-avatar">
            <Icon name="genetics" size="18" />
          </div>
          <div>
            <span class="selector-title-text">Genoma de Referencia / Catálogo de Genes</span>
            <span class="selector-subtext">Selecciona un gen modelo para inyectar su secuencia codificante (CDS) en tiempo real en todo el laboratorio:</span>
          </div>
        </div>

        <!-- Selector de Gen (Chips) -->
        <div class="gene-selector-row">
          <button
            :class="['gene-chip', 'free-chip', { active: selectedGeneId === null }]"
            @click="selectGene(null)"
            title="Modo de entrada libre: introduce cualquier secuencia personalizada en el secuenciador"
          >
            <Icon name="edit_note" size="16" />
            <span class="gene-chip-name">Entrada Libre / Personalizada</span>
            <span class="chip-bp">Manual</span>
            <span class="chip-active-dot" v-if="selectedGeneId === null">●</span>
          </button>

          <button
            v-for="gene in genesCatalog"
            :key="gene.id"
            :class="['gene-chip', { active: selectedGeneId === gene.id, disabled: gene.id === 'tp53_hsapiens' }]"
            :disabled="gene.id === 'tp53_hsapiens'"
            @click="gene.id === 'tp53_hsapiens' ? null : selectGene(gene.id)"
            :title="gene.id === 'tp53_hsapiens' ? 'En desarrollo: próximamente disponible con intrones' : (gene.id === 'didactic_min_control' ? `Cargar secuencia genómica de ${gene.name} (16 bp con intrón GTAG)` : `Cargar secuencia CDS de ${gene.name} (${gene.cds_info?.cds_sequence?.length || 0} bp)`)"
          >
            <Icon :name="gene.gene_type === 'protein_coding' ? 'genetics' : 'science'" size="15" />
            <span class="gene-chip-name">{{ gene.name }}</span>
            <span class="chip-dev-badge" v-if="gene.id === 'tp53_hsapiens'">En desarrollo</span>
            <span class="chip-bp" v-else>{{ gene.id === 'didactic_min_control' ? '16 bp (Genómico)' : `${gene.cds_info?.cds_sequence?.length || (gene.end_coord - gene.start_coord)} bp CDS` }}</span>
            <span class="chip-active-dot" v-if="selectedGeneId === gene.id">●</span>
          </button>
        </div>
      </div>
    </div>

    <!-- ═══════════════════════ CONTENEDOR FASE 1 ═══════════════════════ -->
    <div class="phase-content-wrapper" v-show="activePhaseTab === 'phase1'">

      <!-- Ficha Compacta del Gen Activo en Fase 1 -->
      <div class="gene-compact-card md3-card-outlined" v-if="selectedGene">
        <div class="compact-card-left">
          <div class="compact-gene-indicator">
            <Icon name="biotech" size="20" class="compact-icon" />
            <div class="compact-gene-info">
              <div class="compact-name-row">
                <span class="compact-prefix">GEN ACTIVO:</span>
                <strong class="compact-name">{{ selectedGene.name }}</strong>
                <span :class="['provenance-pill', selectedGene.data_source.type === 'secuencia_curada_publicada' ? 'curated' : 'didactic']">
                  <Icon :name="selectedGene.data_source.type === 'secuencia_curada_publicada' ? 'verified' : 'school'" size="12" />
                  <span>{{ selectedGene.data_source.type === 'secuencia_curada_publicada' ? selectedGene.data_source.database : 'Didáctica' }}</span>
                </span>
              </div>
              <div class="compact-meta-row">
                <span class="meta-tag"><strong>Organismo:</strong> {{ selectedGene.organism }}</span>
                <span class="meta-separator">•</span>
                <span class="meta-tag font-mono"><strong>Coordenadas:</strong> {{ selectedGene.data_source.chromosome || `${selectedGene.start_coord}–${selectedGene.end_coord} bp` }}</span>
                <span class="meta-separator">•</span>
                <span class="meta-tag"><strong>Hebra:</strong> {{ selectedGene.strand_orientation === '+' ? '5\'→3\' (+)' : '3\'→5\' (−)' }}</span>
                <span class="meta-separator">•</span>
                <span class="meta-tag font-mono"><strong>CDS:</strong> {{ selectedGene.cds_info?.cds_sequence?.length || 0 }} bp</span>
              </div>
            </div>
          </div>
        </div>

        <div class="compact-card-right">
          <button class="compact-inspect-btn" @click="activePhaseTab = 'phase2'" title="Inspeccionar estructura exón/intrón y ficha técnica completa en Fase 2">
            <span>Ficha Completa &amp; Estructura</span>
            <Icon name="arrow_forward" size="14" />
          </button>
        </div>
      </div>

      <div class="gene-compact-card custom-mode md3-card-outlined" v-else>
        <div class="compact-card-left">
          <div class="compact-gene-indicator">
            <Icon name="edit_note" size="20" class="compact-icon custom" />
            <div class="compact-gene-info">
              <div class="compact-name-row">
                <span class="compact-prefix">MODO:</span>
                <strong class="compact-name">Secuencia Personalizada / Entrada Libre</strong>
                <span class="provenance-pill custom">
                  <Icon name="edit" size="12" />
                  <span>Manual</span>
                </span>
              </div>
              <div class="compact-meta-row">
                <span class="meta-tag" v-if="cleanSequence">Secuencia libre de <strong>{{ cleanSequence.length }} bp</strong> activa en el secuenciador.</span>
                <span class="meta-tag" v-else>Introduce cualquier secuencia canónica (A, T, C, G) o selecciona un gen modelo del catálogo superior.</span>
              </div>
            </div>
          </div>
        </div>
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
              @keyup.enter="validateAndProcess(true)"
            />
            <button class="md3-button-filled" @click="validateAndProcess(true)" :disabled="loading">
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
      <div class="metrics-grid" v-if="validationData && validationData.is_valid">
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
        <div class="metric-tile backbone-metric-tile">
          <span class="m-k">Esqueleto Azúcar-Fosfato</span>
          <div class="backbone-badges">
            <span class="bb-chip sugar" title="2'-Desoxirribosa (anillo furanosa)">
              <span class="bb-dot s-dot"></span>D: {{ validationData.backbone_info?.total_sugars ?? validationData.length }} Azúcares
            </span>
            <span class="bb-chip phosphate" title="Grupos Fosfato PO4^3-">
              <span class="bb-dot p-dot"></span>P: {{ validationData.backbone_info?.total_phosphates ?? validationData.length }} Fosfatos
            </span>
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
      <div class="validation-error-alert" v-if="validationData && !validationData.is_valid && sequenceInput.trim()">
        <Icon name="warning" size="20" class="err-icon" />
        <div class="err-text">
          <strong>Secuencia no válida para el motor genético:</strong>
          <span>{{ validationData.error_message || 'Contiene caracteres no canónicos. Solo se aceptan A, T, C, G.' }}</span>
        </div>
      </div>
    </div>

    <!-- Aviso si la secuencia actual contiene símbolos no válidos -->
    <div class="invalid-sequence-placeholder md3-card-outlined" v-if="validationData && !validationData.is_valid && sequenceInput.trim()">
      <div class="placeholder-content">
        <Icon name="warning" size="36" class="placeholder-icon" />
        <div>
          <h3>Secuencia con Símbolos No Permitidos</h3>
          <p>La cadena ingresada contiene caracteres no canónicos <strong>({{ (validationData.invalid_chars || []).join(', ') }})</strong>. Corrige la secuencia eliminando los símbolos no válidos para restaurar la doble hélice 3D y habilitar las operaciones de recombinación.</p>
        </div>
      </div>
    </div>

    <!-- Guía Inicial: Estación Lista para Entrada Manual -->
    <div class="manual-input-prompt-card md3-card-outlined" v-if="!sequenceInput.trim() || (!cleanSequence && !validationData?.is_valid)">
      <div class="prompt-content">
        <div class="prompt-icon-box">
          <Icon name="biotech" size="34" />
        </div>
        <div class="prompt-text">
          <h3>Estación Molecular en Espera</h3>
          <p>Introduce una cadena molde de nucleótidos (bases <strong>A</strong>, <strong>T</strong>, <strong>C</strong>, <strong>G</strong>) en el campo superior y presiona <strong>Validar Molde</strong> o la tecla <strong>Enter</strong> para inicializar el mapa 2D y el modelo macromolecular 3D.</p>
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
              <span class="hint">Haz clic en cualquier base para posicionar el inductor de lesión dirigida o aducto</span>
            </div>
          </div>

          <div class="spectral-legend">
            <span class="leg-item a"><span class="square"></span> A (Adenina)</span>
            <span class="leg-item t"><span class="square"></span> T (Timina)</span>
            <span class="leg-item c"><span class="square"></span> C (Citosina)</span>
            <span class="leg-item g"><span class="square"></span> G (Guanina)</span>
          </div>
        </div>

        <!-- Navegador de Ventana Activa 2D (cuando la secuencia supera 70 pb) -->
        <div class="filmstrip-window-navigator" v-if="cleanSequence && cleanSequence.length > 70">
          <div class="f-nav-info">
            <Icon name="view_timeline" size="16" />
            <span class="font-mono">Ventana 2D: pb {{ filmstripStartPos + 1 }} – {{ Math.min(cleanSequence.length, filmstripStartPos + 70) }} <small class="text-dim">de {{ cleanSequence.length }} pb</small></span>
          </div>
          <div class="f-nav-controls">
            <button class="nav-arrow-btn" @click="scrollFilmstrip(-35)" :disabled="filmstripStartPos <= 0" title="Retroceder 35 pb">
              <Icon name="arrow_back" size="14" />
            </button>
            <input 
              type="range" 
              class="filmstrip-scrubber"
              :min="0" 
              :max="Math.max(0, cleanSequence.length - 70)" 
              v-model.number="filmstripStartPos" 
              :title="`Desplazar ventana (pb ${filmstripStartPos + 1})`"
            />
            <button class="nav-arrow-btn" @click="scrollFilmstrip(35)" :disabled="filmstripStartPos >= cleanSequence.length - 70" title="Avanzar 35 pb">
              <Icon name="arrow_forward" size="14" />
            </button>
            <button class="md3-chip interactive-chip center-btn" @click="centerFilmstripOnSelected" v-if="selectedPosition !== null" title="Centrar en el nucleótido seleccionado">
              <Icon name="my_location" size="12" />
              <span>Centrar pb {{ selectedPosition }}</span>
            </button>
          </div>
        </div>

        <!-- Segmento Gráfico de Bases con Esqueleto Azúcar-Fosfato (5' a 3' y complementaria 3' a 5') -->
        <div class="track-viewport">
          <div class="track-polarity-col left">
            <span class="polarity-tag p5" title="Extremo 5' Fosfato libre">5' (P)</span>
            <div class="polarity-v-link"></div>
            <span class="polarity-tag p3" title="Extremo 3' Hidroxilo (-OH) complementario">3' (OH)</span>
          </div>

          <div class="bases-filmstrip">
            <div 
              v-for="item in visibleFilmstripBases" 
              :key="item.idx"
              :class="['base-column', item.base.toLowerCase(), { selected: selectedPosition === item.idx }]"
              @click="selectBaseForMutation(item.idx, item.base)"
            >
              <span class="pos-index font-mono">{{ item.idx }}</span>

              <!-- Esqueleto Superior Azúcar-Fosfato (5' -> 3') -->
              <div class="bb-monomer top" title="Monómero 5': Fosfato (PO4) + 2'-Desoxirribosa">
                <span class="bb-dot phosphate" title="Grupo Fosfato 5' (PO4^3-)">P</span>
                <span class="bb-hyphen">—</span>
                <span class="bb-dot sugar" title="Azúcar 2'-Desoxirribosa (pentosa)">D</span>
                <div class="bb-stem-down"></div>
              </div>

              <!-- Base Nitrogenada Sentido (5' -> 3') -->
              <div class="base-capsule primary-strand" :title="`Base nitrogenada: ${item.base} (unida al C1' de la desoxirribosa)`">
                <span class="letter font-mono">{{ item.base }}</span>
              </div>

              <!-- Enlaces de Hidrógeno Watson-Crick -->
              <div class="hydrogen-bond" :title="item.base === 'C' || item.base === 'G' ? '3 puentes de hidrógeno (C≡G)' : '2 puentes de hidrógeno (A=T)'">
                <span class="h-line"></span>
                <span class="h-line"></span>
                <span class="h-line" v-if="item.base === 'C' || item.base === 'G'"></span>
              </div>

              <!-- Base Nitrogenada Complementaria (3' -> 5') -->
              <div class="base-capsule comp-strand" :title="`Base complementaria: ${complementMap[item.base]}`">
                <span class="letter font-mono">{{ complementMap[item.base] }}</span>
              </div>

              <!-- Esqueleto Inferior Antiparalelo Azúcar-Fosfato (3' -> 5') -->
              <div class="bb-monomer bottom" title="Monómero 3': 2'-Desoxirribosa + Fosfato (antiparalelo)">
                <div class="bb-stem-up"></div>
                <span class="bb-dot sugar" title="Azúcar 2'-Desoxirribosa">D</span>
                <span class="bb-hyphen">—</span>
                <span class="bb-dot phosphate" title="Grupo Fosfato (PO4^3-)">P</span>
              </div>
            </div>
          </div>

          <div class="track-polarity-col right">
            <span class="polarity-tag p3" title="Extremo 3' Hidroxilo libre (-OH)">3' (OH)</span>
            <div class="polarity-v-link"></div>
            <span class="polarity-tag p5" title="Extremo 5' Fosfato libre complementario">5' (P)</span>
          </div>
        </div>

        <!-- Leyenda Macromolecular: Monómero de Nucleótido -->
        <div class="backbone-explanation-bar">
          <div class="legend-eq-item">
            <span class="sym-badge p">P</span>
            <span class="txt">Fosfato (PO₄³⁻)</span>
          </div>
          <span class="eq-op">+</span>
          <div class="legend-eq-item">
            <span class="sym-badge d">D</span>
            <span class="txt">2'-Desoxirribosa (Azúcar)</span>
          </div>
          <span class="eq-op">+</span>
          <div class="legend-eq-item">
            <span class="sym-badge b">Base</span>
            <span class="txt">A, T, C, G</span>
          </div>
          <span class="eq-op">=</span>
          <div class="legend-eq-item final">
            <span class="highlight-txt">Nucleótido Completo (dNMP)</span>
            <small>Cadenas unidas por enlaces fosfodiéster 3'→5' y puentes de H</small>
          </div>
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

    <!-- ========================================================================= -->
    <!-- MÓDULO 1: MUTAGÉNESIS Y REPARACIÓN CONTROLADA                             -->
    <!-- ========================================================================= -->
    <div class="phase-block g1-phase-block md3-card-outlined" v-if="cleanSequence">
      <div class="phase-block-header">
        <div class="phase-title-group">
          <div class="phase-avatar g1">1</div>
          <div>
            <h3>Fase G1: Vigilancia del Molde, Daño Químico y Reparación Pre-Replicativa</h3>
            <span class="subtext">Monitoreo pre-replicativo del molde: inducción de aductos/lesiones, sensor p53/MDM2 y reparación guiada por plantilla</span>
          </div>
        </div>
        <div :class="['checkpoint-status-pill', checkpointG1Status.badgeClass]">
          <Icon :name="checkpointG1Status.icon" size="16" />
          <span>{{ checkpointG1Status.statusTitle }}</span>
        </div>
      </div>

      <!-- Tarjeta Científica de Estado de Checkpoint G1/S, Dinámica p53/MDM2 y Freno Celular -->
      <div :class="['checkpoint-g1-card', 'md3-card-outlined', checkpointG1Status.state]">
        <div class="cp-card-header">
          <div class="cp-status-badge">
            <span :class="['cp-status-dot', checkpointG1Status.state]"></span>
            <Icon :name="checkpointG1Status.icon" size="20" />
            <span class="cp-status-title">{{ checkpointG1Status.statusTitle }}</span>
          </div>
          <div class="cp-phase-badge">
            <Icon name="verified_user" size="14" />
            <span>Fase G1 · Control Pre-Replicativo</span>
          </div>
        </div>

        <!-- Grid de los 3 Pilares Moleculares -->
        <div class="cp-grid-3col">
          <!-- Pilar 1: Dinámica p53 / MDM2 -->
          <div class="cp-node-box p53-node">
            <div class="cp-node-header">
              <Icon name="biotech" size="16" class="node-icon" />
              <span class="node-title">{{ checkpointG1Status.p53Title }}</span>
            </div>
            <div class="node-badge" :class="checkpointG1Status.state">
              {{ checkpointG1Status.p53Badge }}
            </div>
            <p class="node-desc">{{ checkpointG1Status.p53Details }}</p>
          </div>

          <!-- Pilar 2: Efector p21 / Freno CDK / Apoptosis -->
          <div class="cp-node-box p21-node">
            <div class="cp-node-header">
              <Icon name="block" size="16" class="node-icon" />
              <span class="node-title">{{ checkpointG1Status.p21Title }}</span>
            </div>
            <div class="node-badge" :class="checkpointG1Status.state">
              {{ checkpointG1Status.p21Badge }}
            </div>
            <p class="node-desc">{{ checkpointG1Status.p21Details }}</p>
          </div>

          <!-- Pilar 3: Separación Conceptual Punto R -->
          <div class="cp-node-box puntor-node">
            <div class="cp-node-header">
              <Icon name="alt_route" size="16" class="node-icon" />
              <span class="node-title">{{ checkpointG1Status.puntoRTitle }}</span>
            </div>
            <div class="node-badge bypass-tag">
              Bypass Externo ATM/ATR &rarr; p53 &rarr; p21
            </div>
            <p class="node-desc">{{ checkpointG1Status.puntoRDetails }}</p>
          </div>
        </div>

        <!-- Banner de Corrección Conceptual: Lesión vs Mutación -->
        <div class="cp-clarification-banner">
          <Icon name="info" size="16" class="banner-icon" />
          <div class="banner-body">
            <strong>Precisión Biológica Fundamental (Lesión vs Mutación):</strong>
            <span>{{ checkpointG1Status.damageNatureClarification }}</span>
          </div>
        </div>
      </div>

      <!-- Grid de G1: [Módulo 1.1 Daño en el Molde] a la IZQUIERDA, y [Módulo 1.3 Reparación Pre-Replicativa] a la DERECHA -->
      <div class="g1-actions-grid">
        <!-- MÓDULO 1.1: INDUCCIÓN DE DAÑO EN EL MOLDE PARENTAL -->
        <div class="op-panel g1-damage-card">
          <div class="op-panel-header">
            <div class="header-icon-mini">
              <Icon name="bolt" size="18" />
            </div>
            <div>
              <h4>Módulo 1.1: Inducción de Daño en el Molde</h4>
              <span class="op-sub">Comprueba cómo las lesiones físicas/químicas o aductos alteran el molde antes de la replicación</span>
            </div>
          </div>

          <!-- Selector de Modo de Daño: Ambiental vs Herramienta Exógena CRISPR -->
          <div class="sub-mode-toggle-row">
            <button 
              type="button" 
              :class="['sub-toggle-btn', { active: g1DamageMode === 'environmental' }]" 
              @click="g1DamageMode = 'environmental'"
            >
              <Icon name="wb_sunny" size="15" />
              <span>Daño Ambiental Estocástico</span>
            </button>
            <button 
              type="button" 
              :class="['sub-toggle-btn', { active: g1DamageMode === 'crispr' }]" 
              @click="g1DamageMode = 'crispr'"
            >
              <Icon name="content_cut" size="15" />
              <span>Herramienta Exógena (CRISPR-Cas9)</span>
            </button>
          </div>

          <!-- MODO A: DAÑO AMBIENTAL ESTOCÁSTICO (Luz UV, Estrés Oxidativo, Desaminación) -->
          <div v-if="g1DamageMode === 'environmental'" class="damage-subpanel">
            <div class="md3-textfield">
              <label>Agente Genotóxico / Lesivo Ambiental (Alberts cap. 5):</label>
              <select v-model="envAgent">
                <option value="uv_radiation">Radiación Ultravioleta (Luz UV · Dímeros T-T)</option>
                <option value="oxidative_ros">Estrés Oxidativo (Radicales Libres ROS · 8-oxo-G)</option>
                <option value="deamination">Desaminación Espontánea (Hidrólisis C → U/T)</option>
              </select>
            </div>

            <div class="slider-module">
              <div class="slider-telemetry">
                <span class="slider-title">Intensidad / Probabilidad de Lesión:</span>
                <span class="slider-rate font-mono">{{ Math.round(envIntensity * 100) }}%</span>
              </div>
              <input 
                type="range" 
                v-model.number="envIntensity" 
                min="0.10" 
                max="0.80" 
                step="0.05" 
                class="md3-range-slider"
              />
              <div class="slider-marks">
                <span>10% (Baja exposición)</span>
                <span>40% (Estrés moderado)</span>
                <span>80% (Sobrecarga de lesiones)</span>
              </div>
            </div>

            <button class="md3-button-filled" @click="applyEnvironmentalDamage" :disabled="loading">
              <Icon name="bolt" size="18" />
              <span>Inducir Lesiones Ambientales en el Molde</span>
            </button>

            <!-- Feedback de lesiones ambientales -->
            <div class="env-damage-feedback" v-if="envDamageResult">
              <span class="env-tag">{{ envDamageResult.agent_name }}</span>
              <p class="env-mechanism">{{ envDamageResult.mechanism_description }}</p>
              <div class="lesions-list font-mono" v-if="envDamageResult.lesions?.length">
                <span v-for="(les, i) in envDamageResult.lesions" :key="i" class="lesion-chip">
                  Pos. {{ les.position }}: {{ les.original_base }} → {{ les.damaged_base }}
                </span>
              </div>
            </div>
          </div>

          <!-- MODO B: EDICIÓN QUIRÚRGICA CRISPR -->
          <div v-else class="damage-subpanel">
            <div class="op-form-grid">
              <div class="md3-textfield">
                <label>Posición Cero-Indexada:</label>
                <input type="number" v-model.number="controlledForm.position" :min="0" :max="cleanSequence.length" class="font-mono" />
              </div>

              <div class="md3-textfield">
                <label>Tipo de Alteración / Lesión:</label>
                <select v-model="controlledForm.type">
                  <option value="substitution">Lesión Puntual / Aducto Químico (Sustitución)</option>
                  <option value="insertion">Lesión por Inserción (+1 Base)</option>
                  <option value="deletion">Lesión por Deleción (-1 Base)</option>
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
              <span>Inducir Lesión Dirigida (CRISPR-Cas9)</span>
            </button>
          </div>
        </div>

        <!-- MÓDULO 1.2: DETECCIÓN DE APAREAMIENTOS INCORRECTOS (junto al 1.1) -->
        <div class="duplex-card s-mmr-card">
          <div class="card-subtitle">
            <Icon name="science" size="18" />
            <span>Módulo 1.2: Detección de Apareamientos Incorrectos</span>
          </div>
          <p class="desc-text">
            Compara la hebra alterada con la complementaria del molde original e identifica los pares no canónicos.
          </p>

          <div class="md3-textfield">
            <label>Cadena a Comprobar:</label>
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

          <!-- Alerta de Validación de Longitudes Desincronizadas -->
          <div class="status-banner warning duplex-length-warning" v-if="duplexLengthMismatch">
            <Icon name="warning" size="18" />
            <span>Las cadenas tienen longitudes diferentes. Pulsa 'Complementaria' para regenerar el dúplex pareado.</span>
          </div>

          <button class="md3-button-filled" @click="runMismatchDetection" :disabled="loading">
            <Icon name="analytics" size="18" />
            <span>Escanear Apareamientos</span>
          </button>

          <!-- Resultados de Apareamientos -->
          <div class="mismatch-feedback" v-if="mismatchResult && Array.isArray(mismatchResult.mismatches)">
            <div :class="['status-banner', mismatchResult.is_fully_canonical ? 'success' : 'warning']">
              <Icon :name="mismatchResult.is_fully_canonical ? 'check_circle' : 'warning'" size="18" />
              <span>
                {{ mismatchResult.is_fully_canonical 
                  ? 'Apareamiento 100% canónico Watson-Crick.' 
                  : `${mismatchResult.mismatch_count || 0} apareamiento(s) no canónico(s) detectado(s).` }}
              </span>
            </div>

            <div class="pairs-visual-strip">
              <div 
                v-for="pair in visibleDuplexPairs" 
                :key="pair.idx" 
                :class="['pair-pill', pair.is_canonical ? 'canonical' : 'non-canonical']"
                :title="pair.note"
              >
                <span class="p-idx font-mono">{{ pair.idx }}</span>
                <span class="p-b1 font-mono">{{ pair.b1 }}</span>
                <span class="p-conn">:</span>
                <span class="p-b2 font-mono">{{ pair.b2 }}</span>
              </div>
            </div>

            <div class="scientific-disclaimer-mini" v-if="(mismatchResult.mismatch_count || 0) > 0">
              <Icon name="info" size="14" />
              <span>Regla del modelo: El sistema marca el error sin conjeturar arbitrariamente la base original en ausencia de plantilla fiable.</span>
            </div>
          </div>
        </div>

        <!-- MÓDULO 1.3: REPARACIÓN PRE-REPLICATIVA DEL MOLDE (BER / NER / HOMOLOGÍA) -->
        <!-- MÓDULO 1.3: REPARACIÓN PRE-REPLICATIVA DEL MOLDE (BER / NER / HOMOLOGÍA) -->
        <div class="duplex-card g1-repair-card">
          <div class="card-subtitle">
            <Icon name="shield" size="18" />
            <span>Módulo 1.3: Reparación del Molde (BER / NER / Homología)</span>
          </div>
          <p class="desc-text">
            Corrige lesiones físicas/químicas o aductos en la hebra molde parental utilizando la plantilla de referencia homóloga.
          </p>

          <!-- Slider de Eficiencia Enzimática de Escisión (BER / NER) -->
          <div class="slider-module repair-eff-slider">
            <div class="slider-telemetry">
              <span class="slider-title">Capacidad / Eficiencia de Escisión (BER / NER):</span>
              <span class="slider-rate font-mono highlight-repair">{{ Math.round(repairEfficiency * 100) }}%</span>
            </div>
            <input 
              type="range" 
              v-model.number="repairEfficiency" 
              min="0.50" 
              max="0.98" 
              step="0.05" 
              class="md3-range-slider repair-range"
            />
            <div class="slider-marks">
              <span>50% (Saturación/Dosis masiva)</span>
              <span>85% (Fisiológica normal)</span>
              <span>98% (Alta concentración)</span>
            </div>
          </div>

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
              <span>Usar Molde Inicial</span>
            </button>
            <button class="md3-button-filled" @click="runReferenceRepair" :disabled="loading">
              <Icon name="build" size="18" />
              <span>Ejecutar Ciclo de Escisión Enzimática</span>
            </button>
          </div>

          <!-- Resultado de Reparación G1 -->
          <div class="repair-feedback" v-if="repairResult && repairResult.repaired_sequence">
            <div :class="['status-banner', repairResult.matches_reference ? 'success' : 'warning']">
              <Icon :name="repairResult.matches_reference ? 'check_circle' : 'warning'" size="18" />
              <div>
                <strong>Estado: {{ repairResult.matches_reference ? 'Molde Restaurado al 100%' : 'Reparación Parcial: Lesiones Escaparon a la Escisión' }}</strong>
                <p>
                  {{ repairResult.matches_reference 
                    ? 'La hebra molde recuperó su secuencia original.' 
                    : `Se repararon ${repairResult.repaired_positions?.length || 0} lesiones. Sin embargo, ${repairResult.escaped_positions?.length || (repairResult.remaining_divergences || 0)} lesiones escaparon al reconocimiento enzimático en este ciclo. Ejecuta otro ciclo enzimático para continuar la escisión de las lesiones remanentes.` }}
                </p>
              </div>
            </div>

            <!-- Chips de lesiones que escaparon -->
            <div class="escaped-lesions-box" v-if="!repairResult.matches_reference && repairResult.escaped_positions?.length">
              <span class="esc-label">Posiciones que escaparon a la reparación:</span>
              <div class="esc-chips font-mono">
                <span v-for="p in repairResult.escaped_positions" :key="p" class="esc-chip">
                  Posición {{ p }}
                </span>
              </div>
            </div>

            <div class="repaired-seq-preview">
              <span class="tag">Molde Consolidado:</span>
              <code class="font-mono">{{ repairResult.repaired_sequence }}</code>
            </div>
          </div>
        </div>
      </div>
    </div>

      <!-- MÓDULO 2: DIFF INSPECTOR -->
      <div class="diff-inspector-card" v-if="diffResult && Array.isArray(diffResult.differences)">
        <div class="diff-header">
          <div class="diff-title-row">
            <Icon name="compare_arrows" size="24" class="diff-icon" />
            <div>
              <h3>Módulo 2: Reporte Diferencial (Original vs Modificada)</h3>
              <span class="diff-meta">Posiciones y cambios detectados entre ambas secuencias</span>
            </div>
          </div>

          <div :class="['diff-badge-pill', { alert: (diffResult.difference_count || 0) > 0 }]">
            <Icon :name="(diffResult.difference_count || 0) > 0 ? 'warning' : 'check_circle'" size="16" class="pill-icon" />
            <span>{{ diffResult.difference_count || 0 }} mutaciones detectadas</span>
          </div>
        </div>

        <div class="diff-alignment-table" v-if="diffResult.reference !== undefined || diffResult.modified !== undefined">
          <div class="alignment-row">
            <span class="row-tag">MOLDE REFERENCIA:</span>
            <code class="font-mono strand-stream">{{ diffResult.reference || '' }}</code>
          </div>
          <div class="alignment-row">
            <span class="row-tag modified">MODIFICADA:</span>
            <code class="font-mono strand-stream mod-stream">{{ diffResult.modified || '' }}</code>
          </div>
        </div>

        <div class="mutation-events-grid" v-if="diffResult.differences && diffResult.differences.length > 0">
          <div v-for="(d, i) in (diffResult.differences || [])" :key="i" class="mutation-card">
            <div class="m-top">
              <span class="m-coord font-mono">Posición {{ d.position }}</span>
              <span :class="['m-type-chip', d.status]">
                {{ d.status === 'changed' ? 'Sustitución' : d.status === 'inserted' ? 'Inserción' : d.status === 'deleted' ? 'Deleción' : d.status }}
              </span>
            </div>
            <div class="m-transition">
              <span class="base-old font-mono">{{ d.reference_base || '∅' }}</span>
              <Icon name="arrow_forward" size="14" class="arrow" />
              <span class="base-new font-mono">{{ d.modified_base || '∅' }}</span>
            </div>
          </div>
        </div>
      </div>


    <!-- 7 & 10: Cuaderno de Bitácora / Registro de Experimentos & Marco Científico -->
    <div class="audit-log-card md3-card-outlined" v-if="cleanSequence">
      <div class="section-header">
        <div class="section-title-group">
          <Icon name="history" size="22" class="section-icon" />
          <div>
            <h3>Módulo 3: Registro de Experimentos & Trazabilidad de Operaciones</h3>
            <span class="subtext">Auditoría inmutable de secuencias, mutaciones, métodos y resoluciones</span>
          </div>
        </div>
        <div class="audit-header-chips">
          <button class="md3-chip" type="button" @click="fetchLogs" title="Actualizar lista de eventos">
            <Icon name="restart_alt" size="14" />
            <span>Refrescar Registro ({{ experimentLogs.length }})</span>
          </button>
          <button class="md3-chip clear-logs-chip" type="button" @click="handleClearLogs" :disabled="experimentLogs.length === 0" title="Vaciar todo el historial de auditoría de la sesión">
            <Icon name="delete" size="14" />
            <span>Limpiar Historial</span>
          </button>
        </div>
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
              <th>ID Ensayo</th>
              <th>Operación</th>
              <th>Detalle Molecular</th>
              <th>Secuencia Inicial</th>
              <th>Secuencia Resultante</th>
              <th>Plantilla Guía</th>
              <th>Conclusión / Estado</th>
              <th>Acción</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="ev in experimentLogs" :key="ev.experiment_id">
              <td>
                <code class="font-mono exp-id">{{ ev.experiment_id }}</code>
                <div v-if="ev.parameters?.saved_name" class="exp-custom-name" title="Nombre asignado por el usuario">
                  <Icon name="bookmark" size="11" />
                  <span>{{ ev.parameters.saved_name }}</span>
                </div>
              </td>
              <td>
                <span :class="['op-chip', getOpBadgeClass(ev.operation_type)]">
                  {{ formatOperationName(ev.operation_type) }}
                </span>
              </td>
              <td>
                <span class="event-detail-text">{{ formatEventDetails(ev) }}</span>
              </td>
              <td><code class="font-mono seq-cell">{{ ev.initial_sequence }}</code></td>
              <td><code class="font-mono seq-cell">{{ ev.final_sequence }}</code></td>
              <td>
                <span v-if="ev.reference_used" class="font-mono ref-text">{{ ev.reference_used }}</span>
                <span v-else class="no-ref">Sin plantilla homóloga</span>
              </td>
              <td>
                <span :class="['res-status', getResultBadgeClass(ev)]">
                  {{ formatResultName(ev) }}
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
      <!-- Estado Vacío cuando no hay eventos -->
      <div class="empty-logs-notice" v-else>
        <Icon name="history_toggle_off" size="26" class="empty-icon" />
        <span>No hay eventos de mutación o reparación registrados en esta sesión.</span>
      </div>
    </div>

    </div><!-- /phase-content-wrapper Phase 1 -->

    <!-- ═══════════════════════ CONTENEDOR FASE 2: EXPRESIÓN GÉNICA ═══════════════════════ -->
    <div class="phase-content-wrapper" v-show="activePhaseTab === 'phase2'">

      <!-- Módulo A: Inspección y Arquitectura del Gen Modelo -->
      <div class="module-a-gene-card md3-card-outlined" v-if="selectedGene">
        <div class="module-a-header">
          <div class="module-a-title-group">
            <div class="module-a-avatar">A</div>
            <div>
              <div class="module-a-title-row">
                <h3>Módulo A: Inspección y Arquitectura del Gen Modelo</h3>
                <span class="gene-active-pill">{{ selectedGene.name }}</span>
              </div>
              <span class="subtext">Ficha biofísica detallada, organización exón/intrón y marco de lectura para la expresión génica</span>
            </div>
          </div>
          <div :class="['provenance-badge', selectedGene.data_source.type === 'secuencia_curada_publicada' ? 'curated' : 'didactic']">
            <Icon :name="selectedGene.data_source.type === 'secuencia_curada_publicada' ? 'verified' : 'school'" size="14" />
            <span>{{ selectedGene.data_source.type === 'secuencia_curada_publicada' ? 'Curada Oficial' : 'Didáctica Sintética' }}</span>
          </div>
        </div>

        <div class="module-a-body">

        <!-- Cuadrícula de Telemetría -->
        <div class="hud-telemetry-grid">
          <div class="hud-cell">
            <span class="hud-label">Organismo</span>
            <span class="hud-value">{{ selectedGene.organism }}</span>
          </div>
          <div class="hud-cell">
            <span class="hud-label">Tipo Celular</span>
            <span class="hud-value">{{ selectedGene.cell_type }}</span>
          </div>
          <div class="hud-cell">
            <span class="hud-label">Coordenadas Genómicas</span>
            <span class="hud-value font-mono">{{ selectedGene.data_source.chromosome || `${selectedGene.start_coord}–${selectedGene.end_coord}` }}</span>
          </div>
          <div class="hud-cell">
            <span class="hud-label">Hebra Molde</span>
            <span :class="['hud-value', 'strand-badge', selectedGene.strand_orientation === '+' ? 'sense' : 'antisense']">
              {{ selectedGene.strand_orientation === '+' ? '+ Sentido (5→3)' : '− Antisentido (3→5)' }}
            </span>
          </div>
          <div class="hud-cell">
            <span class="hud-label">Tipo de Gen</span>
            <span :class="['hud-value', 'genetype-badge', selectedGene.gene_type]">
              {{ selectedGene.gene_type === 'protein_coding' ? '🧬 Codificante de Proteína' : '🔬 ARN No Codificante' }}
            </span>
          </div>
          <div class="hud-cell">
            <span class="hud-label">Marco de Lectura (ORF)</span>
            <span class="hud-value font-mono">Frame {{ selectedGene.cds_info.reading_frame }}</span>
          </div>
          <div class="hud-cell">
            <span class="hud-label">Promotor (TSS)</span>
            <span class="hud-value font-mono">{{ selectedGene.promoter.region }}</span>
          </div>
          <div class="hud-cell">
            <span class="hud-label">Codones CDS</span>
            <span class="hud-value font-mono">{{ selectedGene.cds_info.start_codon }} &rarr; {{ selectedGene.cds_info.stop_codon }} ({{ selectedGene.cds_info.cds_sequence.length }} bp)</span>
          </div>
        </div>

        <!-- Trazabilidad de Fuente -->
        <div class="hud-source-bar">
          <Icon name="info" size="14" />
          <span class="source-label">Fuente &amp; Trazabilidad:</span>
          <span class="source-value" v-if="selectedGene.data_source.type === 'secuencia_curada_publicada'">
            {{ selectedGene.data_source.database }} · Acceso: {{ selectedGene.data_source.accession }} · Versión: {{ selectedGene.data_source.version }} · Gen ID: {{ selectedGene.data_source.gene_id || 'N/A' }}
          </span>
          <span class="source-value" v-else>
            {{ selectedGene.data_source.description || 'Secuencia didáctica inventada para fines pedagógicos — no proviene de bases de datos biológicas.' }}
          </span>
        </div>

        <!-- Estructura Exón / Intrón Visual -->
        <div class="exon-intron-track">
          <div class="track-label-row">
            <Icon name="view_timeline" size="16" />
            <h5>Estructura Exón / Intrón (Arquitectura de Transcritos)</h5>
          </div>
          <div class="structure-strip">
            <div
              v-for="(segment, idx) in selectedGene.structure"
              :key="idx"
              :class="['strip-segment', segment.type]"
              :style="{ flex: (segment.end - segment.start) }"
              :title="`${segment.type === 'exon' ? 'Exón' : 'Intrón'} ${segment.label}: ${segment.start}–${segment.end} (${segment.end - segment.start} bp)`"
            >
              <span class="seg-label">{{ segment.label }}</span>
              <span class="seg-coords font-mono">{{ segment.start }}–{{ segment.end }}</span>
            </div>
          </div>
          <div class="structure-legend">
            <span class="legend-item exon"><span class="legend-dot"></span> Exón (secuencia codificante conservada)</span>
            <span class="legend-item intron"><span class="legend-dot"></span> Intrón (región intercalada que se remueve por empalme)</span>
            <span class="legend-item splice"><span class="legend-dot"></span> Sitios de empalme consenso (GU...AG)</span>
          </div>
        </div>

        <!-- Secuencia CDS para referencia rápida -->
        <div class="cds-preview-bar" v-if="selectedGene.cds_info.cds_sequence">
          <div class="cds-header-row">
            <div class="cds-label-group">
              <Icon name="code" size="16" />
              <span class="cds-label">Secuencia Codificante CDS ({{ selectedGene.cds_info.cds_sequence.length }} bp):</span>
            </div>
            <button class="cds-copy-btn" @click="handleCopySequence(selectedGene.cds_info.cds_sequence)" title="Copiar secuencia CDS">
              <Icon name="content_copy" size="14" />
              <span>Copiar CDS</span>
            </button>
          </div>
          <code class="font-mono cds-code">{{ selectedGene.cds_info.cds_sequence }}</code>
        </div>
      </div>
    </div>

      <!-- ═══════════════════════ MÓDULO B: TRANSCRIPCIÓN (ADN → PRE-ARNM) ═══════════════════════ -->
      <div class="module-b-transcription-card md3-card-outlined" id="module-b-transcription-card" v-if="selectedGene || cleanSequence">
        <div class="module-b-header">
          <div class="module-b-title-group">
            <div class="module-b-avatar">B</div>
            <div>
              <div class="module-b-title-row">
                <h3>Módulo B: Transcripción in Silico (ADN → Pre-ARNm)</h3>
                <span :class="['module-b-pill', { 'synthesized': !!transcriptionResult }]">
                  {{ transcriptionResult ? 'Transcrito Primario Activo' : 'ARN Polimerasa II en Espera' }}
                </span>
              </div>
              <span class="subtext">Catálisis enzimática por ARN Polimerasa II: lectura de hebra molde 3'&rarr;5' y síntesis complementaria de ribonucleótidos 5'&rarr;3'</span>
            </div>
          </div>
        </div>

        <div class="module-b-body">
          <!-- Contexto Enzimático: ARN Polimerasa II -->
          <div class="enzyme-context-box">
            <div class="enzyme-icon-circle">
              <Icon name="biotech" size="22" />
            </div>
            <div class="enzyme-text">
              <div class="enzyme-headline">
                <strong>ARN Polimerasa II (Pol II)</strong>
                <span class="enzyme-tag">Maquinaria de Transcripción Eucariota</span>
              </div>
              <p>
                La enzima desenrolla la doble hélice de ADN a partir de la región promotora y recorre la <strong>Hebra Molde en dirección 3' &rarr; 5'</strong>.
                Incorpora ribonucleótidos trifosfato (rNTPs) canónicos complementarios: <strong>A&rarr;U, T&rarr;A, C&rarr;G, G&rarr;C</strong>,
                sintetizando el <strong>Pre-ARNm en dirección 5' &rarr; 3'</strong> con <strong>Uracilo (U)</strong> como base pirimidínica del ARN.
              </p>
            </div>
          </div>

          <!-- Caja de Inspección Pre-Transcripcional (Visible siempre en Módulo B) -->
          <div class="pre-transcription-dna-box">
            <div class="dna-buffer-header">
              <div class="dna-buffer-title-row">
                <div class="dna-buffer-title-group">
                  <Icon name="science" size="18" class="text-teal" />
                  <h4>ADN Activo en Buffer (Molde para ARN Pol II)</h4>
                </div>
                <div class="dna-buffer-badges">
                  <span class="dna-len-badge font-mono">
                    <Icon name="straighten" size="13" />
                    <strong>{{ activeDnaSequence.length }} bp</strong>
                  </span>
                  <span :class="['mold-status-badge', isDnaMoldModified ? 'mutated' : 'intact']">
                    <Icon :name="isDnaMoldModified ? 'warning' : 'verified'" size="14" />
                    <span>{{ isDnaMoldModified ? 'Molde Alterado en Fase 1 (Mutación activa / no reparada)' : 'Molde Canónico Intacto' }}</span>
                  </span>
                </div>
              </div>
              <p class="dna-buffer-notice">
                <Icon name="info" size="14" />
                <span>Esta es la secuencia exacta que leerá la ARN Polimerasa II al iniciar la transcripción.</span>
              </p>
            </div>

            <!-- Secuencia de ADN en tipografía mono -->
            <div class="dna-buffer-sequence-wrapper font-mono">
              <span class="dna-end-label">5'-</span>
              <div class="dna-buffer-code-ribbon">
                <span 
                  v-for="(base, idx) in activeDnaSequence" 
                  :key="idx"
                  :class="['dna-char', `base-${base.toLowerCase()}`, { 'char-modified': isBaseModifiedAt(idx) }]"
                  :title="`Posición ${idx + 1}: ${base}${isBaseModifiedAt(idx) ? ' [Base alterada respecto al molde inicial]' : ''}`"
                >{{ base }}</span>
              </div>
              <span class="dna-end-label">-3'</span>
            </div>

            <!-- Botón de Acción Principal y Estado -->
            <div class="dna-buffer-action-row">
              <div class="dna-buffer-status-text">
                <template v-if="transcriptionResult">
                  <span class="sync-status text-green">
                    <Icon name="check_circle" size="15" />
                    Transcrito de <strong>{{ transcriptionResult.length }} nt</strong> sintetizado y sincronizado con este ADN.
                  </span>
                </template>
                <template v-else>
                  <span class="sync-status text-dim">
                    <Icon name="play_arrow" size="15" />
                    Pulsa para que la ARN Polimerasa II abra la burbuja transcripcional y sintetice el Pre-ARNm.
                  </span>
                </template>
              </div>

              <button
                class="transcribe-action-btn md3-btn-filled"
                @click="runTranscription"
                :disabled="isTranscribing || !activeDnaSequence"
                id="btn-run-transcription"
                :title="isTranscribing ? 'Sintetizando pre-ARNm con ARN Polimerasa II...' : 'Iniciar síntesis enzimática de Pre-ARNm 5\' → 3\''"
              >
                <span class="btn-spinner" v-if="isTranscribing"></span>
                <Icon :name="isTranscribing ? 'autorenew' : (transcriptionResult ? 'restart_alt' : 'play_arrow')" size="18" v-else />
                <span>{{ isTranscribing ? 'ARN Polimerasa II Sintetizando...' : (transcriptionResult ? 'Re-sintetizar Pre-ARNm (5\' → 3\')' : 'Sintetizar Pre-ARNm (Transcripción 5\' → 3\')') }}</span>
              </button>
            </div>
          </div>

          <!-- Panel de Alineamiento Bioquímico de 3 Carriles (Visible cuando transcriptionResult exista) -->
          <div class="transcription-alignment-panel" v-if="transcriptionResult">
            <div class="alignment-panel-header">
              <div class="alignment-title-group">
                <Icon name="view_week" size="18" class="alignment-icon" />
                <div>
                  <h4>Panel de Alineamiento Bioquímico de Transcripción (3 Carriles)</h4>
                  <span class="alignment-subtext">Hebra Codificante 5'&rarr;3' &bull; Hebra Molde 3'&rarr;5' &bull; Pre-ARNm Transcrito Primario 5'&rarr;3'</span>
                </div>
              </div>

              <!-- Controles de Ventana/Paginación para secuencias de mayor longitud -->
              <div class="alignment-window-controls" v-if="transcriptionResult.length > TRANSCRIPTION_PAGE_SIZE">
                <span class="font-mono window-range-text">
                  nt {{ transcriptionWindowStart + 1 }}–{{ Math.min(transcriptionResult.length, transcriptionWindowStart + TRANSCRIPTION_PAGE_SIZE) }}
                  <small class="text-dim">de {{ transcriptionResult.length }} nt</small>
                </span>
                <button
                  class="nav-arrow-btn"
                  @click="scrollTranscriptionWindow(-TRANSCRIPTION_PAGE_SIZE)"
                  :disabled="transcriptionWindowStart === 0"
                  title="Retroceder ventana de ribonucleótidos"
                >
                  <Icon name="chevron_left" size="16" />
                </button>
                <button
                  class="nav-arrow-btn"
                  @click="scrollTranscriptionWindow(TRANSCRIPTION_PAGE_SIZE)"
                  :disabled="transcriptionWindowStart >= transcriptionResult.length - TRANSCRIPTION_PAGE_SIZE"
                  title="Avanzar ventana de ribonucleótidos"
                >
                  <Icon name="chevron_right" size="16" />
                </button>
              </div>
            </div>

            <!-- Carriles alineados tridimensionales / cinta ribbon -->
            <div class="alignment-lanes-container">
              <!-- Carril 1: Hebra Codificante ADN (5' → 3') -->
              <div class="alignment-lane lane-coding">
                <div class="lane-header-col">
                  <span class="lane-role-badge coding">Hebra Codificante ADN</span>
                  <span class="lane-orientation font-mono">5' &rarr; 3'</span>
                </div>
                <div class="lane-bases-track">
                  <div
                    v-for="col in visibleTranscriptionColumns"
                    :key="'cod-' + col.pos"
                    :class="['lane-base-cell', `base-${col.coding.toLowerCase()}`, { 'in-intron': col.isIntron }]"
                    :title="`Posición ${col.pos}: ${col.coding} (Hebra Codificante de Entrada)`"
                  >
                    <span class="pos-index font-mono">{{ col.pos }}</span>
                    <span class="base-char font-mono">{{ col.coding }}</span>
                  </div>
                </div>
              </div>

              <!-- Carril Intermedio 1-2: Puentes de Hidrógeno Watson-Crick -->
              <div class="alignment-lane lane-connectors">
                <div class="lane-header-col connector-label">
                  <span>Puentes H</span>
                </div>
                <div class="lane-bases-track">
                  <div
                    v-for="col in visibleTranscriptionColumns"
                    :key="'conn1-' + col.pos"
                    class="lane-connector-cell"
                    :title="(col.coding === 'A' || col.coding === 'T') ? '2 Puentes de Hidrógeno (A=T)' : '3 Puentes de Hidrógeno (G≡C)'"
                  >
                    <span class="h-bond-symbol font-mono">{{ (col.coding === 'A' || col.coding === 'T') ? '::' : ':::' }}</span>
                  </div>
                </div>
              </div>

              <!-- Carril 2: Hebra Molde ADN (3' → 5') -->
              <div class="alignment-lane lane-template">
                <div class="lane-header-col">
                  <span class="lane-role-badge template">Hebra Molde ADN</span>
                  <span class="lane-orientation font-mono">3' &rarr; 5'</span>
                </div>
                <div class="lane-bases-track">
                  <div
                    v-for="col in visibleTranscriptionColumns"
                    :key="'tpl-' + col.pos"
                    :class="['lane-base-cell', `base-${col.template.toLowerCase()}`, { 'in-intron': col.isIntron }]"
                    :title="`Posición ${col.pos}: ${col.template} (Hebra Molde complementaria leída por ARN Pol II)`"
                  >
                    <span class="base-char font-mono">{{ col.template }}</span>
                  </div>
                </div>
              </div>

              <!-- Carril Intermedio 2-3: Flecha de Catálisis ARN Polimerasa II -->
              <div class="alignment-lane lane-pol-arrow">
                <div class="lane-header-col pol-label">
                  <span>ARN Pol II &darr;</span>
                </div>
                <div class="lane-bases-track">
                  <div
                    v-for="col in visibleTranscriptionColumns"
                    :key="'pol-' + col.pos"
                    class="lane-connector-cell pol-arrow-cell"
                    :title="`ARN Pol II lee molde ${col.template} e incorpora ribonucleótido ${col.rna}`"
                  >
                    <span class="pol-arrow">&darr;</span>
                  </div>
                </div>
              </div>

              <!-- Carril 3: Pre-ARNm Transcrito Primario (5' → 3') -->
              <div class="alignment-lane lane-rna">
                <div class="lane-header-col">
                  <span class="lane-role-badge rna">Pre-ARNm Primario</span>
                  <span class="lane-orientation font-mono">5' &rarr; 3'</span>
                </div>
                <div class="lane-bases-track">
                  <div
                    v-for="col in visibleTranscriptionColumns"
                    :key="'rna-' + col.pos"
                    :class="[
                      'lane-base-cell',
                      'rna-cell',
                      `base-${col.rna.toLowerCase()}`,
                      { 'is-uracil': col.isUracil, 'in-intron': col.isIntron }
                    ]"
                    :title="`Ribonucleótido ${col.pos}: ${col.rna} ${col.isUracil ? '(Uracilo incorporado en lugar de Timina)' : ''} ${col.isIntron ? '[Segmento Intrónico]' : ''}`"
                  >
                    <span class="base-char font-mono">{{ col.rna }}</span>
                    <span class="u-glow-dot" v-if="col.isUracil"></span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Leyenda del Alineamiento -->
            <div class="alignment-legend-bar">
              <div class="legend-chip">
                <span class="legend-color-dot coding-dot"></span>
                <span>Hebra Codificante ADN (5'&rarr;3')</span>
              </div>
              <div class="legend-chip">
                <span class="legend-color-dot template-dot"></span>
                <span>Hebra Molde ADN (3'&rarr;5')</span>
              </div>
              <div class="legend-chip highlight-uracil">
                <span class="legend-color-dot uracil-dot"></span>
                <span>Ribonucleótido Uracilo (U) &bull; Sustitución Canónica de Timina</span>
              </div>
              <div class="legend-chip" v-if="transcriptionResult.has_introns">
                <span class="legend-color-dot intron-dot"></span>
                <span>Región Intrón (GTAG / GUAG)</span>
              </div>
            </div>

            <!-- HUD de Telemetría del Pre-ARNm -->
            <div class="transcription-hud-grid">
              <div class="hud-stat-card">
                <div class="stat-header">
                  <Icon name="straighten" size="16" />
                  <span>Longitud Total</span>
                </div>
                <div class="stat-value font-mono">
                  <span class="value-number">{{ transcriptionResult.length }}</span>
                  <span class="value-unit">nt</span>
                </div>
                <span class="stat-subtext">Ribonucleótidos sintetizados por ARN Pol II</span>
              </div>

              <div class="hud-stat-card">
                <div class="stat-header">
                  <Icon name="science" size="16" />
                  <span>Contenido de Uracilo</span>
                </div>
                <div class="stat-value font-mono">
                  <span class="value-number text-uracil">{{ transcriptionResult.uracil_content }}</span>
                  <span class="value-unit">%</span>
                </div>
                <div class="stat-progress-bar">
                  <div class="stat-progress-fill uracil-fill" :style="{ width: `${transcriptionResult.uracil_content}%` }"></div>
                </div>
                <span class="stat-subtext">{{ transcriptionResult.base_counts.U }} de {{ transcriptionResult.length }} ribonucleótidos son Uracilo (U)</span>
              </div>

              <div class="hud-stat-card ribonucleotide-distribution-card">
                <div class="stat-header">
                  <Icon name="pie_chart" size="16" />
                  <span>Distribución de Ribonucleótidos</span>
                </div>
                <div class="ribo-distribution-row">
                  <div class="ribo-count-pill ribo-a">
                    <span class="pill-base">A</span>
                    <span class="pill-val font-mono">{{ transcriptionResult.base_counts.A }}</span>
                  </div>
                  <div class="ribo-count-pill ribo-u highlight">
                    <span class="pill-base">U</span>
                    <span class="pill-val font-mono">{{ transcriptionResult.base_counts.U }}</span>
                  </div>
                  <div class="ribo-count-pill ribo-c">
                    <span class="pill-base">C</span>
                    <span class="pill-val font-mono">{{ transcriptionResult.base_counts.C }}</span>
                  </div>
                  <div class="ribo-count-pill ribo-g">
                    <span class="pill-base">G</span>
                    <span class="pill-val font-mono">{{ transcriptionResult.base_counts.G }}</span>
                  </div>
                </div>
                <span class="stat-subtext">Composición estequiométrica del transcrito primario</span>
              </div>

              <div class="hud-stat-card status-card" :class="{ 'has-intron-warning': transcriptionResult.has_introns }">
                <div class="stat-header">
                  <Icon :name="transcriptionResult.has_introns ? 'warning' : 'info'" size="16" />
                  <span>Estado Biofísico del Transcrito</span>
                </div>
                <div class="immature-status-banner">
                  <strong>Transcrito Primario Inmaduro</strong>
                  <span class="status-detail">Requiere procesamiento de Splicing en Módulo C</span>
                </div>
                <div class="intron-flag-pill" v-if="transcriptionResult.has_introns">
                  <Icon name="content_cut" size="13" />
                  <span>Intrones presentes (ej. GUAG) &bull; No traducible directamente</span>
                </div>
                <div class="intron-flag-pill no-introns" v-else>
                  <Icon name="check" size="13" />
                  <span>Secuencia homogénea (preparada para procesamiento)</span>
                </div>
              </div>
            </div>

            <!-- Secuencia Completa de Pre-ARNm (5' → 3') -->
            <div class="pre-mrna-sequence-box">
              <div class="seq-box-header">
                <div class="seq-box-title">
                  <Icon name="code" size="16" />
                  <span class="cds-label">Cadena Completa de Pre-ARNm (5' &rarr; 3') [{{ transcriptionResult.length }} nt]:</span>
                </div>
                <button class="cds-copy-btn" @click="copyPreMrnaSequence" title="Copiar cadena de Pre-ARNm al portapapeles">
                  <Icon name="content_copy" size="14" />
                  <span>Copiar Pre-ARNm</span>
                </button>
              </div>
              <code class="font-mono pre-mrna-code"><span class="end-tag">5'-</span><template v-for="(char, cIdx) in transcriptionResult.pre_mrna" :key="cIdx"><span :class="['rna-char', { 'char-u': char === 'U' }]">{{ char }}</span></template><span class="end-tag">-3'</span></code>
            </div>
          </div>
        </div>
      </div>

      <!-- Estado Informativo cuando selectedGene es null (Entrada Libre / Personalizada) -->
      <div class="phase2-empty-state md3-card-outlined" v-if="!selectedGene">
        <div class="empty-state-content">
          <div class="empty-icon-box">
            <Icon name="biotech" size="38" class="empty-icon-large" />
          </div>
          <h3>Secuencia Personalizada / Entrada Libre</h3>
          <p>Introduce cualquier secuencia canónica (A, T, C, G) en el campo superior o selecciona un gen modelo del catálogo para cargar su estructura biofísica oficial.</p>
        </div>
      </div>

    </div><!-- /phase-content-wrapper Phase 2 -->

    <!-- Diálogo Modal: Guardar Experimento con Nombre Personalizado -->
    <div class="md3-dialog-backdrop" v-if="showSaveDialog" @click.self="showSaveDialog = false">
      <div class="md3-dialog-surface md3-card-outlined save-dialog-surface">
        <div class="dialog-header">
          <div class="dialog-title-group">
            <Icon name="save" size="24" class="dialog-icon highlight" />
            <div>
              <h3>Guardar Experimento en Bitácora</h3>
              <span class="dialog-sub">Asigna un nombre descriptivo y notas científicas a este ensayo</span>
            </div>
          </div>
          <button class="dialog-close-btn" @click="showSaveDialog = false" title="Cerrar">✕</button>
        </div>

        <div class="dialog-body save-dialog-body">
          <!-- Resumen rápido del estado actual a guardar -->
          <div class="save-preview-card">
            <div class="preview-row">
              <span class="preview-label">Secuencia Actual (Resultante):</span>
              <code class="font-mono preview-code">{{ cleanSequence || sequenceInput }}</code>
            </div>
            <div class="preview-row" v-if="initialMoldSequence">
              <span class="preview-label">Molde Original:</span>
              <code class="font-mono preview-code-dim">{{ initialMoldSequence }}</code>
            </div>
            <div class="preview-row" v-if="lastMutationApplied">
              <span class="preview-label">Último Proceso Aplicado:</span>
              <span class="preview-tag">{{ formatMutationLabel(lastMutationApplied) }}</span>
            </div>
          </div>

          <div class="md3-textfield form-group">
            <label for="save-exp-name-input">Nombre del Experimento <span class="required-star">*</span>:</label>
            <input 
              id="save-exp-name-input"
              type="text" 
              v-model="saveExpForm.name" 
              placeholder="Ej: Ensayo de corte DSB y unión por extremos NHEJ..."
              class="save-input-name"
              @keydown.enter.prevent="confirmSaveExperiment"
              autofocus
            />
          </div>

          <div class="md3-textfield form-group">
            <label for="save-exp-notes-input">Notas / Observaciones del Investigador (Opcional):</label>
            <textarea 
              id="save-exp-notes-input"
              v-model="saveExpForm.notes" 
              rows="3"
              placeholder="Añade observaciones, condiciones del ensayo o justificación biológica..."
              class="save-input-notes"
            ></textarea>
          </div>
        </div>

        <div class="dialog-footer save-dialog-footer">
          <button class="md3-button-outlined" type="button" @click="showSaveDialog = false">
            <span>Cancelar</span>
          </button>
          <button class="md3-button-filled save-confirm-btn" type="button" @click="confirmSaveExperiment" :disabled="loading || !saveExpForm.name.trim()">
            <Icon name="check" size="18" />
            <span>Confirmar y Guardar</span>
          </button>
        </div>
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
            <p>Realiza inducción de daño o reparaciones en el laboratorio y pulsa <strong>"Guardar Experimento"</strong> para conservarlos aquí.</p>
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
                  <span :class="['exp-status-chip', exp.status]">{{ formatStatusText(exp.status) }}</span>
                </div>
                <h4 class="exp-title">{{ exp.name }}</h4>
                <p class="exp-notes-snippet" v-if="exp.notes">{{ exp.notes }}</p>

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
            <span>1. Flujo de Trabajo</span>
          </button>
          <button 
            :class="['manual-tab-btn', { active: manualActiveTab === 'buttons' }]" 
            @click="manualActiveTab = 'buttons'"
          >
            <Icon name="build" size="16" />
            <span>2. Guía de Botones</span>
          </button>
          <button 
            :class="['manual-tab-btn', { active: manualActiveTab === 'protocols' }]" 
            @click="manualActiveTab = 'protocols'"
          >
            <Icon name="biotech" size="16" />
            <span>3. Protocolos de Ensayo</span>
          </button>
          <button 
            :class="['manual-tab-btn', { active: manualActiveTab === 'faq' }]" 
            @click="manualActiveTab = 'faq'"
          >
            <Icon name="psychology" size="16" />
            <span>4. Fundamentos & FAQ</span>
          </button>
        </div>

        <div class="dialog-body manual-dialog-body">
          <!-- Pestaña 1: Flujo Experimental Paso a Paso -->
          <div v-if="manualActiveTab === 'flow'" class="manual-section-content">
            <div class="manual-hero-banner">
              <Icon name="science" size="24" />
              <div>
                <h4>Guía Operativa del Laboratorio (Módulos Activos de Fase G1)</h4>
                <p>Basado en <strong>Alberts et al. (Molecular Biology of the Cell 7.ª ed. cap. 5 y 9)</strong> y <strong>Lehninger (8.ª ed.)</strong>: Esta guía describe exclusivamente los módulos funcionales del simulador: validación molecular del molde parental B-DNA, inducción de daño genotóxico, sensor biofísico del Checkpoint G1/S (eje p53/MDM2/p21) y cinética enzimática de escisión pre-replicativa (BER/NER).</p>
              </div>
            </div>

            <!-- Mapa Visual de los 3 Bloques Funcionales Implementados -->
            <div class="manual-pipeline-roadmap">
              <div class="roadmap-phase phase-molde">
                <div class="rm-header">
                  <span class="rm-tag">ENTRADA Y ESTRUCTURA</span>
                  <h5>1. Molde Parental B-DNA</h5>
                </div>
                <div class="rm-content">
                  <span>• Validación de bases A, T, C, G</span>
                  <span>• Doble hélice B-DNA 3D interactiva</span>
                  <span>• Mapa 2D con esqueleto azúcar-fosfato</span>
                  <span>• Polaridad 5'→3' / 3'→5' y puentes H (2 vs 3)</span>
                </div>
                <div class="rm-footer cleared">Molde Base Validado</div>
              </div>

              <div class="roadmap-phase phase-dano">
                <div class="rm-header">
                  <span class="rm-tag">VIGILANCIA GENÓMICA</span>
                  <h5>2. Módulo 1.1 & Checkpoint G1/S</h5>
                </div>
                <div class="rm-content">
                  <span>• Daño ambiental estocástico (UV, ROS)</span>
                  <span>• Edición quirúrgica dirigida CRISPR-Cas9</span>
                  <span>• Distinción clave: Lesión vs Mutación</span>
                  <span class="rm-alert">• Eje ATM/ATR → p53/MDM2 → p21</span>
                </div>
                <div class="rm-footer alert-active">Freno Celular Activo</div>
              </div>

              <div class="roadmap-phase phase-escision">
                <div class="rm-header">
                  <span class="rm-tag">RESOLUCIÓN Y CONTROL</span>
                  <h5>3. Escisión, Diff & Auditoría</h5>
                </div>
                <div class="rm-content">
                  <span>• Módulo 1.2: Detección de Apareamientos</span>
                  <span>• Módulo 1.3: Escisión BER/NER (50%-98%)</span>
                  <span>• Módulo 2: Reporte Diff de Variantes</span>
                  <span>• Módulo 3: Bitácora Inmutable de Ensayos</span>
                </div>
                <div class="rm-footer restored">Molde Restaurado / Trazable</div>
              </div>
            </div>

            <!-- Acordeón Detallado de los Pasos Implementados en el Sistema -->
            <div class="flow-steps-accordion">
              <div class="flow-step-item">
                <div class="step-badge step-1">Paso 1</div>
                <div class="step-info">
                  <h5>Paso 1: Validación Físico-Química y Modelado Estructural del Molde Parental</h5>
                  <p>
                    <strong>Dónde ocurre:</strong> En la cabecera del laboratorio y visores macromoleculares.
                    <br>
                    <strong>Fundamento Biológico:</strong> En G1 la célula cuenta con su molécula parental sin duplicar. La secuencia ingresada establece la <strong>plantilla de referencia inmutable</strong>. El motor computacional valida reactivamente las bases nitrogenadas canónicas (A, T, C, G), calcula la longitud en pares de bases (bp), el porcentaje GC y la complementaria antiparalela Watson-Crick (5'→3' frente a 3'→5'), generando la doble hélice B-DNA 3D fotorrealista y el mapa 2D con monómeros azúcar-fosfato y puentes de hidrógeno estequiométricos (2 para A=T, 3 para C≡G).
                  </p>
                </div>
              </div>

              <div class="flow-step-item">
                <div class="step-badge step-2">Paso 2</div>
                <div class="step-info">
                  <h5>Paso 2: Inducción de Daño en el Molde y Distinción Fundamental (Lesión vs Mutación) (Módulo 1.1)</h5>
                  <p>
                    <strong>Dónde y cuándo ocurre:</strong> En la hebra molde en Fase G1, previo a cualquier evento de síntesis.
                    <br>
                    <strong>Precisión Biológica Fundamental (Lesión vs Mutación):</strong> En este simulador, las alteraciones moleculares inducidas en el molde son <em>lesiones o aductos en el ADN</em>: el sistema preserva la capacidad de extirparlas limpiamente mediante la maquinaria de escisión enzimática (BER/NER) guiada por el molde de referencia. Una mutación consolidada representaría un cambio irreversible que ya no es detectado como daño por los complejos enzimáticos.
                    <br>
                    • <em>Radiación Ultravioleta (Luz UV):</em> Provoca dímeros de ciclobutano entre timinas adyacentes (T-T) que curvan e impiden la geometría canónica de la hélice.
                    <br>
                    • <em>Estrés Oxidativo (ROS):</em> Radicales libres oxidan la guanina a 8-oxo-7,8-dihidroguanina (8-oxo-G), que aparea aberrantemente con adenina generando transversiones.
                    <br>
                    • <em>Desaminación Espontánea:</em> Hidrólisis que desamina la citosina convirtiéndola en uracilo (U), leído como timina.
                    <br>
                    • <em>Herramienta Exógena CRISPR-Cas9:</em> Modela la edición molecular quirúrgica dirigida (sustitución de base, inserción puntual +1 o microdeleción -1) en una coordenada específica.
                  </p>
                </div>
              </div>

              <div class="flow-step-item">
                <div class="step-badge step-3">Paso 3</div>
                <div class="step-info">
                  <h5>Paso 3: Monitoreo Molecular del Checkpoint G1/S (Eje ATM/ATR → p53/MDM2 → p21)</h5>
                  <p>
                    <strong>Respuesta Biológica Real del Sensor:</strong> En condiciones basales de reposo, el supresor tumoral p53 es ubiquitinado continuamente por la ligasa <strong>MDM2</strong> y degradado en el proteasoma 26S (vida media corta ~20 min).
                    <br>
                    1. <em>Detección y Fosforilación:</em> Ante lesiones del molde, quinasas sensoras (<strong>ATM y ATR</strong>) fosforilan a p53 en Ser15 y Ser20, impidiendo la unión de MDM2 y estabilizando al tetrámero de p53.
                    <br>
                    2. <em>Bypass y Freno sobre el Punto R:</em> p53 induce la transcripción del inhibidor universal de CDKs <strong>p21 (CDKN1A)</strong>. p21 bloquea los complejos Ciclina E-CDK2 y Ciclina D-CDK4/6, manteniendo hipofosforilada a la proteína del Retinoblastoma (<strong>Rb</strong>) e impidiendo la liberación del factor <strong>E2F</strong>. Esto impone un bypass de arresto celular estricto antes del Punto de Restricción (Punto R).
                    <br>
                    3. <em>Decisión Celular por Dosis:</em> Daños moderados activan el programa de reparación por escisión (BER/NER). Daños masivos o persistentes activan promotores de baja afinidad (<strong>BAX, PUMA, NOXA</strong>), conmutando a la apoptosis mitocondrial para proteger la viabilidad tisular.
                  </p>
                </div>
              </div>

              <div class="flow-step-item">
                <div class="step-badge step-4">Paso 4</div>
                <div class="step-info">
                  <h5>Paso 4: Inspección de Apareamientos en el Dúplex Molecular (Módulo 1.2)</h5>
                  <p>
                    <strong>Dónde ocurre:</strong> En el módulo de apareamiento bicatenario complementario.
                    <br>
                    <strong>Módulo 1.2:</strong> Permite contrastar la hebra molde contra una cadena de ensayo complementaria generada in silico, detectando enlaces canónicos Watson-Crick (A=T, C≡G) y localizando desajustes no canónicos (mismatches). Este escaneo visualiza la distorsión topológica que sufre la doble hélice ante pérdidas de complementariedad estricta.
                  </p>
                </div>
              </div>

              <div class="flow-step-item">
                <div class="step-badge step-5">Paso 5</div>
                <div class="step-info">
                  <h5>Paso 5: Cinética Enzimática de Escisión Pre-Replicativa (BER / NER) (Módulo 1.3)</h5>
                  <p>
                    <strong>Mecanismo Biológico de Escisión:</strong> Durante el arresto pre-replicativo en G1, la célula moviliza la <em>Reparación por Escisión de Bases (BER)</em> —mediante ADN glicosilasas que extirpan bases oxidadas o uracilos y AP endonucleasas— y la <em>Reparación por Escisión de Nucleótidos (NER)</em> —complejos escinucleasa TFIIH/XPC que cortan el parche lesionado—.
                    <br>
                    <strong>Cinética Enzimática Estocástica y Saturable:</strong> En la célula viva (Alberts cap. 5), la reparación no es un acto instantáneo al 100%; depende de la probabilidad de colisión catalítica y de la saturación del pool enzimático, regulada por el slider de <strong>Capacidad / Eficiencia de Escisión (50% a 98%)</strong>:
                    <br>
                    • Si en un ciclo catalítico escapan lesiones, <strong>el sensor p53 y p21 permanecen en alerta activa</strong> y la célula continúa arrestada en G1, informando las coordenadas exactas de las lesiones remanentes.
                    <br>
                    • La ejecución de ciclos catalíticos sucesivos reduce progresivamente la carga genotóxica. Al lograr la escisión completa (100%), MDM2 reanuda la degradación fisiológica de p53, p21 se desactiva y se restituye el estado basal para el avance celular.
                  </p>
                </div>
              </div>

              <div class="flow-step-item">
                <div class="step-badge step-6">Paso 6</div>
                <div class="step-info">
                  <h5>Paso 6: Reporte Diferencial (Módulo 2) y Trazabilidad Permanente (Módulo 3)</h5>
                  <p>
                    <strong>Módulo 2 (Diff Inspector):</strong> Contrasta directamente y en paralelo la secuencia molde de referencia frente a la secuencia modificada o reparada, desglosando cada variante molecular por coordenada exacta, tipo (Sustitución, Inserción, Deleción) y transición de base nitrogenada.
                    <br>
                    <strong>Módulo 3 (Auditoría & Trazabilidad):</strong> Registra criptográficamente cada operación en una bitácora inmutable con timestamp, permitiendo almacenar ensayos en disco local en formato JSON y restaurar el estado molecular íntegro de la simulación en cualquier momento.
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- Pestaña 2: Diccionario Exhaustivo de Cada Botón -->
          <div v-if="manualActiveTab === 'buttons'" class="manual-section-content">
            <div class="button-guide-grid">
              <!-- Header y Gestión de Sesión -->
              <div class="button-guide-card">
                <div class="card-tag">1. Cabecera, Muestras y Persistencia</div>
                <div class="btn-entry">
                  <span class="btn-name filled"><Icon name="save" size="14" /> Guardar Experimento</span>
                  <p>Persiste en disco inmutable del backend el ciclo de vida completo del ensayo: molde original, daño aplicado, apareamientos detectados, reparación ejecutada y reporte diff.</p>
                </div>
                <div class="btn-entry">
                  <span class="btn-name tonal"><Icon name="history" size="14" /> Cargar Experimento (N)</span>
                  <p>Despliega el catálogo de ensayos archivados para restaurar instantáneamente el estado molecular en el modelo 3D y todos los campos de análisis.</p>
                </div>
                <div class="btn-entry">
                  <span class="btn-name chip"><Icon name="restart_alt" size="14" /> Restaurar a Molde</span>
                  <p>Limpia lesiones y mutaciones activas, restableciendo la doble hélice al estado inicial del molde parental.</p>
                </div>
                <div class="btn-entry">
                  <span class="btn-name chip"><Icon name="menu_book" size="14" /> Manual del Lab</span>
                  <p>Abre este manual interactivo con la guía biológica paso a paso, diccionario de botones y protocolos experimentales.</p>
                </div>
                <div class="btn-entry">
                  <span class="btn-name chip"><Icon name="tag" size="14" /> Chips Muestras Estándar</span>
                  <p>Cargan secuencias patrón predefinidas: <em>Control Corto (12bp)</em> equilibrado, <em>Gen Sintético (20bp)</em> representativo de un ORF, y <em>Rica en GC (64.7%)</em> para ensayar estabilidad termodinámica.</p>
                </div>
              </div>

              <!-- Secuenciación y Entrada -->
              <div class="button-guide-card">
                <div class="card-tag">2. Secuenciación & Entrada de Datos</div>
                <div class="btn-entry">
                  <span class="btn-name filled"><Icon name="analytics" size="14" /> Validar Molde</span>
                  <p>Evalúa reactivamente la hebra de entrada, regenera la cadena complementaria antiparalela, calcula el porcentaje GC, conteo estequiométrico y actualiza la hélice 3D.</p>
                </div>
                <div class="btn-entry">
                  <span class="btn-name tonal"><Icon name="content_copy" size="14" /> Generar Copia de Trabajo</span>
                  <p>Copia de forma fidedigna la secuencia actual para experimentar libremente sobre ella manteniendo el molde parental como referencia inmutable.</p>
                </div>
              </div>

              <!-- Visor 3D y Controles de Cámara -->
              <div class="button-guide-card">
                <div class="card-tag">3. Visor Macromolecular 3D & Cámara</div>
                <div class="btn-entry">
                  <span class="btn-name chip"><Icon name="visibility" size="14" /> Curva In Vivo / Eje Lineal</span>
                  <p>Alterna la conformación espacial del B-DNA entre curvatura molecular natural en solución acuosa nuclear y un eje recto para medición cristalográfica.</p>
                </div>
                <div class="btn-entry">
                  <span class="btn-name icon-btn"><Icon name="fullscreen" size="14" /> Expandir / Contraer Visor</span>
                  <p>Amplía el canvas molecular a modo cinematográfico a pantalla completa para inspeccionar detalladamente surcos mayores y menores.</p>
                </div>
                <div class="btn-entry">
                  <span class="btn-name icon-btn"><Icon name="play_arrow" size="14" /> Pausar / Reanudar Rotación</span>
                  <p>Detiene o reactiva el giro orbital automático de la doble hélice para examinar pares de bases en un ángulo fijo.</p>
                </div>
                <div class="btn-entry">
                  <span class="btn-name icon-btn"><Icon name="add" size="14" /> Zoom + / Zoom -</span>
                  <p>Aproxima o aleja la cámara virtual respecto al centroide de la macromolécula (también disponible con la rueda del ratón).</p>
                </div>
                <div class="btn-entry">
                  <span class="btn-name icon-btn"><Icon name="restart_alt" size="14" /> Resetear Perspectiva Cenital</span>
                  <p>Centra la cámara virtual y restablece la inclinación y distancia orbital óptimas.</p>
                </div>
                <div class="btn-entry">
                  <span class="btn-name chip"><Icon name="touch_app" size="14" /> Clic en Peldaño / Base 3D</span>
                  <p>Selecciona el par de bases en la escena, despliega el anillo iluminado y activa el HUD con el detalle de puentes de hidrógeno Watson-Crick.</p>
                </div>
              </div>

              <!-- Track 2D y Esqueleto Azúcar-Fosfato -->
              <div class="button-guide-card">
                <div class="card-tag">4. Mapa 2D & Esqueleto Azúcar-Fosfato</div>
                <div class="btn-entry">
                  <span class="btn-name chip"><Icon name="touch_app" size="14" /> Clic en Columna de Base</span>
                  <p>Selecciona el nucleótido exacto, enfoca la cámara 3D sobre él y auto-rellena la posición en el formulario de edición quirúrgica CRISPR.</p>
                </div>
                <div class="btn-entry">
                  <span class="btn-name chip">Esqueleto 5' [P]-[D] y 3' [D]-[P]</span>
                  <p>Visualiza los enlaces fosfodiéster covalentes entre el grupo fosfato (P) y la desoxirribosa (D) con polaridad antiparalela estricta.</p>
                </div>
                <div class="btn-entry">
                  <span class="btn-name chip">Puentes H (2 vs 3 líneas)</span>
                  <p>Representa físicamente 2 puentes de hidrógeno para el par A=T y 3 puentes de hidrógeno para el par C≡G.</p>
                </div>
              </div>

              <!-- Módulo 1 -->
              <div class="button-guide-card">
                <div class="card-tag">5. Fase G1 · Vigilancia del Molde, Checkpoint p53/MDM2, Freno y Reparación</div>
                <div class="btn-entry">
                  <span class="btn-name chip"><Icon name="verified_user" size="14" /> Tarjeta de Estado Checkpoint G1/S</span>
                  <p>Muestra en tiempo real la dinámica biofísica del eje ATM/ATR → p53/MDM2 → p21. En reposo: p53 tiene vida media corta (~20 min) degradado por MDM2 en proteasoma. Daño leve/moderado: ATM/ATR fosforilan p53 (Ser15/Ser20), impidiendo degradación e induciendo p21 para frenar CDKs y activar BER/NER. Daño masivo: fosforilación sostenida (Ser46) que conmuta a programa de apoptosis mitocondrial (BAX, PUMA, NOXA).</p>
                </div>
                <div class="btn-entry">
                  <span class="btn-name chip"><Icon name="alt_route" size="14" /> Separación Conceptual: Punto R</span>
                  <p>Aclara que el Punto R evalúa únicamente factores mitogénicos de proliferación celular (Ciclina D/CDK4/6/Rb/E2F) y no detecta daños directamente. El freno celular ante lesiones es un bypass impuesto externamente desde la cascada ATM/ATR → p53 → p21.</p>
                </div>
                <div class="btn-entry">
                  <span class="btn-name chip"><Icon name="info" size="14" /> Banner de Precisión: Lesión vs Mutación</span>
                  <p>Aclara que en Fase G1 toda alteración es una lesión física/química o aducto reparable, y que solo se convertirá en mutación permanente si no se repara y se replica más adelante en la Fase S.</p>
                </div>
                <div class="btn-entry">
                  <span class="btn-name chip"><Icon name="wb_sunny" size="14" /> Daño Ambiental Estocástico (Módulo 1.1)</span>
                  <p>Activa el inductor de lesiones ambientales: Luz UV (dímeros TT), Estrés Oxidativo ROS (8-oxo-G) o Desaminación espontánea (C→U).</p>
                </div>
                <div class="btn-entry">
                  <span class="btn-name chip"><Icon name="content_cut" size="14" /> Herramienta Exógena (CRISPR-Cas9)</span>
                  <p>Modo de alteración dirigida en una coordenada indexada: lesión puntual / aducto (sustitución), inserción (+1 base) o deleción (-1 base).</p>
                </div>
                <div class="btn-entry">
                  <span class="btn-name filled"><Icon name="bolt" size="14" /> Inducir Lesiones Ambientales en el Molde</span>
                  <p>Aplica el agente genotóxico seleccionado según la intensidad regulada por el slider (10% a 80%), alertando al sensor p53/MDM2.</p>
                </div>
                <div class="btn-entry">
                  <span class="btn-name filled"><Icon name="content_cut" size="14" /> Inducir Lesión Dirigida (CRISPR-Cas9)</span>
                  <p>Aplica la edición quirúrgica en la posición elegida e informa al sensor molecular de daño.</p>
                </div>
                <div class="btn-entry">
                  <span class="btn-name chip"><Icon name="shuffle" size="14" /> Inducir Error / Complementaria (Módulo 1.2)</span>
                  <p>Alterna entre la complementaria exacta o inyectar deliberadamente una base no apareada en el Módulo 1.2 para probar la detección.</p>
                </div>
                <div class="btn-entry">
                  <span class="btn-name filled"><Icon name="analytics" size="14" /> Escanear Apareamientos (Módulo 1.2)</span>
                  <p>Compara la cadena con la complementaria del molde y marca pares canónicos Watson-Crick (verdes) y no canónicos (rojos).</p>
                </div>
                <div class="btn-entry">
                  <span class="btn-name chip"><Icon name="biotech" size="14" /> Cinética Enzimática de Escisión (BER / NER)</span>
                  <p>Modelo biológico in vivo del Módulo 1.3: reparación catalítica probabilística según capacidad enzimática fisiológica (50% - 98%).</p>
                </div>
                <div class="btn-entry">
                  <span class="btn-name chip">Slider Eficiencia de Escisión (50% - 98%)</span>
                  <p>Regula la probabilidad estocástica de escisión enzimática de cada lesión por ciclo (BER/NER).</p>
                </div>
                <div class="btn-entry">
                  <span class="btn-name tonal"><Icon name="tag" size="14" /> Usar Molde Inicial</span>
                  <p>Carga la secuencia parental original limpia en el campo de referencia homóloga para la reparación.</p>
                </div>
                <div class="btn-entry">
                  <span class="btn-name filled"><Icon name="build" size="14" /> Ejecutar Ciclo de Escisión Enzimática</span>
                  <p>Ejecuta una ronda catalítica de escisión. Si se limpia el 100% de las lesiones, p53/MDM2 vuelve al reposo basal y se desactiva el freno sobre las CDKs; si escapan lesiones por saturación, se reportan las posiciones no reparadas y continúa el arresto en G1.</p>
                </div>
              </div>

              <!-- Módulo 2 -->
              <div class="button-guide-card">
                <div class="card-tag">6. Módulo 2 · Reporte Diferencial</div>
                <div class="btn-entry">
                  <span class="btn-name chip">Diff Inspector (Módulo 2)</span>
                  <p>Muestra el contraste base a base entre el molde original y la secuencia modificada, con posición y tipo de cambio (sustitución, inserción, deleción).</p>
                </div>
              </div>

              <!-- Auditoría y Diálogos -->
              <div class="button-guide-card">
                <div class="card-tag">7. Módulo 3 · Auditoría & Modales</div>
                <div class="btn-entry">
                  <span class="btn-name chip"><Icon name="restart_alt" size="14" /> Refrescar Registro</span>
                  <p>Recarga desde el backend la tabla de auditoría con la trazabilidad completa de eventos, secuencias y dictámenes moleculares.</p>
                </div>
                <div class="btn-entry">
                  <span class="btn-name chip"><Icon name="delete" size="14" /> Limpiar Historial</span>
                  <p>Vacía el historial de auditoría de la sesión actual tras confirmación del investigador.</p>
                </div>
                <div class="btn-entry">
                  <span class="btn-name chip"><Icon name="arrow_forward" size="14" /> Cargar (en fila de tabla)</span>
                  <p>Restaura al instante en la pantalla de simulación el estado exacto de ese evento auditado.</p>
                </div>
                <div class="btn-entry">
                  <span class="btn-name filled">Confirmar y Guardar (Modal)</span>
                  <p>Registra en el archivo permanente JSON el experimento con título personalizado y notas de laboratorio del investigador.</p>
                </div>
                <div class="btn-entry">
                  <span class="btn-name filled">Cargar en Lab (Modal)</span>
                  <p>Restaura el experimento guardado completo: secuencias, conformación 3D, mutaciones y reporte diff.</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Pestaña 3: Protocolos de Ensayo Guiados -->
          <div v-if="manualActiveTab === 'protocols'" class="manual-section-content">
            <div class="protocol-card">
              <div class="protocol-card-header">
                <span class="proto-tag g1">Protocolo A (Fase G1)</span>
                <h4>Daño Ambiental en G1, Cinética Enzimática de Escisión y Checkpoint G1/S</h4>
              </div>
              <ol class="protocol-steps-list">
                <li>En la cabecera, haz clic en el chip <strong>"Control Corto (12bp)"</strong> para fijar un molde parental limpio.</li>
                <li>Observa la tarjeta de <strong>Checkpoint G1/S</strong> en estado verde (Reposo: MDM2 degrada continuamente a p53, sin freno activo sobre CDKs ni bloqueo del Punto R).</li>
                <li>En el <strong>Módulo 1.1</strong>, selecciona <em>"Daño Ambiental Estocástico"</em> y el agente <em>"Radiación Ultravioleta (Luz UV)"</em> con intensidad al 40%.</li>
                <li>Pulsa <strong>"Inducir Lesiones Ambientales en el Molde"</strong>.</li>
                <li>Observa la <strong>Tarjeta de Checkpoint G1/S</strong>: pasa de inmediato a alerta activa con ATM/ATR fosforilando a p53 (Ser15/Ser20), impidiendo su degradación por MDM2 e induciendo p21 para frenar las CDKs (Rb hipofosforilado) y activar la escisión BER/NER. Si la intensidad supera el 60% o se acumulan >3 lesiones, conmuta a alerta crítica de apoptosis mitocondrial (BAX, PUMA, NOXA).</li>
                <li>Desplázate al <strong>Módulo 1.3</strong> a la derecha, pulsa <strong>"Usar Molde Inicial"</strong>.</li>
                <li>Ajusta el slider de <strong>"Capacidad / Eficiencia de Escisión"</strong> al 75%.</li>
                <li>Pulsa <strong>"Ejecutar Ciclo de Escisión Enzimática"</strong>: comprueba cómo se reparan lesiones pero algunas escapan por cinética estocástica/saturación, manteniendo activo el sensor p53/p21 y mostrando los chips de posiciones no reparadas.</li>
                <li>Pulsa de nuevo <strong>"Ejecutar Ciclo de Escisión Enzimática"</strong> (ronda enzimática sucesiva) hasta resolver las lesiones remanentes: al alcanzar el 100%, p53/p21 vuelven al reposo basal degradado por MDM2 y se levanta el freno sobre las CDKs.</li>
              </ol>
            </div>

            <div class="protocol-card">
              <div class="protocol-card-header">
                <span class="proto-tag crispr">Protocolo B (Edición CRISPR)</span>
                <h4>Edición Quirúrgica CRISPR y Reporte Diferencial en Módulo 2</h4>
              </div>
              <ol class="protocol-steps-list">
                <li>En el <strong>Mapa de Alineamiento 2D</strong> o en el visor 3D, haz clic sobre la base en la posición 4.</li>
                <li>En el <strong>Módulo 1.1</strong>, cambia al modo <em>"Edición Quirúrgica CRISPR"</em>.</li>
                <li>Comprueba que la coordenada 4 se auto-asignó. Selecciona tipo <em>"Sustitución / Lesión Puntual"</em> y escoge una base nitrogenada diferente.</li>
                <li>Pulsa <strong>"Inducir Lesión Dirigida (CRISPR-Cas9)"</strong>: observa la alteración en la cadena y la activación del freno p53/p21 sobre el Punto R.</li>
                <li>Desplázate al <strong>Módulo 2 (Reporte Diferencial)</strong>: revisa el alineamiento comparativo entre el Molde Referencia y la secuencia Modificada, verificando la tarjeta de mutación con posición, tipo y bases implicadas.</li>
              </ol>
            </div>

            <div class="protocol-card">
              <div class="protocol-card-header">
                <span class="proto-tag duplex">Protocolo C (Dúplex Mismatch)</span>
                <h4>Detección de Apareamientos Incorrectos en el Dúplex (Módulo 1.2)</h4>
              </div>
              <ol class="protocol-steps-list">
                <li>Con un molde válido cargado, desplázate al <strong>Módulo 1.2 (Detección de Apareamientos Incorrectos)</strong>.</li>
                <li>Pulsa <strong>"Inducir Error / Complementaria"</strong> para inyectar deliberadamente una base no canónica en la cadena complementaria de prueba.</li>
                <li>Pulsa <strong>"Escanear Apareamientos"</strong>: el sistema analiza base a base el dúplex y marca los pares canónicos Watson-Crick en verde y los desajustes no canónicos en rojo.</li>
                <li>Analiza cómo la presencia de un desajuste altera la estabilidad energética y la complementariedad antiparalela del dúplex molecular.</li>
              </ol>
            </div>

            <div class="protocol-card">
              <div class="protocol-card-header">
                <span class="proto-tag audit">Protocolo D (Trazabilidad)</span>
                <h4>Auditoría Criptográfica, Guardado y Restauración de Ensayos (Módulo 3)</h4>
              </div>
              <ol class="protocol-steps-list">
                <li>Tras inducir daño o ejecutar escisiones enzimáticas, desplázate al <strong>Módulo 3 (Registro de Experimentos & Trazabilidad de Operaciones)</strong>.</li>
                <li>Examina la tabla de auditoría: verifica cómo cada evento cuenta con ID de ensayo, operación molecular, secuencia inicial, secuencia resultante y estado de resolución inmutable.</li>
                <li>Pulsa <strong>"Guardar Experimento"</strong> en la cabecera: asigna un título descriptivo (ej. "Ensayo_UV_Escision_12bp") y notas de laboratorio del investigador.</li>
                <li>En cualquier momento, abre <strong>"Cargar Experimento"</strong> para restaurar el estado molecular íntegro de la simulación o pulsa <strong>"Limpiar Historial"</strong> en el Módulo 3 para reiniciar la bitácora de trabajo.</li>
              </ol>
            </div>
          </div>

          <!-- Pestaña 4: Fundamentos, FAQ & Bibliografía -->
          <div v-if="manualActiveTab === 'faq'" class="manual-section-content">
            <div class="faq-container">
              <!-- FAQ 1: Cinética de reparación real -->
              <div class="faq-card">
                <div class="faq-q">
                  <Icon name="help" size="18" class="q-icon" />
                  <h5>¿La reparación del molde (BER/NER) se hace con probabilidad según la realidad biológica?</h5>
                </div>
                <div class="faq-a">
                  <p>
                    <strong>Fundamento Bioquímico (Alberts cap. 5; Lehninger cap. 25):</strong>
                    <br>
                    <strong>SÍ.</strong> En la célula viva, las enzimas de reparación (ADN glicosilasas para BER y complejos TFIIH/XPC para NER) no tienen un interruptor mágico que repare al 100% de manera instantánea.
                    <br>
                    Operan bajo <strong>cinética enzimática de colisión (Km, kcat)</strong>:
                    <br>
                    1. <em>Probabilidad finita de escisión:</em> Cada aducto o fotodímero tiene una probabilidad estocástica de ser reconocido y extirpado por unidad de tiempo.
                    <br>
                    2. <em>Saturación por sobrecarga:</em> Si la exposición a luz UV o ROS es alta, la concentración nuclear de glicosilasas y polimerasa β se satura. Algunas lesiones <strong>escapan</strong> a la primera ronda de inspección.
                    <br>
                    3. <em>Respuesta del Checkpoint G1/S:</em> Esta es precisamente la razón de ser de <strong>p53 y p21</strong>. Si una sola lesión escapa a la escisión, el sensor p53 permanece fosforilado y retiene a la célula en G1. Si la célula no consigue limpiar el molde tras varios ciclos, p53 activa la apoptosis para evitar transferir moldes lesionados a la síntesis celular.
                  </p>
                </div>
              </div>

              <!-- FAQ 2: Lesión vs Mutación -->
              <div class="faq-card">
                <div class="faq-q">
                  <Icon name="help" size="18" class="q-icon" />
                  <h5>¿Cómo distingue el simulador entre una lesión del molde y una mutación consolidada?</h5>
                </div>
                <div class="faq-a">
                  <p>
                    <strong>Precisión Conceptual Canónica:</strong>
                    <br>
                    En el simulador, las alteraciones inducidas en el molde (UV, ROS o desaminación) son tratadas como <strong>lesiones físicas o aductos reversibles</strong>. La información original no se destruye porque el complejo de escisión enzimática (BER/NER) puede identificar y extirpar la base alterada restaurando la secuencia fidedigna guiado por la plantilla de referencia.
                    <br>
                    Por el contrario, una <strong>mutación</strong> representa una base incorporada de forma permanente que forma enlaces canónicos normales y ya no es detectada como daño por las ADN glicosilasas, requiriéndose el <strong>Reporte Diferencial (Módulo 2)</strong> para contrastarla contra el molde de referencia.
                  </p>
                </div>
              </div>

              <!-- FAQ 3: Punto R vs Checkpoint G1/S -->
              <div class="faq-card">
                <div class="faq-q">
                  <Icon name="help" size="18" class="q-icon" />
                  <h5>¿Por qué el Punto de Restricción (Punto R) y el Checkpoint G1/S no son lo mismo?</h5>
                </div>
                <div class="faq-a">
                  <p>
                    <strong>Separación Molecular (Lodish cap. 9; Alberts cap. 9):</strong>
                    <br>
                    El <strong>Punto de Restricción (Punto R)</strong> es un punto de compromiso metabólico regulado por factores de crecimiento extracelulares y mitógenos que activan la vía Ras-MAPK → Ciclina D-CDK4/6 para iniciar la fosforilación de Rb. El Punto R no inspecciona la integridad del ADN.
                    <br>
                    El freno ante daño en el ADN lo impone un <strong>bypass de emergencia colateral</strong>: las quinasas ATM/ATR detectan las lesiones, estabilizan a p53 e inducen la síntesis masiva de <strong>p21</strong>. p21 secuestra e inhibe a las quinasas dependientes de ciclina (CDK2 y CDK4/6), impidiendo que Rb se hiperfosforile y manteniendo a E2F secuestrado. Así, la célula queda congelada antes de cruzar el Punto R hasta que el molde se repare.
                  </p>
                </div>
              </div>

              <!-- FAQ 4: Imposibilidad de reparar mismatch sin molde -->
              <div class="faq-card">
                <div class="faq-q">
                  <Icon name="help" size="18" class="q-icon" />
                  <h5>¿Por qué es químicamente imposible reparar un desapareamiento (mismatch) sin hebra molde?</h5>
                </div>
                <div class="faq-a">
                  <p>
                    <strong>Regla de Oro de la Biología Molecular:</strong> Cuando el sistema detecta un desapareamiento, por ejemplo un par erróneo <strong>A — C</strong>, físicamente ambos nucleótidos son bases químicas normales.
                    <br>
                    El complejo de reparación no tiene forma física de "adivinar" si la secuencia original era un par canónico <strong>A — T</strong> (donde la C es la equivocada) o un par canónico <strong>G — C</strong> (donde la A es la equivocada).
                    <br>
                    Por esta razón, la naturaleza utiliza marcadores epigenéticos para identificar cuál es la hebra molde parental auténtica. Sin una <em>hebra molde parental o referencia homóloga</em>, el sistema tendría un 50% de probabilidad de fijar el error en vez de corregirlo.
                  </p>
                </div>
              </div>

              <!-- FAQ 5: Módulos implementados -->
              <div class="faq-card">
                <div class="faq-q">
                  <Icon name="help" size="18" class="q-icon" />
                  <h5>¿Qué módulos y funciones integran este laboratorio actualmente?</h5>
                </div>
                <div class="faq-a">
                  <p>
                    <strong>Arquitectura Funcional Completa del Simulador:</strong>
                    <br>
                    El laboratorio implementa 4 bloques operacionales rigurosos:
                    <br>
                    • <strong>Molde Parental & Estructura:</strong> Visualización tridimensional fotorrealista de la doble hélice B-DNA, mapa 2D de nucleótidos con monómeros de azúcar-fosfato, polaridad antiparalela 5'→3' / 3'→5' y puentes de hidrógeno Watson-Crick.
                    <br>
                    • <strong>Módulo 1.1 & Sensor Checkpoint G1/S:</strong> Generador de daño ambiental estocástico (UV, ROS, desaminación) y edición quirúrgica CRISPR-Cas9, acoplado al sensor biofísico de arresto celular (eje ATM/ATR → p53/MDM2 → p21 / apoptosis mitocondrial).
                    <br>
                    • <strong>Módulo 1.2 & Módulo 1.3:</strong> Detección y escaneo de apareamientos Watson-Crick en el dúplex bicatenario y cinética enzimática estocástica de escisión de lesiones (BER/NER) regulable (50% a 98%) con reporte de lesiones remanentes.
                    <br>
                    • <strong>Módulo 2 & Módulo 3:</strong> Reporte Diferencial base a base (Diff Inspector) para identificar sustituciones e indels, y Bitácora Inmutable de Auditoría criptográfica con persistencia y carga de experimentos en formato JSON.
                  </p>
                </div>
              </div>

              <!-- Fuentes Bibliográficas -->
              <div class="biblio-box">
                <div class="biblio-header">
                  <Icon name="menu_book" size="20" />
                  <h6>Referencias Bibliográficas Canónicas del Modelo</h6>
                </div>
                <ul class="biblio-list">
                  <li>
                    <strong>Alberts, B., Johnson, A., Lewis, J., Morgan, D., Raff, M., Roberts, K., & Walter, P. (2022).</strong>
                    <em>Molecular Biology of the Cell</em> (7.ª edición). W. W. Norton & Company.
                    <br>
                    <small>• Capítulo 5: "DNA Replication, Repair, and Recombination" (mecanismos de escisión BER, NER y cinética enzimática).</small>
                    <br>
                    <small>• Capítulo 9: "The Cell Cycle" (sistema de control del ciclo celular, sensor p53, inhibidor p21, complejos Ciclina-CDK y punto de restricción G1/S).</small>
                  </li>
                  <li>
                    <strong>Lodish, H., Berk, A., Kaiser, C. A., Krieger, M., Bretscher, A., Ploegh, H., Martin, K. C., Yaffe, M. B., & Amon, A. (2021).</strong>
                    <em>Molecular Cell Biology</em> (9.ª edición). Macmillan Learning.
                    <br>
                    <small>• Capítulo 5: "Molecular Genetic Mechanisms" (mecanismos de daño y mutagénesis).</small>
                    <br>
                    <small>• Capítulo 9: "Cell Cycle Control and Checkpoints" (regulación del punto de restricción R y respuesta al daño en el ADN).</small>
                  </li>
                  <li>
                    <strong>Nelson, D. L., & Cox, M. M. (2021).</strong>
                    <em>Lehninger Principles of Biochemistry</em> (8.ª edición). W. H. Freeman.
                    <br>
                    <small>• Capítulo 25: "DNA Metabolism: Replication, Repair, and Recombination" (estequiometría de enlaces de hidrógeno, polaridad 5'→3' y termodinámica del B-DNA).</small>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <div class="dialog-footer">
          <span class="doc-file-hint font-mono">Manual completo persistido en: MANUAL_LABORATORIO_ADN.txt</span>
          <button class="md3-button-filled" @click="showManualDialog = false">
            <span>Entendido, Volver al Laboratorio</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Diálogo Modal: Renderizado ADN Prueba (Modelos Reales: ADN Atómico y ADN Fotorrealista) -->
    <div class="md3-dialog-backdrop" v-if="showDnaTestDialog" @click.self="showDnaTestDialog = false">
      <div class="md3-dialog-surface dna-test-dialog-surface md3-card-outlined">
        <div class="dialog-header">
          <div class="dialog-title-group">
            <div class="dna-test-icon-badge">
              <Icon name="dna" size="24" class="dialog-icon highlight" />
            </div>
            <div>
              <h3>ADN Prueba · Modelos Reales de ADN-B (21 pb)</h3>
              <span class="dialog-sub">Estructuras derivadas del modelo molecular real · 855 átomos, 985 enlaces y esqueleto paramétrico</span>
            </div>
          </div>

          <!-- Switcher de Modelos -->
          <div class="dna-test-model-switcher">
            <button 
              class="model-tab-btn" 
              :class="{ active: dnaTestActiveModel === 'atomico' }"
              @click="dnaTestActiveModel = 'atomico'"
              title="Ver Modelo Atómico Fiel con 855 átomos y 985 enlaces"
            >
              <span class="tab-dot dot-atomico"></span>
              <span>Modelo Atómico</span>
              <span class="tab-badge">855 Átomos</span>
            </button>
            <button 
              class="model-tab-btn" 
              :class="{ active: dnaTestActiveModel === 'fotorealista' }"
              @click="dnaTestActiveModel = 'fotorealista'"
              title="Ver Vista Fotorrealista con tubos brillantes y clearcoat"
            >
              <span class="tab-dot dot-foto"></span>
              <span>Fotorrealista</span>
              <span class="tab-badge">Tubos PBR</span>
            </button>
            <button 
              class="model-tab-btn" 
              :class="{ active: dnaTestActiveModel === 'dual' }"
              @click="dnaTestActiveModel = 'dual'"
              title="Comparar ambos modelos lado a lado"
            >
              <span>⚡ Comparativa Dual</span>
            </button>
          </div>

          <button class="dialog-close-btn" @click="showDnaTestDialog = false" title="Cerrar ADN Prueba">✕</button>
        </div>

        <div class="dna-test-dialog-body" :class="{ 'is-dual-view': dnaTestActiveModel === 'dual' }">
          <!-- Vista Atómica -->
          <div v-if="dnaTestActiveModel === 'atomico'" class="dna-model-wrapper">
            <ADNAtomico />
          </div>

          <!-- Vista Fotorrealista -->
          <div v-else-if="dnaTestActiveModel === 'fotorealista'" class="dna-model-wrapper">
            <ADNFotorrealista />
          </div>

          <!-- Vista Dual Lado a Lado -->
          <div v-else-if="dnaTestActiveModel === 'dual'" class="dna-dual-container">
            <div class="dual-pane">
              <div class="dual-pane-header">
                <span class="dual-badge atomico-badge">Modelo Atómico Fiel</span>
                <span class="dual-info">855 átomos · 985 enlaces</span>
              </div>
              <div class="dual-pane-canvas">
                <ADNAtomico />
              </div>
            </div>
            <div class="dual-pane">
              <div class="dual-pane-header">
                <span class="dual-badge foto-badge">Vista Fotorrealista PBR</span>
                <span class="dual-info">Esqueleto de fósforos · Tubos PBR</span>
              </div>
              <div class="dual-pane-canvas">
                <ADNFotorrealista />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { api } from '../api/client';
import Icon from './Icon.vue';
import DNAHelix3D from './DNAHelix3D.vue';
import ADNAtomico from './ADNAtomico.vue';
import ADNFotorrealista from './ADNFotorrealista.vue';

const sequenceInput = ref('');
const initialMoldSequence = ref('');
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

// Modos de daño G1 (Ambiental vs CRISPR)
const g1DamageMode = ref('environmental'); // 'environmental' | 'crispr'
const envAgent = ref('uv_radiation'); // 'uv_radiation' | 'oxidative_ros' | 'deamination'
const envIntensity = ref(0.25);
const envDamageResult = ref(null);

// Modos de Replicación Fase S (Fiel vs Estocástica)
const sReplicationMode = ref('stochastic'); // 'faithful' | 'stochastic'
const mutationRate = ref(0.02);
const diffResult = ref(null);

// Fase 1: Copia y validación
const copyNotification = ref('');

// Fase 1: Apareamientos Dúplex y Reparación Guiada
const duplexStrand = ref('');
const mismatchResult = ref(null);
const referenceStrand = ref('');
const repairResult = ref(null);
const repairEfficiency = ref(0.85); // 85% de capacidad de escisión por defecto

// Fase 1: Roturas Bicatenarias (DSB)
const breakPosition = ref(4);
const breakResult = ref(null);

// Fase 1: Bitácora de Experimentos (Trazabilidad) y Persistencia
const experimentLogs = ref([]);
const savedExperimentsList = ref([]);
const showLoadDialog = ref(false);
const showSaveDialog = ref(false);
const saveExpForm = ref({
  name: '',
  notes: ''
});
const showManualDialog = ref(false);
const showDnaTestDialog = ref(false);
const dnaTestActiveModel = ref('atomico');
const manualActiveTab = ref('flow');
const experimentNotification = ref(null);
const lastMutationApplied = ref(null);

// ═══════════════════════ FASE 2: EXPRESIÓN GÉNICA — MÓDULO A ═══════════════════════
const activePhaseTab = ref('phase1'); // 'phase1' | 'phase2'
const selectedGeneId = ref(null);

const genesCatalog = ref([
  {
    id: 'didactic_min_control',
    name: 'Control Didáctico Mínimo',
    organism: 'Sintético',
    cell_type: 'No especificado',
    strand_orientation: '+',
    start_coord: 0,
    end_coord: 16,
    genomic_sequence: 'ATGGAAGTAGTTTTGA',
    promoter: {
      region: 'TATAAA (didáctico)',
      tss: -1
    },
    gene_type: 'protein_coding',
    structure: [
      { type: 'exon', label: 'Exón 1', start: 0, end: 6, sequence: 'ATGGAA' },
      { type: 'intron', label: 'Intrón 1', start: 6, end: 10, sequence: 'GTAG', splice_donor: 'GU', splice_acceptor: 'AG' },
      { type: 'exon', label: 'Exón 2', start: 10, end: 16, sequence: 'TTTTGA' }
    ],
    cds_info: {
      cds_sequence: 'ATGGAATTTTGA',
      reading_frame: 0,
      start_codon: 'ATG',
      stop_codon: 'TGA',
      cds_start: 0,
      cds_end: 12
    },
    data_source: {
      type: 'secuencia_didactica_inventada',
      description: 'Secuencia genómica didáctica de 16 bp (Exón 1 [6 bp] + Intrón 1 [4 bp GTAG] + Exón 2 [6 bp]) diseñada exclusivamente para demostración pedagógica del flujo transcripción → splicing → traducción.'
    }
  },
  {
    id: 'tp53_hsapiens',
    name: 'Gen TP53 — Supresor Tumoral',
    organism: 'Homo sapiens',
    cell_type: 'Línea de referencia estándar',
    strand_orientation: '-',
    start_coord: 7668402,
    end_coord: 7687550,
    promoter: {
      region: 'Promotor CpG-island (Chr17:7687490–7687550)',
      tss: 7687490
    },
    gene_type: 'protein_coding',
    structure: [
      { type: 'exon', label: 'Exón 1', start: 0, end: 68, sequence: null },
      { type: 'intron', label: 'Intrón 1', start: 68, end: 11150, sequence: null, splice_donor: 'GU', splice_acceptor: 'AG' },
      { type: 'exon', label: 'Exón 2', start: 11150, end: 11326, sequence: null },
      { type: 'intron', label: 'Intrón 2', start: 11326, end: 11439, sequence: null, splice_donor: 'GU', splice_acceptor: 'AG' },
      { type: 'exon', label: 'Exón 3', start: 11439, end: 11561, sequence: null },
      { type: 'intron', label: 'Intrón 3', start: 11561, end: 11709, sequence: null, splice_donor: 'GU', splice_acceptor: 'AG' },
      { type: 'exon', label: 'Exón 4', start: 11709, end: 12004, sequence: null },
      { type: 'intron', label: 'Intrón 4', start: 12004, end: 13055, sequence: null, splice_donor: 'GU', splice_acceptor: 'AG' },
      { type: 'exon', label: 'Exón 5', start: 13055, end: 13238, sequence: null },
      { type: 'intron', label: 'Intrón 5', start: 13238, end: 13320, sequence: null, splice_donor: 'GU', splice_acceptor: 'AG' },
      { type: 'exon', label: 'Exón 6', start: 13320, end: 13477, sequence: null },
      { type: 'intron', label: 'Intrón 6', start: 13477, end: 14588, sequence: null, splice_donor: 'GU', splice_acceptor: 'AG' },
      { type: 'exon', label: 'Exón 7', start: 14588, end: 14738, sequence: null },
      { type: 'intron', label: 'Intrón 7', start: 14738, end: 14875, sequence: null, splice_donor: 'GU', splice_acceptor: 'AG' },
      { type: 'exon', label: 'Exón 8', start: 14875, end: 15032, sequence: null },
      { type: 'intron', label: 'Intrón 8', start: 15032, end: 17468, sequence: null, splice_donor: 'GU', splice_acceptor: 'AG' },
      { type: 'exon', label: 'Exón 9', start: 17468, end: 17603, sequence: null },
      { type: 'intron', label: 'Intrón 9', start: 17603, end: 18595, sequence: null, splice_donor: 'GU', splice_acceptor: 'AG' },
      { type: 'exon', label: 'Exón 10', start: 18595, end: 18679, sequence: null },
      { type: 'intron', label: 'Intrón 10', start: 18679, end: 19073, sequence: null, splice_donor: 'GU', splice_acceptor: 'AG' },
      { type: 'exon', label: 'Exón 11', start: 19073, end: 19148, sequence: null }
    ],
    cds_info: {
      cds_sequence: 'ATGGAGGAGCCGCAGTCAGATCCTAGCGTCGAGCCCCCTCTGAGTCAGGAAACATTTTCAGACCTATGGAAACTACTTCCTGAAAACAACGTTCTGTCCCCCTTGCCGTCCCAAGCAATGGATGATTTGATGCTGTCCCCGGACGATATTGAACAATGGTTCACTGAAGACCCAGGTCCAGATGAAGCTCCCAGAATGCCAGAGGCTGCTCCCCCCGTGGCCCCTGCACCAGCAGCTCCTACACCGGCGGCCCCTGCACCAGCCCCCTCCTGGCCCCTGTCATCTTCTGTCCCTTCCCAGAAAACCTACCAGGGCAGCTACGGTTTCCGTCTGGGCTTCTTGCATTCTGGGACAGCCAAGTCTGTGACTTGCACGTACTCCCCTGCCCTCAACAAGATGTTTTGCCAACTGGCCAAGACCTGCCCTGTGCAGCTGTGGGTTGATTCCACACCCCCGCCCGGCACCCGCGTCCGCGCCATGGCCATCTACAAGCAGTCACAGCACATGACGGAGGTTGTGAGGCGCTGCCCCCACCATGAGCGCTGCTCAGATAGCGATGGTCTGGCCCCTCCTCAGCATCTTATCCGAGTGGAAGGAAATTTGCGTGTGGAGTATTTGGATGACAGAAACACTTTTCGACATAGTGTGGTGGTGCCCTATGAGCCGCCTGAGGTTGGCTCTGACTGTACCACCATCCACTACAACTACATGTGTAACAGTTCCTGCATGGGCGGCATGAACCGGAGGCCCATCCTCACCATCATCACACTGGAAGACTCCAGTGGTAATCTACTGGGACGGAACAGCTTTGAGGTGCGTGTTTGTGCCTGTCCTGGGAGAGACCGGCGCACAGAGGAAGAGAATCTCCGCAAGAAAGGGGAGCCTCACCACGAGCTGCCCCCAGGGAGCACTAAGCGAGCACTGCCCAACAACACCAGCTCCTCTCCCCAGCCAAAGAAGAAACCACTGGATGGAGAATATTTCACCCTTCAGATCCGTGGGCGTGAGCGCTTCGAGATGTTCCGAGAGCTGAATGAGGCCTTGGAACTCAAGGATGCCCAGGCTGGGAAGGAGCCAGGGGGGAGCAGGGCTCACTCCAGCCACCTGAAGTCCAAAAAGGGTCAGTCTACCTCCCGCCATAAAAAACTCATGTTCAAGACAGAAGGGCCTGACTCAGACTGA',
      reading_frame: 0,
      start_codon: 'ATG',
      stop_codon: 'TGA',
      cds_start: 203,
      cds_end: 1384,
      protein_length: 393,
      protein_name: 'Proteína p53 (Guardián del Genoma)'
    },
    data_source: {
      type: 'secuencia_curada_publicada',
      database: 'UniProt / NCBI RefSeq',
      accession: 'P04637 / NM_000546.6',
      version: 'GRCh38.p14 (hg38)',
      gene_id: 'ENSG00000141510',
      chromosome: 'Chr17:7,668,402–7,687,550',
      description: 'Ficha técnica de referencia curada para la proteína tumoral p53 humana. Coordenadas genómicas según ensamblaje GRCh38.'
    }
  }
]);

const selectedGene = computed(() => {
  if (!selectedGeneId.value) return null;
  return genesCatalog.value.find(g => g.id === selectedGeneId.value) || null;
});

function selectGene(geneId, showToast = true) {
  if (geneId === 'tp53_hsapiens') {
    return;
  }
  selectedGeneId.value = geneId;
  if (!geneId) {
    return;
  }
  const gene = genesCatalog.value.find(g => g.id === geneId);
  if (gene) {
    // Si es didactic_min_control, cargamos su secuencia genomica (16 bp con intron GTAG); si es TP53, cargamos su CDS
    const seqToLoad = gene.id === 'didactic_min_control'
      ? (gene.genomic_sequence || gene.cds_info?.cds_sequence)
      : gene.cds_info?.cds_sequence;

    if (seqToLoad) {
      sequenceInput.value = seqToLoad;
      initialMoldSequence.value = seqToLoad;
      transcriptionResult.value = null; // Reiniciar transcripcion previa para el nuevo gen
      validateAndProcess(true);
      if (showToast) {
        experimentNotification.value = {
          title: `Gen Activo: ${gene.name}`,
          message: gene.id === 'didactic_min_control'
            ? `Secuencia genómica previa a transcripción (${seqToLoad.length} bp, con intrón GTAG) cargada en el laboratorio.`
            : `Secuencia CDS (${seqToLoad.length} bp) inyectada al molde y sincronizada en el visor 3D y sensores.`
        };
        setTimeout(() => {
          experimentNotification.value = null;
        }, 3500);
      }
    }
  }
}

function handleCopySequence(seq) {
  if (!seq) return;
  if (navigator?.clipboard?.writeText) {
    navigator.clipboard.writeText(seq).then(() => {
      copyNotification.value = `Secuencia copiada (${seq.length} bp)`;
      setTimeout(() => {
        copyNotification.value = '';
      }, 3500);
    });
  }
}

// ═══════════════════════ FASE 2: MÓDULO B — MOTOR DE TRANSCRIPCIÓN (ADN → PRE-ARNM) ═══════════════════════
const transcriptionResult = ref(null);
const isTranscribing = ref(false);
const transcriptionWindowStart = ref(0);
const TRANSCRIPTION_PAGE_SIZE = 40;

const activeDnaSequence = computed(() => {
  return (cleanSequence.value || sequenceInput.value.trim().toUpperCase()).replace(/[^ATCG]/g, '');
});

const isDnaMoldModified = computed(() => {
  if (!initialMoldSequence.value) return false;
  return activeDnaSequence.value !== initialMoldSequence.value.trim().toUpperCase();
});

function isBaseModifiedAt(idx) {
  if (!initialMoldSequence.value) return false;
  const initial = initialMoldSequence.value.trim().toUpperCase();
  if (idx >= initial.length) return true;
  return activeDnaSequence.value[idx] !== initial[idx];
}

const rnaPolTranscriptionMap = {
  A: 'U', // Molde A -> Pre-ARNm U
  T: 'A', // Molde T -> Pre-ARNm A
  C: 'G', // Molde C -> Pre-ARNm G
  G: 'C'  // Molde G -> Pre-ARNm C
};

async function runTranscription() {
  const rawDna = activeDnaSequence.value;
  if (!rawDna) return;

  isTranscribing.value = true;

  // Latencia biocatalítica simulada (ARN Polimerasa II)
  await new Promise(resolve => setTimeout(resolve, 380));

  try {
    const coding_dna = rawDna;

    // 1. Determina Hebra Molde (Antisentido 3' → 5') complementaria a la codificante (5' → 3') por Watson-Crick
    const dnaComplementMap = { A: 'T', T: 'A', C: 'G', G: 'C' };
    const template_dna = coding_dna.split('').map(b => dnaComplementMap[b] || 'N').join('');

    // 2. ARN Polimerasa II leyendo la hebra molde en 3' → 5' y sintetizando Pre-ARNm en 5' → 3'
    // A→U, T→A, C→G, G→C respecto a la hebra molde.
    // El Pre-ARNm resultante equivale a la hebra codificante sustituyendo T por U.
    const pre_mrna = template_dna.split('').map(b => rnaPolTranscriptionMap[b] || 'N').join('');

    // 3. Métricas Bioquímicas
    const length = pre_mrna.length;
    let countA = 0, countU = 0, countC = 0, countG = 0;
    for (let i = 0; i < length; i++) {
      const b = pre_mrna[i];
      if (b === 'A') countA++;
      else if (b === 'U') countU++;
      else if (b === 'C') countC++;
      else if (b === 'G') countG++;
    }
    const base_counts = { A: countA, U: countU, C: countC, G: countG };
    const uracil_content = length > 0 ? Number(((countU / length) * 100).toFixed(1)) : 0;

    // 4. Detección de intrones (ej. contiene 'GUAG' en el control didáctico)
    const has_introns = Boolean(
      pre_mrna.includes('GUAG') ||
      (selectedGene.value?.id === 'didactic_min_control' && length === 16) ||
      (selectedGene.value?.structure?.some(s => s.type === 'intron' && s.sequence && pre_mrna.includes(s.sequence.replace(/T/g, 'U'))))
    );

    transcriptionResult.value = {
      coding_dna,
      template_dna,
      pre_mrna,
      length,
      uracil_content,
      base_counts,
      has_introns,
      timestamp: new Date().toLocaleTimeString()
    };
    transcriptionWindowStart.value = 0;

    experimentNotification.value = {
      title: 'Transcripción Enzimática Exitosa',
      message: `ARN Polimerasa II sintetizó el Pre-ARNm (${length} nt, ${uracil_content}% Uracilo). Transcrito inmaduro listo para Módulo C.`
    };
    setTimeout(() => {
      experimentNotification.value = null;
    }, 4000);
  } catch (err) {
    console.error('Error durante la transcripción in silico:', err);
  } finally {
    isTranscribing.value = false;
  }
}

function resetTranscription() {
  transcriptionResult.value = null;
  transcriptionWindowStart.value = 0;
}

function copyPreMrnaSequence() {
  if (!transcriptionResult.value?.pre_mrna) return;
  const seq = transcriptionResult.value.pre_mrna;
  if (navigator?.clipboard?.writeText) {
    navigator.clipboard.writeText(seq).then(() => {
      copyNotification.value = `Pre-ARNm copiado (${seq.length} nt)`;
      setTimeout(() => {
        copyNotification.value = '';
      }, 3500);
    });
  }
}

function scrollTranscriptionWindow(delta) {
  if (!transcriptionResult.value) return;
  const maxStart = Math.max(0, transcriptionResult.value.length - TRANSCRIPTION_PAGE_SIZE);
  transcriptionWindowStart.value = Math.max(0, Math.min(maxStart, transcriptionWindowStart.value + delta));
}

const visibleTranscriptionColumns = computed(() => {
  if (!transcriptionResult.value) return [];
  const start = transcriptionWindowStart.value;
  const end = Math.min(transcriptionResult.value.length, start + TRANSCRIPTION_PAGE_SIZE);
  const cols = [];
  for (let i = start; i < end; i++) {
    const coding = transcriptionResult.value.coding_dna[i];
    const template = transcriptionResult.value.template_dna[i];
    const rna = transcriptionResult.value.pre_mrna[i];
    // Intrón 1 para didactic_min_control está en las posiciones 6 a 9 (0-indexado)
    const isIntron = (selectedGene.value?.id === 'didactic_min_control' && i >= 6 && i < 10);
    cols.push({
      pos: i + 1,
      coding,
      template,
      rna,
      isIntron,
      isUracil: rna === 'U'
    });
  }
  return cols;
});

const isFullyRepaired = computed(() => {
  return repairResult.value?.matches_reference === true || (breakResult.value?.matches_initial === true && diffResult.value?.difference_count === 0);
});

const isMoldDamaged = computed(() => {
  if (!initialMoldSequence.value) return false;
  // Solo se considera dañado el molde si se indujo una lesión ambiental o mutación dirigida activa no reparada
  if (!envDamageResult.value && !lastMutationApplied.value) return false;
  if (isFullyRepaired.value) return false;
  return true;
});

const currentCellPhase = computed(() => {
  if (breakResult.value) return 'G2';
  if (copyNotification.value || (lastMutationApplied.value && lastMutationApplied.value.type === 'stochastic_replication') || (mismatchResult.value && mismatchResult.value.strand2)) return 'S';
  return 'G1';
});

const currentCellPhaseName = computed(() => {
  switch (currentCellPhase.value) {
    case 'G1': return 'Fase G1 · Molde, Checkpoint p53/p21 & Bypass del Punto R';
    case 'S': return 'Fase S · Replicación & Triple Filtro MMR';
    case 'G2': return 'Fase G2 / M · Integridad Post-Replicativa & DSB';
    default: return 'Fase G1';
  }
});

const checkpointG1Status = computed(() => {
  if (!cleanSequence.value || !validationData.value?.is_valid) {
    return {
      state: 'idle',
      icon: 'hourglass_empty',
      statusTitle: 'Sin validar · Esperando molde genómico',
      badgeClass: 'idle',
      p53Title: 'Dinámica p53 / MDM2',
      p53Badge: 'En espera',
      p53Details: 'Introduce y valida una secuencia de molde de ADN para iniciar la vigilancia biofísica.',
      p21Title: 'Efector p21 / Freno CDK',
      p21Badge: 'En espera',
      p21Details: 'El sistema sensor permanece inactivo a la espera de una hebra de referencia.',
      puntoRTitle: 'Punto R (Punto de Restricción)',
      puntoRDetails: 'El Punto R solo mide señales mitogénicas de crecimiento; el freno por daño es un bypass externo ATM/ATR → p53 → p21.',
      damageNatureClarification: 'En Fase G1, cualquier alteración es una lesión física/química o aducto reparable. Solo se convertirá en mutación si no se repara y se replica más adelante en la Fase S.',
      decision: 'Introduce una secuencia válida de molde.',
      label: 'Sin validar',
      p53: 'Basal (~20 min vida media · degradado por MDM2)',
      p21: 'Inactivo',
      risk: null
    };
  }

  if (isMoldDamaged.value) {
    const lesionCount = envDamageResult.value?.lesion_count || 0;
    const diffCount = diffResult.value?.difference_count || 0;
    const isSevere = lesionCount > 3 || diffCount > 3 || (envIntensity.value >= 0.6 && envDamageResult.value);

    if (isSevere) {
      return {
        state: 'arrested_severe',
        icon: 'heart_broken',
        statusTitle: 'Alerta Crítica: Daño Masivo / Irreparable · Programa de Apoptosis Mitocondrial',
        badgeClass: 'arrested',
        p53Title: 'Dinámica p53 / MDM2 (Fosforilación Sostenida)',
        p53Badge: 'Acumulación masiva + Ser46/Lys120 (Apoptosis)',
        p53Details: 'Fosforilación sostenida y acumulación masiva de p53 (Ser46/Lys120). p53 satura los promotores de arresto e invade promotores proapoptóticos de baja afinidad, desacoplándose totalmente de la degradación por MDM2.',
        p21Title: 'Programa Apoptótico Mitocondrial',
        p21Badge: 'Inducción de BAX, PUMA y NOXA',
        p21Details: 'El freno por p21 es rebasado. p53 induce la transcripción de efectores proapoptóticos mitocondriales (BAX, PUMA, NOXA). BAX permeabiliza la membrana mitocondrial externa (MOMP), provocando salida de citocromo c y activación de caspasas para evitar replicar un genoma roto.',
        puntoRTitle: 'Punto R: Bypass Irreversible por Daño Masivo',
        puntoRDetails: 'El Punto R solo evalúa factores mitogénicas de crecimiento (Ciclina D/CDK4/6/Rb/E2F). Ante daño genómico irreparable, la cascada de estrés impone un veto absoluto que cancela definitivamente el avance hacia Fase S.',
        damageNatureClarification: 'Sobrecarga de lesiones físicas/químicas en el molde. Si no se ejecuta una escisión enzimática (BER/NER) o reparación homóloga inmediata, el programa celular ejecuta apoptosis para no perpetuar un molde fragmentado.',
        decision: 'Daño irreparable/masivo: p53 activa promotores de baja afinidad (BAX, PUMA, NOXA), induciendo apoptosis mitocondrial para evitar replicar un genoma roto.',
        label: 'Alerta Crítica: Apoptosis Mitocondrial',
        p53: 'Acumulación masiva + Ser46/Lys120 (Programa Apoptótico)',
        p21: 'Rebasado por activación de BAX / PUMA / NOXA',
        risk: 'El Punto R solo mide mitógenos; ante daño masivo, el bypass ATM/ATR anula el ciclo y activa la apoptosis mitocondrial.'
      };
    }

    return {
      state: 'arrested_mild',
      icon: 'shield_with_heart',
      statusTitle: 'Freno en G1 Activo · Daño Leve/Moderado (ATM/ATR → p53 → p21)',
      badgeClass: 'arrested',
      p53Title: 'Dinámica p53 / MDM2 (Estabilización)',
      p53Badge: 'Fosforilado (Ser15/Ser20) por ATM/ATR · Escapa a MDM2',
      p53Details: 'Las quinasas sensoras ATM/ATR detectan la lesión y fosforilan a p53 en Ser15 y Ser20. Esta modificación alostérica impide la unión de la ubiquitina ligasa MDM2, evitando su degradación proteasómica y aumentando su vida media.',
      p21Title: 'Efector p21 / Freno CDK en G1',
      p21Badge: 'p21 Inducido · CDKs bloqueadas (Rb hipofosforilado)',
      p21Details: 'p53 estabilizado actúa como factor de transcripción e induce p21 (CIP1/WAF1). p21 inhibe directamente los complejos Ciclina D/CDK4/6 y Ciclina E/CDK2, manteniendo a Rb hipofosforilado (secuestra a E2F) y frenando el ciclo en G1 para permitir reparación por escisión BER/NER (OGG1, GADD45).',
      puntoRTitle: 'Punto R: Bypass Externo Impuesto por ATM/ATR → p53 → p21',
      puntoRDetails: 'El Punto R mide exclusivamente señales mitogénicas de crecimiento (Ciclina D / CDK4/6 / Rb / E2F) y NO detecta daños directamente. El freno ante lesiones es un bypass impuesto externamente desde la vía ATM/ATR → p53 → p21.',
      damageNatureClarification: 'En esta etapa el ADN tiene una lesión física/química o aducto reparable (ej. dímero T-T, 8-oxo-G, uracilo), NO una mutación fijada. Solo se convertirá en mutación si no se repara y se replica más adelante en la Fase S.',
      decision: 'Daño moderado: p53 induce p21; la célula detiene el ciclo en G1 y activa reparación por escisión BER/NER (OGG1, GADD45).',
      label: 'Freno en G1 por Daño al ADN',
      p53: 'Fosforilado (Ser15/Ser20) por ATM/ATR · Escapa a MDM2',
      p21: 'Transcrito e inducido (Inhibe CDK2/4/6 · Rb hipofosforilado)',
      risk: 'El Punto R mide mitógenos; ante daño, ATM/ATR fosforilan a p53 para inducir p21 y frenar a las CDKs. La mutación no existe aún: solo se consolidará si la lesión no se repara y se replica en Fase S.'
    };
  }

  return {
    state: 'cleared',
    icon: 'verified',
    statusTitle: 'Estado en Reposo: Molde Íntegro · MDM2 Activo (Autorizado a Fase S)',
    badgeClass: 'cleared',
    p53Title: 'Dinámica p53 / MDM2 (Recambio Continuo)',
    p53Badge: 'Vida media corta (~20 min) · Degradación en Proteasoma',
    p53Details: 'En reposo sin daño genotóxico, p53 tiene una vida media corta (~20 min). La ubiquitina ligasa E3 MDM2 se une continuamente a p53 y cataliza su poliubiquitinación, enviándolo al proteasoma 26S para su degradación continua.',
    p21Title: 'Efector p21 / Complejos CDK Activos',
    p21Badge: 'p21 Inactivo · CDK4/6 y CDK2 activas',
    p21Details: 'Al no haber p53 estabilizado, p21 no se transcribe. Los complejos Ciclina D-CDK4/6 y Ciclina E-CDK2 están activos para responder a mitógenos, fosforilar a la proteína del Retinoblastoma (Rb) y liberar E2F.',
    puntoRTitle: 'Punto R: Libre de Bypass por Daño',
    puntoRDetails: 'El Punto R solo mide señales mitogénicas de crecimiento (Ciclina D / CDK4/6 / Rb / E2F) y no detecta daños directamente. Al estar el molde libre de lesiones, no existe señal de bypass y la célula está autorizada a cruzar a la síntesis en Fase S.',
    damageNatureClarification: 'Molde parental 100% íntegro. No existen lesiones físicas ni aductos químicos en la secuencia.',
    decision: 'Molde libre de lesiones. MDM2 mantiene degradado a p53. Célula autorizada a cruzar a Fase S (Replicación).',
    label: 'Molde Íntegro · Autorizado a Fase S',
    p53: 'Basal bajo (MDM2 ubiquitina y envía continuamente al proteasoma)',
    p21: 'Apagado (CDK4/6 y CDK2 activas · Rb fosforilado libera E2F)',
    risk: null
  };
});

const currentStep = computed(() => {
  if ((breakResult.value && breakResult.value.status) || isFullyRepaired.value) return 5;
  if ((diffResult.value && (diffResult.value.difference_count || 0) > 0) || (mismatchResult.value && (mismatchResult.value.mismatch_count || 0) > 0)) return 4;
  if (repairResult.value && repairResult.value.status) return 3;
  if (isMoldDamaged.value || (lastMutationApplied.value && lastMutationApplied.value.type !== 'stochastic_replication')) return 2;
  return 1;
});

const currentStepName = computed(() => {
  switch (currentStep.value) {
    case 1: return 'G1: Molde Inicial Validado';
    case 2: return 'G1: Freno Checkpoint G1/S (p53 / p21)';
    case 3: return 'G1: Molde Reparado (Vía Homología / BER)';
    case 4: return 'S: Replicación & Triple Filtro MMR';
    case 5: return 'G2/M: Supervisión Post-Replicativa & DSB';
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

function formatStatusText(status) {
  if (!status) return 'Completado';
  const s = status.toUpperCase();
  switch (s) {
    case 'COMPLETED': return 'Completado';
    case 'REPAIRED_HIGH_FIDELITY':
    case 'REPAIRED_CLEAN_HDR': return 'Restaurado (HDR)';
    case 'REPAIRED_PRONE_TO_SCAR':
    case 'REPAIRED_SCARRED_NHEJ': return 'Cicatriz (NHEJ)';
    case 'FULLY_REPAIRED':
    case 'REPAIRED_MATCH':
    case 'REPAIRED_FULL_MATCH': return 'Restaurado 100%';
    case 'PARTIAL_REPAIR':
    case 'PARTIALLY_REPAIRED': return 'Reparación Parcial';
    case 'MUTATED': return 'Secuencia Mutada';
    case 'ALTERED': return 'Secuencia Alterada';
    case 'INTACT':
    case 'COPIED_EXACT': return 'Molde Intacto';
    default: return status.replace(/_/g, ' ');
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
  if (mut.type === 'faithful_replication') {
    return 'Copia fiel (100% fidelidad)';
  }
  if (mut.type === 'environmental_damage') {
    return `${mut.agent_name || 'Daño ambiental'}: ${mut.count || 0} lesión(es)`;
  }
  if (mut.type === 'double_strand_break') {
    const m = (mut.method || '').includes('homology') ? 'HDR' : 'NHEJ';
    return `Rotura de ADN (DSB) en pos ${mut.break_position} (Vía ${m})`;
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

function openSaveDialog() {
  const current = sequenceInput.value.trim().toUpperCase();
  if (!current) {
    alert("Introduce primero una secuencia válida para poder guardar un experimento.");
    return;
  }

  let suggestedName = '';
  if (breakResult.value) {
    const isHDR = (breakResult.value.repair_method || '').includes('homology');
    suggestedName = `Rotura DSB en pos. ${breakResult.value.break_position} (${isHDR ? 'Reparación HDR' : 'Unión NHEJ'})`;
  } else if (lastMutationApplied.value) {
    if (lastMutationApplied.value.type === 'substitution') {
      suggestedName = `Sustitución pos ${lastMutationApplied.value.position} (${lastMutationApplied.value.original_base || '∅'} → ${lastMutationApplied.value.new_base})`;
    } else if (lastMutationApplied.value.type === 'insertion') {
      suggestedName = `Inserción pos ${lastMutationApplied.value.position} (+${lastMutationApplied.value.new_base})`;
    } else if (lastMutationApplied.value.type === 'deletion') {
      suggestedName = `Deleción pos ${lastMutationApplied.value.position}`;
    } else if (lastMutationApplied.value.type === 'stochastic_replication') {
      suggestedName = `Replicación estocástica (${lastMutationApplied.value.count || 0} mutaciones)`;
    } else {
      suggestedName = `Ensayo genético [${current.slice(0, 8)}...]`;
    }
  } else if (diffResult.value && diffResult.value.difference_count > 0) {
    suggestedName = `Edición genética (${diffResult.value.difference_count} variantes)`;
  } else {
    suggestedName = `Control de referencia [${current.slice(0, 8)}...]`;
  }

  saveExpForm.value = {
    name: suggestedName,
    notes: ''
  };
  showSaveDialog.value = true;
}

async function confirmSaveExperiment() {
  const nameToSave = saveExpForm.value.name.trim();
  if (!nameToSave) {
    alert("Por favor ingresa un nombre para el experimento.");
    return;
  }

  const current = sequenceInput.value.trim().toUpperCase();
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
        method: breakResult.value.repair_method,
        scar: breakResult.value.scar
      };
    }

    const payload = {
      name: nameToSave,
      notes: saveExpForm.value.notes?.trim() || 'Ensayo guardado en BioSim Lab.',
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

    showSaveDialog.value = false;

    experimentNotification.value = {
      title: `Experimento guardado: "${saved.name}"`,
      message: `Asignado código [${saved.experiment_id}]. Registrado con éxito en el cuaderno de bitácora.`
    };
    setTimeout(() => {
      experimentNotification.value = null;
    }, 5000);
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

  if (exp.mutation_applied && Object.keys(exp.mutation_applied).length > 0 && exp.mutation_applied.type) {
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
  } else {
    lastMutationApplied.value = null;
  }

  if (exp.detection_result && Object.keys(exp.detection_result).length > 0 && Array.isArray(exp.detection_result.mismatches)) {
    mismatchResult.value = exp.detection_result;
  } else {
    mismatchResult.value = null;
  }
  if (exp.repair_applied && Object.keys(exp.repair_applied).length > 0 && exp.repair_applied.repaired_sequence) {
    repairResult.value = exp.repair_applied;
  } else {
    repairResult.value = null;
  }
  if (exp.diff_result && Object.keys(exp.diff_result).length > 0 && Array.isArray(exp.diff_result.differences)) {
    diffResult.value = exp.diff_result;
  } else {
    diffResult.value = null;
  }

  validateAndProcess(false);
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

  if (ev.repair_result && Object.keys(ev.repair_result).length > 0 && ev.repair_result.repaired_sequence) {
    repairResult.value = ev.repair_result;
  } else {
    repairResult.value = null;
  }
  if (ev.detection_result && Object.keys(ev.detection_result).length > 0 && Array.isArray(ev.detection_result.mismatches)) {
    mismatchResult.value = ev.detection_result;
  } else {
    mismatchResult.value = null;
  }
  if (ev.diff_result && Object.keys(ev.diff_result).length > 0 && Array.isArray(ev.diff_result.differences)) {
    diffResult.value = ev.diff_result;
  } else {
    diffResult.value = null;
  }

  validateAndProcess(false);

  experimentNotification.value = {
    title: `Evento ${ev.experiment_id} cargado`,
    message: `Secuencia restaurada en el laboratorio (${seqToLoad.length} bp).`
  };
  setTimeout(() => {
    experimentNotification.value = null;
  }, 4500);
}

function formatOperationName(op) {
  switch (op) {
    case 'environmental_damage': return 'Daño Ambiental (G1)';
    case 'mismatch_detection': return 'Detección Dúplex (MMR)';
    case 'copy':
    case 'faithful_replication': return 'Duplicación Fiel (Fase S)';
    case 'controlled_mutation': return 'Edición Dirigida (CRISPR)';
    case 'stochastic_replication': return 'Replicación Celular (Fase S)';
    case 'reference_guided_repair': return 'Reparación por Molde';
    case 'dna_break_and_repair':
    case 'double_strand_break_simulation': return 'Rotura Doble Hebra (DSB)';
    case 'save_experiment':
    case 'full_experiment_save': return 'Guardado de Ensayo';
    default: {
      if (!op) return 'Operación';
      return op.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }
  }
}

function getOpBadgeClass(op) {
  switch (op) {
    case 'environmental_damage': return 'crispr';
    case 'mismatch_detection': return 'mmr';
    case 'copy':
    case 'faithful_replication': return 'copy';
    case 'controlled_mutation': return 'crispr';
    case 'dna_break_and_repair':
    case 'double_strand_break_simulation': return 'dsb';
    case 'reference_guided_repair': return 'repair';
    case 'save_experiment':
    case 'full_experiment_save': return 'save';
    default: return 'default';
  }
}

function formatEventDetails(ev) {
  if (!ev) return 'Sin datos adicionales';
  const op = ev.operation_type;
  const p = ev.parameters || {};
  const d = ev.detection_result || {};

  if (op === 'mismatch_detection') {
    const count = p.mismatch_count !== undefined ? p.mismatch_count : d.mismatch_count;
    if (count > 0) {
      return `${count} apareamiento(s) erróneo(s) detectado(s) en la doble hélice`;
    }
    return 'Apareamiento 100% canónico Watson-Crick (A-T, C-G)';
  }
  if (op === 'copy') {
    return `Clonación fidedigna de la hebra molde (${ev.initial_sequence?.length || 0} bp)`;
  }
  if (op === 'controlled_mutation') {
    const t = p.mutation_type === 'substitution' ? 'Sustitución' : p.mutation_type === 'insertion' ? 'Inserción' : 'Deleción';
    return `${t} en posición ${p.position ?? 0} (${p.original_base || '∅'} → ${p.new_base || '∅'})`;
  }
  if (op === 'stochastic_replication') {
    const rate = ((p.mutation_rate || 0) * 100).toFixed(0);
    return `Tasa de error ${rate}% · ${p.mutations_occurred || 0} mutación(es) acumulada(s)`;
  }
  if (op === 'reference_guided_repair') {
    return 'Corrección asistida por secuencia de referencia homóloga (Fidelidad 100%)';
  }
  if (op === 'dna_break_and_repair' || op === 'double_strand_break_simulation') {
    const m = (p.repair_method || '').toLowerCase();
    const isHDR = m.includes('homology') || m.includes('hdr');
    const method = isHDR ? 'HDR (Homología limpia)' : 'NHEJ (Unión directa)';
    const scarInfo = p.scar_type ? (p.scar_type.includes('micro_deletion') ? ' · Cicatriz: Microdeleción (-1 bp)' : (p.scar_type.includes('blunt') ? ' · Ligación directa' : ' · Sin cicatriz')) : '';
    return `Rotura en pos. ${p.break_position ?? '?'} · Resuelta vía ${method}${scarInfo}`;
  }
  if (op === 'full_experiment_save' || op === 'save_experiment') {
    return `Ensayo guardado: "${p.saved_name || 'Registro del ensayo'}"`;
  }
  return 'Operación completada con éxito';
}

function formatResultName(ev) {
  const status = (ev.repair_result?.status || ev.detection_result?.status || ev.status || '').toUpperCase();
  switch (status) {
    case 'COPIED_EXACT': return 'Copia Idéntica (100%)';
    case 'DETECTED_ONLY': return 'Error Marcado (Sin Plantilla)';
    case 'CANONICAL_MATCH': return '100% Canónico (Sin Errores)';
    case 'MISMATCH_DETECTED': return 'Apareamiento Erróneo Detectado';
    case 'REPAIRED_MATCH':
    case 'REPAIRED_FULL_MATCH':
    case 'FULLY_REPAIRED': return 'Restaurado al 100%';
    case 'PARTIAL_REPAIR':
    case 'PARTIALLY_REPAIRED': return 'Reparación Parcial';
    case 'REPAIRED_HIGH_FIDELITY':
    case 'REPAIRED_CLEAN_HDR': return 'Reparado sin Cicatriz (HDR)';
    case 'REPAIRED_PRONE_TO_SCAR':
    case 'REPAIRED_SCARRED_NHEJ': return 'Cicatriz / Microdeleción (NHEJ)';
    case 'DIRECT_BLUNT_LIGATION': return 'Ligación Directa (NHEJ)';
    case 'MUTATION_INTRODUCED': return 'Mutación Incorporada';
    case 'MUTATED': return 'Secuencia Mutada';
    case 'IDENTICAL': return 'Sin Mutaciones (Intacto)';
    case 'ALTERED': return 'Secuencia Alterada';
    case 'COMPLETED': return 'Completado con Éxito';
    case 'INTACT': return 'Secuencia Intacta';
    default: {
      if (!status) return 'Registrado con Éxito';
      return status.replace(/_/g, ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase());
    }
  }
}

function getResultBadgeClass(ev) {
  const status = (ev.repair_result?.status || ev.detection_result?.status || ev.status || '').toUpperCase();
  if (['COPIED_EXACT', 'CANONICAL_MATCH', 'REPAIRED_MATCH', 'REPAIRED_FULL_MATCH', 'FULLY_REPAIRED', 'REPAIRED_CLEAN_HDR', 'REPAIRED_HIGH_FIDELITY', 'IDENTICAL', 'COMPLETED', 'INTACT'].includes(status)) {
    return 'success';
  }
  if (['DETECTED_ONLY', 'MISMATCH_DETECTED', 'REPAIRED_SCARRED_NHEJ', 'REPAIRED_PRONE_TO_SCAR', 'PARTIAL_REPAIR', 'PARTIALLY_REPAIRED', 'MUTATED', 'ALTERED', 'MUTATION_INTRODUCED'].includes(status)) {
    return 'warning';
  }
  return 'info';
}

function formatRepairMethod(method) {
  if (!method) return '';
  const m = method.toLowerCase();
  if (m.includes('homology') || m.includes('hdr')) return 'Vía HDR (Homología Guiada)';
  if (m.includes('joining') || m.includes('nhej')) return 'Vía NHEJ (Unión de Extremos)';
  return method;
}

function formatScarText(scar) {
  if (!scar) return 'Sin cicatriz';
  const s = scar.toLowerCase();
  if (s.includes('none') || s.includes('fidelity')) {
    return 'Sin cicatriz (Fidelidad 100%)';
  }
  if (s.includes('direct') || s.includes('blunt')) {
    return 'Ligación directa (Extremos romos, sin pérdida de bases)';
  }
  if (s.includes('micro_deletion')) {
    const pos = scar.replace(/[^0-9]/g, '');
    return `Microdeleción mutacional (Pérdida de 1 base en pos. ${pos})`;
  }
  return scar;
}

function formatBreakDescription(res) {
  if (!res) return '';
  const m = (res.repair_method || '').toLowerCase();
  if (m.includes('homology') || m.includes('hdr')) {
    return 'Reconstrucción de alta fidelidad asistida por plantilla homóloga (HDR). No deja mutaciones ni cicatriz.';
  }
  if (res.scar?.includes('micro_deletion')) {
    return 'Unión directa de extremos rotos sin plantilla (NHEJ). Se produjo una microdeleción (pérdida de un nucleótido), alterando la secuencia original.';
  }
  return 'Unión directa de extremos rotos sin plantilla (NHEJ). Los fragmentos se unieron directamente de extremo a extremo sin pérdida de bases, pero sin verificación por molde.';
}



const FILMSTRIP_WINDOW_SIZE = 70;
const filmstripStartPos = ref(0);

function scrollFilmstrip(delta) {
  const maxStart = Math.max(0, (cleanSequence.value?.length || 0) - FILMSTRIP_WINDOW_SIZE);
  filmstripStartPos.value = Math.max(0, Math.min(maxStart, filmstripStartPos.value + delta));
}

function centerFilmstripOnSelected() {
  if (selectedPosition.value === null || !cleanSequence.value) return;
  const maxStart = Math.max(0, cleanSequence.value.length - FILMSTRIP_WINDOW_SIZE);
  filmstripStartPos.value = Math.max(0, Math.min(maxStart, selectedPosition.value - Math.floor(FILMSTRIP_WINDOW_SIZE / 2)));
}

const visibleFilmstripBases = computed(() => {
  const seq = cleanSequence.value;
  if (!seq) return [];
  if (seq.length <= FILMSTRIP_WINDOW_SIZE) {
    return seq.split('').map((base, idx) => ({ base, idx }));
  }
  const maxStart = Math.max(0, seq.length - FILMSTRIP_WINDOW_SIZE);
  const start = Math.max(0, Math.min(maxStart, filmstripStartPos.value));
  const end = Math.min(seq.length, start + FILMSTRIP_WINDOW_SIZE);
  const list = [];
  for (let i = start; i < end; i++) {
    list.push({ base: seq[i], idx: i });
  }
  return list;
});

const duplexPairsDisplay = computed(() => {
  const s1 = cleanSequence.value || sequenceInput.value.trim().toUpperCase();
  const s2 = duplexStrand.value.trim().toUpperCase() || complementStrand.value;
  if (!s1 || !s2) return [];
  // Si s1.length !== s2.length, limita la comparación a la longitud mínima común sin casillas artificiales '∅'
  const minLen = Math.min(s1.length, s2.length);
  const pairs = [];
  for (let i = 0; i < minLen; i++) {
    const b1 = s1[i];
    const b2 = s2[i];
    const isCanon = complementMap[b1] === b2;
    pairs.push({
      idx: i,
      b1,
      b2,
      is_canonical: isCanon,
      note: isCanon ? 'Apareamiento Canónico Watson-Crick' : `Apareamiento No Canónico (${b1}-${b2})`
    });
  }
  return pairs;
});

const duplexLengthMismatch = computed(() => {
  const s1 = cleanSequence.value || sequenceInput.value.trim().toUpperCase();
  const s2 = duplexStrand.value.trim().toUpperCase() || complementStrand.value;
  return Boolean(s1 && s2 && s1.length !== s2.length);
});

const visibleDuplexPairs = computed(() => {
  const all = duplexPairsDisplay.value;
  if (all.length <= FILMSTRIP_WINDOW_SIZE) return all;
  const maxStart = Math.max(0, all.length - FILMSTRIP_WINDOW_SIZE);
  const start = Math.max(0, Math.min(maxStart, filmstripStartPos.value));
  return all.slice(start, start + FILMSTRIP_WINDOW_SIZE);
});

watch(selectedPosition, (newPos) => {
  if (newPos !== null && cleanSequence.value && cleanSequence.value.length > FILMSTRIP_WINDOW_SIZE) {
    if (newPos < filmstripStartPos.value || newPos >= filmstripStartPos.value + FILMSTRIP_WINDOW_SIZE) {
      centerFilmstripOnSelected();
    }
  }
});

// Invalidation / Reset Automático: si la secuencia de ADN cambia (mutación, reparación o edición manual), resetea el Pre-ARNm
watch(cleanSequence, (newSeq, oldSeq) => {
  if (newSeq !== oldSeq) {
    transcriptionResult.value = null;
    transcriptionWindowStart.value = 0;
  }
});

function handleInput() {
  sequenceInput.value = sequenceInput.value.toUpperCase();
  if (selectedGeneId.value !== null) {
    selectedGeneId.value = null;
  }
  mismatchResult.value = null;
  duplexStrand.value = '';
}

function loadSample(seq) {
  sequenceInput.value = seq;
  validateAndProcess(true);
}

function resetToInitialMold() {
  if (!initialMoldSequence.value) return;
  sequenceInput.value = initialMoldSequence.value;
  validateAndProcess(true);
  experimentNotification.value = {
    title: 'Molde Inicial Restaurado',
    message: `Se restableció la hebra molde de partida (${initialMoldSequence.value.length} bp) para un nuevo ensayo.`
  };
  setTimeout(() => {
    experimentNotification.value = null;
  }, 3500);
}

async function validateAndProcess(isInitialMold = true) {
  const raw = sequenceInput.value.trim().toUpperCase();
  if (!raw) {
    validationData.value = null;
    complementStrand.value = '';
    binaryStrand.value = '';
    initialMoldSequence.value = '';
    referenceStrand.value = '';
    duplexStrand.value = '';
    envDamageResult.value = null;
    lastMutationApplied.value = null;
    diffResult.value = null;
    mismatchResult.value = null;
    repairResult.value = null;
    breakResult.value = null;
    copyNotification.value = '';
    transcriptionResult.value = null;
    return;
  }

  try {
    loading.value = true;
    const valRes = await api.validateDNA(raw);
    validationData.value = valRes;

    if (valRes.is_valid) {
      if (transcriptionResult.value && transcriptionResult.value.coding_dna !== raw) {
        transcriptionResult.value = null;
        transcriptionWindowStart.value = 0;
      }
      const compRes = await api.complementDNA(raw);
      complementStrand.value = compRes.complement;
      binaryStrand.value = compRes.binary_repr;

      if (isInitialMold) {
        initialMoldSequence.value = raw;
        referenceStrand.value = raw;
        duplexStrand.value = compRes.complement;
        envDamageResult.value = null;
        lastMutationApplied.value = null;
        diffResult.value = null;
        mismatchResult.value = null;
        repairResult.value = null;
        breakResult.value = null;
        copyNotification.value = '';
      } else {
        if (!initialMoldSequence.value) {
          initialMoldSequence.value = raw;
        }
        if (!referenceStrand.value) {
          referenceStrand.value = initialMoldSequence.value || raw;
        }
        if (!duplexStrand.value) {
          duplexStrand.value = compRes.complement;
        }
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
  const eff = repairEfficiency.value;
  try {
    loading.value = true;
    const res = await api.repairWithReference(current, moldRef, null, eff);
    repairResult.value = res;
    // Sincronizar siempre la secuencia resultante (sea completa o parcial)
    sequenceInput.value = res.repaired_sequence;
    await validateAndProcess(false);
    const compMold = await api.complementDNA(moldRef);
    duplexStrand.value = compMold.complement;
    mismatchResult.value = await api.detectMismatches(res.repaired_sequence, compMold.complement);
    diffResult.value = await api.compareDNA(moldRef, res.repaired_sequence);
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
    await validateAndProcess(false);
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

async function handleClearLogs() {
  try {
    await api.clearDNAEvents();
    experimentLogs.value = [];
  } catch (err) {
    console.error('Error al limpiar registros:', err);
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

async function applyEnvironmentalDamage() {
  const currentWorking = cleanSequence.value;
  if (!initialMoldSequence.value) {
    initialMoldSequence.value = currentWorking;
  }
  const moldRef = initialMoldSequence.value;

  try {
    loading.value = true;
    const res = await api.simulateEnvironmentalDamage(currentWorking, envAgent.value, envIntensity.value);
    envDamageResult.value = res;
    sequenceInput.value = res.damaged_sequence;
    lastMutationApplied.value = {
      type: 'environmental_damage',
      agent: res.agent,
      agent_name: res.agent_name,
      lesions: res.lesions,
      count: res.lesion_count
    };
    repairResult.value = null;
    await validateAndProcess(false);
    const compMold = await api.complementDNA(moldRef);
    duplexStrand.value = compMold.complement;
    mismatchResult.value = await api.detectMismatches(res.damaged_sequence, compMold.complement);
    diffResult.value = await api.compareDNA(moldRef, res.damaged_sequence);
    await fetchLogs();
  } catch (err) {
    alert(err.message || 'Error al aplicar daño ambiental');
  } finally {
    loading.value = false;
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
    await validateAndProcess(false);
    const compMold = await api.complementDNA(moldRef);
    duplexStrand.value = compMold.complement;
    mismatchResult.value = await api.detectMismatches(res.modified_sequence, compMold.complement);
    diffResult.value = await api.compareDNA(moldRef, res.modified_sequence);
    await fetchLogs();
  } catch (err) {
    alert(err.message || 'Error al aplicar mutación controlada');
  } finally {
    loading.value = false;
  }
}

async function replicateFaithful() {
  const currentWorking = cleanSequence.value;
  if (!initialMoldSequence.value) {
    initialMoldSequence.value = currentWorking;
  }
  const moldRef = initialMoldSequence.value;

  try {
    loading.value = true;
    const res = await api.copyDNA(currentWorking);
    copyNotification.value = 'Hebra hija duplicada con 100% de fidelidad (sin mutaciones).';
    setTimeout(() => { copyNotification.value = ''; }, 4500);

    lastMutationApplied.value = {
      type: 'faithful_replication',
      rate: 0,
      count: 0
    };
    diffResult.value = await api.compareDNA(moldRef, res.copy);
    const compMold = await api.complementDNA(res.copy);
    duplexStrand.value = compMold.complement;
    mismatchResult.value = await api.detectMismatches(res.copy, compMold.complement);
    await fetchLogs();
  } catch (err) {
    alert(err.message || 'Error en síntesis fiel');
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
    await validateAndProcess(false);

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
  if (sequenceInput.value) {
    validateAndProcess();
  } else if (selectedGeneId.value) {
    selectGene(selectedGeneId.value, false);
  }
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

/* Header Científico con Glassmorphism Bio-Tech */
.dna-header-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.6rem;
  background: rgba(13, 23, 38, 0.65);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(56, 189, 248, 0.15);
  border-radius: var(--md-sys-shape-corner-medium);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
  flex-wrap: wrap;
  gap: 1.2rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.dna-header-card:hover {
  border-color: rgba(56, 189, 248, 0.35);
  box-shadow: 0 0 20px rgba(56, 189, 248, 0.2);
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
  background: linear-gradient(135deg, rgba(14, 165, 233, 0.2) 0%, rgba(2, 132, 199, 0.35) 100%);
  border: 1px solid rgba(56, 189, 248, 0.35);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #38bdf8;
  box-shadow: 0 0 16px rgba(56, 189, 248, 0.25);
}

.header-text h2 {
  font-size: 1.15rem;
  font-weight: 700;
  color: #f1f5f9;
  letter-spacing: -0.2px;
}

.header-text .subtext {
  font-size: 0.74rem;
  color: #94a3b8;
}

.sample-chips-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-wrap: wrap;
}

.chips-label {
  font-size: 0.74rem;
  color: #94a3b8;
}

.sample-chips-row .md3-chip {
  cursor: pointer;
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.8) 0%, rgba(30, 41, 59, 0.6) 100%);
  border: 1px solid rgba(56, 189, 248, 0.18);
  color: #cbd5e1;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.sample-chips-row .md3-chip:hover {
  border-color: rgba(56, 189, 248, 0.45);
  color: #f8fafc;
  box-shadow: 0 0 16px rgba(56, 189, 248, 0.25);
  transform: translateY(-1px);
}

.chip-icon {
  color: #38bdf8;
}

/* Entrada de Secuencia & Métricas - Bio-Tech Glass */
.dna-input-section {
  padding: 1.4rem 1.6rem;
  background: rgba(13, 23, 38, 0.65);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(56, 189, 248, 0.15);
  border-radius: var(--md-sys-shape-corner-medium);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.dna-input-section:hover {
  border-color: rgba(56, 189, 248, 0.3);
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
  font-family: 'JetBrains Mono', 'Fira Code', 'Roboto Mono', monospace;
  font-size: 1.05rem;
  letter-spacing: 2.5px;
  background: rgba(4, 9, 18, 0.75);
  border: 1px solid rgba(56, 189, 248, 0.25);
  border-radius: 8px;
  color: #70d6ff;
  padding: 0.65rem 1rem;
  box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.6);
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.sequence-field:focus {
  border-color: #38bdf8;
  box-shadow: 0 0 18px rgba(56, 189, 248, 0.35), inset 0 2px 5px rgba(0, 0, 0, 0.6);
  outline: none;
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

/* Tarjeta de Espera para Entrada Manual de Cadena */
.manual-input-prompt-card {
  padding: 2.2rem 2rem;
  background: rgba(13, 23, 38, 0.55);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px dashed rgba(56, 189, 248, 0.3);
  border-radius: var(--md-sys-shape-corner-medium);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
  transition: all 0.3s ease;
  margin-bottom: 0.5rem;
}

.manual-input-prompt-card:hover {
  border-color: rgba(56, 189, 248, 0.5);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3), 0 0 20px rgba(56, 189, 248, 0.1);
}

.manual-input-prompt-card .prompt-content {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.manual-input-prompt-card .prompt-icon-box {
  width: 58px;
  height: 58px;
  border-radius: 14px;
  background: rgba(56, 189, 248, 0.12);
  border: 1px solid rgba(56, 189, 248, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #38bdf8;
  flex-shrink: 0;
  box-shadow: 0 0 16px rgba(56, 189, 248, 0.2);
}

.manual-input-prompt-card .prompt-text h3 {
  font-size: 1.15rem;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0 0 0.4rem 0;
  letter-spacing: -0.01em;
}

.manual-input-prompt-card .prompt-text p {
  font-size: 0.88rem;
  color: #94a3b8;
  line-height: 1.55;
  margin: 0;
}

.manual-input-prompt-card .prompt-text strong {
  color: #38bdf8;
}

/* Workbench Grid (Alineamiento 2D + Doble Hélice 3D en Filas Dedicadas) */
.molecular-workbench-grid {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  width: 100%;
}

/* Track Molecular Interactivo - Glassmorphism & Full Width Row */
.sequence-track-card {
  padding: 1.4rem 1.6rem;
  background: rgba(13, 23, 38, 0.65);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(56, 189, 248, 0.15);
  border-radius: var(--md-sys-shape-corner-medium);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
  width: 100%;
  box-sizing: border-box;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.sequence-track-card:hover {
  border-color: rgba(56, 189, 248, 0.35);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37), 0 0 20px rgba(56, 189, 248, 0.15);
}

.track-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
  gap: 0.8rem;
}

.track-title-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.title-icon {
  color: #38bdf8;
  filter: drop-shadow(0 0 6px rgba(56, 189, 248, 0.4));
}

.track-title-group h3 {
  font-size: 1.05rem;
  font-weight: 700;
  color: #f1f5f9;
}

.track-title-group .hint {
  font-size: 0.72rem;
  color: #94a3b8;
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
  color: #94a3b8;
}

.leg-item .square {
  width: 8px;
  height: 8px;
  border-radius: 2px;
}

.leg-item.a .square { background: var(--bio-base-a); box-shadow: 0 0 6px var(--bio-base-a); }
.leg-item.t .square { background: var(--bio-base-t); box-shadow: 0 0 6px var(--bio-base-t); }
.leg-item.c .square { background: var(--bio-base-c); box-shadow: 0 0 6px var(--bio-base-c); }
.leg-item.g .square { background: var(--bio-base-g); box-shadow: 0 0 6px var(--bio-base-g); }

.track-viewport {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  background: rgba(4, 9, 18, 0.75);
  border: 1px solid rgba(56, 189, 248, 0.2);
  border-radius: var(--md-sys-shape-corner-medium);
  padding: 1rem 0.8rem;
  position: relative;
  overflow: hidden;
  box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.6);
}



.track-strand-label {
  font-family: 'JetBrains Mono', 'Fira Code', var(--md-ref-typeface-mono);
  font-weight: 700;
  font-size: 0.9rem;
  color: #38bdf8;
  padding: 0 0.4rem;
}

.filmstrip-window-navigator {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.5rem 0.85rem;
  margin-bottom: 0.6rem;
  background: rgba(14, 28, 48, 0.65);
  border: 1px solid rgba(56, 189, 248, 0.25);
  border-radius: 8px;
  flex-wrap: wrap;
}

.f-nav-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #38bdf8;
  font-size: 0.85rem;
  font-weight: 600;
}

.f-nav-info .text-dim {
  color: rgba(148, 163, 184, 0.7);
  font-weight: 400;
}

.f-nav-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
  max-width: 480px;
}

.filmstrip-scrubber {
  flex: 1;
  accent-color: #38bdf8;
  cursor: pointer;
  height: 6px;
  background: rgba(8, 15, 28, 0.8);
  border-radius: 999px;
}

.nav-arrow-btn {
  background: rgba(56, 189, 248, 0.12);
  border: 1px solid rgba(56, 189, 248, 0.3);
  color: #38bdf8;
  border-radius: 6px;
  width: 26px;
  height: 26px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.15s ease;
}

.nav-arrow-btn:hover:not(:disabled) {
  background: rgba(56, 189, 248, 0.25);
  border-color: #38bdf8;
}

.nav-arrow-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.center-btn {
  font-size: 0.75rem;
  padding: 0.15rem 0.5rem;
}

.bases-filmstrip {
  display: flex;
  gap: 0.45rem;
  flex: 1;
  min-width: 0;
  overflow-x: auto;
  scroll-behavior: smooth;
  -webkit-overflow-scrolling: touch;
  padding: 0.4rem 0.3rem;
  scrollbar-width: thin;
  scrollbar-color: rgba(56, 189, 248, 0.5) rgba(8, 15, 28, 0.7);
}

.bases-filmstrip::-webkit-scrollbar {
  height: 4px;
}
.bases-filmstrip::-webkit-scrollbar-track {
  background: rgba(8, 15, 28, 0.7);
  border-radius: 999px;
}
.bases-filmstrip::-webkit-scrollbar-thumb {
  background: linear-gradient(90deg, rgba(56, 189, 248, 0.4), rgba(14, 165, 233, 0.9));
  border-radius: 999px;
  box-shadow: 0 0 8px rgba(56, 189, 248, 0.6);
}

.base-column {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 44px;
  cursor: pointer;
  padding: 0.4rem 0.25rem;
  border-radius: var(--md-sys-shape-corner-small);
  border: 1px solid transparent;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.base-column:hover {
  background: rgba(56, 189, 248, 0.08);
  border-color: rgba(56, 189, 248, 0.25);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.base-column.selected {
  background: rgba(56, 189, 248, 0.16);
  border-color: #38bdf8;
  box-shadow: 0 0 20px rgba(56, 189, 248, 0.35);
  transform: translateY(-2px);
}

.pos-index {
  font-family: 'JetBrains Mono', 'Fira Code', var(--md-ref-typeface-mono);
  font-size: 0.65rem;
  color: #94a3b8;
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
  transition: all 0.2s ease;
}

.base-column.a .primary-strand { 
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(185, 28, 28, 0.25) 100%); 
  color: var(--bio-base-a); 
  border: 1px solid var(--bio-base-a); 
  box-shadow: 0 0 10px rgba(239, 68, 68, 0.2);
}
.base-column.t .primary-strand { 
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(4, 120, 87, 0.25) 100%); 
  color: var(--bio-base-t); 
  border: 1px solid var(--bio-base-t); 
  box-shadow: 0 0 10px rgba(16, 185, 129, 0.2);
}
.base-column.c .primary-strand { 
  background: linear-gradient(135deg, rgba(6, 182, 212, 0.2) 0%, rgba(14, 116, 144, 0.25) 100%); 
  color: var(--bio-base-c); 
  border: 1px solid var(--bio-base-c); 
  box-shadow: 0 0 10px rgba(6, 182, 212, 0.2);
}
.base-column.g .primary-strand { 
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.2) 0%, rgba(180, 83, 9, 0.25) 100%); 
  color: var(--bio-base-g); 
  border: 1px solid var(--bio-base-g); 
  box-shadow: 0 0 10px rgba(245, 158, 11, 0.2);
}

.base-column:hover .base-capsule {
  transform: scale(1.08);
}

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
  background-color: #38bdf8;
  box-shadow: 0 0 4px rgba(56, 189, 248, 0.6);
}

.comp-strand {
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(56, 189, 248, 0.18);
  color: #94a3b8;
}

.encoded-data-row {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  margin-top: 0.5rem;
  padding-top: 0.9rem;
  border-top: 1px solid rgba(56, 189, 248, 0.15);
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
  color: #94a3b8;
  min-width: 240px;
}

.strand-box {
  padding: 0.35rem 0.8rem;
  border-radius: var(--md-sys-shape-corner-small);
  background: rgba(4, 9, 18, 0.75);
  border: 1px solid rgba(56, 189, 248, 0.2);
  color: #38bdf8;
  font-family: 'JetBrains Mono', 'Fira Code', var(--md-ref-typeface-mono);
  font-size: 0.85rem;
  letter-spacing: 1.5px;
  max-width: 100%;
  overflow-x: auto;
  word-break: break-all;
  box-shadow: inset 0 1px 4px rgba(0, 0, 0, 0.5);
}

.strand-box.binary {
  color: #9ecaff;
}

/* Operaciones Genéticas */
.operations-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
  gap: 1.25rem;
}

.op-panel {
  padding: 1.4rem 1.6rem;
  background: rgba(13, 23, 38, 0.65);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(56, 189, 248, 0.15);
  border-radius: var(--md-sys-shape-corner-medium);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.op-panel:hover {
  border-color: rgba(56, 189, 248, 0.35);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37), 0 0 20px rgba(56, 189, 248, 0.15);
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
  background: linear-gradient(135deg, rgba(14, 165, 233, 0.2) 0%, rgba(2, 132, 199, 0.35) 100%);
  border: 1px solid rgba(56, 189, 248, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #38bdf8;
  box-shadow: 0 0 12px rgba(56, 189, 248, 0.25);
}

.op-panel-header h4 {
  font-size: 0.98rem;
  font-weight: 700;
  color: #f1f5f9;
}

.op-sub {
  font-size: 0.7rem;
  color: #94a3b8;
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
  background: rgba(8, 15, 28, 0.75);
  padding: 0.3rem;
  border-radius: 999px;
  border: 1px solid rgba(56, 189, 248, 0.2);
}

.seg-btn {
  flex: 1;
  height: 38px;
  border-radius: 999px;
  background: transparent;
  border: 1px solid transparent;
  font-family: 'JetBrains Mono', 'Fira Code', var(--md-ref-typeface-mono);
  font-weight: 700;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.seg-btn.a { color: var(--bio-base-a); }
.seg-btn.t { color: var(--bio-base-t); }
.seg-btn.c { color: var(--bio-base-c); }
.seg-btn.g { color: var(--bio-base-g); }

.seg-btn.active {
  box-shadow: 0 0 16px rgba(56, 189, 248, 0.35);
  transform: translateY(-1px);
}
.seg-btn.a.active { background: linear-gradient(135deg, rgba(239, 68, 68, 0.3), rgba(185, 28, 28, 0.4)); border-color: var(--bio-base-a); color: #fff; box-shadow: 0 0 16px rgba(239, 68, 68, 0.4); }
.seg-btn.t.active { background: linear-gradient(135deg, rgba(16, 185, 129, 0.3), rgba(4, 120, 87, 0.4)); border-color: var(--bio-base-t); color: #fff; box-shadow: 0 0 16px rgba(16, 185, 129, 0.4); }
.seg-btn.c.active { background: linear-gradient(135deg, rgba(6, 182, 212, 0.3), rgba(14, 116, 144, 0.4)); border-color: var(--bio-base-c); color: #fff; box-shadow: 0 0 16px rgba(6, 182, 212, 0.4); }
.seg-btn.g.active { background: linear-gradient(135deg, rgba(245, 158, 11, 0.3), rgba(180, 83, 9, 0.4)); border-color: var(--bio-base-g); color: #fff; box-shadow: 0 0 16px rgba(245, 158, 11, 0.4); }

.slider-module {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  background: rgba(10, 18, 32, 0.65);
  padding: 1rem 1.15rem;
  border-radius: 12px;
  border: 1px solid rgba(56, 189, 248, 0.18);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

.slider-telemetry {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.slider-title {
  font-size: 0.78rem;
  font-weight: 500;
  color: #cbd5e1;
}

.slider-rate {
  font-family: 'JetBrains Mono', 'Fira Code', var(--md-ref-typeface-mono);
  font-size: 1.05rem;
  font-weight: 700;
  color: #38bdf8;
  text-shadow: 0 0 10px rgba(56, 189, 248, 0.45);
}

.md3-range-slider {
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  height: 7px;
  border-radius: 999px;
  background: linear-gradient(90deg, rgba(56, 189, 248, 0.25) 0%, rgba(14, 165, 233, 0.7) 50%, rgba(56, 189, 248, 1) 100%);
  outline: none;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.6), 0 0 8px rgba(56, 189, 248, 0.2);
}

.md3-range-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #38bdf8;
  border: 2px solid #ffffff;
  box-shadow: 0 0 12px rgba(56, 189, 248, 0.95), 0 0 20px rgba(56, 189, 248, 0.5);
  cursor: grab;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.md3-range-slider::-webkit-slider-thumb:hover {
  transform: scale(1.15);
  box-shadow: 0 0 16px rgba(56, 189, 248, 1), 0 0 26px rgba(56, 189, 248, 0.7);
}

.md3-range-slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #38bdf8;
  border: 2px solid #ffffff;
  box-shadow: 0 0 12px rgba(56, 189, 248, 0.95), 0 0 20px rgba(56, 189, 248, 0.5);
  cursor: grab;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.slider-marks {
  display: flex;
  justify-content: space-between;
  font-size: 0.68rem;
  color: #94a3b8;
  font-family: 'JetBrains Mono', 'Fira Code', var(--md-ref-typeface-mono);
  font-weight: 500;
}

/* Diff Inspector */
.diff-inspector-card {
  padding: 1.4rem 1.6rem;
  background: rgba(13, 23, 38, 0.65);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(56, 189, 248, 0.15);
  border-radius: var(--md-sys-shape-corner-medium);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.diff-inspector-card:hover {
  border-color: rgba(56, 189, 248, 0.35);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37), 0 0 20px rgba(56, 189, 248, 0.15);
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
  background: rgba(13, 23, 38, 0.65);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(56, 189, 248, 0.15);
  border-radius: var(--md-sys-shape-corner-medium);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.mismatch-repair-card:hover,
.dsb-card:hover,
.audit-log-card:hover {
  border-color: rgba(56, 189, 248, 0.35);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37), 0 0 20px rgba(56, 189, 248, 0.15);
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
  background: rgba(13, 23, 38, 0.65);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(56, 189, 248, 0.15);
  border-radius: var(--md-sys-shape-corner-medium);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
  padding: 1.2rem 1.4rem;
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.duplex-card:hover {
  border-color: rgba(56, 189, 248, 0.35);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37), 0 0 20px rgba(56, 189, 248, 0.15);
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

/* Cascada Enzimática y Complejos Proteicos */
.protein-cascade-panel {
  background: var(--md-sys-color-surface-container-lowest);
  border: 1px solid var(--md-sys-color-outline-variant);
  border-radius: var(--md-sys-shape-corner-small);
  padding: 1rem 1.2rem;
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
}

.cascade-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.8rem;
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
  padding-bottom: 0.75rem;
}

.cascade-title {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.cascade-icon {
  color: #38bdf8;
}

.cascade-title h4 {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
}

.cascade-subtext {
  font-size: 0.72rem;
  color: var(--md-sys-color-on-surface-variant);
}

.viability-pill {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.3rem 0.7rem;
  border-radius: 999px;
  font-size: 0.74rem;
  font-weight: 600;
}

.viability-pill.high {
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.4);
  color: #34d399;
}

.viability-pill.medium {
  background: rgba(245, 158, 11, 0.15);
  border: 1px solid rgba(245, 158, 11, 0.4);
  color: #fbbf24;
}

.cascade-timeline {
  display: flex;
  flex-direction: column;
  gap: 0.7rem;
  position: relative;
}

.cascade-step {
  display: flex;
  gap: 0.85rem;
  align-items: flex-start;
  padding: 0.5rem 0.7rem;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 6px;
  border-left: 3px solid #38bdf8;
}

.step-num {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #0284c7;
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 700;
  flex-shrink: 0;
  margin-top: 0.1rem;
}

.step-body {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  flex: 1;
}

.step-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.prot-name {
  font-size: 0.82rem;
  font-weight: 600;
  color: #70d6ff;
}

.prot-role {
  font-size: 0.68rem;
  padding: 0.1rem 0.45rem;
  border-radius: 4px;
  font-weight: 600;
  text-transform: uppercase;
}

.prot-role.sensor {
  background: rgba(14, 165, 233, 0.18);
  color: #38bdf8;
}

.prot-role.hdr {
  background: rgba(16, 185, 129, 0.18);
  color: #34d399;
}

.prot-role.nhej {
  background: rgba(245, 158, 11, 0.18);
  color: #fbbf24;
}

.prot-role.success {
  background: rgba(16, 185, 129, 0.22);
  color: #10b981;
}

.prot-role.warning {
  background: rgba(244, 63, 94, 0.18);
  color: #fb7185;
}

.step-desc {
  font-size: 0.75rem;
  color: var(--md-sys-color-on-surface-variant);
  line-height: 1.4;
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

.audit-header-chips {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-wrap: wrap;
}

.clear-logs-chip {
  color: #f87171 !important;
  border-color: rgba(248, 113, 113, 0.3) !important;
}

.clear-logs-chip:hover:not(:disabled) {
  background: rgba(248, 113, 113, 0.15) !important;
  border-color: rgba(248, 113, 113, 0.5) !important;
}

.empty-logs-notice {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 1.6rem;
  background: rgba(4, 9, 18, 0.45);
  border: 1px dashed rgba(56, 189, 248, 0.2);
  border-radius: var(--md-sys-shape-corner-small);
  color: #94a3b8;
  font-size: 0.88rem;
  justify-content: center;
}

.empty-logs-notice .empty-icon {
  color: #64748b;
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

.exp-custom-name {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.72rem;
  color: #38bdf8;
  margin-top: 0.25rem;
  max-width: 160px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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
.res-status.copied_exact,
.res-status.success {
  color: #10b981;
}

.res-status.partially_repaired,
.res-status.repaired_prone_to_scar,
.res-status.warning {
  color: #f59e0b;
}

.res-status.info {
  color: #38bdf8;
}

.event-detail-text {
  font-size: 0.76rem;
  color: var(--md-sys-color-on-surface);
  line-height: 1.35;
  display: block;
  max-width: 250px;
}

.op-chip.mmr {
  background: rgba(14, 165, 233, 0.15);
  color: #38bdf8;
}

.op-chip.copy {
  background: rgba(16, 185, 129, 0.15);
  color: #34d399;
}

.op-chip.crispr {
  background: rgba(244, 63, 94, 0.15);
  color: #fb7185;
}

.op-chip.dsb {
  background: rgba(245, 158, 11, 0.15);
  color: #fbbf24;
}

.op-chip.repair {
  background: rgba(16, 185, 129, 0.15);
  color: #34d399;
}

.op-chip.save {
  background: rgba(99, 102, 241, 0.15);
  color: #818cf8;
}

/* Modal de Guardar Experimento con Nombre */
.save-dialog-surface {
  max-width: 560px;
}

.save-dialog-body {
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
}

.save-preview-card {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  padding: 0.85rem 1.1rem;
  background: var(--md-sys-color-surface-container-high);
  border: 1px solid var(--md-sys-color-outline-variant);
  border-radius: var(--md-sys-shape-corner-medium);
}

.preview-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.8rem;
  font-size: 0.78rem;
}

.preview-label {
  color: var(--md-sys-color-on-surface-variant);
  font-size: 0.74rem;
}

.preview-code {
  color: var(--md-sys-color-primary);
  font-weight: 600;
  letter-spacing: 0.8px;
}

.preview-code-dim {
  color: var(--md-sys-color-outline);
  letter-spacing: 0.8px;
}

.preview-tag {
  color: #38bdf8;
  font-weight: 500;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.form-group label {
  font-size: 0.82rem;
  font-weight: 500;
  color: var(--md-sys-color-on-surface);
}

.required-star {
  color: #ef4444;
}

.save-input-name,
.save-input-notes {
  width: 100%;
  padding: 0.7rem 0.9rem;
  border-radius: var(--md-sys-shape-corner-small);
  background: var(--md-sys-color-surface-container-highest);
  border: 1px solid var(--md-sys-color-outline-variant);
  color: var(--md-sys-color-on-surface);
  font-family: inherit;
  font-size: 0.88rem;
  transition: border-color 0.2s, box-shadow 0.2s;
  box-sizing: border-box;
}

.save-input-name:focus,
.save-input-notes:focus {
  outline: none;
  border-color: var(--md-sys-color-primary);
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.25);
}

.save-dialog-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.8rem;
  padding: 1.1rem 1.6rem;
  border-top: 1px solid var(--md-sys-color-outline-variant);
  background: var(--md-sys-color-surface-container-high);
}

.save-confirm-btn {
  background-color: var(--md-sys-color-primary);
  color: var(--md-sys-color-on-primary);
}

.exp-notes-snippet {
  margin: 0.2rem 0 0 0;
  font-size: 0.74rem;
  color: var(--md-sys-color-on-surface-variant);
  line-height: 1.35;
  font-style: italic;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
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
  max-width: 1040px;
  width: min(96vw, 1040px);
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-color: var(--md-sys-color-surface-container);
  border-radius: var(--md-sys-shape-corner-large);
}

.dialog-icon.highlight {
  color: #38bdf8;
}

.manual-tabs-bar {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  background: var(--md-sys-color-surface-container-low);
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
  padding: 0.6rem 1rem;
  gap: 0.6rem;
  align-items: stretch;
}

.manual-tab-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.65rem 0.8rem;
  min-height: 44px;
  background: var(--md-sys-color-surface-container);
  border: 1px solid var(--md-sys-color-outline-variant);
  border-radius: var(--md-sys-shape-corner-small);
  color: var(--md-sys-color-on-surface-variant);
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: normal;
  text-align: center;
  line-height: 1.25;
  box-sizing: border-box;
}

.manual-tab-btn:hover {
  color: var(--md-sys-color-on-surface);
  background: var(--md-sys-color-surface-container-high);
  border-color: rgba(56, 189, 248, 0.35);
}

.manual-tab-btn.active {
  color: #38bdf8;
  background: rgba(56, 189, 248, 0.12);
  border-color: #38bdf8;
  font-weight: 700;
  box-shadow: 0 0 10px rgba(56, 189, 248, 0.12);
}

@media (max-width: 820px) {
  .manual-tabs-bar {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

.manual-dialog-body {
  flex: 1;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: var(--md-sys-color-outline-variant) transparent;
  padding: 1.4rem;
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

.manual-dialog-body::-webkit-scrollbar {
  width: 6px;
}

.manual-dialog-body::-webkit-scrollbar-track {
  background: transparent;
}

.manual-dialog-body::-webkit-scrollbar-thumb {
  background: var(--md-sys-color-outline-variant);
  border-radius: 999px;
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

.protocol-card-header {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  flex-wrap: wrap;
}

.proto-tag {
  font-size: 0.7rem;
  font-weight: 800;
  text-transform: uppercase;
  padding: 0.2rem 0.55rem;
  border-radius: 4px;
  letter-spacing: 0.5px;
}

.proto-tag.g1 { background: rgba(99, 102, 241, 0.2); color: #818cf8; }
.proto-tag.crispr { background: rgba(56, 189, 248, 0.2); color: #38bdf8; }
.proto-tag.duplex { background: rgba(16, 185, 129, 0.2); color: #10b981; }
.proto-tag.audit { background: rgba(245, 158, 11, 0.2); color: #f59e0b; }

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

/* Roadmap Visual de Fases */
.manual-pipeline-roadmap {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
  background: var(--md-sys-color-surface-container-lowest);
  border: 1px solid var(--md-sys-color-outline-variant);
  border-radius: var(--md-sys-shape-corner-medium);
  padding: 1.1rem;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

@media (max-width: 860px) {
  .manual-pipeline-roadmap {
    grid-template-columns: 1fr;
  }
}

.roadmap-phase {
  background: var(--md-sys-color-surface-container-low);
  border: 1px solid var(--md-sys-color-outline-variant);
  border-radius: var(--md-sys-shape-corner-small);
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  min-width: 0;
  box-sizing: border-box;
}

.roadmap-phase.phase-molde { border-top: 3px solid #38bdf8; }
.roadmap-phase.phase-dano { border-top: 3px solid #f59e0b; }
.roadmap-phase.phase-escision { border-top: 3px solid #10b981; }

.roadmap-phase.phase-molde .rm-tag { color: #38bdf8; }
.roadmap-phase.phase-dano .rm-tag { color: #f59e0b; }
.roadmap-phase.phase-escision .rm-tag { color: #10b981; }

.rm-header {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
  padding-bottom: 0.45rem;
}

.rm-tag {
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.5px;
}

.rm-header h5 {
  margin: 0;
  font-size: 0.92rem;
  color: var(--md-sys-color-on-surface);
  font-weight: 700;
}

.rm-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  font-size: 0.76rem;
  color: var(--md-sys-color-on-surface-variant);
  line-height: 1.4;
}

.rm-alert {
  color: #f59e0b;
  font-weight: 600;
}

.rm-footer {
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.35rem 0.6rem;
  border-radius: 4px;
  text-align: center;
}

.rm-footer.cleared { background: rgba(56, 189, 248, 0.15); color: #38bdf8; }
.rm-footer.alert-active { background: rgba(245, 158, 11, 0.15); color: #f59e0b; }
.rm-footer.restored { background: rgba(16, 185, 129, 0.15); color: #10b981; }

@media (max-width: 860px) {
  .manual-pipeline-roadmap {
    grid-template-columns: 1fr;
  }
}

/* Stepper Enlace de Ayuda Rápida */
.stepper-help-link {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.25rem 0.65rem;
  background: rgba(56, 189, 248, 0.12);
  border: 1px solid rgba(56, 189, 248, 0.3);
  border-radius: 999px;
  color: #38bdf8;
  font-size: 0.73rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.stepper-help-link:hover {
  background: rgba(56, 189, 248, 0.22);
  border-color: #38bdf8;
  transform: translateY(-1px);
}

/* FAQ y Fundamentos */
.faq-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.faq-card {
  background: var(--md-sys-color-surface-container-low);
  border: 1px solid var(--md-sys-color-outline-variant);
  border-radius: var(--md-sys-shape-corner-medium);
  padding: 1.1rem 1.3rem;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.faq-q {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
}

.faq-q .q-icon {
  color: #38bdf8;
  margin-top: 0.1rem;
  flex-shrink: 0;
}

.faq-q h5 {
  margin: 0;
  color: var(--md-sys-color-on-surface);
  font-size: 0.95rem;
  line-height: 1.35;
}

.faq-a p {
  margin: 0;
  font-size: 0.82rem;
  line-height: 1.5;
  color: var(--md-sys-color-on-surface-variant);
}

/* Bibliografía */
.biblio-box {
  background: rgba(56, 189, 248, 0.05);
  border: 1px solid rgba(56, 189, 248, 0.25);
  border-radius: var(--md-sys-shape-corner-medium);
  padding: 1.2rem;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  margin-top: 0.5rem;
}

.biblio-header {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  color: #38bdf8;
}

.biblio-header h6 {
  margin: 0;
  font-size: 0.92rem;
  font-weight: 700;
}

.biblio-list {
  margin: 0;
  padding-left: 1.2rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  font-size: 0.8rem;
  color: var(--md-sys-color-on-surface);
  line-height: 1.45;
}

.biblio-list li {
  color: var(--md-sys-color-on-surface-variant);
}

.biblio-list strong {
  color: var(--md-sys-color-on-surface);
}

.biblio-list small {
  color: var(--md-sys-color-outline);
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

/* Esqueleto de Azúcar-Fosfato en Métricas */
.backbone-metric-tile {
  grid-column: span 1;
}
.backbone-badges {
  display: flex;
  gap: 0.4rem;
  margin-top: 0.25rem;
  flex-wrap: wrap;
}
.bb-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.72rem;
  padding: 0.2rem 0.5rem;
  border-radius: var(--md-sys-shape-corner-small);
  font-family: var(--md-ref-typeface-mono);
}
.bb-chip.sugar {
  background: rgba(6, 182, 212, 0.15);
  color: #38bdf8;
  border: 1px solid rgba(6, 182, 212, 0.3);
}
.bb-chip.phosphate {
  background: rgba(245, 158, 11, 0.15);
  color: #fbbf24;
  border: 1px solid rgba(245, 158, 11, 0.3);
}
.bb-dot.s-dot { width: 6px; height: 6px; border-radius: 50%; background: #38bdf8; }
.bb-dot.p-dot { width: 6px; height: 6px; border-radius: 50%; background: #fbbf24; }

/* 2D Track con Esqueleto Azúcar-Fosfato */
.track-polarity-col {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  padding: 0 0.35rem;
  height: 140px;
}
.polarity-tag {
  font-family: var(--md-ref-typeface-mono);
  font-size: 0.7rem;
  font-weight: 700;
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
  white-space: nowrap;
}
.polarity-tag.p5 {
  background: rgba(245, 158, 11, 0.2);
  color: #fbbf24;
  border: 1px solid rgba(245, 158, 11, 0.4);
}
.polarity-tag.p3 {
  background: rgba(56, 189, 248, 0.2);
  color: #38bdf8;
  border: 1px solid rgba(56, 189, 248, 0.4);
}
.polarity-v-link {
  width: 1px;
  flex: 1;
  background: repeating-linear-gradient(to bottom, rgba(255,255,255,0.2) 0, rgba(255,255,255,0.2) 3px, transparent 3px, transparent 6px);
  margin: 4px 0;
}
.bb-monomer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2px;
  position: relative;
  width: 100%;
}
.bb-monomer.top {
  margin-bottom: 5px;
}
.bb-monomer.bottom {
  margin-top: 5px;
}
.bb-dot {
  font-family: var(--md-ref-typeface-mono);
  font-size: 0.65rem;
  font-weight: 800;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}
.bb-dot.phosphate {
  background: #f59e0b;
  color: #000;
  box-shadow: 0 0 6px rgba(245, 158, 11, 0.5);
}
.bb-dot.sugar {
  background: #94a3b8;
  color: #0f172a;
  border-radius: 3px;
  box-shadow: 0 0 6px rgba(148, 163, 184, 0.5);
}
.bb-hyphen {
  font-size: 0.65rem;
  font-weight: 700;
  color: var(--md-sys-color-outline);
}
.bb-stem-down {
  position: absolute;
  bottom: -5px;
  left: 50%;
  width: 1px;
  height: 5px;
  background: var(--md-sys-color-outline-variant);
}
.bb-stem-up {
  position: absolute;
  top: -5px;
  left: 50%;
  width: 1px;
  height: 5px;
  background: var(--md-sys-color-outline-variant);
}

.backbone-explanation-bar {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.65rem 0.9rem;
  background: var(--md-sys-color-surface-container-high);
  border-radius: var(--md-sys-shape-corner-small);
  margin-top: 0.8rem;
  flex-wrap: wrap;
  border: 1px solid var(--md-sys-color-outline-variant);
}
.legend-eq-item {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}
.legend-eq-item.final {
  flex-direction: column;
  align-items: flex-start;
  gap: 0.1rem;
}
.legend-eq-item.final .highlight-txt {
  font-weight: 700;
  color: #38bdf8;
  font-size: 0.8rem;
}
.legend-eq-item.final small {
  font-size: 0.68rem;
  color: var(--md-sys-color-on-surface-variant);
}
.sym-badge {
  font-family: var(--md-ref-typeface-mono);
  font-size: 0.72rem;
  font-weight: 800;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
}
.sym-badge.p { background: #f59e0b; color: #000; }
.sym-badge.d { background: #94a3b8; color: #0f172a; }
.sym-badge.b { background: rgba(255, 255, 255, 0.1); color: var(--md-sys-color-on-surface); }
.eq-op {
  font-weight: 700;
  color: var(--md-sys-color-outline);
}

/* Stepper del Ciclo Celular */
.cell-cycle-stepper-track {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  overflow-x: auto;
  padding: 0.5rem 0.2rem;
}
.cycle-phase-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0.6rem 0.8rem;
  background: var(--md-sys-color-surface-container-low);
  border-radius: var(--md-sys-shape-corner-medium);
  border: 1px solid var(--md-sys-color-outline-variant);
  transition: all 0.25s ease;
}
.cycle-phase-section.active {
  border-color: var(--md-sys-color-primary);
  background: rgba(99, 102, 241, 0.08);
  box-shadow: 0 0 16px rgba(99, 102, 241, 0.15);
}
.phase-section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.phase-code {
  font-size: 0.75rem;
  font-weight: 800;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  background: var(--md-sys-color-surface-container-highest);
  color: var(--md-sys-color-primary);
}
.phase-subtitle {
  font-size: 0.7rem;
  color: var(--md-sys-color-on-surface-variant);
}
.phase-steps-container {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}
.phase-inter-divider {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--md-sys-color-outline);
}
.phase-badge-pill {
  font-size: 0.74rem;
  font-weight: 600;
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  background: var(--md-sys-color-surface-container-highest);
  color: var(--md-sys-color-on-surface);
  border: 1px solid var(--md-sys-color-outline-variant);
}
.phase-badge-pill.g1 { color: #38bdf8; border-color: rgba(56, 189, 248, 0.4); background: rgba(56, 189, 248, 0.1); }
.phase-badge-pill.s { color: #4ade80; border-color: rgba(74, 222, 128, 0.4); background: rgba(74, 222, 128, 0.1); }
.phase-badge-pill.g2 { color: #f59e0b; border-color: rgba(245, 158, 11, 0.4); background: rgba(245, 158, 11, 0.1); }

/* Bloques de Fases */
.phase-block {
  padding: 1.4rem 1.6rem;
  border-radius: var(--md-sys-shape-corner-medium);
  background: rgba(13, 23, 38, 0.65);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(56, 189, 248, 0.15);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.phase-block:hover {
  border-color: rgba(56, 189, 248, 0.35);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37), 0 0 20px rgba(56, 189, 248, 0.15);
}
.phase-block-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}
.phase-title-group {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}
.phase-avatar {
  width: 38px;
  height: 38px;
  border-radius: var(--md-sys-shape-corner-medium);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 900;
  font-size: 0.95rem;
}
.phase-avatar.g1 { background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.4); }
.phase-avatar.s { background: rgba(74, 222, 128, 0.15); color: #4ade80; border: 1px solid rgba(74, 222, 128, 0.4); }
.phase-avatar.g2 { background: rgba(245, 158, 11, 0.15); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.4); }

.checkpoint-status-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.35rem 0.85rem;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 600;
  backdrop-filter: blur(8px);
  transition: all 0.25s ease;
}
.checkpoint-status-pill.cleared { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4); box-shadow: 0 0 12px rgba(16, 185, 129, 0.2); }
.checkpoint-status-pill.arrested { background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.4); box-shadow: 0 0 12px rgba(239, 68, 68, 0.2); }
.checkpoint-status-pill.idle { background: rgba(30, 41, 59, 0.6); color: #94a3b8; border: 1px solid rgba(71, 85, 105, 0.4); }

/* Tarjeta de Checkpoint G1 / Dinámica p53-MDM2 / Punto R - Bio-Tech HUD */
.checkpoint-g1-card {
  padding: 1.3rem 1.5rem;
  border-radius: var(--md-sys-shape-corner-medium);
  display: flex;
  flex-direction: column;
  gap: 1.15rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  margin-bottom: 0.25rem;
  background: rgba(13, 23, 38, 0.65);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(56, 189, 248, 0.15);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
  position: relative;
  overflow: hidden;
}

.checkpoint-g1-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(56, 189, 248, 0.7), transparent);
}

.checkpoint-g1-card.cleared {
  background: linear-gradient(135deg, rgba(13, 23, 38, 0.75) 0%, rgba(6, 78, 59, 0.18) 100%);
  border-color: rgba(16, 185, 129, 0.35);
  box-shadow: 0 0 20px rgba(16, 185, 129, 0.2);
}
.checkpoint-g1-card.arrested_mild {
  background: linear-gradient(135deg, rgba(13, 23, 38, 0.75) 0%, rgba(120, 53, 15, 0.18) 100%);
  border-color: rgba(245, 158, 11, 0.4);
  box-shadow: 0 0 20px rgba(245, 158, 11, 0.2);
}
.checkpoint-g1-card.arrested_severe {
  background: linear-gradient(135deg, rgba(13, 23, 38, 0.8) 0%, rgba(127, 29, 29, 0.25) 100%);
  border-color: rgba(239, 68, 68, 0.5);
  box-shadow: 0 0 25px rgba(239, 68, 68, 0.25);
}
.checkpoint-g1-card.idle {
  background: rgba(13, 23, 38, 0.65);
  border: 1px solid rgba(56, 189, 248, 0.15);
}

.cp-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.8rem;
  border-bottom: 1px solid rgba(56, 189, 248, 0.12);
  padding-bottom: 0.75rem;
}

.cp-status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.65rem;
  font-weight: 700;
  font-size: 0.95rem;
  color: #f1f5f9;
  letter-spacing: -0.2px;
}

.cp-status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
  transition: all 0.3s ease;
}
.cp-status-dot.cleared {
  background: #10b981;
  box-shadow: 0 0 10px #10b981, 0 0 16px rgba(16, 185, 129, 0.6);
  animation: pulse-glow-emerald 2s infinite ease-in-out;
}
.cp-status-dot.arrested_mild {
  background: #f59e0b;
  box-shadow: 0 0 10px #f59e0b, 0 0 16px rgba(245, 158, 11, 0.6);
  animation: pulse-glow-amber 1.8s infinite ease-in-out;
}
.cp-status-dot.arrested_severe {
  background: #ef4444;
  box-shadow: 0 0 12px #ef4444, 0 0 20px rgba(239, 68, 68, 0.8);
  animation: pulse-glow-danger 1.4s infinite ease-in-out;
}
.cp-status-dot.idle {
  background: #64748b;
  box-shadow: 0 0 6px #64748b;
}

@keyframes pulse-glow-emerald {
  0%, 100% { transform: scale(0.9); opacity: 0.8; box-shadow: 0 0 8px #10b981; }
  50% { transform: scale(1.2); opacity: 1; box-shadow: 0 0 16px #10b981, 0 0 24px rgba(16, 185, 129, 0.5); }
}

@keyframes pulse-glow-amber {
  0%, 100% { transform: scale(0.9); opacity: 0.8; box-shadow: 0 0 8px #f59e0b; }
  50% { transform: scale(1.2); opacity: 1; box-shadow: 0 0 16px #f59e0b, 0 0 24px rgba(245, 158, 11, 0.5); }
}

@keyframes pulse-glow-danger {
  0%, 100% { transform: scale(0.9); opacity: 0.8; box-shadow: 0 0 10px #ef4444; }
  50% { transform: scale(1.25); opacity: 1; box-shadow: 0 0 20px #ef4444, 0 0 30px rgba(239, 68, 68, 0.6); }
}

.cp-phase-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.74rem;
  font-weight: 600;
  padding: 0.3rem 0.75rem;
  border-radius: 999px;
  background: linear-gradient(135deg, rgba(56, 189, 248, 0.12) 0%, rgba(14, 165, 233, 0.2) 100%);
  color: #38bdf8;
  border: 1px solid rgba(56, 189, 248, 0.3);
  box-shadow: 0 0 10px rgba(56, 189, 248, 0.15);
}

/* Grid responsivo auto-fit para los 3 nodos */
.cp-grid-3col {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1rem;
}

/* Tarjetas de Instrumentación Biofísica para los Nodos */
.cp-node-box {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  padding: 1.1rem 1.2rem;
  border-radius: 12px;
  background: rgba(10, 18, 32, 0.7);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid rgba(56, 189, 248, 0.14);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06), 0 4px 16px rgba(0, 0, 0, 0.25);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.cp-node-box::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  opacity: 0.75;
}

.cp-node-box.p53-node::before { background: linear-gradient(90deg, #38bdf8, transparent); }
.cp-node-box.p21-node::before { background: linear-gradient(90deg, #f59e0b, transparent); }
.cp-node-box.puntor-node::before { background: linear-gradient(90deg, #a78bfa, transparent); }

.cp-node-box:hover {
  transform: translateY(-2px);
  border-color: rgba(56, 189, 248, 0.35);
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.4), 0 0 20px rgba(56, 189, 248, 0.2);
}

.cp-node-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-family: 'JetBrains Mono', 'Fira Code', var(--md-ref-typeface-mono);
  font-size: 0.74rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  color: #cbd5e1;
}

.cp-node-box.p53-node .node-icon { color: #38bdf8; filter: drop-shadow(0 0 6px rgba(56, 189, 248, 0.5)); }
.cp-node-box.p21-node .node-icon { color: #f59e0b; filter: drop-shadow(0 0 6px rgba(245, 158, 11, 0.5)); }
.cp-node-box.puntor-node .node-icon { color: #a78bfa; filter: drop-shadow(0 0 6px rgba(167, 139, 250, 0.5)); }

.node-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  align-self: flex-start;
  font-family: 'JetBrains Mono', 'Fira Code', var(--md-ref-typeface-mono);
  font-size: 0.74rem;
  font-weight: 700;
  padding: 0.28rem 0.65rem;
  border-radius: 6px;
  line-height: 1.25;
  letter-spacing: 0.2px;
  position: relative;
}

.node-badge::before {
  content: '';
  display: inline-block;
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: currentColor;
  box-shadow: 0 0 8px currentColor;
  animation: pulse-badge-dot 1.8s infinite ease-in-out;
  flex-shrink: 0;
}

@keyframes pulse-badge-dot {
  0%, 100% { transform: scale(0.85); opacity: 0.6; }
  50% { transform: scale(1.3); opacity: 1; box-shadow: 0 0 12px currentColor; }
}

.node-badge.cleared {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(6, 78, 59, 0.25) 100%);
  color: #34d399;
  border: 1px solid rgba(16, 185, 129, 0.4);
  box-shadow: 0 0 12px rgba(16, 185, 129, 0.2);
}

.node-badge.arrested_mild {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(120, 53, 15, 0.25) 100%);
  color: #fbbf24;
  border: 1px solid rgba(245, 158, 11, 0.4);
  box-shadow: 0 0 12px rgba(245, 158, 11, 0.2);
}

.node-badge.arrested_severe {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.18) 0%, rgba(127, 29, 29, 0.3) 100%);
  color: #f87171;
  border: 1px solid rgba(239, 68, 68, 0.45);
  box-shadow: 0 0 14px rgba(239, 68, 68, 0.3);
}

.node-badge.idle {
  background: rgba(30, 41, 59, 0.6);
  color: #94a3b8;
  border: 1px solid rgba(71, 85, 105, 0.4);
}

.node-badge.bypass-tag {
  background: linear-gradient(135deg, rgba(167, 139, 250, 0.15) 0%, rgba(109, 40, 217, 0.2) 100%);
  color: #c4b5fd;
  border: 1px solid rgba(167, 139, 250, 0.4);
  box-shadow: 0 0 12px rgba(167, 139, 250, 0.2);
}

.node-desc {
  font-size: 0.77rem;
  line-height: 1.45;
  color: #94a3b8;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.cp-clarification-banner {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.8rem 1.1rem;
  border-radius: var(--md-sys-shape-corner-medium);
  background: linear-gradient(135deg, rgba(14, 165, 233, 0.1) 0%, rgba(2, 132, 199, 0.05) 100%);
  border: 1px solid rgba(56, 189, 248, 0.28);
  color: #e2e8f0;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05);
}
.cp-clarification-banner .banner-icon {
  color: #38bdf8;
  filter: drop-shadow(0 0 6px rgba(56, 189, 248, 0.5));
  flex-shrink: 0;
  margin-top: 2px;
}
.cp-clarification-banner .banner-body {
  font-size: 0.78rem;
  line-height: 1.45;
}
.cp-clarification-banner strong {
  color: #38bdf8;
  margin-right: 0.4rem;
}

.g1-repair-card { grid-column: 1 / -1; }
.g1-actions-grid, .s-replication-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.2rem;
}
@media (max-width: 900px) {
  .g1-repair-card { grid-column: 1 / -1; }
.g1-actions-grid, .s-replication-grid { grid-template-columns: 1fr; }
}

.triple-fidelity-card {
  padding: 1.1rem 1.4rem;
  background: rgba(74, 222, 128, 0.04);
  border: 1px solid rgba(74, 222, 128, 0.2);
  border-radius: var(--md-sys-shape-corner-medium);
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
}
.card-subtitle-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #4ade80;
  font-weight: 600;
  font-size: 0.85rem;
}
.fidelity-filters-grid {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.8rem;
}
@media (max-width: 800px) {
  .fidelity-filters-grid { flex-direction: column; align-items: stretch; }
}
.filter-box {
  flex: 1;
  display: flex;
  gap: 0.6rem;
  padding: 0.8rem 1rem;
  background: var(--md-sys-color-surface-container-low);
  border-radius: var(--md-sys-shape-corner-medium);
  border: 1px solid var(--md-sys-color-outline-variant);
}
.filter-num {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: rgba(74, 222, 128, 0.15);
  color: #4ade80;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  flex-shrink: 0;
}
.filter-content {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}
.filter-content strong {
  font-size: 0.82rem;
  color: var(--md-sys-color-on-surface);
}
.filter-rate {
  font-family: var(--md-ref-typeface-mono);
  font-size: 0.76rem;
  font-weight: 700;
  color: #4ade80;
}
.filter-content p {
  font-size: 0.7rem;
  color: var(--md-sys-color-on-surface-variant);
  line-height: 1.25;
}
.filter-arrow {
  font-weight: 800;
  color: #4ade80;
  font-size: 1.2rem;
}
.fidelity-summary-banner {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.78rem;
  color: var(--md-sys-color-on-surface);
  background: rgba(74, 222, 128, 0.1);
  padding: 0.5rem 0.8rem;
  border-radius: var(--md-sys-shape-corner-small);
}

.card-mini-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  color: var(--md-sys-color-primary);
}

/* Toggles de Modo: Cápsula Flotante Bio-Tech */
.sub-mode-toggle-row,
.repair-mode-toggle-row {
  display: flex;
  gap: 0.5rem;
  padding: 0.35rem;
  background: rgba(8, 15, 28, 0.75);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border-radius: 999px;
  border: 1px solid rgba(56, 189, 248, 0.2);
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.4);
  margin-bottom: 0.3rem;
}

.sub-toggle-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.5rem 0.9rem;
  border-radius: 999px;
  border: 1px solid transparent;
  background: transparent;
  color: #94a3b8;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  white-space: nowrap;
}

.sub-toggle-btn:hover {
  color: #f1f5f9;
  background: rgba(56, 189, 248, 0.08);
}

.sub-toggle-btn.active {
  background: linear-gradient(135deg, rgba(14, 165, 233, 0.3) 0%, rgba(2, 132, 199, 0.45) 100%);
  color: #38bdf8;
  border: 1px solid rgba(56, 189, 248, 0.45);
  box-shadow: 0 0 16px rgba(56, 189, 248, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.15);
  transform: translateY(-1px);
}

.damage-subpanel, .replication-mode-box {
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
}

.env-damage-feedback {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  padding: 0.8rem 1rem;
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(180, 83, 9, 0.06) 100%);
  border: 1px solid rgba(245, 158, 11, 0.35);
  border-radius: 10px;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

.env-tag {
  font-size: 0.78rem;
  font-weight: 700;
  color: #f59e0b;
}

.env-mechanism {
  font-size: 0.75rem;
  color: #cbd5e1;
  margin: 0;
  line-height: 1.4;
}

.lesions-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  margin-top: 0.25rem;
}

.lesion-chip {
  font-size: 0.72rem;
  font-family: 'JetBrains Mono', 'Fira Code', var(--md-ref-typeface-mono);
  font-weight: 600;
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(127, 29, 29, 0.3) 100%);
  border: 1px solid rgba(239, 68, 68, 0.45);
  color: #f87171;
  box-shadow: 0 0 10px rgba(239, 68, 68, 0.2);
}

/* Slider de Eficiencia Enzimática de Reparación G1 */
.repair-eff-slider {
  background: rgba(10, 18, 32, 0.7);
  border: 1px solid rgba(56, 189, 248, 0.22);
  border-radius: 12px;
  padding: 0.9rem 1.1rem;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

.highlight-repair {
  color: #38bdf8;
  font-weight: 700;
  text-shadow: 0 0 10px rgba(56, 189, 248, 0.5);
}

.repair-range::-webkit-slider-thumb {
  background: #38bdf8;
  box-shadow: 0 0 14px rgba(56, 189, 248, 1), 0 0 22px rgba(56, 189, 248, 0.6);
}

.escaped-lesions-box {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  padding: 0.75rem 0.95rem;
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.09) 0%, rgba(180, 83, 9, 0.05) 100%);
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: 10px;
}

.esc-label {
  font-size: 0.75rem;
  color: #f59e0b;
  font-weight: 600;
}

.esc-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.esc-chip {
  font-family: 'JetBrains Mono', 'Fira Code', var(--md-ref-typeface-mono);
  font-size: 0.72rem;
  font-weight: 600;
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
  background: rgba(245, 158, 11, 0.2);
  border: 1px solid rgba(245, 158, 11, 0.45);
  color: #fbbf24;
  box-shadow: 0 0 8px rgba(245, 158, 11, 0.25);
}

/* Botones y Controles con Degradados Sutiles Bioluminiscentes */
.dna-lab-layout .md3-button-filled {
  background: linear-gradient(135deg, #0284c7 0%, #0369a1 50%, #0284c7 100%);
  background-size: 200% auto;
  border: 1px solid rgba(56, 189, 248, 0.4);
  color: #f0f9ff;
  box-shadow: 0 0 14px rgba(56, 189, 248, 0.25);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.dna-lab-layout .md3-button-filled:hover:not(:disabled) {
  background-position: right center;
  border-color: #38bdf8;
  box-shadow: 0 0 22px rgba(56, 189, 248, 0.5);
  transform: translateY(-1px);
}

.dna-lab-layout .md3-button-tonal {
  background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%);
  border: 1px solid rgba(56, 189, 248, 0.22);
  color: #70d6ff;
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.dna-lab-layout .md3-button-tonal:hover:not(:disabled) {
  background: linear-gradient(135deg, rgba(56, 189, 248, 0.2) 0%, rgba(14, 165, 233, 0.25) 100%);
  border-color: rgba(56, 189, 248, 0.45);
  box-shadow: 0 0 18px rgba(56, 189, 248, 0.25);
  transform: translateY(-1px);
}

.dna-lab-layout .md3-chip {
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.85) 0%, rgba(30, 41, 59, 0.65) 100%);
  border: 1px solid rgba(56, 189, 248, 0.2);
  color: #cbd5e1;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.dna-lab-layout .md3-chip:hover {
  border-color: rgba(56, 189, 248, 0.45);
  box-shadow: 0 0 14px rgba(56, 189, 248, 0.25);
  color: #f8fafc;
  transform: translateY(-1px);
}

/* ==========================================================================
   5. MEDIA QUERIES Y ADAPTABILIDAD MÓVIL / TABLET ESTRUCTURADA
   ========================================================================== */
.dna-lab-layout { min-width: 0; max-width: 100%; }
.dna-lab-layout > * { min-width: 0; max-width: 100%; }
.dna-lab-layout code, .dna-lab-layout .font-mono { overflow-wrap: anywhere; word-break: break-all; }
.events-table-wrapper { overflow-x: auto; -webkit-overflow-scrolling: touch; max-width: 100%; }
.pairs-visual-strip { flex-wrap: wrap; }
.sub-mode-toggle-row, .repair-mode-toggle-row, .action-buttons-row, .dsb-action-buttons { flex-wrap: wrap; }
.phase-block-header, .section-header, .diff-header { flex-wrap: wrap; gap: 0.75rem; }
.manual-tab-btn { white-space: normal; }
.manual-dialog-body { min-width: 0; }
.manual-dialog-body img, .manual-dialog-body table { max-width: 100%; }

/* Punto de Quiebre 1: Desktop (> 1200px) - Distribución Espaciosa en Filas */
@media (min-width: 1200px) {
  .molecular-workbench-grid {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    width: 100%;
  }
  .g1-actions-grid {
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  }
}

/* Punto de Quiebre 2: Laptop / Tablet (768px - 1199px) - Adaptativo */
@media (max-width: 1199px) and (min-width: 768px) {
  .molecular-workbench-grid {
    grid-template-columns: minmax(0, 1fr);
    gap: 1.25rem;
  }
  .g1-actions-grid {
    grid-template-columns: minmax(0, 1fr);
    gap: 1.25rem;
  }
  .button-guide-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .manual-pipeline-roadmap {
    grid-template-columns: minmax(0, 1fr);
  }
  .manual-dialog-surface {
    width: 95vw;
    max-height: 94vh;
  }
  .sequence-track-card {
    min-height: auto;
  }
}

/* Punto de Quiebre 3: Mobile (< 767px) - Padding 0.8rem, Botones 100%, Touch Friendly */
@media (max-width: 767px) {
  .dna-header-card,
  .dna-input-section,
  .sequence-track-card,
  .phase-block,
  .checkpoint-g1-card,
  .op-panel,
  .duplex-card,
  .diff-inspector-card,
  .mismatch-repair-card,
  .dsb-card,
  .audit-log-card {
    padding: 0.8rem;
    border-radius: 12px;
  }

  .molecular-workbench-grid {
    grid-template-columns: minmax(0, 1fr);
    gap: 1rem;
  }

  .sequence-track-card {
    min-height: auto;
  }

  .g1-actions-grid {
    grid-template-columns: minmax(0, 1fr);
    gap: 1rem;
  }

  .input-primary-row {
    flex-direction: column;
    gap: 0.75rem;
  }

  .sub-mode-toggle-row,
  .repair-mode-toggle-row {
    flex-direction: column;
    padding: 0.35rem;
    border-radius: 16px;
    gap: 0.35rem;
  }

  .sub-toggle-btn {
    width: 100%;
    justify-content: center;
    border-radius: 10px;
    padding: 0.6rem 0.8rem;
    white-space: normal;
    text-align: center;
  }

  .md3-button-filled,
  .md3-button-tonal,
  .dna-lab-layout .md3-button-filled,
  .dna-lab-layout .md3-button-tonal {
    width: 100%;
    justify-content: center;
    padding: 0 14px;
    font-size: 0.84rem;
  }

  .action-buttons-row,
  .dsb-action-buttons,
  .input-action-bar {
    flex-direction: column;
    width: 100%;
    gap: 0.6rem;
  }

  .input-with-actions {
    flex-direction: column;
    align-items: stretch;
    gap: 0.6rem;
  }

  .input-with-actions input {
    width: 100%;
    min-width: 0;
  }

  .header-text h2,
  .phase-title-group h3,
  .section-header h3,
  .diff-title-row h3 {
    font-size: 1rem;
    line-height: 1.35;
  }

  .track-title-group h3 {
    font-size: 0.95rem;
  }

  .slider-marks {
    font-size: 0.62rem;
    gap: 0.25rem;
  }

  .slider-module {
    padding: 0.75rem 0.85rem;
  }

  .manual-dialog-surface {
    width: 98vw;
    max-height: 95vh;
    border-radius: 14px;
  }

  .manual-dialog-body {
    padding: 0.8rem;
    gap: 0.8rem;
  }

  .manual-tabs-bar {
    grid-template-columns: minmax(0, 1fr);
    padding: 0.4rem;
  }

  .manual-tab-btn {
    padding: 0.5rem;
    font-size: 0.76rem;
  }

  .button-guide-grid {
    grid-template-columns: minmax(0, 1fr);
  }

  .flow-step-item {
    flex-direction: column;
    gap: 0.5rem;
  }

  .op-form-grid {
    grid-template-columns: minmax(0, 1fr);
  }

  .dsb-controls-row {
    flex-direction: column;
    align-items: stretch;
  }

  .mutation-events-grid {
    grid-template-columns: minmax(0, 1fr);
  }

  .cp-grid-3col {
    grid-template-columns: minmax(0, 1fr);
  }
}

/* ═══════════════════════════════════════════════════════════════════════ */
/* BARRA DE NAVEGACIÓN POR FASES (TABS BIO-TECH)                         */
/* ═══════════════════════════════════════════════════════════════════════ */
.phase-tabs-nav {
  display: flex;
  align-items: stretch;
  gap: 4px;
  padding: 4px;
  background: linear-gradient(135deg, rgba(10, 18, 30, 0.85), rgba(16, 28, 48, 0.9));
  border: 1px solid rgba(0, 240, 200, 0.12);
  border-radius: 14px;
  position: relative;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  box-shadow:
    0 0 20px rgba(0, 200, 160, 0.06),
    inset 0 1px 0 rgba(255, 255, 255, 0.04);
}

.phase-tab-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 18px;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 11px;
  color: rgba(178, 198, 220, 0.65);
  font-size: 0.82rem;
  font-weight: 500;
  letter-spacing: 0.02em;
  cursor: pointer;
  transition: all 0.35s cubic-bezier(0.22, 1, 0.36, 1);
  position: relative;
  z-index: 1;
  white-space: nowrap;
}

.phase-tab-btn:hover {
  color: rgba(200, 230, 255, 0.85);
  background: rgba(0, 200, 180, 0.06);
}

.phase-tab-btn.active {
  color: #e0f7fa;
  background: linear-gradient(135deg, rgba(0, 200, 180, 0.14), rgba(0, 120, 200, 0.1));
  border-color: rgba(0, 240, 200, 0.25);
  box-shadow:
    0 0 16px rgba(0, 240, 200, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.06);
  font-weight: 600;
}

.phase-tab-btn.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 20%;
  width: 60%;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(0, 240, 200, 0.7), transparent);
  border-radius: 1px;
}

.tab-label {
  font-size: 0.82rem;
}

.tab-badge {
  font-size: 0.68rem;
  padding: 2px 8px;
  border-radius: 10px;
  background: rgba(0, 240, 200, 0.12);
  color: rgba(0, 240, 200, 0.85);
  font-weight: 600;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  border: 1px solid rgba(0, 240, 200, 0.15);
}

.tab-badge.phase2-badge {
  background: rgba(130, 80, 255, 0.12);
  color: rgba(180, 140, 255, 0.9);
  border-color: rgba(130, 80, 255, 0.2);
}

.tab-indicator {
  display: none; /* indicator is handled via .active pseudo-element */
}

/* Phase content wrapper */
.phase-content-wrapper {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

/* ═══════════════════════ CABECERA GENERAL COMPARTIDA: SELECTOR DE GENES ═══════════════════════ */
.shared-gene-selector-card {
  background: linear-gradient(135deg, rgba(10, 16, 32, 0.94), rgba(16, 26, 48, 0.9));
  border: 1px solid rgba(0, 220, 200, 0.22);
  border-radius: 16px;
  padding: 1rem 1.4rem;
  backdrop-filter: blur(14px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25), 0 0 15px rgba(0, 220, 200, 0.05);
  transition: all 0.3s ease;
}

.shared-gene-selector-card:hover {
  border-color: rgba(0, 220, 200, 0.35);
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.3), 0 0 20px rgba(0, 220, 200, 0.08);
}

.shared-selector-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.shared-selector-title {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  min-width: 260px;
}

.selector-badge-avatar {
  width: 36px;
  height: 36px;
  min-width: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, rgba(0, 220, 200, 0.2), rgba(130, 80, 255, 0.2));
  border: 1px solid rgba(0, 220, 200, 0.35);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #00f0d0;
  box-shadow: 0 0 12px rgba(0, 220, 200, 0.2);
}

.selector-title-text {
  display: block;
  font-size: 0.88rem;
  font-weight: 700;
  color: rgba(230, 245, 255, 0.95);
  letter-spacing: 0.02em;
}

.selector-subtext {
  display: block;
  font-size: 0.74rem;
  color: rgba(160, 190, 220, 0.7);
  margin-top: 2px;
}

.gene-selector-row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: center;
}

.gene-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  border-radius: 12px;
  background: rgba(130, 80, 255, 0.08);
  border: 1px solid rgba(130, 80, 255, 0.2);
  color: rgba(200, 215, 240, 0.85);
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.2, 0.8, 0.2, 1);
  user-select: none;
}

.gene-chip:hover {
  background: rgba(130, 80, 255, 0.16);
  border-color: rgba(130, 80, 255, 0.4);
  color: #ffffff;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(130, 80, 255, 0.15);
}

.gene-chip.active {
  background: linear-gradient(135deg, rgba(0, 220, 200, 0.2), rgba(130, 80, 255, 0.25));
  border-color: rgba(0, 220, 200, 0.6);
  color: #ffffff;
  font-weight: 600;
  box-shadow: 0 0 16px rgba(0, 220, 200, 0.25);
}

.gene-chip.free-chip.active {
  background: linear-gradient(135deg, rgba(80, 160, 240, 0.22), rgba(0, 200, 180, 0.25));
  border-color: rgba(0, 220, 200, 0.6);
  color: #ffffff;
  box-shadow: 0 0 16px rgba(0, 220, 200, 0.22);
}

.gene-chip-name {
  font-weight: 600;
}

.chip-bp {
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 0.68rem;
  padding: 2px 7px;
  border-radius: 6px;
  background: rgba(0, 0, 0, 0.3);
  color: rgba(160, 210, 255, 0.8);
}

.gene-chip.active .chip-bp {
  background: rgba(0, 220, 200, 0.2);
  color: #70fff0;
}

.gene-chip:disabled,
.gene-chip.disabled,
.gene-chip:disabled:hover,
.gene-chip.disabled:hover {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: auto;
  background: rgba(255, 255, 255, 0.03) !important;
  border-color: rgba(255, 255, 255, 0.1) !important;
  color: rgba(160, 180, 210, 0.5) !important;
  transform: none !important;
  box-shadow: none !important;
}

.chip-dev-badge {
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 0.65rem;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 6px;
  background: rgba(255, 171, 0, 0.14);
  border: 1px solid rgba(255, 171, 0, 0.35);
  color: #ffb74d;
  letter-spacing: 0.02em;
}

.chip-active-dot {
  color: #00f0d0;
  font-size: 0.75rem;
  animation: pulse-dot 1.8s infinite ease-in-out;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.85); }
}

/* ═══════════════════════ FICHA COMPACTA GEN ACTIVO (FASE 1) ═══════════════════════ */
.gene-compact-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.85rem 1.25rem;
  background: linear-gradient(135deg, rgba(12, 18, 34, 0.88), rgba(16, 24, 42, 0.82));
  border: 1px solid rgba(80, 160, 240, 0.18);
  border-left: 4px solid #00c8b4;
  border-radius: 12px;
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.2);
}

.compact-card-left {
  display: flex;
  align-items: center;
  flex: 1;
}

.compact-gene-indicator {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.compact-icon {
  color: #00c8b4;
}

.compact-gene-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.compact-name-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.compact-prefix {
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: rgba(140, 170, 210, 0.65);
}

.compact-name {
  font-size: 0.92rem;
  color: #eaf2ff;
  letter-spacing: 0.01em;
}

.provenance-pill {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 0.68rem;
  font-weight: 600;
  border: 1px solid;
}

.provenance-pill.curated {
  background: rgba(0, 200, 120, 0.12);
  color: #50e6a0;
  border-color: rgba(0, 200, 120, 0.3);
}

.provenance-pill.didactic {
  background: rgba(255, 180, 50, 0.12);
  color: #ffc864;
  border-color: rgba(255, 180, 50, 0.3);
}

.provenance-pill.custom {
  background: rgba(80, 160, 240, 0.12);
  color: #70b8ff;
  border-color: rgba(80, 160, 240, 0.3);
}

.gene-compact-card.custom-mode {
  border-left-color: rgba(80, 160, 240, 0.7);
}

.compact-icon.custom {
  color: #50a0f0;
}

.compact-meta-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.74rem;
  color: rgba(160, 185, 215, 0.75);
  flex-wrap: wrap;
}

.meta-tag strong {
  color: rgba(190, 210, 240, 0.9);
}

.meta-separator {
  color: rgba(120, 140, 180, 0.35);
}

.compact-card-right {
  display: flex;
  align-items: center;
}

.compact-inspect-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 10px;
  background: rgba(130, 80, 255, 0.12);
  border: 1px solid rgba(130, 80, 255, 0.28);
  color: #d6c6ff;
  font-size: 0.76rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s ease;
  white-space: nowrap;
}

.compact-inspect-btn:hover {
  background: rgba(130, 80, 255, 0.25);
  border-color: rgba(130, 80, 255, 0.5);
  color: #ffffff;
  transform: translateX(2px);
  box-shadow: 0 0 12px rgba(130, 80, 255, 0.25);
}

/* ═══════════════════════ MÓDULO A: INSPECCIÓN Y ARQUITECTURA (FASE 2) ═══════════════════════ */
.module-a-gene-card {
  background: linear-gradient(155deg, rgba(8, 14, 28, 0.95), rgba(12, 20, 38, 0.92));
  border: 1px solid rgba(130, 80, 255, 0.2);
  border-radius: 16px;
  overflow: hidden;
  backdrop-filter: blur(14px);
  box-shadow: 0 6px 28px rgba(0, 0, 0, 0.3);
}

.module-a-header {
  padding: 1.25rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  background: rgba(130, 80, 255, 0.04);
  border-bottom: 1px solid rgba(130, 80, 255, 0.12);
}

.module-a-title-group {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.module-a-avatar {
  width: 38px;
  height: 38px;
  min-width: 38px;
  border-radius: 10px;
  background: linear-gradient(135deg, rgba(130, 80, 255, 0.28), rgba(200, 100, 255, 0.18));
  border: 1px solid rgba(130, 80, 255, 0.38);
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(210, 175, 255, 0.98);
  font-size: 1.05rem;
  font-weight: 700;
  box-shadow: 0 0 14px rgba(130, 80, 255, 0.18);
}

.module-a-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.module-a-title-row h3 {
  margin: 0;
  font-size: 1.02rem;
  font-weight: 600;
  color: rgba(230, 240, 255, 0.95);
}

.gene-active-pill {
  padding: 2px 10px;
  border-radius: 10px;
  background: rgba(0, 220, 200, 0.12);
  border: 1px solid rgba(0, 220, 200, 0.3);
  color: #00f0d0;
  font-size: 0.76rem;
  font-weight: 700;
}

.module-a-title-group .subtext {
  font-size: 0.78rem;
  color: rgba(160, 180, 210, 0.7);
  margin-top: 2px;
  display: block;
}

.module-a-body {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.hud-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.hud-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  color: rgba(200, 220, 255, 0.9);
}

.hud-title-row h4 {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 600;
}

/* Provenance Badge */
.provenance-badge {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 5px 12px;
  border-radius: 10px;
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  border: 1px solid;
}

.provenance-badge.curated {
  background: rgba(0, 200, 120, 0.08);
  color: rgba(80, 230, 160, 0.95);
  border-color: rgba(0, 200, 120, 0.25);
  box-shadow: 0 0 10px rgba(0, 200, 120, 0.08);
}

.provenance-badge.didactic {
  background: rgba(255, 180, 50, 0.08);
  color: rgba(255, 200, 100, 0.95);
  border-color: rgba(255, 180, 50, 0.25);
  box-shadow: 0 0 10px rgba(255, 180, 50, 0.08);
}

/* Telemetry Grid */
.hud-telemetry-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
}

.hud-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(130, 80, 255, 0.08);
  border-radius: 10px;
  transition: all 0.25s ease;
}

.hud-cell:hover {
  background: rgba(130, 80, 255, 0.05);
  border-color: rgba(130, 80, 255, 0.18);
}

.hud-label {
  font-size: 0.66rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: rgba(140, 160, 200, 0.6);
  font-weight: 600;
}

.hud-value {
  font-size: 0.82rem;
  color: rgba(220, 230, 255, 0.9);
  font-weight: 500;
}

.strand-badge.sense {
  color: rgba(80, 200, 255, 0.95);
}

.strand-badge.antisense {
  color: rgba(255, 140, 180, 0.95);
}

.genetype-badge.protein_coding {
  color: rgba(80, 230, 180, 0.95);
}

.genetype-badge.functional_rna {
  color: rgba(255, 200, 80, 0.95);
}

/* Source Bar */
.hud-source-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 8px;
  border: 1px solid rgba(130, 80, 255, 0.06);
  font-size: 0.74rem;
  color: rgba(140, 160, 200, 0.6);
}

.source-label {
  font-weight: 600;
  color: rgba(160, 180, 210, 0.75);
}

.source-value {
  color: rgba(180, 195, 220, 0.8);
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 0.72rem;
}

/* ═══════════════════════════════════════════════════════════════════════ */
/* ESTRUCTURA EXÓN / INTRÓN VISUAL STRIP                                  */
/* ═══════════════════════════════════════════════════════════════════════ */
.exon-intron-track {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.track-label-row {
  display: flex;
  align-items: center;
  gap: 6px;
  color: rgba(180, 200, 230, 0.8);
}

.track-label-row h5 {
  margin: 0;
  font-size: 0.82rem;
  font-weight: 600;
}

.structure-strip {
  display: flex;
  align-items: stretch;
  gap: 2px;
  min-height: 42px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid rgba(130, 80, 255, 0.1);
}

.strip-segment {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  padding: 6px 4px;
  min-width: 28px;
  position: relative;
  transition: all 0.3s ease;
  cursor: default;
}

.strip-segment.exon {
  background: linear-gradient(180deg, rgba(80, 200, 255, 0.18), rgba(60, 160, 220, 0.1));
  border-bottom: 2px solid rgba(80, 200, 255, 0.45);
}

.strip-segment.exon:hover {
  background: linear-gradient(180deg, rgba(80, 200, 255, 0.28), rgba(60, 160, 220, 0.18));
}

.strip-segment.intron {
  background: repeating-linear-gradient(
    90deg,
    rgba(255, 180, 50, 0.04),
    rgba(255, 180, 50, 0.04) 4px,
    transparent 4px,
    transparent 8px
  );
  border-bottom: 2px dashed rgba(255, 180, 50, 0.3);
}

.strip-segment.intron:hover {
  background: repeating-linear-gradient(
    90deg,
    rgba(255, 180, 50, 0.08),
    rgba(255, 180, 50, 0.08) 4px,
    transparent 4px,
    transparent 8px
  );
}

.seg-label {
  font-size: 0.62rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

.strip-segment.exon .seg-label {
  color: rgba(100, 210, 255, 0.9);
}

.strip-segment.intron .seg-label {
  color: rgba(255, 200, 100, 0.75);
}

.seg-coords {
  font-size: 0.58rem;
  color: rgba(160, 180, 210, 0.5);
}

.structure-legend {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 0.7rem;
  color: rgba(160, 180, 210, 0.65);
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 3px;
}

.legend-item.exon .legend-dot {
  background: rgba(80, 200, 255, 0.6);
  box-shadow: 0 0 4px rgba(80, 200, 255, 0.3);
}

.legend-item.intron .legend-dot {
  background: rgba(255, 180, 50, 0.5);
  box-shadow: 0 0 4px rgba(255, 180, 50, 0.25);
}

.legend-item.splice .legend-dot {
  background: rgba(255, 100, 130, 0.5);
  box-shadow: 0 0 4px rgba(255, 100, 130, 0.25);
}

/* CDS Preview */
.cds-preview-bar {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 10px 14px;
  background: rgba(0, 200, 180, 0.03);
  border-radius: 10px;
  border: 1px solid rgba(0, 200, 180, 0.12);
}

.cds-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.cds-label-group {
  display: flex;
  align-items: center;
  gap: 6px;
  color: rgba(0, 220, 180, 0.85);
}

.cds-label {
  font-size: 0.74rem;
  font-weight: 600;
  color: rgba(0, 220, 180, 0.9);
}

.cds-copy-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 10px;
  border-radius: 6px;
  background: rgba(0, 220, 180, 0.1);
  border: 1px solid rgba(0, 220, 180, 0.25);
  color: #00f0d0;
  font-size: 0.72rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cds-copy-btn:hover {
  background: rgba(0, 220, 180, 0.2);
  border-color: rgba(0, 220, 180, 0.45);
  color: #ffffff;
}

.cds-code {
  font-size: 0.78rem;
  color: rgba(0, 240, 200, 0.95);
  letter-spacing: 0.08em;
  word-break: break-all;
  line-height: 1.6;
  max-height: 120px;
  overflow-y: auto;
  background: rgba(0, 0, 0, 0.35);
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid rgba(0, 220, 200, 0.15);
}

/* ═══════════════════════ ROADMAP PIPELINE PREVIEW (FASE 2) ═══════════════════════ */
.phase2-pipeline-preview {
  background: linear-gradient(145deg, rgba(10, 16, 32, 0.88), rgba(14, 22, 40, 0.82));
  border: 1px dashed rgba(130, 80, 255, 0.22);
  border-radius: 16px;
  padding: 1.25rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  backdrop-filter: blur(10px);
}

.pipeline-header {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.pipeline-icon {
  color: rgba(130, 80, 255, 0.7);
}

.pipeline-text h5 {
  margin: 0;
  font-size: 0.88rem;
  font-weight: 600;
  color: rgba(210, 225, 250, 0.9);
}

.pipeline-text span {
  font-size: 0.74rem;
  color: rgba(150, 175, 210, 0.65);
  margin-top: 2px;
  display: block;
}

.pipeline-steps-preview {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.pipeline-step-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 1rem;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(130, 80, 255, 0.1);
  position: relative;
  transition: all 0.25s ease;
}

.pipeline-step-card.disabled {
  opacity: 0.65;
}

.step-num {
  width: 26px;
  height: 26px;
  border-radius: 7px;
  background: rgba(130, 80, 255, 0.15);
  border: 1px solid rgba(130, 80, 255, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.76rem;
  font-weight: 700;
  color: #cbb4ff;
}

.step-info {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.step-info strong {
  font-size: 0.82rem;
  color: rgba(220, 235, 255, 0.9);
}

.step-info span {
  font-size: 0.7rem;
  color: rgba(150, 175, 210, 0.65);
  line-height: 1.4;
}

.step-status {
  margin-top: auto;
  align-self: flex-start;
  font-size: 0.64rem;
  font-weight: 600;
  padding: 2px 7px;
  border-radius: 6px;
  background: rgba(130, 80, 255, 0.08);
  border: 1px solid rgba(130, 80, 255, 0.18);
  color: rgba(190, 175, 240, 0.7);
  letter-spacing: 0.03em;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.pipeline-step-card.active-step {
  background: linear-gradient(135deg, rgba(0, 220, 200, 0.08), rgba(0, 150, 255, 0.05));
  border-color: rgba(0, 220, 200, 0.35);
  box-shadow: 0 0 16px rgba(0, 220, 200, 0.12);
}

.pipeline-step-card.completed {
  background: linear-gradient(135deg, rgba(0, 230, 118, 0.08), rgba(0, 200, 180, 0.04));
  border-color: rgba(0, 230, 118, 0.35);
  box-shadow: 0 0 14px rgba(0, 230, 118, 0.1);
}

.pipeline-step-card.completed .step-num {
  background: rgba(0, 230, 118, 0.2);
  border-color: rgba(0, 230, 118, 0.4);
  color: #00e676;
}

.pipeline-step-card.active-step .step-num {
  background: rgba(0, 220, 200, 0.2);
  border-color: rgba(0, 220, 200, 0.45);
  color: #00f0d0;
}

.step-status.status-done {
  background: rgba(0, 230, 118, 0.12);
  border-color: rgba(0, 230, 118, 0.35);
  color: #00e676;
}

.step-status.status-current {
  background: rgba(0, 220, 200, 0.12);
  border-color: rgba(0, 220, 200, 0.35);
  color: #00f0d0;
}

/* ═══════════════════════ MÓDULO B: TRANSCRIPCIÓN (FASE 2) ═══════════════════════ */
.module-b-transcription-card {
  background: linear-gradient(155deg, rgba(8, 16, 32, 0.95), rgba(10, 24, 44, 0.92));
  border: 1px solid rgba(0, 220, 200, 0.22);
  border-radius: 16px;
  overflow: hidden;
  backdrop-filter: blur(14px);
  box-shadow: 0 6px 28px rgba(0, 0, 0, 0.3);
  margin-top: 1.25rem;
}

.module-b-header {
  padding: 1.25rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  background: rgba(0, 220, 200, 0.04);
  border-bottom: 1px solid rgba(0, 220, 200, 0.12);
  flex-wrap: wrap;
}

.module-b-title-group {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.module-b-avatar {
  width: 38px;
  height: 38px;
  min-width: 38px;
  border-radius: 10px;
  background: linear-gradient(135deg, rgba(0, 220, 200, 0.28), rgba(0, 150, 255, 0.2));
  border: 1px solid rgba(0, 220, 200, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #00f0d0;
  font-size: 1.05rem;
  font-weight: 700;
  box-shadow: 0 0 14px rgba(0, 220, 200, 0.25);
}

.module-b-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.module-b-title-row h3 {
  margin: 0;
  font-size: 1.02rem;
  font-weight: 600;
  color: rgba(230, 245, 255, 0.95);
}

.module-b-pill {
  padding: 2px 10px;
  border-radius: 10px;
  background: rgba(0, 220, 200, 0.1);
  border: 1px solid rgba(0, 220, 200, 0.25);
  color: #00f0d0;
  font-size: 0.74rem;
  font-weight: 700;
  transition: all 0.3s ease;
}

.module-b-pill.synthesized {
  background: rgba(0, 230, 118, 0.12);
  border-color: rgba(0, 230, 118, 0.35);
  color: #00e676;
}

.module-b-title-group .subtext {
  font-size: 0.78rem;
  color: rgba(160, 190, 220, 0.7);
  margin-top: 2px;
  display: block;
}

.module-b-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.transcribe-action-btn {
  background: linear-gradient(135deg, #00c4aa 0%, #0088ff 100%);
  color: #050d1a;
  font-weight: 700;
  font-size: 0.82rem;
  border: none;
  border-radius: 10px;
  padding: 8px 18px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(0, 196, 170, 0.35);
  transition: all 0.25s ease;
}

.transcribe-action-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(0, 196, 170, 0.5);
  filter: brightness(1.08);
}

.transcribe-action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.btn-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(5, 13, 26, 0.3);
  border-top-color: #050d1a;
  border-radius: 50%;
  animation: spin-transcribe 0.8s linear infinite;
}

@keyframes spin-transcribe {
  to {
    transform: rotate(360deg);
  }
}

.module-b-body {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

/* Banner Informativo Enzimático */
.enzyme-context-box {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 12px 16px;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(0, 220, 200, 0.05), rgba(0, 140, 255, 0.03));
  border: 1px solid rgba(0, 220, 200, 0.16);
}

.enzyme-icon-circle {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(0, 220, 200, 0.12);
  border: 1px solid rgba(0, 220, 200, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #00f0d0;
  flex-shrink: 0;
  margin-top: 2px;
}

.enzyme-text {
  flex: 1;
}

.enzyme-headline {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.enzyme-headline strong {
  color: #00f0d0;
  font-size: 0.88rem;
}

.enzyme-tag {
  font-size: 0.68rem;
  font-weight: 600;
  color: rgba(160, 210, 255, 0.8);
  background: rgba(0, 150, 255, 0.1);
  padding: 2px 8px;
  border-radius: 6px;
  border: 1px solid rgba(0, 150, 255, 0.2);
}

.enzyme-text p {
  margin: 4px 0 0;
  font-size: 0.78rem;
  line-height: 1.5;
  color: rgba(180, 205, 235, 0.8);
}

.enzyme-text p strong {
  color: #ffffff;
}

/* ═══════════════════════ CAJA DE INSPECCIÓN PRE-TRANSCRIPCIONAL ═══════════════════════ */
.pre-transcription-dna-box {
  background: linear-gradient(145deg, rgba(6, 12, 26, 0.92), rgba(10, 20, 38, 0.88));
  border: 1px solid rgba(0, 220, 200, 0.22);
  border-radius: 14px;
  padding: 1.25rem 1.4rem;
  display: flex;
  flex-direction: column;
  gap: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
}

.dna-buffer-header {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.dna-buffer-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.dna-buffer-title-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.dna-buffer-title-group h4 {
  margin: 0;
  font-size: 0.96rem;
  font-weight: 700;
  color: rgba(230, 245, 255, 0.95);
}

.dna-buffer-badges {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.dna-len-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 3px 10px;
  border-radius: 8px;
  background: rgba(0, 220, 200, 0.12);
  border: 1px solid rgba(0, 220, 200, 0.3);
  color: #00f0d0;
  font-size: 0.78rem;
  font-weight: 700;
}

.mold-status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 3px 10px;
  border-radius: 8px;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.mold-status-badge.intact {
  background: rgba(0, 230, 118, 0.12);
  border: 1px solid rgba(0, 230, 118, 0.35);
  color: #00e676;
}

.mold-status-badge.mutated {
  background: rgba(255, 171, 0, 0.14);
  border: 1px solid rgba(255, 171, 0, 0.45);
  color: #ffb74d;
  box-shadow: 0 0 12px rgba(255, 171, 0, 0.18);
}

.dna-buffer-notice {
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 0;
  font-size: 0.75rem;
  color: rgba(160, 190, 225, 0.75);
  line-height: 1.4;
}

.dna-buffer-sequence-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: rgba(2, 6, 16, 0.75);
  border: 1px solid rgba(0, 220, 200, 0.18);
  border-radius: 10px;
  overflow-x: auto;
}

.dna-end-label {
  color: rgba(140, 175, 210, 0.65);
  font-size: 0.8rem;
  font-weight: 800;
  flex-shrink: 0;
}

.dna-buffer-code-ribbon {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
}

.dna-char {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 28px;
  border-radius: 5px;
  font-size: 0.85rem;
  font-weight: 800;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  transition: transform 0.15s ease;
}

.dna-char:hover {
  transform: translateY(-2px);
  filter: brightness(1.2);
}

.dna-char.char-modified {
  border-color: #ff9100;
  background: rgba(255, 145, 0, 0.2);
  color: #ffb74d;
  box-shadow: 0 0 8px rgba(255, 145, 0, 0.45);
}

.dna-buffer-action-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 4px;
  flex-wrap: wrap;
}

.dna-buffer-status-text {
  font-size: 0.75rem;
  color: rgba(170, 195, 225, 0.7);
}

.sync-status {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.sync-status.text-green {
  color: #00e676;
}

.sync-status.text-dim {
  color: rgba(160, 190, 220, 0.65);
}

/* ═══════════════════════ PANEL DE ALINEAMIENTO DE 3 CARRILES ═══════════════════════ */
.transcription-alignment-panel {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.alignment-panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.alignment-title-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.alignment-icon {
  color: #00f0d0;
}

.alignment-title-group h4 {
  margin: 0;
  font-size: 0.92rem;
  font-weight: 600;
  color: rgba(225, 240, 255, 0.95);
}

.alignment-subtext {
  font-size: 0.72rem;
  color: rgba(150, 180, 215, 0.65);
  display: block;
  margin-top: 2px;
}

.alignment-window-controls {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(0, 0, 0, 0.25);
  padding: 4px 10px;
  border-radius: 8px;
  border: 1px solid rgba(0, 220, 200, 0.15);
}

.window-range-text {
  font-size: 0.74rem;
  color: #00f0d0;
}

.alignment-lanes-container {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 14px 16px;
  background: rgba(4, 10, 22, 0.8);
  border: 1px solid rgba(0, 220, 200, 0.18);
  border-radius: 12px;
  overflow-x: auto;
  box-shadow: inset 0 2px 10px rgba(0, 0, 0, 0.4);
}

.alignment-lane {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: max-content;
}

.lane-header-col {
  width: 155px;
  min-width: 155px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  position: sticky;
  left: 0;
  background: rgba(4, 10, 22, 0.95);
  padding: 4px 8px 4px 0;
  z-index: 2;
}

.lane-role-badge {
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.02em;
  padding: 2px 8px;
  border-radius: 6px;
  text-align: center;
}

.lane-role-badge.coding {
  background: rgba(80, 200, 255, 0.15);
  border: 1px solid rgba(80, 200, 255, 0.35);
  color: #70d4ff;
}

.lane-role-badge.template {
  background: rgba(180, 130, 255, 0.15);
  border: 1px solid rgba(180, 130, 255, 0.35);
  color: #caa0ff;
}

.lane-role-badge.rna {
  background: linear-gradient(135deg, rgba(0, 220, 200, 0.2), rgba(255, 150, 0, 0.15));
  border: 1px solid rgba(0, 220, 200, 0.4);
  color: #00f0d0;
}

.lane-orientation {
  font-size: 0.65rem;
  color: rgba(160, 185, 215, 0.6);
  text-align: center;
}

.connector-label,
.pol-label {
  font-size: 0.62rem;
  font-weight: 600;
  color: rgba(140, 170, 200, 0.5);
  text-align: center;
}

.pol-label {
  color: rgba(0, 220, 200, 0.75);
}

.lane-bases-track {
  display: flex;
  align-items: center;
  gap: 6px;
}

.lane-base-cell {
  width: 28px;
  height: 38px;
  min-width: 28px;
  border-radius: 7px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  position: relative;
  transition: all 0.2s ease;
}

.lane-base-cell .pos-index {
  font-size: 0.55rem;
  color: rgba(150, 175, 205, 0.5);
  line-height: 1;
  margin-bottom: 2px;
}

.lane-base-cell .base-char {
  font-size: 0.88rem;
  font-weight: 800;
  line-height: 1;
}

.lane-base-cell.base-a .base-char { color: #00e676; }
.lane-base-cell.base-t .base-char { color: #ff5252; }
.lane-base-cell.base-c .base-char { color: #40c4ff; }
.lane-base-cell.base-g .base-char { color: #ffd740; }

.lane-base-cell.in-intron {
  background: rgba(255, 171, 0, 0.08);
  border-color: rgba(255, 171, 0, 0.35);
}

/* Ribonucleótidos y Uracilo */
.lane-base-cell.rna-cell {
  background: rgba(0, 220, 200, 0.05);
  border-color: rgba(0, 220, 200, 0.2);
}

.lane-base-cell.rna-cell.is-uracil {
  background: linear-gradient(180deg, rgba(255, 145, 0, 0.22), rgba(255, 110, 0, 0.1));
  border: 1.5px solid #ff9100;
  box-shadow: 0 0 12px rgba(255, 145, 0, 0.4);
}

.lane-base-cell.rna-cell.is-uracil .base-char {
  color: #ff9d00;
  text-shadow: 0 0 8px rgba(255, 157, 0, 0.6);
}

.u-glow-dot {
  position: absolute;
  top: 3px;
  right: 3px;
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: #ff9100;
  box-shadow: 0 0 4px #ff9100;
}

/* Conectores */
.lane-connector-cell {
  width: 28px;
  min-width: 28px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.h-bond-symbol {
  font-size: 0.65rem;
  letter-spacing: -1px;
  color: rgba(140, 180, 230, 0.45);
}

.pol-arrow-cell .pol-arrow {
  color: #00f0d0;
  font-size: 0.95rem;
  font-weight: 700;
  opacity: 0.85;
}

/* Leyenda */
.alignment-legend-bar {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  padding: 6px 4px;
}

.legend-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.72rem;
  color: rgba(170, 195, 225, 0.75);
}

.legend-chip.highlight-uracil {
  color: #ffb74d;
  font-weight: 600;
}

.legend-color-dot {
  width: 9px;
  height: 9px;
  border-radius: 3px;
}

.coding-dot { background: #50c8ff; }
.template-dot { background: #b482ff; }
.uracil-dot {
  background: #ff9100;
  box-shadow: 0 0 6px rgba(255, 145, 0, 0.6);
}
.intron-dot { background: #ffb432; }

/* ═══════════════════════ HUD DE TELEMETRÍA DEL PRE-ARNM ═══════════════════════ */
.transcription-hud-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
  gap: 12px;
}

.hud-stat-card {
  background: rgba(6, 12, 26, 0.75);
  border: 1px solid rgba(0, 220, 200, 0.16);
  border-radius: 12px;
  padding: 1.1rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 6px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
}

.stat-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.74rem;
  font-weight: 600;
  color: rgba(160, 200, 235, 0.8);
}

.stat-value {
  display: flex;
  align-items: baseline;
  gap: 5px;
}

.value-number {
  font-size: 1.65rem;
  font-weight: 800;
  color: #e0f2fe;
}

.value-number.text-uracil {
  color: #ff9800;
  text-shadow: 0 0 10px rgba(255, 152, 0, 0.35);
}

.value-unit {
  font-size: 0.85rem;
  color: rgba(160, 195, 230, 0.65);
}

.stat-progress-bar {
  width: 100%;
  height: 6px;
  border-radius: 3px;
  background: rgba(255, 255, 255, 0.06);
  overflow: hidden;
  margin: 2px 0;
}

.stat-progress-fill.uracil-fill {
  height: 100%;
  background: linear-gradient(90deg, #ff9100, #ffb300);
  box-shadow: 0 0 8px rgba(255, 145, 0, 0.5);
  transition: width 0.4s ease;
}

.stat-subtext {
  font-size: 0.68rem;
  color: rgba(150, 175, 205, 0.6);
  line-height: 1.35;
}

/* Distribución ribonucleotídica */
.ribo-distribution-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 4px 0;
  flex-wrap: wrap;
}

.ribo-count-pill {
  flex: 1;
  min-width: 44px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 4px 8px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.ribo-count-pill .pill-base {
  font-size: 0.74rem;
  font-weight: 800;
}

.ribo-count-pill .pill-val {
  font-size: 0.78rem;
  font-weight: 700;
}

.ribo-count-pill.ribo-a .pill-base { color: #00e676; }
.ribo-count-pill.ribo-c .pill-base { color: #40c4ff; }
.ribo-count-pill.ribo-g .pill-base { color: #ffd740; }

.ribo-count-pill.ribo-u.highlight {
  background: rgba(255, 145, 0, 0.16);
  border-color: rgba(255, 145, 0, 0.45);
}

.ribo-count-pill.ribo-u.highlight .pill-base,
.ribo-count-pill.ribo-u.highlight .pill-val {
  color: #ff9800;
}

/* Estado del Transcrito */
.immature-status-banner {
  background: rgba(255, 145, 0, 0.1);
  border: 1px solid rgba(255, 145, 0, 0.3);
  border-radius: 8px;
  padding: 8px 10px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.immature-status-banner strong {
  font-size: 0.8rem;
  color: #ffb74d;
}

.immature-status-banner .status-detail {
  font-size: 0.7rem;
  color: rgba(255, 225, 185, 0.75);
}

.intron-flag-pill {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.68rem;
  color: #ffb74d;
  margin-top: 2px;
}

.intron-flag-pill.no-introns {
  color: #00e676;
}

/* Secuencia Completa Pre-ARNm */
.pre-mrna-sequence-box {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px 16px;
  background: rgba(4, 10, 22, 0.85);
  border: 1px solid rgba(0, 220, 200, 0.16);
  border-radius: 12px;
}

.seq-box-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.seq-box-title {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #00f0d0;
}

.pre-mrna-code {
  font-size: 0.8rem;
  letter-spacing: 0.08em;
  word-break: break-all;
  line-height: 1.6;
  max-height: 130px;
  overflow-y: auto;
  background: rgba(0, 0, 0, 0.4);
  padding: 10px 14px;
  border-radius: 8px;
  border: 1px solid rgba(0, 220, 200, 0.12);
  color: #bbf7d0;
}

.pre-mrna-code .end-tag {
  color: rgba(160, 195, 230, 0.55);
}

.pre-mrna-code .char-u {
  color: #ff9800;
  font-weight: 800;
  text-shadow: 0 0 6px rgba(255, 152, 0, 0.55);
}

/* Estado Idle (Espera) */
.transcription-idle-banner {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 2rem 1.5rem;
  border: 1px dashed rgba(0, 220, 200, 0.22);
  border-radius: 12px;
  background: rgba(0, 220, 200, 0.02);
}

.idle-icon-wrap {
  color: #00f0d0;
  opacity: 0.85;
}

.idle-text-wrap strong {
  display: block;
  font-size: 0.92rem;
  color: rgba(220, 240, 255, 0.92);
  margin-bottom: 4px;
}

.idle-text-wrap p {
  margin: 0;
  font-size: 0.78rem;
  color: rgba(160, 190, 220, 0.65);
  line-height: 1.45;
}

/* Phase 2 Empty State */
.phase2-empty-state {
  background: linear-gradient(145deg, rgba(10, 16, 32, 0.88), rgba(14, 22, 40, 0.84));
  border: 1px dashed rgba(130, 80, 255, 0.2);
  border-radius: 16px;
  padding: 3rem 2rem;
}

.empty-state-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 0.75rem;
}

.empty-icon-box {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  background: linear-gradient(135deg, rgba(0, 220, 200, 0.12), rgba(130, 80, 255, 0.15));
  border: 1px solid rgba(0, 220, 200, 0.28);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 6px;
  box-shadow: 0 0 18px rgba(0, 220, 200, 0.15);
}

.empty-icon-large {
  color: #00f0d0;
  opacity: 0.9;
}

.empty-state-content h3 {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 600;
  color: rgba(200, 210, 240, 0.8);
}

.empty-state-content p {
  margin: 0;
  font-size: 0.82rem;
  color: rgba(160, 180, 210, 0.55);
  max-width: 460px;
  line-height: 1.5;
}

/* ═══════════════════════ RESPONSIVE PHASE TABS ═══════════════════════ */
@media (max-width: 820px) {
  .pipeline-steps-preview {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .phase-tabs-nav {
    flex-direction: column;
    gap: 2px;
  }

  .phase-tab-btn {
    justify-content: flex-start;
    padding: 10px 14px;
    font-size: 0.76rem;
  }

  .tab-label {
    font-size: 0.76rem;
  }

  .hud-telemetry-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .gene-selector-row {
    flex-direction: column;
  }

  .shared-selector-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .gene-compact-card {
    flex-direction: column;
    align-items: flex-start;
  }

  .compact-card-right {
    width: 100%;
    justify-content: flex-end;
  }
}

@media (max-width: 520px) {
  .hud-telemetry-grid {
    grid-template-columns: 1fr;
  }

  .structure-strip {
    min-height: 36px;
  }

  .hud-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .module-a-header {
    flex-direction: column;
    align-items: flex-start;
  }
}

/* Estilos para el botón y modal de ADN Prueba (DnaHelix) */
.dna-test-btn {
  background: rgba(0, 210, 255, 0.12) !important;
  border-color: rgba(0, 242, 254, 0.45) !important;
  color: #7df9ff !important;
  transition: all 0.2s ease !important;
}

.dna-test-btn:hover {
  background: rgba(0, 210, 255, 0.25) !important;
  border-color: #00f2fe !important;
  color: #ffffff !important;
  box-shadow: 0 0 14px rgba(0, 242, 254, 0.35) !important;
  transform: translateY(-1px);
}

.dna-test-dialog-surface {
  width: 96vw;
  max-width: 1400px;
  height: 90vh;
  max-height: 920px;
  display: flex;
  flex-direction: column;
  padding: 0;
  overflow: hidden;
  background: #020818;
  border: 1px solid rgba(0, 210, 255, 0.35);
  box-shadow: 0 16px 50px rgba(0, 0, 0, 0.8), 0 0 30px rgba(0, 102, 255, 0.2);
}

.dna-test-model-switcher {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(3, 11, 28, 0.85);
  border: 1px solid rgba(0, 210, 255, 0.25);
  border-radius: 10px;
  padding: 4px;
}

.model-tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  font-size: 13px;
  font-weight: 500;
  border: 1px solid transparent;
  border-radius: 7px;
  background: transparent;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.2s ease;
}

.model-tab-btn:hover {
  color: #e2e8f0;
  background: rgba(255, 255, 255, 0.05);
}

.model-tab-btn.active {
  background: rgba(0, 210, 255, 0.18);
  border-color: rgba(0, 242, 254, 0.5);
  color: #ffffff;
  box-shadow: 0 0 12px rgba(0, 210, 255, 0.2);
}

.tab-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.dot-atomico {
  background: #38bdf8;
  box-shadow: 0 0 8px #38bdf8;
}

.dot-foto {
  background: #818cf8;
  box-shadow: 0 0 8px #818cf8;
}

.tab-badge {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.1);
  color: #7dd3fc;
  font-weight: 600;
}

.dna-test-dialog-body {
  flex: 1;
  width: 100%;
  height: calc(100% - 70px);
  position: relative;
  overflow: hidden;
  background: #020612;
}

.dna-model-wrapper {
  width: 100%;
  height: 100%;
  position: relative;
}

.dna-dual-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  width: 100%;
  height: 100%;
  gap: 2px;
  background: rgba(0, 210, 255, 0.15);
}

.dual-pane {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  background: #020612;
}

.dual-pane-header {
  position: absolute;
  top: 14px;
  right: 18px;
  z-index: 15;
  display: flex;
  align-items: center;
  gap: 8px;
  pointer-events: none;
}

.dual-badge {
  font-size: 11px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.atomico-badge {
  background: rgba(56, 189, 248, 0.22);
  color: #7dd3fc;
  border: 1px solid rgba(56, 189, 248, 0.45);
}

.foto-badge {
  background: rgba(129, 140, 248, 0.22);
  color: #c7d2fe;
  border: 1px solid rgba(129, 140, 248, 0.45);
}

.dual-info {
  font-size: 11px;
  color: #94a3b8;
  background: rgba(2, 6, 18, 0.75);
  padding: 4px 8px;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(4px);
}

.dual-pane-canvas {
  flex: 1;
  width: 100%;
  height: 100%;
  position: relative;
}

.dna-test-icon-badge {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: linear-gradient(135deg, rgba(0, 210, 255, 0.2), rgba(0, 102, 255, 0.4));
  border: 1px solid rgba(0, 242, 254, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #7df9ff;
}
</style>
