<template>
  <div class="experimental-workstation md3-card-outlined">
    <!-- Header de la Estación Experimental -->
    <div class="workstation-header">
      <div class="header-left">
        <div class="header-icon-box">
          <Icon name="science" size="26" />
        </div>
        <div>
          <div class="title-with-badge">
            <h2>Modelo Experimental de Célula Madre Pluripotencial</h2>
            <span class="badge-gemini">
              <span class="sparkle">✦</span> Gemini 2.5 Flash + Motor Bioquímico
            </span>
          </div>
          <span class="subtext">
            Simulación determinista basada en <em>Molecular Biology of the Cell</em> (Alberts et al.) y guías científicas Fase 1 & 2
          </span>
        </div>
      </div>

      <!-- Live Execution Controls in Header -->
      <div class="sim-master-controls">
        <div class="speed-selector">
          <span class="ctrl-label">VELOCIDAD:</span>
          <button 
            v-for="s in speedOptions" 
            :key="s.value"
            :class="['speed-btn', { active: currentSpeed === s.value }]"
            @click="changeSpeed(s.value)"
          >
            {{ s.label }}
          </button>
        </div>

        <div class="execution-actions">
          <button 
            :class="['btn-primary-action', isRunning ? 'pause' : 'play']"
            @click="toggleRun"
          >
            <Icon :name="isRunning ? 'pause' : 'play_arrow'" size="18" />
            <span>{{ isRunning ? 'Pausar' : 'Iniciar Simulación' }}</span>
          </button>

          <button class="btn-subtle-action" @click="stepForward(3600)" title="Avanzar 1 hora">
            +1h
          </button>
          <button class="btn-subtle-action" @click="stepForward(86400)" title="Avanzar 24 horas (1 día)">
            +1 día
          </button>
          <button class="btn-subtle-action" @click="resetSimulation" title="Reiniciar experimento">
            <Icon name="restart_alt" size="18" />
          </button>
        </div>
      </div>
    </div>

    <!-- Main Experimental Workspace Grid -->
    <div class="experimental-grid">
      <!-- Columna Izquierda: Planificador IA y Parámetros Experimentales -->
      <div class="config-column">
        <!-- Tarjeta de Planificación con Gemini IA -->
        <div class="card-panel ai-planner-card">
          <div class="panel-header">
            <div class="title-row">
              <Icon name="terminal" size="18" class="text-cyan" />
              <h3>Hipótesis / Protocolo Experimental (Lenguaje Natural)</h3>
            </div>
            <span class="ai-status-pill">Gemini-2.5-Flash</span>
          </div>

          <div class="ai-input-wrapper">
            <textarea 
              v-model="aiPrompt" 
              class="ai-prompt-input"
              rows="3"
              placeholder="Ej: Célula madre sometida a 2 Gy de radiación a la hora 1 para observar si p53 induce apoptosis o reparación..."
            ></textarea>
            <button 
              class="btn-plan-gemini" 
              :disabled="isLoadingAi || !aiPrompt.trim()"
              @click="planWithGemini"
            >
              <span v-if="isLoadingAi" class="spinner-small"></span>
              <Icon v-else name="science" size="16" />
              <span>{{ isLoadingAi ? 'Interpretando Reglas con Gemini...' : 'Planificar con Gemini IA' }}</span>
            </button>
          </div>

          <!-- Presets Rápidos de 1 Clic -->
          <div class="presets-section">
            <span class="section-label">ESCENARIOS EXPERIMENTALES RÁPIDOS:</span>
            <div class="presets-grid">
              <button 
                v-for="p in presets" 
                :key="p.id" 
                :class="['preset-chip', { active: activePresetId === p.id }]"
                @click="applyPreset(p)"
                :title="p.desc"
              >
                <span class="preset-icon">{{ p.icon }}</span>
                <span class="preset-name">{{ p.name }}</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Parámetros Manuales de la Célula Madre -->
        <div class="card-panel manual-conditions-card">
          <div class="panel-header">
            <div class="title-row">
              <Icon name="tune" size="18" class="text-emerald" />
              <h3>Condiciones Iniciales del Medio & Genoma</h3>
            </div>
            <button class="btn-text-action" @click="restoreDefaults">Restablecer</button>
          </div>

          <div class="conditions-groups">
            <!-- Grupo 1: Señalización & Factores de Diferenciación -->
            <div class="param-group">
              <div class="group-title">FACTORES DE PLURIPOTENCIA & LINAJES</div>
              
              <div class="slider-row">
                <div class="slider-labels">
                  <span class="p-name">LIF / FGF2 (Mantenimiento)</span>
                  <span class="p-val">{{ conditions.LIF_o_FGF2.toFixed(2) }}</span>
                </div>
                <input type="range" min="0" max="1" step="0.05" v-model.number="conditions.LIF_o_FGF2" @change="onParamChange" />
              </div>

              <div class="slider-row">
                <div class="slider-labels">
                  <span class="p-name">Ácido Retinoico (Ectodermo)</span>
                  <span class="p-val">{{ conditions.acido_retinoico.toFixed(2) }}</span>
                </div>
                <input type="range" min="0" max="1" step="0.05" v-model.number="conditions.acido_retinoico" @change="onParamChange" />
              </div>

              <div class="slider-row">
                <div class="slider-labels">
                  <span class="p-name">Activina A / WNT (Endodermo)</span>
                  <span class="p-val">{{ conditions.ActivinaA_WNT.toFixed(2) }}</span>
                </div>
                <input type="range" min="0" max="1" step="0.05" v-model.number="conditions.ActivinaA_WNT" @change="onParamChange" />
              </div>

              <div class="slider-row">
                <div class="slider-labels">
                  <span class="p-name">BMP4 (Mesodermo / Trofo)</span>
                  <span class="p-val">{{ conditions.BMP4.toFixed(2) }}</span>
                </div>
                <input type="range" min="0" max="1" step="0.05" v-model.number="conditions.BMP4" @change="onParamChange" />
              </div>

              <div class="slider-row">
                <div class="slider-labels">
                  <span class="p-name">Mitógenos (Vía ERK → Ciclina D)</span>
                  <span class="p-val">{{ conditions.mitogenos.toFixed(2) }}</span>
                </div>
                <input type="range" min="0" max="1" step="0.05" v-model.number="conditions.mitogenos" @change="onParamChange" />
              </div>
            </div>

            <!-- Grupo 2: Factores de Estrés Físico/Químico -->
            <div class="param-group">
              <div class="group-title">ESTRÉS FÍSICO-QUÍMICO & LESIONES</div>

              <div class="slider-row">
                <div class="slider-labels">
                  <span class="p-name">Radiación Ionizante (Gy)</span>
                  <span class="p-val text-red">{{ conditions.radiacion_ionizante_Gy }} Gy</span>
                </div>
                <input type="range" min="0" max="10" step="0.5" v-model.number="conditions.radiacion_ionizante_Gy" @change="onParamChange" />
              </div>

              <div class="slider-row">
                <div class="slider-labels">
                  <span class="p-name">Estrés Oxidativo ROS</span>
                  <span class="p-val">{{ conditions.ROS.toFixed(2) }}</span>
                </div>
                <input type="range" min="0" max="1" step="0.05" v-model.number="conditions.ROS" @change="onParamChange" />
              </div>

              <div class="slider-row">
                <div class="slider-labels">
                  <span class="p-name">Radiación UV (J/m²)</span>
                  <span class="p-val">{{ conditions.UV_J_m2 }} J/m²</span>
                </div>
                <input type="range" min="0" max="50" step="5" v-model.number="conditions.UV_J_m2" @change="onParamChange" />
              </div>
            </div>

            <!-- Grupo 3: Control Genético & Bioquímica -->
            <div class="param-group">
              <div class="group-title">MECANISMOS MOLECULARES & REPORTERO</div>

              <div class="switch-row">
                <label class="switch-label">
                  <span class="switch-title">TP53 Funcional (Guardián del Genoma)</span>
                  <span class="switch-sub">Si se inactiva, la célula salta la apoptosis y el punto R</span>
                </label>
                <input type="checkbox" v-model="conditions.TP53_funcional" @change="onParamChange" class="lab-checkbox" />
              </div>

              <div class="slider-row">
                <div class="slider-labels">
                  <span class="p-name">Eficiencia Cinética Enzimática</span>
                  <span class="p-val">{{ (conditions.eficiencia_reparacion * 100).toFixed(0) }}%</span>
                </div>
                <input type="range" min="0.5" max="0.98" step="0.02" v-model.number="conditions.eficiencia_reparacion" @change="onParamChange" />
              </div>

              <div class="select-row">
                <span class="p-name">Reportero Fluorescente GFP:</span>
                <select v-model="conditions.reportero_GFP_bajo" @change="onParamChange" class="lab-select">
                  <option value="ninguno">Ninguno</option>
                  <option value="OCT4">Bajo promotor OCT4 (Pluripotencia)</option>
                  <option value="p53">Bajo promotor p53 (Estrés/Daño)</option>
                  <option value="E2F">Bajo sitios E2F (Cruce Punto R)</option>
                  <option value="PAX6">Bajo promotor PAX6 (Ectodermo)</option>
                  <option value="SOX17">Bajo promotor SOX17 (Endodermo)</option>
                  <option value="BRACHYURY">Bajo promotor BRACHYURY (Mesodermo)</option>
                </select>
              </div>
            </div>

            <!-- Intervenciones Programadas -->
            <div class="param-group">
              <div class="group-header-with-btn">
                <div class="group-title">INTERVENCIONES PROGRAMADAS (t)</div>
                <button class="btn-micro-add" @click="addInterventionPrompt">+ Añadir</button>
              </div>

              <div v-if="interventions.length === 0" class="empty-interventions">
                Sin intervenciones programadas. La célula se simulará con las condiciones basales.
              </div>
              <div v-else class="interventions-list">
                <div v-for="(it, idx) in interventions" :key="idx" class="intervention-item">
                  <div class="it-time">t = {{ formatHours(it.t_s) }}</div>
                  <div class="it-desc">{{ formatInterventionDesc(it) }}</div>
                  <button class="it-del" @click="removeIntervention(idx)" title="Eliminar">×</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Columna Central/Derecha: Visualizador Dinámico, Telemetría y Bitácora -->
      <div class="display-column">
        <!-- HUD Principal de Telemetría Celular en Vivo -->
        <div class="card-panel hud-status-card">
          <div class="hud-top-metrics">
            <!-- Metric: Tiempo Simulado -->
            <div class="hud-metric-box">
              <span class="metric-label">TIEMPO SIMULADO</span>
              <div class="metric-value time-val">{{ formattedTime }}</div>
              <span class="metric-sub">{{ totalHours.toFixed(1) }} horas / {{ (totalHours / 24).toFixed(2) }} días</span>
            </div>

            <!-- Metric: Estado Vital -->
            <div class="hud-metric-box" :class="snap.alive ? 'status-alive' : 'status-dead'">
              <span class="metric-label">ESTADO VITAL</span>
              <div class="metric-value">
                <span class="vital-indicator" :class="{ alive: snap.alive, dead: !snap.alive }"></span>
                {{ snap.alive ? 'CÉLULA VIVA' : 'APOPTOSIS' }}
              </div>
              <span class="metric-sub">{{ snap.alive ? 'Metabolismo activo' : 'Fragmentación mitocondrial' }}</span>
            </div>

            <!-- Metric: Linaje / Destino Celular -->
            <div class="hud-metric-box">
              <span class="metric-label">DESTINO CELULAR</span>
              <div class="metric-value fate-val" :class="'fate-' + snap.fate">
                {{ formatFate(snap.fate) }}
              </div>
              <span class="metric-sub">Marcador dominante</span>
            </div>

            <!-- Metric: Fase del Ciclo & Punto R -->
            <div class="hud-metric-box">
              <span class="metric-label">CICLO CELULAR</span>
              <div class="metric-value cycle-val">
                FASE {{ snap.phase }}
              </div>
              <span class="metric-sub" :class="snap.pointR ? 'text-emerald' : 'text-amber'">
                Punto R: {{ snap.pointR ? 'CRUZADO (E2F)' : 'BLOQUEADO' }}
              </span>
            </div>

            <!-- Metric: Divisiones -->
            <div class="hud-metric-box">
              <span class="metric-label">DIVISIONES (MITOSIS)</span>
              <div class="metric-value text-cyan">{{ snap.divisions }}</div>
              <span class="metric-sub">Generación clonal</span>
            </div>
          </div>
        </div>

        <!-- Canvas Visual Dinámico 2D/3D (Morfología & Fluorescencia Confocal) -->
        <div class="card-panel cell-canvas-card">
          <div class="canvas-header">
            <div class="ch-left">
              <span class="live-dot"></span>
              <span class="canvas-title">CÉLULA MADRE PLURIPOTENTE — VISUALIZACIÓN MORFOLÓGICA DINÁMICA</span>
            </div>
            <div class="ch-tags">
              <span v-if="snap.state.GFP_fluor > 0.05" class="tag-fluor gfp-active">
                GFP Fluor: {{ (snap.state.GFP_fluor * 100).toFixed(0) }}%
              </span>
              <span v-if="snap.state.dsb > 0" class="tag-fluor dsb-active">
                {{ snap.state.dsb }} Focos DSB
              </span>
              <span class="tag-fidelity">Motor Integrador: Euler dt=1s</span>
            </div>
          </div>

          <div class="canvas-viewport-container">
            <canvas ref="canvasRef" width="700" height="320" class="interactive-cell-canvas"></canvas>
            
            <!-- Overlay Informativo Flotante -->
            <div class="canvas-watermark">
              <span>OCT4: {{ (snap.state.OCT4 * 100).toFixed(0) }}%</span> | 
              <span>p53: {{ (snap.state.p53 * 100).toFixed(0) }}%</span> | 
              <span>Caspasa: {{ (snap.state.caspasa * 100).toFixed(0) }}%</span>
            </div>
          </div>
        </div>

        <!-- Modelación Tridimensional de ADN & Segmento Genómico Activo -->
        <ADNExperimental3D 
          :kb="kb"
          :cellFate="snap.fate"
          :cellPhase="snap.phase"
          :cellState="snap.state"
          :alive="snap.alive"
        />

        <!-- Panel de Biomarcadores Cuantitativos en Tiempo Real -->
        <div class="card-panel biomarkers-card">
          <div class="panel-header">
            <div class="title-row">
              <Icon name="analytics" size="18" class="text-cyan" />
              <h3>Biomarcadores Moleculares Cuantitativos en Tiempo Real</h3>
            </div>
            <div class="biomarker-tabs">
              <button 
                :class="['bio-tab', { active: activeBioTab === 'pluri' }]" 
                @click="activeBioTab = 'pluri'"
              >
                Pluripotencia & Linajes
              </button>
              <button 
                :class="['bio-tab', { active: activeBioTab === 'damage' }]" 
                @click="activeBioTab = 'damage'"
              >
                Eje p53 & Daño ADN
              </button>
              <button 
                :class="['bio-tab', { active: activeBioTab === 'cycle' }]" 
                @click="activeBioTab = 'cycle'"
              >
                Punto R & Ciclo Celular
              </button>
            </div>
          </div>

          <!-- Tab 1: Pluripotencia & Linajes -->
          <div v-show="activeBioTab === 'pluri'" class="biomarker-grid">
            <div class="bio-bar-item">
              <div class="bio-label-row">
                <span class="bio-name">OCT4 (POU5F1)</span>
                <span class="bio-val">{{ (snap.state.OCT4 * 100).toFixed(1) }}%</span>
              </div>
              <div class="bar-track">
                <div class="bar-fill pluri" :style="{ width: (snap.state.OCT4 * 100) + '%' }"></div>
              </div>
              <span class="bio-note">Factor central de pluripotencia (Boyer et al. 2005)</span>
            </div>

            <div class="bio-bar-item">
              <div class="bio-label-row">
                <span class="bio-name">SOX2</span>
                <span class="bio-val">{{ (snap.state.SOX2 * 100).toFixed(1) }}%</span>
              </div>
              <div class="bar-track">
                <div class="bar-fill pluri" :style="{ width: (snap.state.SOX2 * 100) + '%' }"></div>
              </div>
              <span class="bio-note">Heterodímero con OCT4 / Marcador neural</span>
            </div>

            <div class="bio-bar-item">
              <div class="bio-label-row">
                <span class="bio-name">NANOG</span>
                <span class="bio-val">{{ (snap.state.NANOG * 100).toFixed(1) }}%</span>
              </div>
              <div class="bar-track">
                <div class="bar-fill pluri" :style="{ width: (snap.state.NANOG * 100) + '%' }"></div>
              </div>
              <span class="bio-note">Estabilizador de estado naive pluripotente</span>
            </div>

            <div class="bio-bar-item">
              <div class="bio-label-row">
                <span class="bio-name">PAX6 (Ectodermo Neuroepitelial)</span>
                <span class="bio-val">{{ (snap.state.PAX6 * 100).toFixed(1) }}%</span>
              </div>
              <div class="bar-track">
                <div class="bar-fill ecto" :style="{ width: (snap.state.PAX6 * 100) + '%' }"></div>
              </div>
              <span class="bio-note">Inducido por Ácido Retinoico y baja de FGF2</span>
            </div>

            <div class="bio-bar-item">
              <div class="bio-label-row">
                <span class="bio-name">SOX17 (Endodermo Definitivo)</span>
                <span class="bio-val">{{ (snap.state.SOX17 * 100).toFixed(1) }}%</span>
              </div>
              <div class="bar-track">
                <div class="bar-fill endo" :style="{ width: (snap.state.SOX17 * 100) + '%' }"></div>
              </div>
              <span class="bio-note">Inducido por Activina A / WNT alta</span>
            </div>

            <div class="bio-bar-item">
              <div class="bio-label-row">
                <span class="bio-name">BRACHYURY / T (Mesodermo)</span>
                <span class="bio-val">{{ (snap.state.BRACHYURY * 100).toFixed(1) }}%</span>
              </div>
              <div class="bar-track">
                <div class="bar-fill meso" :style="{ width: (snap.state.BRACHYURY * 100) + '%' }"></div>
              </div>
              <span class="bio-note">Inducido por BMP4 + WNT moderado</span>
            </div>
          </div>

          <!-- Tab 2: Daño ADN & Vía p53 -->
          <div v-show="activeBioTab === 'damage'" class="biomarker-grid">
            <div class="bio-bar-item">
              <div class="bio-label-row">
                <span class="bio-name">p53 Activo (Fosforilado)</span>
                <span class="bio-val">{{ (snap.state.p53 * 100).toFixed(1) }}%</span>
              </div>
              <div class="bar-track">
                <div class="bar-fill p53" :style="{ width: (snap.state.p53 * 100) + '%' }"></div>
              </div>
              <span class="bio-note">Basal bajo (~20m vida media por MDM2); estabilizado por ATM</span>
            </div>

            <div class="bio-bar-item">
              <div class="bio-label-row">
                <span class="bio-name">MDM2 (E3 Ubiquitina Ligasa)</span>
                <span class="bio-val">{{ (snap.state.MDM2 * 100).toFixed(1) }}%</span>
              </div>
              <div class="bar-track">
                <div class="bar-fill mdm2" :style="{ width: (Math.min(snap.state.MDM2, 1) * 100) + '%' }"></div>
              </div>
              <span class="bio-note">Bucle de retroalimentación negativa que degrada a p53</span>
            </div>

            <div class="bio-bar-item">
              <div class="bio-label-row">
                <span class="bio-name">p21 (CDKN1A — Freno del Ciclo)</span>
                <span class="bio-val">{{ (snap.state.p21 * 100).toFixed(1) }}%</span>
              </div>
              <div class="bar-track">
                <div class="bar-fill p21" :style="{ width: (Math.min(snap.state.p21, 1) * 100) + '%' }"></div>
              </div>
              <span class="bio-note">Inhibe CDK2/4/6 bloqueando el cruce de Punto R</span>
            </div>

            <div class="bio-bar-item">
              <div class="bio-label-row">
                <span class="bio-name">PUMA / BAX (Pro-Apoptosis)</span>
                <span class="bio-val">{{ ((snap.state.PUMA + snap.state.BAX) * 50).toFixed(1) }}%</span>
              </div>
              <div class="bar-track">
                <div class="bar-fill apop" :style="{ width: (Math.min(snap.state.PUMA + snap.state.BAX, 2) * 50) + '%' }"></div>
              </div>
              <span class="bio-note">Activación de baja afinidad por p53 alto y sostenido</span>
            </div>

            <div class="bio-bar-item">
              <div class="bio-label-row">
                <span class="bio-name">Roturas de Doble Cadena (DSB)</span>
                <span class="bio-val text-red">{{ snap.state.dsb }} roturas</span>
              </div>
              <div class="bar-track">
                <div class="bar-fill dsb-bar" :style="{ width: Math.min(snap.state.dsb * 1.5, 100) + '%' }"></div>
              </div>
              <span class="bio-note">Recluta complejo MRN y ATM quinasa (~35 DSB/Gy)</span>
            </div>

            <div class="bio-bar-item">
              <div class="bio-label-row">
                <span class="bio-name">Caspasas Ejecutoras (3/7)</span>
                <span class="bio-val" :class="{ 'text-red': snap.state.caspasa > 0.5 }">{{ (snap.state.caspasa * 100).toFixed(1) }}%</span>
              </div>
              <div class="bar-track">
                <div class="bar-fill caspase" :style="{ width: (snap.state.caspasa * 100) + '%' }"></div>
              </div>
              <span class="bio-note">Liberación de Citocromo c → Apoptosoma → Muerte Celular</span>
            </div>
          </div>

          <!-- Tab 3: Punto R & Ciclo Celular -->
          <div v-show="activeBioTab === 'cycle'" class="biomarker-grid">
            <div class="bio-bar-item">
              <div class="bio-label-row">
                <span class="bio-name">Ciclina D (Mitogénica)</span>
                <span class="bio-val">{{ (snap.state.ciclinaD * 100).toFixed(1) }}%</span>
              </div>
              <div class="bar-track">
                <div class="bar-fill cycle" :style="{ width: (Math.min(snap.state.ciclinaD, 1) * 100) + '%' }"></div>
              </div>
              <span class="bio-note">Dependiente de factores de crecimiento y vía MAPK</span>
            </div>

            <div class="bio-bar-item">
              <div class="bio-label-row">
                <span class="bio-name">Rb Fosforilado (RbP)</span>
                <span class="bio-val">{{ (snap.state.RbP * 100).toFixed(1) }}%</span>
              </div>
              <div class="bar-track">
                <div class="bar-fill rbp" :style="{ width: (snap.state.RbP * 100) + '%' }"></div>
              </div>
              <span class="bio-note">Umbral Punto R: > 70% libera irreversiblemente a E2F</span>
            </div>

            <div class="bio-bar-item">
              <div class="bio-label-row">
                <span class="bio-name">E2F Libre / Ciclina E</span>
                <span class="bio-val">{{ (snap.state.E2F * 100).toFixed(1) }}%</span>
              </div>
              <div class="bar-track">
                <div class="bar-fill e2f" :style="{ width: (snap.state.E2F * 100) + '%' }"></div>
              </div>
              <span class="bio-note">Bucle biestable que autoriza el ingreso a Fase S</span>
            </div>

            <div class="bio-bar-item">
              <div class="bio-label-row">
                <span class="bio-name">GFP Madurado (Reportero)</span>
                <span class="bio-val">{{ (snap.state.GFP_fluor * 100).toFixed(1) }}%</span>
              </div>
              <div class="bar-track">
                <div class="bar-fill gfp-fluor" :style="{ width: (Math.min(snap.state.GFP_fluor, 1) * 100) + '%' }"></div>
              </div>
              <span class="bio-note">Cinética de maduración cromófora (~1 hora de retraso)</span>
            </div>
          </div>
        </div>

        <!-- Bitácora Científica en Tiempo Real (Reglas R01-R17) -->
        <div class="card-panel log-panel-card">
          <div class="panel-header">
            <div class="title-row">
              <Icon name="history" size="18" class="text-amber" />
              <h3>Trazabilidad de Reglas Biológicas Disparadas (R01..R17)</h3>
            </div>
            <span class="log-count">{{ simLog.length }} eventos registrados</span>
          </div>

          <div class="log-scroll-area">
            <div v-if="simLog.length === 0" class="empty-log">
              Inicia la simulación para registrar eventos y reglas moleculares.
            </div>
            <div 
              v-for="(ev, idx) in recentLogReversed" 
              :key="idx" 
              class="log-entry-row"
            >
              <span class="log-timestamp">{{ formatHours(ev.t) }}</span>
              <span class="log-rule-badge" :class="'rule-' + ev.rule">{{ ev.rule }}</span>
              <span class="log-msg">{{ ev.msg }}</span>
            </div>
          </div>
        </div>

        <!-- Plan Esperado y Fundamento Bibliográfico de la Base de Conocimiento -->
        <div v-if="currentPlan" class="card-panel kb-summary-card">
          <div class="panel-header">
            <div class="title-row">
              <Icon name="menu_book" size="18" class="text-cyan" />
              <h3>Metadatos Científicos del Experimento (Base de Conocimiento)</h3>
            </div>
            <span class="version-tag">Modelo: {{ currentPlan.model_version }}</span>
          </div>

          <div class="plan-details-content">
            <div class="detail-row">
              <span class="d-label">Hipótesis / Resultado Esperado:</span>
              <ul class="d-list">
                <li v-for="(exp, i) in currentPlan.expected" :key="i">{{ exp }}</li>
              </ul>
            </div>

            <div class="detail-row">
              <span class="d-label">Reglas Biológicas Aplicadas:</span>
              <div class="rules-chips">
                <span v-for="r in currentPlan.rules_used" :key="r" class="rule-chip">{{ r }}</span>
              </div>
            </div>

            <div class="detail-row">
              <span class="d-label">Fuentes Bibliográficas Centrales:</span>
              <div class="sources-list">
                <span class="source-tag">Alberts et al., Molecular Biology of the Cell (NCBI Bookshelf)</span>
                <span class="source-tag">Jackson & Bartek, Nature 2009 (Respuesta Daño ATM/p53)</span>
                <span class="source-tag">Boyer et al., Cell 2005 (Red Pluripotencia OCT4/SOX2/NANOG)</span>
                <span class="source-tag">Levine & Oren, Nat Rev Cancer 2009 (Eje p53-MDM2)</span>
              </div>
            </div>

            <div v-if="currentPlan.warnings && currentPlan.warnings.length" class="warnings-box">
              <Icon name="warning" size="16" class="text-amber" />
              <span>Avisos de validación: {{ currentPlan.warnings.join('; ') }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue';
import Icon from './Icon.vue';
import { api } from '../api/client';
import { CellSimulation } from '../sim/engine';
import ADNExperimental3D from './ADNExperimental3D.vue';

// --- Estado Base ---
const kb = ref(null);
const currentPlan = ref(null);
let sim = null;

const isRunning = ref(false);
const isLoadingAi = ref(false);
const aiPrompt = ref('Célula madre expuesta a 2 Gy de radiación ionizante a la hora 1 para evaluar activación de p53 y parada de ciclo.');
const activePresetId = ref('radiation_2gy');
const activeBioTab = ref('pluri');
const currentSpeed = ref(600); // 600 segundos simulados por segundo real

const speedOptions = [
  { label: '60x (1m/s)', value: 60 },
  { label: '600x (10m/s)', value: 600 },
  { label: '3600x (1h/s)', value: 3600 },
  { label: '14400x (4h/s)', value: 14400 },
];

// Snapshot reactivo de la célula en simulación
const snap = reactive({
  t: 0,
  phase: 'G1',
  fate: 'pluripotente',
  alive: true,
  pointR: false,
  divisions: 0,
  state: {
    OCT4: 1.0, SOX2: 1.0, NANOG: 0.8,
    PAX6: 0, BRACHYURY: 0, SOX17: 0, CDX2: 0,
    p53: 0.05, MDM2: 0.3, p21: 0.02, PUMA: 0.01, BAX: 0.1, caspasa: 0,
    ciclinaD: 0.3, ciclinaE: 0.1, RbP: 0.2, E2F: 0.2,
    dsb: 0, lesiones_oxidativas: 0, ATM: 0,
    GFP: 0, GFP_fluor: 0, GADD45: 0.05
  }
});

const simLog = ref([]);
const canvasRef = ref(null);
let animFrameId = null;

// Condiciones experimentales editables
const conditions = reactive({
  medio: 'mantenimiento_pluripotencia',
  LIF_o_FGF2: 1.0,
  BMP4: 0.0,
  ActivinaA_WNT: 0.0,
  acido_retinoico: 0.0,
  mitogenos: 0.8,
  ROS: 0.05,
  radiacion_ionizante_Gy: 0.0,
  UV_J_m2: 0.0,
  oxigeno_pct: 5.0,
  eficiencia_reparacion: 0.90,
  TP53_funcional: true,
  reportero_GFP_bajo: 'ninguno'
});

const interventions = ref([]);

// Presets Experimentales Listos
const presets = [
  {
    id: 'control_stem',
    name: 'Control Célula Madre',
    icon: '🟢',
    desc: 'Medio de mantenimiento basal con LIF/FGF2. Sin daño. Autoactivación de OCT4/SOX2/NANOG y divisiones periódicas.',
    conditions: { LIF_o_FGF2: 1.0, acido_retinoico: 0.0, ActivinaA_WNT: 0.0, BMP4: 0.0, radiacion_ionizante_Gy: 0.0, TP53_funcional: true, reportero_GFP_bajo: 'OCT4' },
    interventions: [],
    expected: 'Mantenimiento indefinido del estado pluripotente y división celular aproximadamente cada 16h.'
  },
  {
    id: 'radiation_2gy',
    name: 'Radiación 2 Gy (Daño Agudo)',
    icon: '⚡',
    desc: 'Pulso de radiación que genera ~70 roturas de doble cadena (DSB). ATM fosforila a p53.',
    conditions: { LIF_o_FGF2: 1.0, acido_retinoico: 0.0, ActivinaA_WNT: 0.0, BMP4: 0.0, radiacion_ionizante_Gy: 2.0, TP53_funcional: true, reportero_GFP_bajo: 'p53' },
    interventions: [{ t_s: 3600, type: 'pulso_radiacion', params: { Gy: 2.0 } }],
    expected: 'Fosforilación rápida de ATM y p53 en Ser15/20. En PSC el umbral de apoptosis es menor: muerte celular programada.'
  },
  {
    id: 'tp53_knockout_radiation',
    name: 'Mutante TP53-/- + 4 Gy',
    icon: '🧬',
    desc: 'Célula con mutación nula en TP53 expuesta a alta radiación. Falla la apoptosis y el arresto.',
    conditions: { LIF_o_FGF2: 1.0, acido_retinoico: 0.0, ActivinaA_WNT: 0.0, BMP4: 0.0, radiacion_ionizante_Gy: 4.0, TP53_funcional: false, reportero_GFP_bajo: 'E2F' },
    interventions: [{ t_s: 3600, type: 'pulso_radiacion', params: { Gy: 4.0 } }],
    expected: 'Ausencia de respuesta apoptótica mediada por p53; arresto anómalo en G2 o bypass aberrante con daño.'
  },
  {
    id: 'diff_ectoderm',
    name: 'Diferenciación Ectodermo',
    icon: '🧠',
    desc: 'Retiro de FGF2 y agregado de Ácido Retinoico para activar linaje neuroectodérmico.',
    conditions: { LIF_o_FGF2: 0.0, acido_retinoico: 1.0, ActivinaA_WNT: 0.0, BMP4: 0.0, radiacion_ionizante_Gy: 0.0, TP53_funcional: true, reportero_GFP_bajo: 'PAX6' },
    interventions: [],
    expected: 'Caída de OCT4 y NANOG; inducción rápida del factor de transcripción neural PAX6.'
  },
  {
    id: 'diff_endoderm',
    name: 'Diferenciación Endodermo',
    icon: '🫁',
    desc: 'Adición de alta Activina A / WNT para especificar endodermo definitivo.',
    conditions: { LIF_o_FGF2: 0.0, acido_retinoico: 0.0, ActivinaA_WNT: 1.0, BMP4: 0.0, radiacion_ionizante_Gy: 0.0, TP53_funcional: true, reportero_GFP_bajo: 'SOX17' },
    interventions: [],
    expected: 'Diferenciación hacia endodermo con activación de SOX17 y extinción de pluripotencia.'
  },
  {
    id: 'diff_mesoderm',
    name: 'Diferenciación Mesodermo',
    icon: '🫀',
    desc: 'Señalización combinada de BMP4 y WNT para inducir mesodermo temprano.',
    conditions: { LIF_o_FGF2: 0.0, acido_retinoico: 0.0, ActivinaA_WNT: 0.4, BMP4: 0.8, radiacion_ionizante_Gy: 0.0, TP53_funcional: true, reportero_GFP_bajo: 'BRACHYURY' },
    interventions: [],
    expected: 'Inducción del marcador mesodérmico BRACHYURY (gen T).'
  },
  {
    id: 'crispr_cut',
    name: 'Corte Dirigido CRISPR',
    icon: '✂️',
    desc: 'Bisturí molecular externo que introduce una rotura de doble cadena (DSB) en un locus específico.',
    conditions: { LIF_o_FGF2: 1.0, acido_retinoico: 0.0, ActivinaA_WNT: 0.0, BMP4: 0.0, radiacion_ionizante_Gy: 0.0, TP53_funcional: true, reportero_GFP_bajo: 'p53' },
    interventions: [{ t_s: 1800, type: 'CRISPR_corte', params: { gen: 'TP53', reparacion: 'NHEJ' } }],
    expected: 'DSB única dirigida; intento de reparación por unión no homóloga de extremos (NHEJ).'
  }
];

// Computeds
const totalHours = computed(() => snap.t / 3600);

const formattedTime = computed(() => {
  const s = snap.t;
  const d = Math.floor(s / 86400);
  const h = Math.floor((s % 86400) / 3600);
  const m = Math.floor((s % 3600) / 60);
  const sec = Math.floor(s % 60);
  return `${d}d ${h.toString().padStart(2, '0')}h ${m.toString().padStart(2, '0')}m ${sec.toString().padStart(2, '0')}s`;
});

const recentLogReversed = computed(() => {
  return [...simLog.value].reverse().slice(0, 15);
});

// Helpers
function formatHours(seconds) {
  const h = seconds / 3600;
  return `${h.toFixed(1)}h`;
}

function formatFate(fate) {
  switch (fate) {
    case 'pluripotente': return 'Pluripotente (ESC/iPSC)';
    case 'ectodermo': return 'Ectodermo (Neuroectodermo)';
    case 'mesodermo': return 'Mesodermo (Cardíaco/Muscular)';
    case 'endodermo': return 'Endodermo (Gastro/Respiratorio)';
    case 'trofectodermo': return 'Trofectodermo';
    case 'apoptosis': return 'Muerte por Apoptosis';
    case 'transicion': return 'Transición de Linaje';
    default: return fate;
  }
}

function formatInterventionDesc(it) {
  if (it.type === 'pulso_radiacion') return `Pulso Radiación ${it.params?.Gy || 0} Gy`;
  if (it.type === 'CRISPR_corte') return `Corte CRISPR en ${it.params?.gen || 'Locus'} (${it.params?.reparacion || 'NHEJ'})`;
  if (it.type === 'anadir_factor') return `Adición de ${it.params?.factor} = ${it.params?.nivel}`;
  if (it.type === 'retirar_factor') return `Retiro de factor ${it.params?.factor}`;
  return it.type;
}

// Inicialización de la Base de Conocimiento y Simulación
async function initKB() {
  try {
    const data = await api.getSimulationKB();
    kb.value = data;
    applyPreset(presets[1]); // Default: 2 Gy
  } catch (err) {
    console.warn('No se pudo obtener KB del backend, usando modo directo:', err);
    // Fallback mínimo
    kb.value = {
      version: 'kb-0.1.0',
      model_version: 'biosim-fase2-pluri-0.1',
      time: { default_dt_s: 1, default_speed_sim_s_per_real_s: 600 },
      thresholds: {
        p53_apoptosis: { value: 0.7 },
        p53_sustained_s: { value: 14400 },
        psc_apoptosis_factor: { value: 0.7 },
        rb_point_r: { value: 0.7 },
        dsb_per_Gy: { value: 35 },
        lineage_commit: { value: 0.45 }
      },
      initial_cell: {
        state: {
          OCT4: 1.0, SOX2: 1.0, NANOG: 0.8,
          PAX6: 0, BRACHYURY: 0, SOX17: 0, CDX2: 0,
          p53: 0.05, MDM2: 0.3, p21: 0.02, PUMA: 0.01, BAX: 0.1, caspasa: 0,
          ciclinaD: 0.3, ciclinaE: 0.1, RbP: 0.2, E2F: 0.2,
          dsb: 0, lesiones_oxidativas: 0, ATM: 0,
          GFP: 0, GFP_fluor: 0
        }
      },
      genes: {
        TP53: { product: 'p53', protein_half_life_s: 1200 },
        MDM2: { product: 'MDM2', protein_half_life_s: 1500 },
        CDKN1A: { product: 'p21', protein_half_life_s: 3600 },
        BBC3: { product: 'PUMA', protein_half_life_s: 7200 },
        BAX: { product: 'BAX', protein_half_life_s: 36000 },
        CCND1: { product: 'ciclinaD', protein_half_life_s: 1800 },
        CCNE1: { product: 'ciclinaE', protein_half_life_s: 1800 },
        GFP: { product: 'GFP', protein_half_life_s: 93600, maturation_s: 3600 }
      }
    };
    applyPreset(presets[1]);
  }
}

// Iniciar nueva simulación con las condiciones actuales
function startSimulationInstance() {
  if (sim) {
    sim.stop();
  }

  const plan = {
    model_version: kb.value?.model_version || 'biosim-fase2-pluri-0.1',
    conditions: { ...conditions },
    interventions: [...interventions.value],
    duration_s: 86400 * 5, // 5 días de simulación
    expected: currentPlan.value?.expected || ['Simulación celular en curso.'],
    rules_used: currentPlan.value?.rules_used || ['R01', 'R02', 'R03', 'R04', 'R05', 'R06', 'R07', 'R08']
  };

  sim = new CellSimulation(kb.value, plan, { seed: 42 });
  sim.setSpeed(currentSpeed.value);
  
  sim.on((snapshot) => {
    Object.assign(snap, snapshot);
    simLog.value = sim.log;
    drawCellVisual();
  });

  // Snapshot inicial
  Object.assign(snap, sim.snapshot());
  simLog.value = sim.log;
  drawCellVisual();
}

function toggleRun() {
  if (!sim) {
    startSimulationInstance();
  }

  if (isRunning.value) {
    sim.stop();
    isRunning.value = false;
  } else {
    sim.start();
    isRunning.value = true;
  }
}

function changeSpeed(speed) {
  currentSpeed.value = speed;
  if (sim) {
    sim.setSpeed(speed);
  }
}

function stepForward(simSeconds) {
  if (!sim) {
    startSimulationInstance();
  }
  sim.advance(simSeconds);
}

function resetSimulation() {
  if (sim) {
    sim.stop();
  }
  isRunning.value = false;
  startSimulationInstance();
}

// Planificador Gemini IA
async function planWithGemini() {
  if (!aiPrompt.value.trim()) return;
  isLoadingAi.value = true;

  try {
    const result = await api.planExperiment(aiPrompt.value);
    currentPlan.value = result;

    // Actualizar condiciones con las interpretadas por Gemini
    if (result.conditions) {
      Object.assign(conditions, result.conditions);
    }
    if (result.interventions) {
      interventions.value = [...result.interventions];
    }

    activePresetId.value = null;
    resetSimulation();
  } catch (err) {
    console.error('Error al planificar con Gemini:', err);
    alert('Error al conectar con el planificador Gemini: ' + (err.message || 'Verifica el backend'));
  } finally {
    isLoadingAi.value = false;
  }
}

// Aplicar Preset
function applyPreset(p) {
  activePresetId.value = p.id;
  Object.assign(conditions, p.conditions);
  interventions.value = JSON.parse(JSON.stringify(p.interventions));
  aiPrompt.value = p.desc;
  currentPlan.value = {
    titulo: p.name,
    model_version: kb.value?.model_version || 'biosim-fase2-pluri-0.1',
    expected: [p.expected],
    rules_used: ['R01', 'R02', 'R03', 'R04', 'R05', 'R06', 'R07', 'R08'],
    sources_used: ['ALB_BGM', 'ALB_DNA_RNA', 'ALB_CGE', 'COLAB']
  };

  resetSimulation();
}

function restoreDefaults() {
  applyPreset(presets[0]);
}

function onParamChange() {
  activePresetId.value = null;
  resetSimulation();
}

function addInterventionPrompt() {
  const type = prompt('Tipo de intervención:\n1 = pulso_radiacion\n2 = CRISPR_corte\n3 = anadir_factor', '1');
  if (type === '1') {
    const t_h = parseFloat(prompt('¿A qué hora del experimento (en horas)?', '2') || '2');
    const gy = parseFloat(prompt('¿Dosis de radiación (Gy)?', '2.0') || '2.0');
    interventions.value.push({
      t_s: t_h * 3600,
      type: 'pulso_radiacion',
      params: { Gy: gy }
    });
  } else if (type === '2') {
    const t_h = parseFloat(prompt('¿A qué hora (en horas)?', '1') || '1');
    const gen = prompt('¿Gen diana para corte?', 'TP53') || 'TP53';
    interventions.value.push({
      t_s: t_h * 3600,
      type: 'CRISPR_corte',
      params: { gen, reparacion: 'NHEJ' }
    });
  } else if (type === '3') {
    const t_h = parseFloat(prompt('¿A qué hora (en horas)?', '4') || '4');
    const factor = prompt('¿Qué factor añadir? (acido_retinoico, BMP4, ActivinaA_WNT)', 'acido_retinoico');
    const nivel = parseFloat(prompt('¿Nivel relativo (0.0 a 1.0)?', '1.0') || '1.0');
    interventions.value.push({
      t_s: t_h * 3600,
      type: 'anadir_factor',
      params: { factor, nivel }
    });
  }
  interventions.value.sort((a, b) => a.t_s - b.t_s);
  resetSimulation();
}

function removeIntervention(idx) {
  interventions.value.splice(idx, 1);
  resetSimulation();
}

// Canvas Visualizador 2D de Morfología Celular
function drawCellVisual() {
  const canvas = canvasRef.value;
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const w = canvas.width;
  const h = canvas.height;

  ctx.clearRect(0, 0, w, h);

  // Fondo citológico oscuro
  const bgGrad = ctx.createRadialGradient(w / 2, h / 2, 20, w / 2, h / 2, w / 1.5);
  bgGrad.addColorStop(0, '#0f1826');
  bgGrad.addColorStop(1, '#070a10');
  ctx.fillStyle = bgGrad;
  ctx.fillRect(0, 0, w, h);

  // Cuadrícula óptica confocal
  ctx.strokeStyle = 'rgba(71, 85, 105, 0.15)';
  ctx.lineWidth = 1;
  const gridSize = 40;
  for (let x = 0; x < w; x += gridSize) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, h);
    ctx.stroke();
  }
  for (let y = 0; y < h; y += gridSize) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(w, y);
    ctx.stroke();
  }

  const cx = w / 2;
  const cy = h / 2;
  const state = snap.state;
  const fate = snap.fate;
  const alive = snap.alive;

  // Radio y forma base
  let cellRadius = 85;
  if (snap.phase === 'M') cellRadius = 95; // Hinchamiento premitótico

  // 1. Halo de Fluorescencia GFP si el reportero está activo
  if (state.GFP_fluor > 0.02) {
    const gfpGrad = ctx.createRadialGradient(cx, cy, 20, cx, cy, cellRadius * 1.6);
    gfpGrad.addColorStop(0, `rgba(74, 222, 128, ${Math.min(state.GFP_fluor * 0.7, 0.6)})`);
    gfpGrad.addColorStop(1, 'rgba(74, 222, 128, 0)');
    ctx.fillStyle = gfpGrad;
    ctx.beginPath();
    ctx.arc(cx, cy, cellRadius * 1.6, 0, Math.PI * 2);
    ctx.fill();
  }

  // 2. Halo de Pluripotencia (Azul cian / turquesa)
  if (state.OCT4 > 0.4 && alive) {
    const pluriGrad = ctx.createRadialGradient(cx, cy, 30, cx, cy, cellRadius * 1.4);
    pluriGrad.addColorStop(0, `rgba(112, 214, 255, ${state.OCT4 * 0.35})`);
    pluriGrad.addColorStop(1, 'rgba(112, 214, 255, 0)');
    ctx.fillStyle = pluriGrad;
    ctx.beginPath();
    ctx.arc(cx, cy, cellRadius * 1.4, 0, Math.PI * 2);
    ctx.fill();
  }

  // 3. Membrana Celular con Deformación según Estado / Linaje
  ctx.save();
  ctx.beginPath();

  if (!alive) {
    // Apoptosis: Blebbing extremo / fragmentación
    const numBlebs = 14;
    for (let i = 0; i <= numBlebs; i++) {
      const angle = (i / numBlebs) * Math.PI * 2;
      const rMod = cellRadius * (0.6 + 0.35 * Math.sin(angle * 5 + snap.t * 0.05));
      const px = cx + Math.cos(angle) * rMod;
      const py = cy + Math.sin(angle) * rMod;
      if (i === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    }
    ctx.closePath();
    ctx.fillStyle = 'rgba(147, 0, 10, 0.55)';
    ctx.strokeStyle = '#ef4444';
    ctx.lineWidth = 3;
    ctx.fill();
    ctx.stroke();
  } else if (fate === 'ectodermo') {
    // Ectodermo: Proyecciones neuríticas radiales
    const spikes = 10;
    for (let i = 0; i <= spikes; i++) {
      const angle = (i / spikes) * Math.PI * 2;
      const rMod = (i % 2 === 0) ? cellRadius * 1.35 : cellRadius * 0.75;
      const px = cx + Math.cos(angle) * rMod;
      const py = cy + Math.sin(angle) * rMod;
      if (i === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    }
    ctx.closePath();
    ctx.fillStyle = 'rgba(168, 85, 247, 0.35)';
    ctx.strokeStyle = '#c084fc';
    ctx.lineWidth = 2.5;
    ctx.fill();
    ctx.stroke();
  } else if (fate === 'endodermo' || fate === 'mesodermo') {
    // Endodermo / Mesodermo: Morfología ovalada epitelial extendida
    ctx.ellipse(cx, cy, cellRadius * 1.25, cellRadius * 0.85, Math.PI / 6, 0, Math.PI * 2);
    ctx.fillStyle = fate === 'endodermo' ? 'rgba(234, 179, 8, 0.35)' : 'rgba(239, 68, 68, 0.35)';
    ctx.strokeStyle = fate === 'endodermo' ? '#facc15' : '#f87171';
    ctx.lineWidth = 2.5;
    ctx.fill();
    ctx.stroke();
  } else {
    // Pluripotente: Colonia compacta lisa esférica
    ctx.arc(cx, cy, cellRadius, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(15, 76, 129, 0.45)';
    ctx.strokeStyle = '#70d6ff';
    ctx.lineWidth = 2.5;
    ctx.fill();
    ctx.stroke();
  }
  ctx.restore();

  // 4. Núcleo Celular (Fluorescencia DAPI Azul)
  const nucleusR = alive ? cellRadius * 0.45 : cellRadius * 0.25; // Condensación nuclear si apoptosis
  const nucGrad = ctx.createRadialGradient(cx, cy, 5, cx, cy, nucleusR);
  if (alive) {
    nucGrad.addColorStop(0, '#60a5fa');
    nucGrad.addColorStop(0.7, '#2563eb');
    nucGrad.addColorStop(1, '#1e3a8a');
  } else {
    // Picnosis (núcleo condensado y fragmentado)
    nucGrad.addColorStop(0, '#f87171');
    nucGrad.addColorStop(1, '#7f1d1d');
  }

  ctx.beginPath();
  ctx.arc(cx, cy, nucleusR, 0, Math.PI * 2);
  ctx.fillStyle = nucGrad;
  ctx.fill();
  ctx.strokeStyle = alive ? 'rgba(147, 197, 253, 0.8)' : '#ef4444';
  ctx.lineWidth = 1.5;
  ctx.stroke();

  // 5. Focos de Daño al ADN (Roturas de Doble Cadena - DSB)
  const dsbCount = Math.min(state.dsb, 25);
  if (dsbCount > 0) {
    ctx.fillStyle = '#ef4444';
    for (let i = 0; i < dsbCount; i++) {
      const angle = (i / dsbCount) * Math.PI * 2 + i * 1.3;
      const dist = (nucleusR * 0.7) * Math.sin(i * 99 + 1);
      const fx = cx + Math.cos(angle) * dist;
      const fy = cy + Math.sin(angle) * dist;
      ctx.beginPath();
      ctx.arc(fx, fy, 2.5, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  // 6. Si está en Mitosis (Fase M), dibujar surco de división
  if (snap.phase === 'M' && alive) {
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.85)';
    ctx.setLineDash([4, 4]);
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(cx, cy - cellRadius * 1.1);
    ctx.lineTo(cx, cy + cellRadius * 1.1);
    ctx.stroke();
    ctx.setLineDash([]);
  }
}

onMounted(() => {
  initKB();
  drawCellVisual();
});

onUnmounted(() => {
  if (sim) {
    sim.stop();
  }
  if (animFrameId) {
    cancelAnimationFrame(animFrameId);
  }
});
</script>

<style scoped>
.experimental-workstation {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  padding: 1.5rem;
  background-color: var(--md-sys-color-surface-container-lowest);
  border-radius: var(--md-sys-shape-corner-large);
  border: 1px solid var(--md-sys-color-outline-variant);
  min-height: calc(100vh - 120px);
}

/* Header */
.workstation-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 1.25rem;
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
  flex-wrap: wrap;
  gap: 1rem;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-icon-box {
  width: 48px;
  height: 48px;
  border-radius: var(--md-sys-shape-corner-medium);
  background: linear-gradient(135deg, rgba(112, 214, 255, 0.2), rgba(122, 229, 130, 0.1));
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--md-sys-color-primary);
  border: 1px solid rgba(112, 214, 255, 0.3);
}

.title-with-badge {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.workstation-header h2 {
  font-size: 1.35rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
}

.badge-gemini {
  font-size: 0.72rem;
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  background: linear-gradient(90deg, rgba(112, 214, 255, 0.15), rgba(122, 229, 130, 0.15));
  color: var(--md-sys-color-primary);
  border: 1px solid rgba(112, 214, 255, 0.35);
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.subtext {
  font-size: 0.82rem;
  color: var(--md-sys-color-on-surface-variant);
}

/* Master Controls */
.sim-master-controls {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  flex-wrap: wrap;
}

.speed-selector {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  background: var(--md-sys-color-surface-container);
  padding: 0.25rem 0.5rem;
  border-radius: var(--md-sys-shape-corner-small);
  border: 1px solid var(--md-sys-color-outline-variant);
}

.ctrl-label {
  font-size: 0.68rem;
  font-weight: 700;
  color: var(--md-sys-color-on-surface-variant);
  margin-right: 0.25rem;
}

.speed-btn {
  background: transparent;
  border: none;
  color: var(--md-sys-color-on-surface-variant);
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  border-radius: var(--md-sys-shape-corner-extra-small);
  cursor: pointer;
  transition: all 0.15s ease;
}

.speed-btn:hover {
  color: var(--md-sys-color-on-surface);
  background: rgba(255, 255, 255, 0.05);
}

.speed-btn.active {
  background: var(--md-sys-color-primary);
  color: var(--md-sys-color-on-primary);
  font-weight: 600;
}

.execution-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-primary-action {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.55rem 1rem;
  border-radius: var(--md-sys-shape-corner-small);
  border: none;
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary-action.play {
  background: var(--md-sys-color-primary);
  color: var(--md-sys-color-on-primary);
}

.btn-primary-action.pause {
  background: #f59e0b;
  color: #000;
}

.btn-subtle-action {
  background: var(--md-sys-color-surface-container);
  border: 1px solid var(--md-sys-color-outline-variant);
  color: var(--md-sys-color-on-surface);
  padding: 0.5rem 0.75rem;
  border-radius: var(--md-sys-shape-corner-small);
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-subtle-action:hover {
  background: var(--md-sys-color-surface-container-high);
  border-color: var(--md-sys-color-primary);
}

/* Grid Layout */
.experimental-grid {
  display: grid;
  grid-template-columns: 420px 1fr;
  gap: 1.25rem;
}

@media (max-width: 1200px) {
  .experimental-grid {
    grid-template-columns: 1fr;
  }
}

/* Panels */
.card-panel {
  background: var(--md-sys-color-surface-container-low);
  border: 1px solid var(--md-sys-color-outline-variant);
  border-radius: var(--md-sys-shape-corner-medium);
  padding: 1.15rem;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.title-row h3 {
  font-size: 0.92rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
}

/* AI Planner */
.ai-planner-card {
  border-left: 3px solid var(--md-sys-color-primary);
}

.ai-status-pill {
  font-size: 0.7rem;
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
  background: rgba(112, 214, 255, 0.1);
  color: var(--md-sys-color-primary);
  border: 1px solid rgba(112, 214, 255, 0.25);
  font-family: var(--md-ref-typeface-mono);
}

.ai-input-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.ai-prompt-input {
  width: 100%;
  background: var(--md-sys-color-surface-container-lowest);
  border: 1px solid var(--md-sys-color-outline);
  color: var(--md-sys-color-on-surface);
  border-radius: var(--md-sys-shape-corner-small);
  padding: 0.65rem;
  font-family: inherit;
  font-size: 0.85rem;
  resize: vertical;
}

.ai-prompt-input:focus {
  outline: none;
  border-color: var(--md-sys-color-primary);
  box-shadow: 0 0 0 2px rgba(112, 214, 255, 0.2);
}

.btn-plan-gemini {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  background: linear-gradient(135deg, #0284c7, #0ea5e9);
  color: #fff;
  border: none;
  padding: 0.6rem;
  border-radius: var(--md-sys-shape-corner-small);
  font-weight: 600;
  font-size: 0.82rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-plan-gemini:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-plan-gemini:hover:not(:disabled) {
  filter: brightness(1.1);
}

.spinner-small {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Presets */
.presets-section {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  margin-top: 0.25rem;
}

.section-label {
  font-size: 0.68rem;
  font-weight: 700;
  color: var(--md-sys-color-on-surface-variant);
  letter-spacing: 0.05em;
}

.presets-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.4rem;
}

.preset-chip {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  background: var(--md-sys-color-surface-container);
  border: 1px solid var(--md-sys-color-outline-variant);
  color: var(--md-sys-color-on-surface);
  padding: 0.45rem 0.6rem;
  border-radius: var(--md-sys-shape-corner-small);
  font-size: 0.75rem;
  cursor: pointer;
  text-align: left;
  transition: all 0.15s ease;
}

.preset-chip:hover {
  background: var(--md-sys-color-surface-container-high);
  border-color: var(--md-sys-color-primary);
}

.preset-chip.active {
  background: rgba(112, 214, 255, 0.15);
  border-color: var(--md-sys-color-primary);
  color: var(--md-sys-color-primary);
  font-weight: 600;
}

/* Manual Conditions */
.manual-conditions-card {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.conditions-groups {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.param-group {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.group-title {
  font-size: 0.7rem;
  font-weight: 700;
  color: var(--md-sys-color-on-surface-variant);
  letter-spacing: 0.05em;
}

.group-header-with-btn {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.btn-micro-add {
  font-size: 0.7rem;
  padding: 0.15rem 0.5rem;
  background: var(--md-sys-color-surface-container-high);
  border: 1px solid var(--md-sys-color-outline);
  color: var(--md-sys-color-primary);
  border-radius: var(--md-sys-shape-corner-extra-small);
  cursor: pointer;
}

.slider-row {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
}

.p-name {
  color: var(--md-sys-color-on-surface);
}

.p-val {
  font-family: var(--md-ref-typeface-mono);
  font-weight: 600;
}

input[type="range"] {
  width: 100%;
  accent-color: var(--md-sys-color-primary);
  cursor: pointer;
}

.switch-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.switch-label {
  display: flex;
  flex-direction: column;
}

.switch-title {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
}

.switch-sub {
  font-size: 0.68rem;
  color: var(--md-sys-color-on-surface-variant);
}

.lab-checkbox {
  width: 18px;
  height: 18px;
  accent-color: var(--md-sys-color-primary);
  cursor: pointer;
}

.select-row {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.lab-select {
  background: var(--md-sys-color-surface-container-lowest);
  border: 1px solid var(--md-sys-color-outline);
  color: var(--md-sys-color-on-surface);
  padding: 0.45rem;
  border-radius: var(--md-sys-shape-corner-extra-small);
  font-size: 0.78rem;
}

.empty-interventions {
  font-size: 0.72rem;
  color: var(--md-sys-color-on-surface-variant);
  font-style: italic;
  padding: 0.4rem 0;
}

.interventions-list {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.intervention-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--md-sys-color-surface-container);
  padding: 0.35rem 0.6rem;
  border-radius: var(--md-sys-shape-corner-extra-small);
  font-size: 0.75rem;
}

.it-time {
  font-family: var(--md-ref-typeface-mono);
  color: var(--md-sys-color-primary);
  font-weight: 600;
}

.it-del {
  background: transparent;
  border: none;
  color: #ef4444;
  font-size: 1rem;
  cursor: pointer;
  line-height: 1;
}

/* Columna Derecha / Telemetría */
.display-column {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.hud-top-metrics {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 0.85rem;
}

@media (max-width: 900px) {
  .hud-top-metrics {
    grid-template-columns: repeat(2, 1fr);
  }
}

.hud-metric-box {
  background: var(--md-sys-color-surface-container);
  border: 1px solid var(--md-sys-color-outline-variant);
  padding: 0.75rem;
  border-radius: var(--md-sys-shape-corner-small);
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.metric-label {
  font-size: 0.65rem;
  font-weight: 700;
  color: var(--md-sys-color-on-surface-variant);
  letter-spacing: 0.05em;
}

.metric-value {
  font-size: 1.05rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.time-val {
  font-family: var(--md-ref-typeface-mono);
  color: #70d6ff;
  font-size: 0.95rem;
}

.vital-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.vital-indicator.alive {
  background: #22c55e;
  box-shadow: 0 0 8px #22c55e;
}

.vital-indicator.dead {
  background: #ef4444;
  box-shadow: 0 0 8px #ef4444;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.status-dead {
  border-color: rgba(239, 68, 68, 0.4);
  background: rgba(239, 68, 68, 0.08);
}

.metric-sub {
  font-size: 0.68rem;
  color: var(--md-sys-color-on-surface-variant);
}

/* Canvas Viewport */
.cell-canvas-card {
  padding: 0.85rem;
}

.canvas-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.ch-left {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.live-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #22c55e;
  box-shadow: 0 0 6px #22c55e;
}

.canvas-title {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--md-sys-color-on-surface-variant);
  letter-spacing: 0.05em;
}

.ch-tags {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.tag-fluor {
  font-size: 0.68rem;
  padding: 0.15rem 0.45rem;
  border-radius: var(--md-sys-shape-corner-extra-small);
  font-weight: 600;
}

.tag-fluor.gfp-active {
  background: rgba(74, 222, 128, 0.2);
  color: #4ade80;
  border: 1px solid rgba(74, 222, 128, 0.4);
}

.tag-fluor.dsb-active {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.4);
}

.tag-fidelity {
  font-size: 0.65rem;
  color: var(--md-sys-color-on-surface-variant);
  font-family: var(--md-ref-typeface-mono);
}

.canvas-viewport-container {
  position: relative;
  width: 100%;
  border-radius: var(--md-sys-shape-corner-small);
  overflow: hidden;
  border: 1px solid var(--md-sys-color-outline-variant);
}

.interactive-cell-canvas {
  width: 100%;
  height: 320px;
  display: block;
}

.canvas-watermark {
  position: absolute;
  bottom: 8px;
  right: 12px;
  background: rgba(0, 0, 0, 0.65);
  padding: 0.25rem 0.6rem;
  border-radius: var(--md-sys-shape-corner-extra-small);
  font-size: 0.7rem;
  font-family: var(--md-ref-typeface-mono);
  color: var(--md-sys-color-on-surface-variant);
  backdrop-filter: blur(4px);
}

/* Biomarkers */
.biomarker-tabs {
  display: flex;
  gap: 0.35rem;
}

.bio-tab {
  background: var(--md-sys-color-surface-container);
  border: 1px solid var(--md-sys-color-outline-variant);
  color: var(--md-sys-color-on-surface-variant);
  padding: 0.3rem 0.6rem;
  border-radius: var(--md-sys-shape-corner-small);
  font-size: 0.72rem;
  cursor: pointer;
  transition: all 0.15s ease;
}

.bio-tab.active {
  background: var(--md-sys-color-primary);
  color: var(--md-sys-color-on-primary);
  font-weight: 600;
}

.biomarker-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.85rem;
}

@media (max-width: 900px) {
  .biomarker-grid {
    grid-template-columns: 1fr;
  }
}

.bio-bar-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  background: var(--md-sys-color-surface-container);
  padding: 0.6rem 0.75rem;
  border-radius: var(--md-sys-shape-corner-small);
  border: 1px solid rgba(255, 255, 255, 0.04);
}

.bio-label-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
}

.bio-name {
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
}

.bio-val {
  font-family: var(--md-ref-typeface-mono);
  font-weight: 700;
}

.bar-track {
  width: 100%;
  height: 6px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 999px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 999px;
  transition: width 0.15s linear;
}

.bar-fill.pluri { background: #38bdf8; }
.bar-fill.ecto { background: #c084fc; }
.bar-fill.endo { background: #facc15; }
.bar-fill.meso { background: #f87171; }
.bar-fill.p53 { background: #f59e0b; }
.bar-fill.mdm2 { background: #94a3b8; }
.bar-fill.p21 { background: #fb923c; }
.bar-fill.apop { background: #ef4444; }
.bar-fill.dsb-bar { background: #dc2626; }
.bar-fill.caspase { background: #e11d48; }
.bar-fill.cycle { background: #10b981; }
.bar-fill.rbp { background: #06b6d4; }
.bar-fill.e2f { background: #3b82f6; }
.bar-fill.gfp-fluor { background: #22c55e; }

.bio-note {
  font-size: 0.65rem;
  color: var(--md-sys-color-on-surface-variant);
  line-height: 1.2;
}

/* Log Panel */
.log-panel-card {
  max-height: 240px;
}

.log-count {
  font-size: 0.72rem;
  color: var(--md-sys-color-on-surface-variant);
  font-family: var(--md-ref-typeface-mono);
}

.log-scroll-area {
  overflow-y: auto;
  max-height: 180px;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  padding-right: 0.35rem;
}

.log-entry-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-size: 0.75rem;
  padding: 0.25rem 0.4rem;
  border-radius: var(--md-sys-shape-corner-extra-small);
  background: rgba(255, 255, 255, 0.02);
}

.log-timestamp {
  font-family: var(--md-ref-typeface-mono);
  color: var(--md-sys-color-primary);
  font-size: 0.7rem;
  min-width: 45px;
}

.log-rule-badge {
  font-size: 0.65rem;
  font-weight: 700;
  padding: 0.1rem 0.35rem;
  border-radius: var(--md-sys-shape-corner-extra-small);
  background: var(--md-sys-color-surface-container-high);
  color: var(--md-sys-color-on-surface);
}

.rule-R01 { color: #f87171; border: 1px solid rgba(248, 113, 113, 0.3); }
.rule-R02 { color: #fbbf24; border: 1px solid rgba(251, 191, 36, 0.3); }
.rule-R03 { color: #34d399; border: 1px solid rgba(52, 211, 153, 0.3); }
.rule-R04 { color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); }
.rule-R07 { color: #60a5fa; border: 1px solid rgba(96, 165, 250, 0.3); }
.rule-R08 { color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); }
.rule-R17 { color: #ec4899; border: 1px solid rgba(236, 72, 153, 0.3); }

.log-msg {
  color: var(--md-sys-color-on-surface);
  flex: 1;
}

.empty-log {
  font-size: 0.75rem;
  color: var(--md-sys-color-on-surface-variant);
  font-style: italic;
  padding: 0.5rem;
}

/* Metadata Card */
.kb-summary-card {
  background: rgba(15, 21, 33, 0.6);
}

.version-tag {
  font-size: 0.7rem;
  font-family: var(--md-ref-typeface-mono);
  color: var(--md-sys-color-primary);
}

.plan-details-content {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  font-size: 0.78rem;
}

.d-label {
  font-weight: 600;
  color: var(--md-sys-color-on-surface-variant);
  display: block;
  margin-bottom: 0.2rem;
}

.d-list {
  padding-left: 1.2rem;
  color: var(--md-sys-color-on-surface);
}

.rules-chips, .sources-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.rule-chip {
  background: var(--md-sys-color-surface-container-high);
  color: var(--md-sys-color-primary);
  font-size: 0.68rem;
  font-weight: 600;
  padding: 0.15rem 0.45rem;
  border-radius: var(--md-sys-shape-corner-extra-small);
}

.source-tag {
  background: var(--md-sys-color-surface-container);
  color: var(--md-sys-color-on-surface-variant);
  font-size: 0.68rem;
  padding: 0.15rem 0.45rem;
  border-radius: var(--md-sys-shape-corner-extra-small);
  border: 1px solid var(--md-sys-color-outline-variant);
}

.warnings-box {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(245, 158, 11, 0.1);
  color: #fbbf24;
  padding: 0.5rem;
  border-radius: var(--md-sys-shape-corner-small);
  border: 1px solid rgba(245, 158, 11, 0.25);
  font-size: 0.75rem;
}

/* Utilities */
.text-cyan { color: #38bdf8; }
.text-emerald { color: #34d399; }
.text-amber { color: #fbbf24; }
.text-red { color: #ef4444; }
.btn-text-action {
  background: transparent;
  border: none;
  color: var(--md-sys-color-primary);
  font-size: 0.75rem;
  cursor: pointer;
}
</style>
