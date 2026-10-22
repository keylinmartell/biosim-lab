from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ValidateSequenceRequest(BaseModel):
    sequence: str = Field(..., description="Cadena de nucleotidos a validar (A, T, C, G)")

class ValidateSequenceResponse(BaseModel):
    sequence: str
    is_valid: bool
    length: int
    gc_content: float
    base_counts: Dict[str, int]
    invalid_chars: List[str] = []
    error_message: Optional[str] = None
    backbone_info: Optional[Dict[str, Any]] = None

class ComplementRequest(BaseModel):
    sequence: str

class ComplementResponse(BaseModel):
    original: str
    complement: str
    reverse_complement: Optional[str] = None
    binary_repr: str
    orientation_note: Optional[str] = None
    backbone_structure: Optional[Dict[str, Any]] = None
    base_pairs: Optional[List[Dict[str, Any]]] = None

class ControlledMutationRequest(BaseModel):
    sequence: str
    mutation_type: str = Field(..., description="'substitution', 'insertion', o 'deletion'")
    position: int = Field(..., ge=0, description="Posicion de la base a modificar (0-based por defecto; 1-based si one_based=true)")
    new_base: Optional[str] = Field(None, description="A, T, C, G (requerido para sustitucion e insercion)")
    one_based: bool = Field(False, description="Si es true, 'position' es un indice humano (1 = primera base)")

class ReplicateRequest(BaseModel):
    sequence: str
    mutation_rate: float = Field(0.01, ge=0.0, le=1.0, description="Tasa de error estocastico por base")
    generations: int = Field(1, ge=1, le=100, description="Numero de rondas de duplicacion")

class ReplicateResponse(BaseModel):
    original_sequence: str
    replicated_sequence: str
    mutations: List[Dict[str, Any]]
    mutation_count: int
    is_identical: bool
    event_id: Optional[str] = None
    fidelity_filters: Optional[Dict[str, Any]] = None

class CompareRequest(BaseModel):
    reference: str
    modified: str

class DiffItem(BaseModel):
    position: int
    reference_base: Optional[str]
    modified_base: Optional[str]
    status: str

class CompareResponse(BaseModel):
    reference: str
    modified: str
    differences: List[DiffItem]
    difference_count: int

class CopyDnaRequest(BaseModel):
    sequence: str = Field(..., description="Secuencia de nucleotidos a copiar")

class CopyDnaResponse(BaseModel):
    original: str
    copy: str
    is_identical: bool
    length: int
    event_id: str

class MismatchItem(BaseModel):
    position: int
    base_strand1: Optional[str] = None
    base_strand2: Optional[str] = None
    pair: str
    is_canonical: bool
    status: str
    note: str
    position_human: Optional[int] = None
    geometry: Optional[str] = None

class MismatchDetectionRequest(BaseModel):
    strand1: str = Field(..., description="Cadena sentido (5'->3' modelo simplificado)")
    strand2: str = Field(..., description="Cadena apareada o complementaria a comprobar")
    orientation: str = Field("aligned", description="'aligned': strand2 ya alineada base a base (3'->5'); 'antiparallel': strand2 escrita 5'->3' y se invierte")

class MismatchDetectionResponse(BaseModel):
    strand1: str
    strand2: str
    strand2_aligned: Optional[str] = None
    orientation: Optional[str] = "aligned"
    length: int
    is_fully_canonical: bool
    mismatch_count: int
    canonical_count: int
    mismatches: List[MismatchItem]
    event_id: str

class RepairWithReferenceRequest(BaseModel):
    altered: str = Field(..., description="Secuencia de ADN que contiene errores o mutaciones")
    reference: str = Field(..., description="Secuencia de referencia homologa fiable")
    positions: Optional[List[int]] = Field(None, description="Posiciones autorizadas a reparar. Si es None, repara todas las divergencias detectadas.")
    efficiency: Optional[float] = Field(1.0, ge=0.1, le=1.0, description="Eficiencia enzimática de reparación (1.0 = 100% determinista, < 1.0 = cinética estocástica)")

class RepairWithReferenceResponse(BaseModel):
    altered_sequence: str
    reference_sequence: str
    repaired_sequence: str
    repaired_positions: List[int]
    escaped_positions: Optional[List[int]] = []
    efficiency: Optional[float] = 1.0
    matches_reference: bool
    status: str
    remaining_divergences: int
    event_id: str
    cell_cycle_phase: Optional[str] = "G1"
    checkpoint_status: Optional[Dict[str, Any]] = None
    basis: Optional[str] = "reference_backed"
    note: Optional[str] = None

class BreakRepairRequest(BaseModel):
    sequence: str = Field(..., description="Secuencia que sufre una rotura bicatenaria (DSB)")
    break_position: int = Field(..., ge=1, description="Posicion del punto de corte/rotura")
    method: str = Field("homology_directed", description="'homology_directed' (HDR) o 'end_joining' (NHEJ)")
    reference: Optional[str] = Field(None, description="Secuencia homologa requerida para reparacion HDR")

class BreakRepairResponse(BaseModel):
    initial_sequence: str
    break_position: int
    fragments: List[str]
    repair_method: str
    repaired_sequence: str
    scar: str
    description: str
    status: str
    matches_initial: bool
    event_id: str

class DnaEventItem(BaseModel):
    experiment_id: str
    timestamp: str
    operation_type: str
    initial_sequence: str
    final_sequence: str
    parameters: Dict[str, Any]
    reference_used: Optional[str] = None
    detection_result: Dict[str, Any]
    repair_result: Dict[str, Any]
    code_version: str
    model_assumptions: str

class DnaEventLogResponse(BaseModel):
    events: List[DnaEventItem]
    total: int

class SaveFullExperimentRequest(BaseModel):
    experiment_id: Optional[str] = None
    name: Optional[str] = None
    created_at: Optional[str] = None
    initial_sequence: str
    working_copy: Optional[str] = None
    mutation_applied: Optional[Dict[str, Any]] = None
    altered_sequence: Optional[str] = None
    detection_result: Optional[Dict[str, Any]] = None
    repair_applied: Optional[Dict[str, Any]] = None
    final_sequence: Optional[str] = None
    diff_result: Optional[Dict[str, Any]] = None
    status: Optional[str] = "completed"
    notes: Optional[str] = None

class FullExperimentReport(BaseModel):
    experiment_id: str
    name: str
    created_at: str
    initial_sequence: str
    working_copy: Optional[str] = None
    mutation_applied: Optional[Dict[str, Any]] = None
    altered_sequence: Optional[str] = None
    detection_result: Optional[Dict[str, Any]] = None
    repair_applied: Optional[Dict[str, Any]] = None
    final_sequence: Optional[str] = None
    diff_result: Optional[Dict[str, Any]] = None
    status: str
    notes: Optional[str] = None
    code_version: str

class SavedExperimentListResponse(BaseModel):
    experiments: List[FullExperimentReport]
    total: int

class EnvironmentalDamageRequest(BaseModel):
    sequence: str = Field(..., description="Cadena de ADN molde a someter a daño ambiental")
    agent: str = Field("uv_radiation", description="'uv_radiation' (dímeros TT), 'oxidative_ros' (8-oxo-G) o 'deamination' (C->T/U)")
    intensity: float = Field(0.25, ge=0.0, le=1.0, description="Intensidad / probabilidad estocástica de lesión por sitio susceptible")

class EnvironmentalDamageResponse(BaseModel):
    original_sequence: str
    damaged_sequence: str
    agent: str
    agent_name: str
    lesions: List[Dict[str, Any]]
    lesion_count: int
    is_damaged: bool
    mechanism_description: str
    checkpoint_consequence: str
    event_id: str



