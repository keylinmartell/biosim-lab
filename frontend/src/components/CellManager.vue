<template>
  <div class="cell-manager-layout">
    <!-- Header Científico del Biobanco Relacional -->
    <div class="manager-header-card md3-card-outlined">
      <div class="header-left">
        <div class="header-icon-box">
          <Icon name="dataset" size="24" />
        </div>
        <div class="header-text">
          <h2>Registro de Cepas y Células Virtuales (PostgreSQL)</h2>
          <span class="subtext">Repositorio transaccional ACID de linajes celulares, mutagénesis y árbol genealógico</span>
        </div>
      </div>

      <div class="header-actions">
        <div class="db-status-pill">
          <Icon name="storage" size="16" class="status-icon" />
          <span>BD: biosim (Conectado)</span>
        </div>
        <button class="md3-button-filled" @click="showModal = true">
          <Icon name="add" size="18" />
          <span>Registrar Nueva Célula</span>
        </button>
      </div>
    </div>

    <!-- Catálogo de Células en Grid MD3 -->
    <div class="cells-grid" v-if="cells.length > 0">
      <div v-for="c in cells" :key="c.id" class="cell-card md3-card-outlined">
        <div class="cell-card-top">
          <div class="identity-box">
            <Icon name="fingerprint" size="22" class="id-icon" />
            <div>
              <span class="cell-code font-mono">{{ c.cell_id }}</span>
              <span class="model-tag font-mono">v{{ c.model_version }}</span>
            </div>
          </div>
          <span :class="['state-badge', c.cell_state]">
            <span class="pip"></span>
            <span>{{ c.cell_state }}</span>
          </span>
        </div>

        <div class="cell-card-content">
          <div class="telemetry-row">
            <span class="t-k">Fase Ciclo Celular:</span>
            <span class="t-v phase-highlight font-mono">{{ c.cell_cycle_phase }}</span>
          </div>

          <div class="telemetry-row">
            <span class="t-k">Linaje / Generación:</span>
            <span class="t-v font-mono">{{ c.division_count }} duplicaciones</span>
          </div>

          <div class="telemetry-row genome-row" v-if="c.genomes && c.genomes.length > 0">
            <span class="t-k">Genoma Activo:</span>
            <code class="font-mono genome-tag">{{ c.genomes[c.genomes.length - 1].sequence }}</code>
          </div>
        </div>

        <div class="cell-card-actions">
          <button class="md3-button-tonal action-flex" @click="divideCell(c.cell_id)" :disabled="loading">
            <Icon name="cell_merge" size="18" />
            <span>Simular División</span>
          </button>
          <button class="md3-button-outlined action-flex" @click="selectFor3D(c)">
            <Icon name="visibility" size="18" />
            <span>Ver en 3D</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Estado Vacío (Empty State) Profesional MD3 -->
    <div v-else class="empty-state-card md3-card-outlined">
      <div class="empty-icon-box">
        <Icon name="inventory_2" size="32" />
      </div>
      <h3>No se encontraron células en la base de datos</h3>
      <p class="empty-desc">
        La base de datos relacional `biosim` está inicializada. Registra la primera muestra celular para iniciar simulaciones de ciclo y replicación.
      </p>
      <button class="md3-button-filled" @click="createDefaultCell" :disabled="loading">
        <Icon name="biotech" size="18" />
        <span>Inicializar Célula de Referencia</span>
      </button>
    </div>

    <!-- Modal Dialog MD3 para Registro de Célula -->
    <div class="md3-dialog-backdrop" v-if="showModal" @click.self="showModal = false">
      <div class="md3-dialog-container md3-card-elevated">
        <div class="dialog-header">
          <div class="dialog-icon-box">
            <Icon name="biotech" size="22" />
          </div>
          <div>
            <h3>Registrar Nueva Célula Virtual</h3>
            <span class="dialog-sub">Inserción en tabla <code>virtual_cells</code> con genoma primario</span>
          </div>
        </div>

        <div class="dialog-form">
          <div class="md3-textfield">
            <label>Identificador Único (Código de Muestra):</label>
            <input type="text" v-model="form.cell_id" placeholder="ej: CELL-BETA-02" class="font-mono" />
          </div>

          <div class="md3-textfield">
            <label>Secuencia Genómica Inicial (A, T, C, G):</label>
            <input type="text" v-model="form.initial_sequence" placeholder="ej: ATCGATCGATCG" class="font-mono" />
          </div>

          <div class="md3-textfield">
            <label>Estado Celular Fisiológico:</label>
            <select v-model="form.cell_state">
              <option value="normal">Normal (Viable)</option>
              <option value="mitosis">Mitosis (División)</option>
              <option value="apoptosis">Apoptosis (Muerte Programada)</option>
              <option value="necrosis">Necrosis (Lisis)</option>
            </select>
          </div>
        </div>

        <div class="dialog-actions">
          <button class="md3-button-outlined" @click="showModal = false">Cancelar</button>
          <button class="md3-button-filled" @click="submitCell" :disabled="loading">
            <Icon name="save" size="18" />
            <span>Guardar Registro</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { api } from '../api/client';
import Icon from './Icon.vue';

const emit = defineEmits(['selectCell']);

const cells = ref([]);
const loading = ref(false);
const showModal = ref(false);

const form = ref({
  cell_id: 'CELL-SIM-01',
  initial_sequence: 'ATCGTAGCTAGCATCG',
  cell_state: 'normal'
});

async function loadCells() {
  try {
    loading.value = true;
    cells.value = await api.listCells();
  } catch (err) {
    console.error('Error al cargar células:', err);
  } finally {
    loading.value = false;
  }
}

async function submitCell() {
  try {
    loading.value = true;
    await api.createCell(form.value.cell_id, form.value.initial_sequence, form.value.cell_state);
    showModal.value = false;
    await loadCells();
  } catch (err) {
    alert(err.message || 'Error al crear célula');
  } finally {
    loading.value = false;
  }
}

async function createDefaultCell() {
  form.value = {
    cell_id: `CELL-${Math.floor(1000 + Math.random() * 9000)}`,
    initial_sequence: 'ATCGATCGATCGATCG',
    cell_state: 'normal'
  };
  await submitCell();
}

async function divideCell(cell_id) {
  try {
    loading.value = true;
    const res = await api.divideCell(cell_id, 0.02);
    alert(`Célula ${cell_id} dividida con éxito. Generación ${res.division_count}. Mutaciones ocurridas: ${res.mutations_occurred}`);
    await loadCells();
  } catch (err) {
    alert(err.message || 'Error en la división');
  } finally {
    loading.value = false;
  }
}

function selectFor3D(cell) {
  emit('selectCell', cell);
}

onMounted(() => {
  loadCells();
});
</script>

<style scoped>
.cell-manager-layout {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

/* Header Científico */
.manager-header-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.2rem 1.6rem;
  background-color: var(--md-sys-color-surface-container);
  flex-wrap: wrap;
  gap: 1.2rem;
}

.header-left {
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

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}

.db-status-pill {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.35rem 0.75rem;
  border-radius: var(--md-sys-shape-corner-full);
  background-color: var(--md-sys-color-surface-container-high);
  border: 1px solid rgba(122, 229, 130, 0.3);
  font-size: 0.75rem;
  color: var(--md-sys-color-tertiary);
}

.status-icon {
  color: inherit;
}

/* Cells Grid */
.cells-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 1.25rem;
}

.cell-card {
  padding: 1.3rem;
  background-color: var(--md-sys-color-surface-container-low);
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.cell-card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.identity-box {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.id-icon {
  color: var(--md-sys-color-primary);
}

.cell-code {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--md-sys-color-on-surface);
  display: block;
}

.model-tag {
  font-size: 0.68rem;
  color: var(--md-sys-color-on-surface-variant);
}

.state-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.25rem 0.65rem;
  border-radius: var(--md-sys-shape-corner-full);
  font-size: 0.72rem;
  font-weight: 600;
  text-transform: capitalize;
}

.state-badge .pip {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.state-badge.normal {
  background: rgba(122, 229, 130, 0.15);
  color: var(--md-sys-color-tertiary);
  border: 1px solid rgba(122, 229, 130, 0.3);
}
.state-badge.normal .pip { background: var(--md-sys-color-tertiary); }

.state-badge.mitosis {
  background: rgba(112, 214, 255, 0.15);
  color: var(--md-sys-color-primary);
  border: 1px solid rgba(112, 214, 255, 0.3);
}
.state-badge.mitosis .pip { background: var(--md-sys-color-primary); }

.state-badge.apoptosis {
  background: rgba(192, 132, 252, 0.15);
  color: #c084fc;
  border: 1px solid rgba(192, 132, 252, 0.3);
}
.state-badge.apoptosis .pip { background: #c084fc; }

.state-badge.necrosis {
  background: rgba(255, 180, 171, 0.15);
  color: var(--md-sys-color-error);
  border: 1px solid rgba(255, 180, 171, 0.3);
}
.state-badge.necrosis .pip { background: var(--md-sys-color-error); }

.cell-card-content {
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
  background-color: var(--md-sys-color-surface-container);
  padding: 0.9rem;
  border-radius: var(--md-sys-shape-corner-small);
  border: 1px solid var(--md-sys-color-outline-variant);
}

.telemetry-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.78rem;
}

.telemetry-row .t-k {
  color: var(--md-sys-color-on-surface-variant);
}

.telemetry-row .t-v {
  color: var(--md-sys-color-on-surface);
  font-weight: 500;
}

.telemetry-row .t-v.phase-highlight {
  color: var(--md-sys-color-primary);
  font-weight: 700;
}

.genome-row {
  gap: 0.6rem;
}

.genome-tag {
  background-color: var(--md-sys-color-surface-container-highest);
  color: var(--md-sys-color-primary);
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
  font-size: 0.72rem;
  max-width: 170px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.cell-card-actions {
  display: flex;
  gap: 0.65rem;
  margin-top: auto;
}

.action-flex {
  flex: 1;
  font-size: 0.8rem;
}

/* Empty State */
.empty-state-card {
  padding: 3.5rem 2rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  background-color: var(--md-sys-color-surface-container);
}

.empty-icon-box {
  width: 60px;
  height: 60px;
  border-radius: var(--md-sys-shape-corner-large);
  background-color: var(--md-sys-color-surface-container-highest);
  color: var(--md-sys-color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-state-card h3 {
  font-size: 1.15rem;
  color: var(--md-sys-color-on-surface);
}

.empty-desc {
  font-size: 0.85rem;
  color: var(--md-sys-color-on-surface-variant);
  max-width: 480px;
}

/* MD3 Modal Dialog */
.md3-dialog-backdrop {
  position: fixed;
  inset: 0;
  background-color: rgba(4, 7, 12, 0.75);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
  padding: 1.5rem;
}

.md3-dialog-container {
  width: 100%;
  max-width: 480px;
  padding: 1.8rem;
  display: flex;
  flex-direction: column;
  gap: 1.4rem;
  border-radius: var(--md-sys-shape-corner-extra-large);
  background-color: var(--md-sys-color-surface-container-high);
}

.dialog-header {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.dialog-icon-box {
  width: 40px;
  height: 40px;
  border-radius: var(--md-sys-shape-corner-medium);
  background-color: var(--md-sys-color-primary-container);
  color: var(--md-sys-color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
}

.dialog-header h3 {
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
}

.dialog-sub {
  font-size: 0.72rem;
  color: var(--md-sys-color-on-surface-variant);
}

.dialog-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.8rem;
  margin-top: 0.5rem;
}
</style>
