"""
Planner de experimentos: Gemini traduce condiciones en lenguaje natural a
parametros estructurados VALIDADOS contra la base de conocimiento local.

Gemini NO simula ni busca en internet: solo interpreta, usando la KB como
system_instruction. La simulacion corre en el motor determinista del frontend.
"""
import hashlib
import json
import logging
from functools import lru_cache
from pathlib import Path

from google.genai import types

from app.services.gemini_service import get_gemini_client

logger = logging.getLogger(__name__)

KB_PATH = Path(__file__).resolve().parent.parent / "knowledge" / "biosim_kb.json"
CANDIDATE_MODELS = ["gemini-3.1-flash-lite", "gemini-3.8-flash", "gemini-3.5-flash-lite"]


@lru_cache(maxsize=1)
def load_kb() -> dict:
    return json.loads(KB_PATH.read_text(encoding="utf-8"))


SYSTEM_RULES = """Eres el planificador de experimentos de BioSim Lab (modelo educativo de celula virtual).
Tu UNICA tarea: convertir la peticion del usuario en un JSON de condiciones iniciales e intervenciones.

REGLAS OBLIGATORIAS:
1. Usa SOLO variables de "conditions_schema" e "interventions_schema" de la base de conocimiento. Respeta rangos y unidades.
2. La celula inicial es SIEMPRE una celula madre pluripotente (initial_cell). No la cambies.
3. No inventes parametros ni genes que no esten en la base. Si el usuario pide algo no modelado, ponlo en "no_modelado".
4. Cada decision debe citar ids de reglas (R01..R17) y claves de "sources". No cites fuentes externas.
5. Distingue evidencia: literatura / supuesto / didactico. Nunca presentes un resultado como medicion real.
6. No hagas predicciones clinicas, de cancer ni de eficacia terapeutica.
7. CRISPR es herramienta externa: modelalo solo como intervencion "CRISPR_corte".
8. "expected" describe cualitativamente lo que deberia ocurrir segun las reglas, no numeros inventados.
Responde solo con el JSON del esquema.

BASE DE CONOCIMIENTO:
"""

RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "titulo": {"type": "STRING"},
        "conditions": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "key": {"type": "STRING"},
                    "value": {"type": "STRING"},
                    "reason": {"type": "STRING"},
                },
                "required": ["key", "value"],
            },
        },
        "interventions": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "t_s": {"type": "NUMBER"},
                    "type": {"type": "STRING"},
                    "params_json": {"type": "STRING"},
                },
                "required": ["t_s", "type"],
            },
        },
        "duration_s": {"type": "NUMBER"},
        "expected": {"type": "ARRAY", "items": {"type": "STRING"}},
        "rules_used": {"type": "ARRAY", "items": {"type": "STRING"}},
        "sources_used": {"type": "ARRAY", "items": {"type": "STRING"}},
        "assumptions": {"type": "ARRAY", "items": {"type": "STRING"}},
        "no_modelado": {"type": "ARRAY", "items": {"type": "STRING"}},
    },
    "required": ["titulo", "conditions", "interventions", "duration_s", "expected", "rules_used"],
}


def _coerce(spec: dict, raw: str):
    t = spec.get("type")
    if t == "number":
        try:
            v = float(raw)
        except (TypeError, ValueError):
            return spec.get("default"), "valor no numerico -> default"
        lo, hi = spec["range"]
        if v < lo or v > hi:
            return min(max(v, lo), hi), f"fuera de rango [{lo},{hi}] -> recortado"
        return v, None
    if t == "boolean":
        return str(raw).strip().lower() in ("true", "1", "si", "yes"), None
    if t == "enum":
        return (raw, None) if raw in spec["values"] else (spec["default"], "valor no permitido -> default")
    return raw, None


def validate_plan(plan: dict) -> dict:
    """Aplica la KB como juez final: lo que Gemini proponga fuera de esquema se descarta."""
    kb = load_kb()
    schema = kb["conditions_schema"]
    conditions = {k: v.get("default") for k, v in schema.items()}
    warnings = []

    for c in plan.get("conditions", []):
        key = c.get("key")
        if key not in schema:
            warnings.append(f"condicion desconocida descartada: {key}")
            continue
        val, warn = _coerce(schema[key], c.get("value"))
        conditions[key] = val
        if warn:
            warnings.append(f"{key}: {warn}")

    interventions = []
    for it in plan.get("interventions", []):
        if it.get("type") not in kb["interventions_schema"]:
            warnings.append(f"intervencion desconocida descartada: {it.get('type')}")
            continue
        try:
            params = json.loads(it.get("params_json") or "{}")
        except json.JSONDecodeError:
            params = {}
        interventions.append({"t_s": max(0.0, float(it.get("t_s", 0))), "type": it["type"], "params": params})
    interventions.sort(key=lambda x: x["t_s"])

    valid_rules = {r["id"] for r in kb["rules"]}
    return {
        "kb_version": kb["version"],
        "model_version": kb["model_version"],
        "titulo": plan.get("titulo", "Experimento"),
        "initial_cell": kb["initial_cell"],
        "conditions": conditions,
        "interventions": interventions,
        "duration_s": min(max(float(plan.get("duration_s", 86400)), 600), 30 * 86400),
        "expected": plan.get("expected", []),
        "rules_used": [r for r in plan.get("rules_used", []) if r in valid_rules],
        "sources_used": [s for s in plan.get("sources_used", []) if s in kb["sources"]],
        "assumptions": plan.get("assumptions", []),
        "no_modelado": plan.get("no_modelado", []),
        "warnings": warnings,
        "evidence": "simulado",
    }


@lru_cache(maxsize=256)
def _plan_cached(prompt_hash: str, prompt: str) -> str:
    kb = load_kb()
    client = get_gemini_client()
    last_err = None
    for model_name in CANDIDATE_MODELS:
        try:
            resp = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_RULES + json.dumps(kb, ensure_ascii=False),
                    response_mime_type="application/json",
                    response_schema=RESPONSE_SCHEMA,
                    temperature=0.0,
                ),
            )
            if resp.text:
                return resp.text
        except Exception as e:
            logger.warning("Fallo modelo %s: %s", model_name, e)
            last_err = e
    if last_err:
        logger.error("Todos los modelos fallaron en _plan_cached: %s", last_err)
    return "{}"


def plan_experiment(user_prompt: str) -> dict:
    prompt = user_prompt.strip()
    h = hashlib.sha256(prompt.encode()).hexdigest()
    raw = _plan_cached(h, prompt)
    try:
        plan = json.loads(raw)
    except json.JSONDecodeError:
        logger.error("Gemini devolvio JSON invalido: %s", raw[:300])
        plan = {}
    return validate_plan(plan)
