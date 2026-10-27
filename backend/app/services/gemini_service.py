import logging
from google import genai
from app.core.config import settings

logger = logging.getLogger(__name__)

_client = None

def get_gemini_client() -> genai.Client:
    """
    Retorna la instancia del cliente Google GenAI configurado con la API key.
    """
    global _client
    if _client is None:
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            logger.warning("GEMINI_API_KEY no está configurada en el entorno.")
        _client = genai.Client(api_key=api_key)
    return _client

def generate_text(prompt: str, model: str = "gemini-3.8-flash") -> str:
    """
    Genera contenido de texto utilizando la API oficial de Google GenAI.
    """
    client = get_gemini_client()
    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt
        )
        return response.text or ""
    except Exception as e:
        logger.error(f"Error al generar contenido con Gemini ({model}): {e}")
        raise e
