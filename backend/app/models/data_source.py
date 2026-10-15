import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class DataSource(Base):
    """
    Trazabilidad obligatoria segun documento BioSIM Lab:
    source_type: observed, literature, assumption, simulated, validated
    """
    __tablename__ = "data_sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_type = Column(String(32), nullable=False)
    reference = Column(Text, nullable=True)     # DOI, paper, institucion o nota
    conditions = Column(Text, nullable=True)    # Condiciones experimentales
    units = Column(String(64), nullable=True)   # Unidades de medicion
    uncertainty = Column(Text, nullable=True)   # Rango o nivel de incertidumbre
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    genomes = relationship("Genome", back_populates="source")
