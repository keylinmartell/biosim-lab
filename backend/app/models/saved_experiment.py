from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from app.core.database import Base


class SavedExperiment(Base):
    """
    Informe integral de un ensayo genetico guardado por el usuario.
    Reemplaza el antiguo almacenamiento en saved_experiments.json.
    """
    __tablename__ = "saved_experiments"

    experiment_id = Column(String(64), primary_key=True)
    name = Column(String(256), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    initial_sequence = Column(Text, nullable=False, default="")
    working_copy = Column(Text, nullable=True)
    mutation_applied = Column(JSONB, default=dict)
    altered_sequence = Column(Text, nullable=True)
    detection_result = Column(JSONB, default=dict)
    repair_applied = Column(JSONB, default=dict)
    final_sequence = Column(Text, nullable=True)
    diff_result = Column(JSONB, default=dict)
    status = Column(String(64), default="completed")
    notes = Column(Text, nullable=True)
    code_version = Column(String(64), default="v1.1-phase1-closed")

    def to_dict(self) -> dict:
        return {
            "experiment_id": self.experiment_id,
            "name": self.name,
            "created_at": self.created_at.isoformat() if self.created_at else "",
            "initial_sequence": self.initial_sequence or "",
            "working_copy": self.working_copy or "",
            "mutation_applied": self.mutation_applied or {},
            "altered_sequence": self.altered_sequence or "",
            "detection_result": self.detection_result or {},
            "repair_applied": self.repair_applied or {},
            "final_sequence": self.final_sequence or "",
            "diff_result": self.diff_result or {},
            "status": self.status or "completed",
            "notes": self.notes,
            "code_version": self.code_version or "v1.1-phase1-closed",
        }
