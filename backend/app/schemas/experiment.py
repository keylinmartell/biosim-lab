from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime

class ExperimentCreate(BaseModel):
    name: str = Field(..., example="Prueba de Mutacion Inducida en Fase S")
    description: Optional[str] = None
    model_version: str = "1.0"
    cell_type: str = "abstract_cell"
    conditions: Dict[str, Any] = Field(default_factory=dict, example={"nutrients": "standard", "temp_c": 37})
    intervention: Dict[str, Any] = Field(default_factory=dict, example={"type": "uv_radiation", "dose_mj": 50})
    controls: Dict[str, Any] = Field(default_factory=dict)
    uncertainty: Optional[str] = "Estimado teorico con fines de prototipo"
    limitations: Optional[str] = "Modelo simplificado sin cinetica enzimatica completa"

class ExperimentRead(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    model_version: str
    cell_type: str
    conditions: Dict[str, Any]
    intervention: Dict[str, Any]
    result: Dict[str, Any]
    uncertainty: Optional[str]
    limitations: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
