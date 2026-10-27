from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import os

from app.core.config import settings
from app.core.database import engine, Base
import app.models # Garantizar que todos los modelos se importen
from app.api.v1.dna import router as dna_router
from app.api.v1.cells import router as cells_router
from app.api.v1.experiments import router as experiments_router
from app.api.v1.simulation import router as simulation_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Solo en local: crear tablas automaticamente. En produccion (Vercel) las tablas se
    # crean una sola vez con backend/sql/schema.sql en el SQL Editor de Supabase.
    if os.getenv("AUTO_CREATE_TABLES", "0") == "1":
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="BioSIM Lab API — Motor de Simulacion Celular y Genetica Abstracta",
    lifespan=lifespan
)

# CORS: ALLOWED_ORIGINS (separados por coma) define los dominios permitidos en produccion.
# Si no se define, se permite todo (desarrollo local).
_origins_env = os.getenv("ALLOWED_ORIGINS", "").strip()
_origins = [o.strip() for o in _origins_env.split(",") if o.strip()] or ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=_origins != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dna_router, prefix=settings.API_V1_STR)
app.include_router(cells_router, prefix=settings.API_V1_STR)
app.include_router(experiments_router, prefix=settings.API_V1_STR)
app.include_router(simulation_router, prefix=settings.API_V1_STR)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {
        "project": "BioSIM Lab",
        "version": settings.VERSION,
        "status": "online",
        "docs": "/docs"
    }
