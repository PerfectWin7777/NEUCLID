import logging
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from src.services.generation import generation_service
from src.core.base_tool import ToolResult

router = APIRouter(tags=["Generation"])

log = logging.getLogger(__name__)

# --- Schema de la requête ---
class GenerateRequest(BaseModel):
    prompt: str = Field(..., description="La description naturelle de ce que l'utilisateur veut tracer.")

# --- Endpoint ---
@router.post("/generate", response_model=ToolResult)
async def generate_content(request: GenerateRequest, http_request: Request):
    """
    Endpoint unique et intelligent.
    1. Reçoit le prompt.
    2. Route vers le bon outil (Géométrie, Graphe, etc.).
    3. Exécute et renvoie le résultat complet.
    """
    try:
        # Appel au service orchestrateur
        result: ToolResult = await generation_service.generate(request.prompt)

        # Construction de l'URL complète pour l'image
        # result.image_url contient pour l'instant juste le nom du fichier (ex: figure_123.png)
        base_url = str(http_request.base_url).rstrip("/")
        full_url = f"{base_url}/static/{result.image_url}"
        
        # Mise à jour du résultat avec l'URL complète
        result.image_url = full_url

        return result

    except ValueError as ve:
        # Erreur de validation ou de routage (ex: outil introuvable)
        log.warning(f"Validation Error: {ve}")
        raise HTTPException(status_code=422, detail=str(ve))
        
    except Exception as e:
        log.error(f"Server Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Une erreur interne est survenue lors de la génération.")