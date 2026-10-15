import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class VirtualCell(Base):
    """
    Entidad Celula Virtual abstracta segun seccion 5 del documento.
    """
    __tablename__ = "virtual_cells"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cell_id = Column(String(64), unique=True, nullable=False, index=True)
    model_version = Column(String(16), default="1.0", nullable=False)
    cell_state = Column(String(32), default="initial") # initial, normal, replicating, mutated, apoptotic, necrotic
    cell_cycle_phase = Column(String(16), default="G1") # G1, S, G2, M
    division_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    genomes = relationship("Genome", back_populates="cell", cascade="all, delete-orphan")
    events = relationship("CellEvent", back_populates="cell", cascade="all, delete-orphan")
