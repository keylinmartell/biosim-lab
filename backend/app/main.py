from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base
import app.models # Garantizar que todos los modelos se importen
from app.api.v1.dna import router as dna_router
from app.api.v1.cells import router as cells_router
from app.api.v1.experiments import router as experiments_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crear tablas automaticamente al iniciar en Postgres / Supabase
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

# CORS permisivo para desarrollo local en Vue y despliegue en Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Ajustable para produccion en Vercel
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dna_router, prefix=settings.API_V1_STR)
app.include_router(cells_router, prefix=settings.API_V1_STR)
app.include_router(experiments_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "project": "BioSIM Lab",
        "version": settings.VERSION,
        "status": "online",
        "docs": "/docs"
    }
