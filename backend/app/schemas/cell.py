from pydantic import BaseModel, Field
from typing import Optional, List, Any
from uuid import UUID
from datetime import datetime

class VirtualCellCreate(BaseModel):
    cell_id: str = Field(..., example="CELL-ALPHA-01")
    model_version: str = Field("1.0", example="1.0")
    initial_sequence: str = Field("ATCGATCGATCG", description="Secuencia inicial de ADN para la celula")
    cell_state: str = Field("initial", description="initial, normal, replicating, mutated, apoptotic, necrotic")

class GenomeRead(BaseModel):
    id: UUID
    sequence: str
    binary_repr: Optional[str]
    is_reference: bool
    created_at: datetime

    class Config:
        from_attributes = True

class VirtualCellRead(BaseModel):
    id: UUID
    cell_id: str
    model_version: str
    cell_state: str
    cell_cycle_phase: str
    division_count: int
    created_at: datetime
    updated_at: datetime
    genomes: List[GenomeRead] = []

    class Config:
        from_attributes = True

class CellStateUpdate(BaseModel):
    cell_state: Optional[str] = None # normal, replicating, mutated, apoptotic, necrotic
    cell_cycle_phase: Optional[str] = None # G1, S, G2, M
