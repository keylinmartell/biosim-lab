from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.models.experiment import Experiment
from app.schemas.experiment import ExperimentCreate, ExperimentRead

router = APIRouter(prefix="/experiments", tags=["Experiments"])

@router.get("/", response_model=List[ExperimentRead])
async def list_experiments(db: AsyncSession = Depends(get_db)):
    stmt = select(Experiment).order_by(Experiment.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/", response_model=ExperimentRead, status_code=201)
async def create_experiment(payload: ExperimentCreate, db: AsyncSession = Depends(get_db)):
    experiment = Experiment(
        name=payload.name,
        description=payload.description,
        model_version=payload.model_version,
        cell_type=payload.cell_type,
        conditions=payload.conditions,
        intervention=payload.intervention,
        controls=payload.controls,
        uncertainty=payload.uncertainty,
        limitations=payload.limitations,
        status="completed"
    )
    db.add(experiment)
    await db.commit()
    await db.refresh(experiment)
    return experiment

@router.get("/{experiment_id}", response_model=ExperimentRead)
async def get_experiment(experiment_id: UUID, db: AsyncSession = Depends(get_db)):
    stmt = select(Experiment).where(Experiment.id == experiment_id)
    result = await db.execute(stmt)
    exp = result.scalar_one_or_none()
    if not exp:
        raise HTTPException(status_code=404, detail="Experimento no encontrado")
    return exp
