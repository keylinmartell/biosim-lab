from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.cell import VirtualCell
from app.models.genome import Genome
from app.models.cell_event import CellEvent
from app.models.mutation import Mutation
from app.schemas.cell import VirtualCellCreate, VirtualCellRead, CellStateUpdate
from app.services.dna_engine import dna_engine

router = APIRouter(prefix="/cells", tags=["Virtual Cells"])

@router.get("/", response_model=List[VirtualCellRead])
async def list_cells(db: AsyncSession = Depends(get_db)):
    stmt = select(VirtualCell).options(selectinload(VirtualCell.genomes)).order_by(VirtualCell.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/", response_model=VirtualCellRead, status_code=201)
async def create_cell(payload: VirtualCellCreate, db: AsyncSession = Depends(get_db)):
    # 1. Validar secuencia inicial
    seq = payload.initial_sequence.upper().strip()
    if not dna_engine.validate(seq):
        raise HTTPException(status_code=400, detail="Secuencia inicial de ADN invalida (solo A, T, C, G)")

    # 2. Verificar identificador unico
    existing = await db.execute(select(VirtualCell).where(VirtualCell.cell_id == payload.cell_id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail=f"La celula con ID '{payload.cell_id}' ya existe")

    # 3. Crear entidad celula
    cell = VirtualCell(
        cell_id=payload.cell_id,
        model_version=payload.model_version,
        cell_state=payload.cell_state,
        cell_cycle_phase="G1",
        division_count=0
    )
    db.add(cell)
    await db.flush()

    # 4. Crear genoma de referencia
    binary = dna_engine.to_binary(seq)
    genome = Genome(
        cell_id=cell.id,
        sequence=seq,
        binary_repr=binary,
        is_reference=True
    )
    db.add(genome)

    # 5. Registrar evento inicial
    event = CellEvent(
        cell_id=cell.id,
        event_type="creation",
        payload={"initial_sequence": seq, "state": cell.cell_state}
    )
    db.add(event)

    await db.commit()
    
    # Recargar con relaciones
    stmt = select(VirtualCell).options(selectinload(VirtualCell.genomes)).where(VirtualCell.id == cell.id)
    refreshed = await db.execute(stmt)
    return refreshed.scalar_one()

@router.get("/{cell_id}", response_model=VirtualCellRead)
async def get_cell(cell_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(VirtualCell).options(selectinload(VirtualCell.genomes)).where(VirtualCell.cell_id == cell_id)
    result = await db.execute(stmt)
    cell = result.scalar_one_or_none()
    if not cell:
        raise HTTPException(status_code=404, detail="Celula no encontrada")
    return cell

@router.patch("/{cell_id}/state", response_model=VirtualCellRead)
async def update_cell_state(cell_id: str, payload: CellStateUpdate, db: AsyncSession = Depends(get_db)):
    stmt = select(VirtualCell).options(selectinload(VirtualCell.genomes)).where(VirtualCell.cell_id == cell_id)
    result = await db.execute(stmt)
    cell = result.scalar_one_or_none()
    if not cell:
        raise HTTPException(status_code=404, detail="Celula no encontrada")

    old_state = cell.cell_state
    if payload.cell_state:
        cell.cell_state = payload.cell_state
    if payload.cell_cycle_phase:
        cell.cell_cycle_phase = payload.cell_cycle_phase

    # Registrar evento de transicion de estado
    event = CellEvent(
        cell_id=cell.id,
        event_type="state_change",
        payload={"from": old_state, "to": cell.cell_state, "phase": cell.cell_cycle_phase}
    )
    db.add(event)
    await db.commit()
    await db.refresh(cell)
    return cell

@router.post("/{cell_id}/divide")
async def divide_cell(cell_id: str, mutation_rate: float = 0.01, db: AsyncSession = Depends(get_db)):
    """Simula un ciclo de division celular con replicacion de ADN en fase S y mitosis."""
    stmt = select(VirtualCell).options(selectinload(VirtualCell.genomes)).where(VirtualCell.cell_id == cell_id)
    result = await db.execute(stmt)
    cell = result.scalar_one_or_none()
    if not cell:
        raise HTTPException(status_code=404, detail="Celula no encontrada")

    if cell.cell_state in ("apoptotic", "necrotic"):
        raise HTTPException(status_code=400, detail="Una celula en apoptosis o necrosis no puede dividirse")

    current_genome = cell.genomes[-1] if cell.genomes else None
    if not current_genome:
        raise HTTPException(status_code=400, detail="La celula no tiene genoma registrado")

    # Replicacion con tasa de mutacion
    rep_result = dna_engine.replicate_with_mutations(
        sequence=current_genome.sequence,
        mutation_rate=mutation_rate
    )

    cell.division_count += 1
    cell.cell_cycle_phase = "M"

    # Si hubo mutacion, guardar en la base de datos
    new_genome = Genome(
        cell_id=cell.id,
        sequence=rep_result["replicated_sequence"],
        binary_repr=dna_engine.to_binary(rep_result["replicated_sequence"]),
        is_reference=False
    )
    db.add(new_genome)
    await db.flush()

    for m in rep_result["mutations"]:
        mut_record = Mutation(
            genome_id=new_genome.id,
            mutation_type=m["type"],
            position=m["position"],
            original_base=m.get("original_base"),
            new_base=m.get("new_base"),
            context={"mode": "replication_error", "rate": mutation_rate}
        )
        db.add(mut_record)

    event = CellEvent(
        cell_id=cell.id,
        event_type="division",
        payload={
            "generation": cell.division_count,
            "mutations_occurred": rep_result["mutation_count"],
            "new_sequence": rep_result["replicated_sequence"]
        }
    )
    db.add(event)
    await db.commit()

    return {
        "cell_id": cell.cell_id,
        "division_count": cell.division_count,
        "mutations_occurred": rep_result["mutation_count"],
        "mutations": rep_result["mutations"],
        "new_sequence": rep_result["replicated_sequence"],
        "cell_state": cell.cell_state
    }
