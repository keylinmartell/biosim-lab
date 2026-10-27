from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field

from app.services.experiment_planner import load_kb, plan_experiment, validate_plan

router = APIRouter(prefix="/simulation", tags=["Simulation"])


class PlanRequest(BaseModel):
    prompt: str = Field(..., min_length=3, max_length=4000)


@router.get("/kb")
def get_kb():
    """Base de conocimiento completa: el motor del frontend lee parametros de aqui."""
    return load_kb()


@router.post("/plan")
async def plan(req: PlanRequest):
    """Lenguaje natural -> condiciones validadas (Gemini, 1 llamada, cacheada)."""
    try:
        return await run_in_threadpool(plan_experiment, req.prompt)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error del planner: {e}")


@router.post("/validate")
def validate(plan_json: dict):
    """Condiciones manuales (sin IA) validadas contra la KB."""
    return validate_plan(plan_json)
