import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base

class Mutation(Base):
    """
    Registro auditable de cada mutacion (sustitucion, insercion, delecion).
    """
    __tablename__ = "mutations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    genome_id = Column(UUID(as_uuid=True), ForeignKey("genomes.id", ondelete="CASCADE"), nullable=False)
    mutation_type = Column(String(16), nullable=False) # substitution, insertion, deletion
    position = Column(Integer, nullable=False)
    original_base = Column(String(8), nullable=True)
    new_base = Column(String(8), nullable=True)
    context = Column(JSONB, default=dict)              # Modo (controlled vs stochastic), tasa, etc.
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    genome = relationship("Genome", back_populates="mutations")
