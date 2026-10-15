import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base

class Genome(Base):
    """
    Secuencias de nucleotidos asociadas a una celula segun seccion 6 del documento.
    """
    __tablename__ = "genomes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cell_id = Column(UUID(as_uuid=True), ForeignKey("virtual_cells.id", ondelete="CASCADE"), nullable=False)
    sequence = Column(Text, nullable=False)            # Cadena de letras A, T, C, G
    binary_repr = Column(Text, nullable=True)          # Representacion 00, 11, 01, 10
    gene_regions = Column(JSONB, default=list)         # [{name, start, end, strand}]
    variants = Column(JSONB, default=list)             # Variantes detectadas
    is_reference = Column(Boolean, default=False)
    source_id = Column(UUID(as_uuid=True), ForeignKey("data_sources.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    cell = relationship("VirtualCell", back_populates="genomes")
    source = relationship("DataSource", back_populates="genomes")
    mutations = relationship("Mutation", back_populates="genome", cascade="all, delete-orphan")
