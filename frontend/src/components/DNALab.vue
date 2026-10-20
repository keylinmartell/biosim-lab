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
      <div class="validation-error-alert" v-if="validationData && !validationData.is_valid">
        <Icon name="warning" size="20" class="err-icon" />
        <div class="err-text">
          <strong>Secuencia no válida para el motor genético:</strong>
          <span>{{ validationData.error_message || 'Contiene caracteres no canónicos. Solo se aceptan A, T, C, G.' }}</span>
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

        <!-- Segmento Gráfico de Bases con Esqueleto Azúcar-Fosfato (5' a 3' y complementaria 3' a 5') -->
        <div class="track-viewport">
          <div class="track-polarity-col left">
            <span class="polarity-tag p5" title="Extremo 5' Fosfato libre">5' (P)</span>
            <div class="polarity-v-link"></div>
            <span class="polarity-tag p3" title="Extremo 3' Hidroxilo (-OH) complementario">3' (OH)</span>
          </div>

          <div class="bases-filmstrip">
            <div 
              v-for="(base, idx) in cleanSequence" 
              :key="idx"
              :class="['base-column', base.toLowerCase(), { selected: selectedPosition === idx }]"
              @click="selectBaseForMutation(idx, base)"
            >
              <span class="pos-index font-mono">{{ idx }}</span>

              <!-- Esqueleto Superior Azúcar-Fosfato (5' -> 3') -->
              <div class="bb-monomer top" title="Monómero 5': Fosfato (PO4) + 2'-Desoxirribosa">
                <span class="bb-dot phosphate" title="Grupo Fosfato 5' (PO4^3-)">P</span>
                <span class="bb-hyphen">—</span>
                <span class="bb-dot sugar" title="Azúcar 2'-Desoxirribosa (pentosa)">D</span>
                <div class="bb-stem-down"></div>
              </div>

              <!-- Base Nitrogenada Sentido (5' -> 3') -->
              <div class="base-capsule primary-strand" :title="`Base nitrogenada: ${base} (unida al C1' de la desoxirribosa)`">
                <span class="letter font-mono">{{ base }}</span>
              </div>

              <!-- Enlaces de Hidrógeno Watson-Crick -->
              <div class="hydrogen-bond" :title="base === 'C' || base === 'G' ? '3 puentes de hidrógeno (C≡G)' : '2 puentes de hidrógeno (A=T)'">
                <span class="h-line"></span>
                <span class="h-line"></span>
                <span class="h-line" v-if="base === 'C' || base === 'G'"></span>
              </div>

              <!-- Base Nitrogenada Complementaria (3' -> 5') -->
              <div class="base-capsule comp-strand" :title="`Base complementaria: ${complementMap[base]}`">
                <span class="letter font-mono">{{ complementMap[base] }}</span>
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
            <h3>Módulo 1: Mutagénesis y Reparación de ADN</h3>
            <span class="subtext">Modificaciones puntuales en coordenadas específicas y reparación guiada con plantilla</span>
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
              <span class="op-sub">Comprueba cómo las lesiones físicas/químicas o la intervención dirigida sobre la secuencia</span>
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
              <label>Agente Mutagénico Ambiental (Alberts cap. 5):</label>
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
            Corrige lesiones o mutaciones en la hebra molde parental utilizando la plantilla de referencia.
          </p>

          <!-- Toggle: Modo de Reparación (Control 100% vs Cinética Enzimática Real) -->
          <div class="repair-mode-toggle-row">
            <button 
              type="button" 
              :class="['sub-toggle-btn', { active: repairMode === 'stochastic' }]" 
              @click="repairMode = 'stochastic'"
              title="Modela la probabilidad de escisión enzimática in vivo según Alberts cap. 5"
            >
              <Icon name="biotech" size="15" />
              <span>Cinética Enzimática Real (Probabilístico)</span>
            </button>
            <button 
              type="button" 
              :class="['sub-toggle-btn', { active: repairMode === 'deterministic' }]" 
              @click="repairMode = 'deterministic'"
              title="Restaura la secuencia completa al 100% como control didáctico limpio"
            >
              <Icon name="verified" size="15" />
              <span>Control Asistido (100% Fiel)</span>
            </button>
          </div>

          <!-- Slider de Eficiencia Enzimática de Escisión (Solo en modo estocástico) -->
          <div class="slider-module repair-eff-slider" v-if="repairMode === 'stochastic'">
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
              <span>{{ repairMode === 'stochastic' ? 'Ejecutar Ciclo de Escisión Enzimática' : 'Reparar Molde al 100%' }}</span>
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
                    : `Se repararon ${repairResult.repaired_positions?.length || 0} lesiones. Sin embargo, ${repairResult.escaped_positions?.length || (repairResult.remaining_divergences || 0)} lesiones escaparon al reconocimiento enzimático en este ciclo. Ejecuta otro ciclo o usa control asistido.` }}
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
    <div class="audit-log-card md3-card-outlined">
      <div class="section-header">
        <div class="section-title-group">
          <Icon name="history" size="22" class="section-icon" />
          <div>
            <h3>Módulo 3: Registro de Experimentos & Trazabilidad de Operaciones</h3>
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
    </div>

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
            <span>1. Flujo del Ciclo (G1-S-G2)</span>
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
                <h4>Arquitectura Científica del Flujo Experimental (Ciclo Celular G1 → S → G2/M)</h4>
                <p>Basado en <strong>Alberts et al. (Molecular Biology of the Cell 7.ª ed. cap. 5 y 9)</strong>, <strong>Lodish et al. (9.ª ed.)</strong> y <strong>Lehninger (8.ª ed.)</strong>: La célula no copia ADN a ciegas. El control de calidad genómico avanza por puntos de control estrictos donde cada error tiene su momento biológico, causa físico-química y maquinaria de resolución especializada.</p>
              </div>
            </div>

            <!-- Mapa Visual de Transición por Fases del Ciclo Celular -->
            <div class="manual-pipeline-roadmap">
              <div class="roadmap-phase g1">
                <div class="rm-header">
                  <span class="rm-tag">FASE G1</span>
                  <h5>Vigilancia del Molde</h5>
                </div>
                <div class="rm-content">
                  <span>1. Molde Parental Inmutable</span>
                  <span class="rm-arrow">↓</span>
                  <span>2. Daño Físico-Químico / CRISPR</span>
                  <span class="rm-arrow">↓</span>
                  <span class="rm-alert">Checkpoint G1/S (Freno p53 / p21)</span>
                  <span class="rm-arrow">↓</span>
                  <span>3. Reparación Pre-Replicativa (BER/NER)</span>
                </div>
                <div class="rm-footer cleared">Punto R Despejado → Pase a Fase S</div>
              </div>

              <div class="roadmap-connector">
                <Icon name="arrow_forward" size="20" />
              </div>

              <div class="roadmap-phase s">
                <div class="rm-header">
                  <span class="rm-tag">FASE S</span>
                  <h5>Síntesis Semiconservativa</h5>
                </div>
                <div class="rm-content">
                  <span>4. Horquilla de Replicación 5'→3'</span>
                  <span class="rm-arrow">↓</span>
                  <span>Triple Filtro de Fidelidad:</span>
                  <small>• Polimerasa (~10⁻⁵)</small>
                  <small>• Proofreading 3'→5' (~10⁻⁷)</small>
                  <small>• Escaneo MMR MutS/MutL (~10⁻¹⁰)</small>
                  <span class="rm-arrow">↓</span>
                  <span>Reporte Diff de Mutaciones</span>
                </div>
                <div class="rm-footer s-done">Genoma Duplicado al 100%</div>
              </div>

              <div class="roadmap-connector">
                <Icon name="arrow_forward" size="20" />
              </div>

              <div class="roadmap-phase g2">
                <div class="rm-header">
                  <span class="rm-tag">FASE G2 / M</span>
                  <h5>Integridad Pre-Mitótica</h5>
                </div>
                <div class="rm-content">
                  <span>5. Detección Roturas Bicatenarias (DSB)</span>
                  <span class="rm-arrow">↓</span>
                  <span>Cromatida Hermana Disponible:</span>
                  <small>• Vía HDR: Fiel sin cicatriz (RAD51/BRCA)</small>
                  <small>• Vía NHEJ: Emergencia con cicatriz (Ku70/80)</small>
                </div>
                <div class="rm-footer mit-done">Aprobación para Mitosis (M)</div>
              </div>
            </div>

            <!-- Acordeón Detallado de los 5 Pasos -->
            <div class="flow-steps-accordion">
              <div class="flow-step-item">
                <div class="step-badge step-1">Paso 1</div>
                <div class="step-info">
                  <h5>Paso 1 (Fase G1): Establecimiento y Validación del Molde Parental Inmutable</h5>
                  <p>
                    <strong>Dónde ocurre:</strong> En el núcleo de la célula antes de cualquier evento de duplicación genómica.
                    <br>
                    <strong>Fundamento Biológico:</strong> En G1 la célula crece metabólicamente y cuenta únicamente con una copia de cada molécula de ADN bicatenario. La cadena ingresada en el laboratorio se establece como la <strong>plantilla parental de referencia inmutable</strong>. El motor valida reactivamente las bases nitrogenadas (A, T, C, G), calcula la longitud en pares de bases (bp), el porcentaje GC y la complementaria antiparalela Watson-Crick (5'→3' frente a 3'→5'), generando la doble hélice B-DNA tridimensional reactiva.
                  </p>
                </div>
              </div>

              <div class="flow-step-item">
                <div class="step-badge step-2">Paso 2</div>
                <div class="step-info">
                  <h5>Paso 2 (Fase G1): Detección de Daño en el Molde y Freno en G1 (Eje ATM/ATR → p53/MDM2 → p21)</h5>
                  <p>
                    <strong>Dónde y cuándo ocurre:</strong> En la doble hebra parental en Fase G1, antes de entrar a replicación.
                    <br>
                    <strong>Naturaleza de las lesiones (Módulo 1.1):</strong> En este punto <em>no son mutaciones</em>, sino <em>lesiones físicas y químicas</em> en el ADN. La mutación solo se fijará si la célula replica una lesión sin reparar en Fase S.
                    <br>
                    • <em>Radiación Ultravioleta (Luz UV):</em> Dímeros covalentes de ciclobutano entre timinas adyacentes (T-T) o citosinas (C→T), distorsionando físicamente la hélice.
                    <br>
                    • <em>Estrés Oxidativo (ROS):</em> Radicales libres del metabolismo oxidan guanina a 8-oxo-7,8-dihidroguanina (8-oxo-G), que aparea incorrectamente con adenina y genera transversiones G→T.
                    <br>
                    • <em>Desaminación Espontánea:</em> Ataque hidrolítico que transforma citosina en uracilo (U), leído como timina (transición C→T).
                    <br>
                    • <em>Herramienta Exógena CRISPR-Cas9:</em> Bisturí molecular externo (*S. pyogenes*) que crea un corte de doble cadena dirigido en una diana elegida.
                    <br>
                    <strong>Respuesta Biológica Real (Módulo 1.2):</strong> En reposo, p53 se degrada continuamente por la ubiquitina-ligasa <strong>MDM2</strong> (vida media ~20 min). Al surgir daño:
                    <br>
                    1. <em>Sensores reales:</em> Complejo <strong>MRN / ATM</strong> (roturas de doble cadena) y <strong>RPA / ATR</strong> (cadena sencilla) detectan la lesión y fosforilan a p53 (Ser15/Ser20) y a MDM2.
                    <br>
                    2. <em>Estabilización:</em> Fosforilado, p53 deja de ser reconocido por MDM2, se estabiliza, tetrameriza y actúa como factor de transcripción.
                    <br>
                    3. <em>Decisión por afinidad y dosis:</em>
                    <br>
                    • <strong>Daño leve-moderado:</strong> p53 induce promotores de alta afinidad: <strong>p21</strong> (inhibe CDK2/4/6 manteniendo a Rb hipofosforilado y secuestrando a E2F para frenar en G1) y <strong>GADD45/DDB2</strong> (favorecen BER/NER). Reparado el daño, MDM2 vuelve a degradar a p53.
                    <br>
                    • <strong>Daño masivo o persistente:</strong> p53 sostenido + Ser46/Lys120 activa promotores de baja afinidad: <strong>BAX, PUMA, NOXA</strong>, induciendo apoptosis mitocondrial.
                    <br>
                    <em>Nota sobre el Punto R:</em> El Punto R no inspecciona calidad de ADN; solo mide señales mitogénicas. El freno ante daño lo impone la vía colateral ATM/ATR → p53 → p21.
                  </p>
                </div>
              </div>

              <div class="flow-step-item">
                <div class="step-badge step-3">Paso 3</div>
                <div class="step-info">
                  <h5>Paso 3 (Fase G1): Reparación Pre-Replicativa del Molde (Módulo 1.3 - BER / NER / Homología)</h5>
                  <p>
                    <strong>Cómo se resuelve:</strong> Durante el arresto en G1, la célula activa vías de reparación por escisión:
                    <br>
                    • <em>Reparación por Escisión de Bases (BER):</em> ADN glicosilasas eliminan bases oxidadas o desaminadas (como uracilos u 8-oxo-G), una AP endonucleasa corta el esqueleto de azúcar y la ADN polimerasa β rellena el hueco guiada por la hebra complementaria intacta.
                    <br>
                    • <em>Reparación por Escisión de Nucleótidos (NER):</em> Complejos escinucleasa cortan un oligonucleótido de 24-32 bases alrededor del dímero UV distorsionado y la polimerasa sintetiza el parche.
                    <br>
                    <strong>Cinética Enzimática Real vs Control Asistido:</strong> En la célula real, las enzimas de escisión no reparan mágicamente al 100% de golpe; tienen una probabilidad de reconocimiento y pueden saturarse ante dosis elevadas. Por ello, el laboratorio incorpora el modo <em>"Cinética Enzimática Real (Probabilístico)"</em> con slider de <strong>Capacidad / Eficiencia de Escisión (50% a 98%)</strong>:
                    <br>
                    • Si alguna lesión escapa a la escisión en ese ciclo, <strong>el sensor p53 y p21 permanecen en alerta roja</strong> y el Punto R sigue bloqueado.
                    <br>
                    • La célula puede ejecutar un segundo ciclo enzimático o recurrir al <em>Control Asistido (100% Fiel)</em> para restaurar el molde al 100%, desactivando p53/p21 y autorizando el ingreso a Fase S.
                  </p>
                </div>
              </div>

              <div class="flow-step-item">
                <div class="step-badge step-4">Paso 4</div>
                <div class="step-info">
                  <h5>Paso 4 (Fase S): Duplicación Celular Semiconservativa y Triple Filtro de Fidelidad</h5>
                  <p>
                    <strong>Dónde y cuándo ocurre:</strong> En la horquilla de replicación durante la Fase S de síntesis.
                    <br>
                    <strong>Módulo 2.1:</strong> La ADN polimerasa abre la doble hélice y sintetiza la hebra hija complementaria $5'\rightarrow3'$. El usuario puede optar por <em>Copia Fiel</em> (100% de pureza) o <em>Replicación Estocástica</em> modulando la tasa de error de polimerasa mediante el slider.
                    <br>
                    <strong>El Triple Filtro Biológico de Fidelidad Celular (Alberts cap. 5):</strong>
                    <br>
                    1. <em>Selección de Base por ADN Polimerasa (~10⁻⁵):</em> La geometría del bolsillo catalítico selecciona dNTPs complementarios Watson-Crick. Tasa de error inicial: ~1 error cada 100.000 bases.
                    <br>
                    2. <em>Corrección de Pruebas ("Proofreading" ~10⁻⁷):</em> El dominio exonucleasa 3'→5' de la polimerasa retrocede y extirpa monómeros mal apareados en el extremo 3'-OH.
                    <br>
                    3. <em>Reparación de Apareamientos Incorrectos Post-Replicativo (MMR ~10⁻¹⁰):</em> Las proteínas <strong>MutS y MutL</strong> escanean la hebra recién sintetizada reconociendo desajustes (ej. pares A-G o C-T), cortan la hebra hija y la resintetizan con fidelidad perfecta.
                    <br>
                    <strong>Módulos 2.2 y 2.3:</strong> Al pulsar <strong>"Escanear Apareamientos"</strong>, el sistema señala pares canónicos y no canónicos, y el <strong>Módulo 2.3 (Diff Inspector)</strong> desglosa cada mutación por posición, tipo y base alterada.
                  </p>
                </div>
              </div>

              <div class="flow-step-item">
                <div class="step-badge step-5">Paso 5</div>
                <div class="step-info">
                  <h5>Paso 5 (Fase G2 / M): Roturas Bicatenarias (DSB) y Control Pre-Mitótico (Módulos 3.1 y 3.2)</h5>
                  <p>
                    <strong>Dónde y cuándo ocurre:</strong> En la fase G2, después de que el genoma ha sido totalmente duplicado y antes de dividirse en mitosis (M).
                    <br>
                    <strong>Módulo 3.1:</strong> Se establece la coordenada de corte de una <em>Rotura de Doble Cadena (Double-Strand Break - DSB)</em> provocada por radiación ionizante o colapso de horquillas.
                    <br>
                    <strong>Módulo 3.2 (Resolución Mecanística):</strong>
                    <br>
                    • <strong>Vía HDR (Recombinación Homóloga Asistida por Cromátida Hermana):</strong> Dado que en Fase G2 <strong>la cromátida hermana idéntica recién sintetizada en Fase S está físicamente adyacente</strong>, las nucleasas resecan los extremos 5' y la recombinasa <strong>RAD51 con BRCA1/2</strong> invade la cromátida hermana para copiar fielmente la secuencia perdida. <em>Resultado: Reconstrucción molecular pura al 100% sin dejar cicatriz.</em>
                    <br>
                    • <strong>Vía NHEJ (Unión de Extremos No Homólogos):</strong> Si no se dispone de plantilla homóloga o la lesión ocurre en emergencia, el dímero <strong>Ku70/Ku80 con DNA-PKcs y Ligasa IV</strong> unen directamente los extremos rotos a ciegas tras un recorte nucleolítico. <em>Resultado: Resolución rápida pero propensa a pérdida de bases y cicatriz mutacional (microdeleciones).</em>
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
                  <p>Limpia mutaciones, roturas y lesiones activas, restableciendo la doble hélice al estado inicial del molde parental.</p>
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
                <div class="card-tag">5. Módulo 1 · Mutagénesis, Detección y Reparación</div>
                <div class="btn-entry">
                  <span class="btn-name chip"><Icon name="wb_sunny" size="14" /> Daño Ambiental Estocástico</span>
                  <p>Activa el inductor de lesiones ambientales: Luz UV (dímeros TT), Estrés Oxidativo ROS (8-oxo-G) o Desaminación espontánea (C→U).</p>
                </div>
                <div class="btn-entry">
                  <span class="btn-name chip"><Icon name="content_cut" size="14" /> Herramienta Exógena (CRISPR-Cas9)</span>
                  <p>Modo de alteración dirigida en una posición: sustitución puntual, inserción (+1 base) o deleción (-1 base).</p>
                </div>
                <div class="btn-entry">
                  <span class="btn-name filled"><Icon name="bolt" size="14" /> Inducir Lesiones / Inducir Lesión Dirigida</span>
                  <p>Aplica la alteración sobre el molde (Módulo 1.1). El Módulo 1.2 revisa de inmediato los apareamientos.</p>
                </div>
                <div class="btn-entry">
                  <span class="btn-name chip"><Icon name="shuffle" size="14" /> Inducir Error / Complementaria</span>
                  <p>Alterna entre la complementaria exacta o inyectar deliberadamente una base no apareada para probar la detección.</p>
                </div>
                <div class="btn-entry">
                  <span class="btn-name filled"><Icon name="analytics" size="14" /> Escanear Apareamientos (Módulo 1.2)</span>
                  <p>Compara la cadena con la complementaria del molde y marca pares canónicos (verdes) y no canónicos (rojos).</p>
                </div>
                <div class="btn-entry">
                  <span class="btn-name chip"><Icon name="biotech" size="14" /> Cinética Enzimática Real vs Control Asistido</span>
                  <p>Switcher del Módulo 1.3: alterna entre reparación probabilística (puede dejar lesiones sin reparar) y reparación al 100%.</p>
                </div>
                <div class="btn-entry">
                  <span class="btn-name chip">Slider Eficiencia de Escisión (50% - 98%)</span>
                  <p>Regula la probabilidad de que cada lesión sea reparada en un ciclo.</p>
                </div>
                <div class="btn-entry">
                  <span class="btn-name tonal"><Icon name="tag" size="14" /> Usar Molde Inicial</span>
                  <p>Carga la secuencia original limpia en el campo de referencia para la reparación.</p>
                </div>
                <div class="btn-entry">
                  <span class="btn-name filled"><Icon name="build" size="14" /> Ciclo de Escisión / Reparar Molde</span>
                  <p>Ejecuta la ronda de reparación. Reporta lesiones reparadas y posiciones que escaparon.</p>
                </div>
              </div>

              <!-- Módulo 2 -->
              <div class="button-guide-card">
                <div class="card-tag">6. Módulo 2 · Reporte Diferencial</div>
                <div class="btn-entry">
                  <span class="btn-name chip">Diff Inspector (Módulo 2)</span>
                  <p>Muestra el contraste base a base entre el molde original y la secuencia modificada, con posición y tipo de cambio.</p>
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
                <li>Observa el Stepper superior en <em>"Paso 1: Molde Parental Validado"</em> y el Checkpoint G1/S en verde (Punto R despejado).</li>
                <li>En el <strong>Módulo 1.1</strong>, selecciona <em>"Daño Ambiental Estocástico"</em> y el agente <em>"Radiación Ultravioleta (Luz UV)"</em> con intensidad al 40%.</li>
                <li>Pulsa <strong>"Inducir Lesiones Ambientales en el Molde"</strong>.</li>
                <li>Observa el <strong>Módulo 1.2</strong>: El Checkpoint G1/S pasa a estado de alerta roja con p53 fosforilado y p21 activo frenando el ciclo en G1 para impedir replicar un molde lesionado.</li>
                <li>Desplázate al <strong>Módulo 1.3</strong> a la derecha, pulsa <strong>"Usar Molde Inicial"</strong>.</li>
                <li>Deja activo el modo <strong>"Cinética Enzimática Real"</strong> y ajusta la eficiencia al 75%.</li>
                <li>Pulsa <strong>"Ejecutar Ciclo de Escisión Enzimática"</strong>: comprueba cómo se reparan lesiones pero algunas escapan por saturación, manteniendo el Punto R en alerta.</li>
                <li>Pulsa de nuevo <strong>"Ejecutar Ciclo"</strong> (segunda ronda de escisión celular) o cambia a <strong>"Control Asistido"</strong>: al alcanzar el 100%, p53/p21 se inactivan y el Punto R autoriza el avance a Fase S.</li>
              </ol>
            </div>

            <div class="protocol-card">
              <div class="protocol-card-header">
                <span class="proto-tag s">Protocolo B (Fase S)</span>
                <h4>Replicación en Fase S, Filtro de Fidelidad MMR y Reporte Diff Inspector</h4>
              </div>
              <ol class="protocol-steps-list">
                <li>Con el molde reparado en G1, desplázate a la <strong>Etapa 2 (Fase S)</strong>.</li>
                <li>En el <strong>Módulo 2.1</strong>, selecciona <em>"Replicación con Error Estocástico"</em> y ajusta la tasa de error al 5.0%.</li>
                <li>Pulsa <strong>"Simular Duplicación con Error de Polimerasa"</strong>.</li>
                <li>La nueva hebra sintetizada se carga de inmediato en el <strong>Módulo 2.2</strong> (Filtro MMR Dúplex).</li>
                <li>Pulsa <strong>"Escanear Apareamientos"</strong>: comprueba las bases no canónicas detectadas por la maquinaria MutS/MutL post-horquilla.</li>
                <li>Revisa el <strong>Módulo 2.3 (Diff Inspector)</strong> para ver el desglose exacto de las sustituciones, inserciones o deleciones ocurridas en la copia.</li>
              </ol>
            </div>

            <div class="protocol-card">
              <div class="protocol-card-header">
                <span class="proto-tag g2">Protocolo C (Fase G2/M)</span>
                <h4>Roturas Bicatenarias (DSB) en G2/M y Comparación Mecanística HDR vs NHEJ</h4>
              </div>
              <ol class="protocol-steps-list">
                <li>Desplázate a la <strong>Etapa 3 (Fase G2/M)</strong> donde el genoma se encuentra completamente duplicado y cada cromosoma dispone de su cromátida hermana.</li>
                <li>En el <strong>Módulo 3.1</strong>, define el punto de rotura en la posición 4 u 8.</li>
                <li>Pulsa <strong>"Reparar vía NHEJ"</strong>: observa la ligación directa de emergencia y la aparición de la cicatriz molecular o microdeleción.</li>
                <li>Pulsa <strong>"Restaurar a Molde"</strong> en la cabecera para regresar al estado intacto.</li>
                <li>Ahora pulsa <strong>"Reparar vía HDR"</strong>: observa la reconstitución limpia y perfecta sin cicatriz, asistida por la cromátida hermana presente en G2.</li>
                <li>Pulsa el botón superior <strong>"Guardar Experimento"</strong> para registrar el ensayo completo en el <strong>Módulo 4 (Auditoría)</strong>.</li>
              </ol>
            </div>

            <div class="protocol-card">
              <div class="protocol-card-header">
                <span class="proto-tag crispr">Protocolo D (CRISPR & Auditoría)</span>
                <h4>Edición Quirúrgica CRISPR, Desfase del Marco (Frameshift) y Auditoría Inmutable</h4>
              </div>
              <ol class="protocol-steps-list">
                <li>Haz clic sobre la base en la posición 2 del <strong>Mapa de Alineamiento 2D</strong>.</li>
                <li>En el <strong>Módulo 1.1</strong>, cambia al modo <em>"Edición Quirúrgica CRISPR"</em>.</li>
                <li>Comprueba que la posición se rellenó automáticamente en 2. Selecciona tipo <em>"Inserción (+1 Base)"</em> y escoge la base <strong>"A"</strong>.</li>
                <li>Pulsa <strong>"Aplicar Mutación Dirigida CRISPR"</strong>: comprueba el desfase (frameshift) en la cadena y la alerta del sensor p53 en el Punto R.</li>
                <li>Abre el <strong>Módulo 4 (Auditoría)</strong> para comprobar la bitácora criptográfica inmutable con el registro del evento EXP.</li>
              </ol>
            </div>
          </div>

          <!-- Pestaña 4: Fundamentos, FAQ & Bibliografía -->
          <div v-if="manualActiveTab === 'faq'" class="manual-section-content">
            <div class="faq-container">
              <!-- Nueva FAQ sobre Probabilidad y Cinética de Reparación -->
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
                    3. <em>Respuesta del Checkpoint G1/S:</em> Esta es precisamente la razón de ser de <strong>p53 y p21</strong>. Si una sola lesión escapa a la escisión, el sensor p53 permanece fosforilado y retiene a la célula en G1. Si la célula no consigue limpiar el molde tras varios ciclos, p53 activa la apoptosis para evitar colapsos letales en la horquilla de replicación de Fase S.
                  </p>
                </div>
              </div>

              <div class="faq-card">
                <div class="faq-q">
                  <Icon name="help" size="18" class="q-icon" />
                  <h5>¿Por qué el laboratorio está ordenado en G1 → S → G2/M y qué pasaba con el "3.2 arriba y 3.1 abajo" de antes?</h5>
                </div>
                <div class="faq-a">
                  <p>
                    <strong>Resolución Biológica:</strong> En versiones tempranas del software existía una confusión estructural: el módulo de reparación con molde se colocó antes del escaneo de desapareamientos, pero con numeraciones desfasadas ("3.2 arriba y 3.1 abajo").
                    <br>
                    Esto era biológicamente incorrecto porque mezclaba eventos pre-replicativos con post-replicativos. En la célula real:
                    <br>
                    • <strong>Fase G1 (Módulos 1.1 a 1.3):</strong> La célula solo tiene el molde parental sin duplicar. Las lesiones son ambientales o mutagenéticas, y la célula las repara antes de replicar mediante BER/NER para no transferir el error a la descendencia.
                    <br>
                    • <strong>Fase S (Módulos 2.1 a 2.3):</strong> Ocurre la replicación activa. Aquí y solo aquí la ADN polimerasa comete errores al incorporar dNTPs en la horquilla, y actúa el filtro MMR post-replicativo.
                    <br>
                    • <strong>Fase G2/M (Módulos 3.1 y 3.2):</strong> El ADN ya se duplicó. Si hay roturas bicatenarias (DSB), la célula puede usar la cromátida hermana idéntica para hacer Recombinación Homóloga (HDR) limpia, o recurrir a NHEJ si hay emergencia.
                    <br>
                    La numeración actual refleja con precisión cristalina esta cronología biológica canónica.
                  </p>
                </div>
              </div>

              <div class="faq-card">
                <div class="faq-q">
                  <Icon name="help" size="18" class="q-icon" />
                  <h5>¿Por qué es matemáticamente imposible que un sistema repare un desapareamiento (mismatch) sin hebra molde?</h5>
                </div>
                <div class="faq-a">
                  <p>
                    <strong>Regla de Oro de la Biología Molecular:</strong> Cuando el sistema detecta un desapareamiento, por ejemplo un par erróneo <strong>A — C</strong>, físicamente ambos nucleótidos son bases químicas normales.
                    <br>
                    El complejo de reparación no tiene forma física de "adivinar" si la secuencia original era un par canónico <strong>A — T</strong> (donde la C es la equivocada) o un par canónico <strong>G — C</strong> (donde la A es la equivocada).
                    <br>
                    Por esta razón, la naturaleza utiliza marcadores epigenéticos (como hemimetilación de adeninas por la metilasa Dam en procariotas o mellas en la hebra retardada por PCNA en eucariotas) para identificar cuál es la hebra molde parental auténtica. Sin una <em>hebra molde parental o referencia homóloga</em>, el sistema tendría un 50% de probabilidad de fijar la mutación en vez de corregirla.
                  </p>
                </div>
              </div>

              <div class="faq-card">
                <div class="faq-q">
                  <Icon name="help" size="18" class="q-icon" />
                  <h5>¿Cómo logra la célula copiar 3.000 millones de nucleótidos con solo ~3 errores? (El Triple Filtro)</h5>
                </div>
                <div class="faq-a">
                  <p>
                    Basado en <strong>Alberts cap. 5</strong>: Ningún proceso químico aislado tiene la energía libre suficiente para distinguir pares de bases con una precisión de 1 en 1.000 millones. La fidelidad extrema se consigue multiplicando tres filtros probabilísticos independientes:
                    <br>
                    1. <em>Apareamiento de bases en el sitio activo de la polimerasa:</em> Error de ~1 cada 10⁵ nt.
                    <br>
                    2. <em>Corrección de pruebas exonucleolítica 3'→5' (Proofreading):</em> Reduce el error en 100 veces, alcanzando ~1 cada 10⁷ nt.
                    <br>
                    3. <em>Reparación post-replicativa de desapareamientos (MMR):</em> Las enzimas MutS/MutL rastrean distorsiones en la hebra hija y reducen el error residual en otro factor de 100 a 1.000, logrando una fidelidad global de <strong>~1 error cada 10⁹ a 10¹⁰ nucleótidos</strong>.
                  </p>
                </div>
              </div>

              <div class="faq-card">
                <div class="faq-q">
                  <Icon name="help" size="18" class="q-icon" />
                  <h5>¿Por qué la Recombinación Homóloga (HDR) solo puede operar en Fase G2/S y no en G1?</h5>
                </div>
                <div class="faq-a">
                  <p>
                    <strong>Fundamento Celular:</strong> Para que la vía HDR reconstruya una rotura de doble cadena (DSB) sin perder información, necesita una molécula de ADN idéntica que actúe como molde de copia.
                    <br>
                    En Fase G1, la célula solo dispone del cromosoma homólogo de origen materno o paterno, el cual contiene polimorfismos alélicos y no está alineado físicamente.
                    <br>
                    En contraste, tras la replicación en Fase S y durante la Fase G2, <strong>cada cromosoma dispone de su cromátida hermana perfectamente idéntica</strong>, mantenida a escasos nanómetros mediante anillos proteicos de <em>cohesina</em>. Esto permite que RAD51 y BRCA1/2 invadan la cromátida hermana y restauren el ADN con 100% de fidelidad sin cicatriz.
                  </p>
                </div>
              </div>

              <div class="faq-card">
                <div class="faq-q">
                  <Icon name="help" size="18" class="q-icon" />
                  <h5>¿Qué ocurre si la célula elude el Punto de Restricción R en G1/S sin reparar el daño?</h5>
                </div>
                <div class="faq-a">
                  <p>
                    Si el sensor <strong>p53 está mutado</strong> (la alteración genética más común en neoplasias humanas, presente en más del 50% de tumores) o la proteína p21 no se expresa, la célula ingresa a Fase S portando lesiones en el molde.
                    <br>
                    Al llegar la horquilla de replicación, la ADN polimerasa colapsa frente a los dímeros de timina o las 8-oxo-guaninas, provocando síntesis translesión altamente mutagénica, roturas cromosómicas descontroladas, aneuploidías e inestabilidad genómica masiva.
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
                    <small>• Capítulo 5: "DNA Replication, Repair, and Recombination" (mecanismos de polimerasas, MMR MutS/MutL, BER, NER, DSB, HDR y NHEJ).</small>
                    <br>
                    <small>• Capítulo 9: "The Cell Cycle" (sistema de control del ciclo celular, sensor p53, inhibidor p21, complejos Ciclina-CDK y punto de restricción G1/S).</small>
                  </li>
                  <li>
                    <strong>Lodish, H., Berk, A., Kaiser, C. A., Krieger, M., Bretscher, A., Ploegh, H., Martin, K. C., Yaffe, M. B., & Amon, A. (2021).</strong>
                    <em>Molecular Cell Biology</em> (9.ª edición). Macmillan Learning.
                    <br>
                    <small>• Capítulo 5: "Molecular Genetic Mechanisms" (fidelidad de replicación y mutagénesis).</small>
                    <br>
                    <small>• Capítulo 9: "Cell Cycle Control and Checkpoints" (regulación del punto de restricción R y respuesta al daño en el ADN).</small>
                  </li>
                  <li>
                    <strong>Nelson, D. L., & Cox, M. M. (2021).</strong>
                    <em>Lehninger Principles of Biochemistry</em> (8.ª edición). W. H. Freeman.
                    <br>
                    <small>• Capítulo 25: "DNA Metabolism: Replication, Repair, and Recombination" (estequiometría de enlaces de hidrógeno, química de la polimerización 5'→3' y termodinámica del B-DNA).</small>
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
const repairMode = ref('stochastic'); // 'stochastic' | 'deterministic'
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
const manualActiveTab = ref('flow');
const experimentNotification = ref(null);
const lastMutationApplied = ref(null);

const isFullyRepaired = computed(() => {
  return repairResult.value?.matches_reference === true || (breakResult.value?.matches_initial === true && diffResult.value?.difference_count === 0);
});

const isMoldDamaged = computed(() => {
  if (!initialMoldSequence.value) return false;
  return sequenceInput.value.trim().toUpperCase() !== initialMoldSequence.value.trim().toUpperCase();
});

const currentCellPhase = computed(() => {
  if (breakResult.value) return 'G2';
  if (copyNotification.value || (lastMutationApplied.value && lastMutationApplied.value.type === 'stochastic_replication') || (mismatchResult.value && mismatchResult.value.strand2)) return 'S';
  return 'G1';
});

const currentCellPhaseName = computed(() => {
  switch (currentCellPhase.value) {
    case 'G1': return 'Fase G1 · Molde & Checkpoint G1/S (Punto R)';
    case 'S': return 'Fase S · Replicación & Triple Filtro MMR';
    case 'G2': return 'Fase G2 / M · Integridad Post-Replicativa & DSB';
    default: return 'Fase G1';
  }
});

const checkpointG1Status = computed(() => {
  if (!cleanSequence.value || !validationData.value?.is_valid) {
    return {
      state: 'idle',
      label: 'Sin validar',
      p53: 'Basal (~20 min vida media · degradado por MDM2)',
      p21: 'Inactivo',
      decision: 'Introduce una secuencia válida de molde.',
      risk: null
    };
  }
  if (isMoldDamaged.value) {
    const isSevere = (envDamageResult.value?.lesion_count || 0) > 3;
    return {
      state: 'arrested',
      label: 'Freno en G1 por Daño al ADN',
      p53: isSevere
        ? 'Acumulación masiva + Ser46/Lys120 (Programa Apoptótico)'
        : 'Fosforilado (Ser15/Ser20) por ATM/ATR · Escapa a MDM2',
      p21: isSevere
        ? 'Rebasado por activación de BAX / PUMA / NOXA'
        : 'Transcrito e inducido (Inhibe CDK2/4/6 · Rb hipofosforilado)',
      decision: isSevere
        ? 'Daño irreparable/masivo: p53 activa promotores de baja afinidad (BAX, PUMA, NOXA), induciendo apoptosis mitocondrial para evitar replicar un genoma roto.'
        : 'Daño moderado: p53 induce p21; la célula detiene el ciclo en G1 y activa reparación por escisión BER/NER (OGG1, GADD45).',
      risk: 'El Punto R mide mitógenos; ante daño, ATM/ATR fosforilan a p53 para inducir p21 y frenar a las CDKs. La mutación no existe aún: solo se consolidará si la lesión no se repara y se replica en Fase S.'
    };
  }
  return {
    state: 'cleared',
    label: 'Molde Íntegro · Autorizado a Fase S',
    p53: 'Basal bajo (MDM2 ubiquitina y envía continuamente al proteasoma)',
    p21: 'Apagado (CDK4/6 y CDK2 activas · Rb fosforilado libera E2F)',
    decision: 'Molde libre de lesiones. MDM2 mantiene degradado a p53. Célula autorizada a cruzar a Fase S (Replicación).',
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

  validateAndProcess();

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
  const eff = repairMode.value === 'deterministic' ? 1.0 : repairEfficiency.value;
  try {
    loading.value = true;
    const res = await api.repairWithReference(current, moldRef, null, eff);
    repairResult.value = res;
    // Sincronizar siempre la secuencia resultante (sea completa o parcial)
    sequenceInput.value = res.repaired_sequence;
    await validateAndProcess();
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
    await validateAndProcess();
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
    await validateAndProcess();
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
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  background: var(--md-sys-color-surface-container-low);
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
  padding: 0.5rem 1rem;
  gap: 0.5rem;
  overflow: hidden;
}

.manual-tab-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  padding: 0.65rem 0.6rem;
  background: var(--md-sys-color-surface-container);
  border: 1px solid var(--md-sys-color-outline-variant);
  border-radius: var(--md-sys-shape-corner-small);
  color: var(--md-sys-color-on-surface-variant);
  font-size: 0.82rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  text-align: center;
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

@media (max-width: 768px) {
  .manual-tabs-bar {
    grid-template-columns: repeat(2, 1fr);
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
.proto-tag.s { background: rgba(239, 68, 68, 0.2); color: #ef4444; }
.proto-tag.g2 { background: rgba(16, 185, 129, 0.2); color: #10b981; }
.proto-tag.crispr { background: rgba(56, 189, 248, 0.2); color: #38bdf8; }

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
  grid-template-columns: 1fr auto 1fr auto 1fr;
  align-items: center;
  gap: 0.6rem;
  background: var(--md-sys-color-surface-container-lowest);
  border: 1px solid var(--md-sys-color-outline-variant);
  border-radius: var(--md-sys-shape-corner-medium);
  padding: 1rem;
}

.roadmap-phase {
  background: var(--md-sys-color-surface-container-low);
  border: 1px solid var(--md-sys-color-outline-variant);
  border-radius: var(--md-sys-shape-corner-small);
  padding: 0.85rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  min-height: 210px;
}

.roadmap-phase.g1 { border-top: 3px solid #818cf8; }
.roadmap-phase.s { border-top: 3px solid #ef4444; }
.roadmap-phase.g2 { border-top: 3px solid #10b981; }

.rm-header {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
  padding-bottom: 0.4rem;
}

.rm-tag {
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.5px;
}

.roadmap-phase.g1 .rm-tag { color: #818cf8; }
.roadmap-phase.s .rm-tag { color: #ef4444; }
.roadmap-phase.g2 .rm-tag { color: #10b981; }

.rm-header h5 {
  margin: 0;
  font-size: 0.88rem;
  color: var(--md-sys-color-on-surface);
}

.rm-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.75rem;
  color: var(--md-sys-color-on-surface-variant);
  line-height: 1.35;
}

.rm-arrow {
  text-align: center;
  color: var(--md-sys-color-outline);
  font-size: 0.7rem;
}

.rm-alert {
  color: #f59e0b;
  font-weight: 600;
}

.rm-content small {
  font-size: 0.69rem;
  color: var(--md-sys-color-outline);
}

.rm-footer {
  font-size: 0.7rem;
  font-weight: 700;
  padding: 0.3rem 0.5rem;
  border-radius: 4px;
  text-align: center;
}

.rm-footer.cleared { background: rgba(16, 185, 129, 0.15); color: #10b981; }
.rm-footer.s-done { background: rgba(56, 189, 248, 0.15); color: #38bdf8; }
.rm-footer.mit-done { background: rgba(99, 102, 241, 0.15); color: #818cf8; }

.roadmap-connector {
  color: var(--md-sys-color-outline);
  display: flex;
  align-items: center;
  justify-content: center;
}

@media (max-width: 860px) {
  .manual-pipeline-roadmap {
    grid-template-columns: 1fr;
  }
  .roadmap-connector {
    transform: rotate(90deg);
    padding: 0.2rem 0;
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

@media (max-width: 1024px) {
  .molecular-workbench-grid {
    grid-template-columns: 1fr;
  }
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
  background: #0284c7;
  color: #fff;
  border-radius: 3px;
  box-shadow: 0 0 6px rgba(2, 132, 199, 0.5);
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
.sym-badge.d { background: #0284c7; color: #fff; }
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
  background-color: var(--md-sys-color-surface-container);
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
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
  gap: 0.4rem;
  padding: 0.35rem 0.8rem;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 600;
}
.checkpoint-status-pill.cleared { background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.4); }
.checkpoint-status-pill.arrested { background: rgba(239, 68, 68, 0.15); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.4); }
.checkpoint-status-pill.idle { background: var(--md-sys-color-surface-container-high); color: var(--md-sys-color-on-surface-variant); }

.p53-checkpoint-card {
  padding: 1.1rem 1.4rem;
  border-radius: var(--md-sys-shape-corner-medium);
  border: 1px solid var(--md-sys-color-outline-variant);
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}
.p53-checkpoint-card.cleared { background: rgba(16, 185, 129, 0.05); border-color: rgba(16, 185, 129, 0.3); }
.p53-checkpoint-card.arrested { background: rgba(239, 68, 68, 0.06); border-color: rgba(239, 68, 68, 0.35); }

.checkpoint-telemetry-row {
  display: grid;
  grid-template-columns: 1fr 1fr 2fr;
  gap: 1rem;
}
@media (max-width: 900px) {
  .checkpoint-telemetry-row { grid-template-columns: 1fr; }
}
.cp-indicator-box {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}
.cp-label {
  font-size: 0.7rem;
  color: var(--md-sys-color-on-surface-variant);
  text-transform: uppercase;
}
.cp-val {
  font-size: 0.85rem;
  color: var(--md-sys-color-on-surface);
}
.cp-val.p53 { color: #38bdf8; }
.cp-val.p21 { color: #f59e0b; }
.cp-val.desc { font-weight: 500; }

.checkpoint-risk-alert {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.6rem 0.9rem;
  background: rgba(239, 68, 68, 0.12);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: var(--md-sys-shape-corner-small);
  color: #fca5a5;
  font-size: 0.78rem;
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

.sub-mode-toggle-row {
  display: flex;
  gap: 0.5rem;
  padding: 0.3rem;
  background: var(--md-sys-color-surface-container-highest);
  border-radius: var(--md-sys-shape-corner-medium);
  border: 1px solid var(--md-sys-color-outline-variant);
}

.sub-toggle-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  padding: 0.45rem 0.75rem;
  border-radius: var(--md-sys-shape-corner-small);
  border: none;
  background: transparent;
  color: var(--md-sys-color-on-surface-variant);
  font-size: 0.76rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.sub-toggle-btn:hover {
  color: var(--md-sys-color-on-surface);
}

.sub-toggle-btn.active {
  background: var(--md-sys-color-surface-container-lowest);
  color: var(--md-sys-color-primary);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(99, 102, 241, 0.35);
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
  padding: 0.75rem 0.9rem;
  background: rgba(245, 158, 11, 0.08);
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: var(--md-sys-shape-corner-small);
}

.env-tag {
  font-size: 0.76rem;
  font-weight: 700;
  color: #f59e0b;
}

.env-mechanism {
  font-size: 0.74rem;
  color: var(--md-sys-color-on-surface-variant);
  margin: 0;
  line-height: 1.35;
}

.lesions-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-top: 0.25rem;
}

.lesion-chip {
  font-size: 0.72rem;
  padding: 0.18rem 0.45rem;
  border-radius: 4px;
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.35);
  color: #ef4444;
}

/* Modos y Cinética de Reparación G1 */
.repair-mode-toggle-row {
  display: flex;
  gap: 0.5rem;
  padding: 0.3rem;
  background: var(--md-sys-color-surface-container-highest);
  border-radius: var(--md-sys-shape-corner-medium);
  border: 1px solid var(--md-sys-color-outline-variant);
  margin-bottom: 0.3rem;
}

.repair-eff-slider {
  background: rgba(56, 189, 248, 0.05);
  border: 1px solid rgba(56, 189, 248, 0.2);
  border-radius: var(--md-sys-shape-corner-small);
  padding: 0.75rem 0.9rem;
}

.highlight-repair {
  color: #38bdf8;
  font-weight: 700;
}

.repair-range::-webkit-slider-thumb {
  background: #38bdf8;
}

.escaped-lesions-box {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  padding: 0.6rem 0.8rem;
  background: rgba(245, 158, 11, 0.08);
  border: 1px solid rgba(245, 158, 11, 0.25);
  border-radius: var(--md-sys-shape-corner-small);
}

.esc-label {
  font-size: 0.74rem;
  color: #f59e0b;
  font-weight: 600;
}

.esc-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.esc-chip {
  font-size: 0.7rem;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
  background: rgba(245, 158, 11, 0.18);
  border: 1px solid rgba(245, 158, 11, 0.4);
  color: #f59e0b;
}
</style>
