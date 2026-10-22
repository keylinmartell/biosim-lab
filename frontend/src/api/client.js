// Cliente API para comunicar Vue 3 con FastAPI / Supabase
const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

async function request(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const res = await fetch(url, config);
    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      throw new Error(errorData.detail || `Error HTTP ${res.status}`);
    }
    return await res.json();
  } catch (err) {
    console.error(`Error en peticion ${url}:`, err);
    throw err;
  }
}

export const api = {
  // DNA Engine
  validateDNA: (sequence) => request('/dna/validate', {
    method: 'POST',
    body: JSON.stringify({ sequence }),
  }),

  complementDNA: (sequence) => request('/dna/complement', {
    method: 'POST',
    body: JSON.stringify({ sequence }),
  }),

  mutateControlled: (sequence, mutation_type, position, new_base = null) => request('/dna/mutate', {
    method: 'POST',
    body: JSON.stringify({ sequence, mutation_type, position, new_base }),
  }),

  replicateStochastic: (sequence, mutation_rate = 0.01) => request('/dna/replicate', {
    method: 'POST',
    body: JSON.stringify({ sequence, mutation_rate }),
  }),

  simulateEnvironmentalDamage: (sequence, agent = 'uv_radiation', intensity = 0.25) => request('/dna/environmental-damage', {
    method: 'POST',
    body: JSON.stringify({ sequence, agent, intensity }),
  }),

  compareDNA: (reference, modified) => request('/dna/compare', {
    method: 'POST',
    body: JSON.stringify({ reference, modified }),
  }),

  copyDNA: (sequence) => request('/dna/copy', {
    method: 'POST',
    body: JSON.stringify({ sequence }),
  }),

  detectMismatches: (strand1, strand2) => request('/dna/mismatches', {
    method: 'POST',
    body: JSON.stringify({ strand1, strand2 }),
  }),

  repairWithReference: (altered, reference, positions = null, efficiency = 1.0) => request('/dna/repair', {
    method: 'POST',
    body: JSON.stringify({ altered, reference, positions, efficiency }),
  }),

  simulateBreakRepair: (sequence, break_position, method = 'homology_directed', reference = null) => request('/dna/break-repair', {
    method: 'POST',
    body: JSON.stringify({ sequence, break_position, method, reference }),
  }),

  getDNAEvents: (limit = 50) => request(`/dna/events?limit=${limit}`),
  clearDNAEvents: () => request('/dna/events', { method: 'DELETE' }),

  saveDNAExperiment: (data) => request('/dna/experiment/save', {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  listDNAExperiments: () => request('/dna/experiment/list'),

  getDNAExperiment: (experiment_id) => request(`/dna/experiment/${experiment_id}`),



  // Virtual Cells (PostgreSQL)
  listCells: () => request('/cells/'),
  createCell: (cell_id, initial_sequence, cell_state = 'normal') => request('/cells/', {
    method: 'POST',
    body: JSON.stringify({ cell_id, initial_sequence, cell_state }),
  }),
  getCell: (cell_id) => request(`/cells/${cell_id}`),
  updateCellState: (cell_id, cell_state, cell_cycle_phase = null) => request(`/cells/${cell_id}/state`, {
    method: 'PATCH',
    body: JSON.stringify({ cell_state, cell_cycle_phase }),
  }),
  divideCell: (cell_id, mutation_rate = 0.01) => request(`/cells/${cell_id}/divide?mutation_rate=${mutation_rate}`, {
    method: 'POST',
  }),

  // Experiments
  listExperiments: () => request('/experiments/'),
  createExperiment: (data) => request('/experiments/', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
};
