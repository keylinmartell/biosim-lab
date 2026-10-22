from fastapi import APIRouter, HTTPException, Depends
from collections import Counter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.saved_experiment import SavedExperiment
from app.services.dna_engine import dna_engine
from app.schemas.dna import (
    ValidateSequenceRequest,
    ValidateSequenceResponse,
    ComplementRequest,
    ComplementResponse,
    ControlledMutationRequest,
    ReplicateRequest,
    ReplicateResponse,
    CompareRequest,
    CompareResponse,
    CopyDnaRequest,
    CopyDnaResponse,
    MismatchDetectionRequest,
    MismatchDetectionResponse,
    RepairWithReferenceRequest,
    RepairWithReferenceResponse,
    BreakRepairRequest,
    BreakRepairResponse,
    DnaEventLogResponse,
    SaveFullExperimentRequest,
    FullExperimentReport,
    SavedExperimentListResponse,
    EnvironmentalDamageRequest,
    EnvironmentalDamageResponse
)

router = APIRouter(prefix="/dna", tags=["DNA Engine"])

@router.post("/validate", response_model=ValidateSequenceResponse)
def validate_sequence(payload: ValidateSequenceRequest):
    seq = payload.sequence.upper().strip()
    is_valid = dna_engine.validate(seq)
    counts = dict(Counter(seq))
    invalid_chars = sorted(list(set(seq) - dna_engine.VALID_BASES))
    gc_count = counts.get("G", 0) + counts.get("C", 0)
    gc_content = round((gc_count / len(seq)) * 100, 2) if (is_valid and len(seq) > 0) else 0.0

    error_message = None
    if not is_valid:
        if len(seq) == 0:
            error_message = "Secuencia vacia. Introduce al menos un nucleotido (A, T, C, G)."
        elif invalid_chars:
            chars_str = ", ".join(f"'{c}'" for c in invalid_chars)
            error_message = f"Simbolos no canonicos detectados: {chars_str}. El alfabeto genetico solo permite A, T, C, G."
        else:
            error_message = "Secuencia no valida."

    backbone_info = {
        "monomer_name": "Desoxirribonucleotido monofosfato (dNMP)",
        "sugar_unit": "2'-Desoxirribosa (pentosa)",
        "phosphate_group": "Grupo Fosfato (PO4^3-)",
        "linkage_type": "Enlace fosfodiéster 3'-5'",
        "total_sugars": len(seq) if is_valid else 0,
        "total_phosphates": len(seq) if is_valid else 0,
        "phosphodiester_bonds": max(0, len(seq) - 1) if is_valid else 0,
        "polarity": "5' Fosfato libre -> 3' Hidroxilo libre (-OH)"
    } if is_valid else None

    return ValidateSequenceResponse(
        sequence=seq,
        is_valid=is_valid,
        length=len(seq),
        gc_content=gc_content,
        base_counts=counts,
        invalid_chars=invalid_chars,
        error_message=error_message,
        backbone_info=backbone_info
    )

@router.post("/complement", response_model=ComplementResponse)
def complement_sequence(payload: ComplementRequest):
    try:
        seq = payload.sequence.upper().strip()
        comp = dna_engine.complement(seq)
        rev_comp = dna_engine.reverse_complement(seq)
        binary = dna_engine.to_binary(seq)
        backbone_structure = {
            "strand_5_to_3": {
                "label": "Hebra Codificante Principal",
                "backbone": f"5'-P - [{' - '.join(seq)}] - OH-3'",
                "polarity": "5' -> 3'"
            },
            "strand_3_to_5": {
                "label": "Hebra Complementaria Antisentido (Apareada)",
                "backbone": f"3'-OH - [{' - '.join(comp)}] - P-5'",
                "polarity": "3' -> 5' (Antiparalela alineada)"
            },
            "strand_rev_5_to_3": {
                "label": "Hebra Complementaria Inversa (Dirección estándar)",
                "backbone": f"5'-P - [{' - '.join(rev_comp)}] - OH-3'",
                "polarity": "5' -> 3' (Lectura estándar)"
            },
            "backbone_type": "Doble esqueleto antiparalelo de azúcar-fosfato"
        }
        orientation_note = (
            f"Orientación apareada directa (3'->5'): {comp} (alineada base a base con el molde). "
            f"Orientación de polimerización estándar (5'->3', complementaria inversa): {rev_comp}."
        )
        return ComplementResponse(
            original=seq,
            complement=comp,
            reverse_complement=rev_comp,
            binary_repr=binary,
            orientation_note=orientation_note,
            backbone_structure=backbone_structure,
            base_pairs=dna_engine.base_pairs(seq)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/mutate")
def mutate_controlled(payload: ControlledMutationRequest):
    """Modo 2: Aplica una mutacion controlada en posicion especifica."""
    try:
        result = dna_engine.apply_controlled_mutation(
            sequence=payload.sequence,
            mutation_type=payload.mutation_type,
            position=payload.position,
            new_base=payload.new_base,
            one_based=payload.one_based
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/environmental-damage", response_model=EnvironmentalDamageResponse)
def environmental_damage(payload: EnvironmentalDamageRequest):
    """Fase G1: Simula daño ambiental estocastico sobre el molde parental (UV, ROS, Desaminacion)."""
    try:
        result = dna_engine.simulate_environmental_damage(
            sequence=payload.sequence,
            agent=payload.agent,
            intensity=payload.intensity
        )
        return EnvironmentalDamageResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/replicate", response_model=ReplicateResponse)
def replicate_stochastic(payload: ReplicateRequest):
    """Modo 1: Replicacion probabilistica con tasa de error."""
    try:
        result = dna_engine.replicate_with_mutations(
            sequence=payload.sequence,
            mutation_rate=payload.mutation_rate
        )
        return ReplicateResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/compare", response_model=CompareResponse)
def compare_sequences(payload: CompareRequest):
    """Detecta diferencias (diff) entre secuencia de referencia y modificada."""
    diffs = dna_engine.compare(payload.reference, payload.modified)
    return CompareResponse(
        reference=payload.reference.upper().strip(),
        modified=payload.modified.upper().strip(),
        differences=diffs,
        difference_count=len(diffs)
    )

@router.post("/copy", response_model=CopyDnaResponse)
def copy_sequence(payload: CopyDnaRequest):
    """Genera una copia sin cambios y comprueba que coincida con la original."""
    try:
        result = dna_engine.copy_dna(payload.sequence)
        return CopyDnaResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/mismatches", response_model=MismatchDetectionResponse)
def detect_mismatches_endpoint(payload: MismatchDetectionRequest):
    """3.1 Deteccion de apareamientos no canonicos entre dos cadenas alineadas."""
    try:
        result = dna_engine.detect_mismatches(payload.strand1, payload.strand2, payload.orientation)
        return MismatchDetectionResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/repair", response_model=RepairWithReferenceResponse)
def repair_with_reference_endpoint(payload: RepairWithReferenceRequest):
    """3.2 Reparacion guiada por secuencia de referencia fiable."""
    try:
        result = dna_engine.repair_with_reference(
            altered=payload.altered,
            reference=payload.reference,
            positions=payload.positions,
            efficiency=payload.efficiency or 1.0
        )
        return RepairWithReferenceResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/break-repair", response_model=BreakRepairResponse)
def break_repair_endpoint(payload: BreakRepairRequest):
    """3.3 Roturas de ADN (DSB) y comparacion entre HDR y NHEJ."""
    try:
        result = dna_engine.simulate_break_repair(
            sequence=payload.sequence,
            break_position=payload.break_position,
            method=payload.method,
            reference=payload.reference
        )
        return BreakRepairResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/events", response_model=DnaEventLogResponse)
def get_dna_events(limit: int = 50):
    """7. Registro de datos de experimentos de ADN."""
    events = dna_engine.get_events(limit=limit)
    return DnaEventLogResponse(
        events=events,
        total=len(events)
    )

@router.delete("/events")
def clear_dna_events():
    """Limpia el registro en memoria de auditoria de experimentos."""
    count = dna_engine.clear_events()
    return {"message": "Historial de eventos de auditoria vaciado", "cleared": count}

@router.post("/experiment/save", response_model=FullExperimentReport)
async def save_full_experiment_endpoint(payload: SaveFullExperimentRequest, db: AsyncSession = Depends(get_db)):
    """Guarda el informe integral del experimento en la base de datos (Supabase/Postgres)."""
    try:
        record = dna_engine.build_experiment_record(payload.dict())
        row = await db.get(SavedExperiment, record["experiment_id"])
        if row is None:
            row = SavedExperiment(experiment_id=record["experiment_id"])
            db.add(row)
        row.name = record["name"]
        row.initial_sequence = record["initial_sequence"]
        row.working_copy = record["working_copy"]
        row.mutation_applied = record["mutation_applied"]
        row.altered_sequence = record["altered_sequence"]
        row.detection_result = record["detection_result"]
        row.repair_applied = record["repair_applied"]
        row.final_sequence = record["final_sequence"]
        row.diff_result = record["diff_result"]
        row.status = record["status"]
        row.notes = record["notes"]
        row.code_version = record["code_version"]
        await db.flush()
        await db.refresh(row)
        return FullExperimentReport(**row.to_dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/experiment/list", response_model=SavedExperimentListResponse)
async def list_saved_experiments_endpoint(db: AsyncSession = Depends(get_db)):
    """Lista todos los experimentos completos guardados en la base de datos."""
    try:
        result = await db.execute(select(SavedExperiment).order_by(SavedExperiment.created_at.desc()))
        exps = [r.to_dict() for r in result.scalars().all()]
        return SavedExperimentListResponse(
            experiments=exps,
            total=len(exps)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {type(e).__name__}: {str(e)}")

@router.get("/experiment/{experiment_id}", response_model=FullExperimentReport)
async def get_saved_experiment_endpoint(experiment_id: str, db: AsyncSession = Depends(get_db)):
    """Obtiene el informe completo de un experimento para restaurar su estado en la UI."""
    row = await db.get(SavedExperiment, experiment_id)
    if not row:
        raise HTTPException(status_code=404, detail=f"Experimento {experiment_id} no encontrado")
    return FullExperimentReport(**row.to_dict())


