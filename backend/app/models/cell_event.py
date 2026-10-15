import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base

class CellEvent(Base):
    """
    Timeline cronologico de la vida de la celula:
    division, mutation, state_transition, exposure.
    """
    __tablename__ = "cell_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cell_id = Column(UUID(as_uuid=True), ForeignKey("virtual_cells.id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String(64), nullable=False) # division, mutation, state_change, exposure
    payload = Column(JSONB, default=dict)
    experiment_id = Column(UUID(as_uuid=True), ForeignKey("experiments.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    cell = relationship("VirtualCell", back_populates="events")
    experiment = relationship("Experiment", back_populates="events")
