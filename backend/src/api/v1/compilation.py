import logging
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from pathlib import Path

# On utilise directement le compilateur "bête" qui accepte tout code
from src.core.latex_compiler import compile_latex_to_image 

router = APIRouter(tags=["Compilation"])
log = logging.getLogger(__name__)

class CompileRequest(BaseModel):
    latex_code: str = Field(..., description="Le code LaTeX complet à compiler.")

class CompileResponse(BaseModel):
    image_url: str
    status: str = "success"

@router.post("/compile", response_model=CompileResponse)
async def manual_compilation(request: CompileRequest, http_request: Request):
    """
    Route directe pour l'éditeur de code.
    Prend du LaTeX brut -> Renvoie l'image.
    Sans passer par l'IA.
    """
    try:
        # Compilation directe
        image_path = compile_latex_to_image(request.latex_code)
        
        # Construction URL
        base_url = str(http_request.base_url).rstrip("/")
        file_url = f"{base_url}/static/{image_path.name}"
        
        return CompileResponse(image_url=file_url)

    except RuntimeError as re:
        # Erreur de compilation LaTeX (syntaxe)
        raise HTTPException(status_code=400, detail=f"Erreur de compilation LaTeX: {str(re)}")
        
    except Exception as e:
        log.error(f"Erreur serveur compilation: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne de compilation.")