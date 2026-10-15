import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base

class Experiment(Base):
    """
    Experimento in silico con condiciones, intervenciones y trazabilidad de limitaciones.
    """
    __tablename__ = "experiments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(256), nullable=False)
    description = Column(Text, nullable=True)
    model_version = Column(String(16), default="1.0", nullable=False)
    cell_type = Column(String(64), default="abstract_cell")
    conditions = Column(JSONB, default=dict)   # nutrientes, senales, temperatura
    intervention = Column(JSONB, default=dict) # radiacion, CRISPR, farmaco
    controls = Column(JSONB, default=dict)     # grupo de control
    result = Column(JSONB, default=dict)       # salida simulada
    uncertainty = Column(Text, nullable=True)  # nivel de incertidumbre
    limitations = Column(Text, nullable=True)  # limitaciones cientificas
    status = Column(String(32), default="pending") # pending, running, completed, failed
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    events = relationship("CellEvent", back_populates="experiment")
