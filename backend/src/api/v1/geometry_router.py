import logging
from fastapi import APIRouter, HTTPException, Request , status
from pydantic import BaseModel, Field

# Import the service singleton
from src.features.geometry.service import geometry_service

from src.config import settings


log = logging.getLogger(__name__)

# Create the router instance
router = APIRouter(prefix="/geometry", tags=["Geometry"])

# --- Request Schema ---
class GeometryRequest(BaseModel):
    """
    Schema for the geometry generation request.
    """
    prompt: str = Field(
        ..., 
        min_length=3, 
        max_length=2000, 
        description="Natural language description of the geometry figure to generate.",
        example="Draw a right-angled triangle ABC with AB=3, AC=4."
    )

# --- Response Schema ---
class GeometryResponse(BaseModel):
    image_url: str
    filename: str

# --- Endpoints ---

@router.post("/generate", response_model=GeometryResponse)
async def generate_geometry(request: GeometryRequest, http_request: Request):
    """
    Generates a 2D geometry figure from a text description and returns its URL.
    
    Returns:
        GeometryResponse: The generated image (PNG) and the url.
    """
    log.info(f"API Request: Generate geometry for prompt: '{request.prompt}'")
    
    try:
        # Call the service layer
        # 1. Generate the image (path is local)
        image_path = await geometry_service.generate_figure_from_text(request.prompt)
        
        # Check if file actually exists before returning
        if not image_path.exists():
            log.error(f"File not found at {image_path}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail="Image generation failed internally (file not found)."
            )

        # 2. Construct the URL
        # We use the incoming request to get the base URL (http://localhost:8000)
        base_url = str(http_request.base_url).rstrip("/")
        filename = image_path.name
        
        # This URL points to the StaticFiles mount we created in main.py
        file_url = f"{base_url}/static/{filename}"

        return GeometryResponse(
            image_url=file_url,
            filename=filename
        )

    except ValueError as ve:
        # This usually means the LLM failed to produce valid JSON
        log.warning(f"Validation Error: {ve}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
            detail=f"AI Validation Error: {str(ve)}"
        )
        
    except RuntimeError as re:
        # This means LaTeX compilation failed
        log.error(f"Runtime Error: {re}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to render the image. The geometry might be too complex."
        )
        
    except Exception as e:
        log.error(f"Unexpected API Error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="An unexpected error occurred."
        )