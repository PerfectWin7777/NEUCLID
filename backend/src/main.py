import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles 

from src.config import settings
from src.firebase_setup import initialize_firebase

from src.core.startup import register_application_tools

from src.api.v1 import generation
from src.api.v1 import compilation


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
log = logging.getLogger(__name__)

# --- LIFESPAN (Startup & Shutdown) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- CODE EXÉCUTÉ AU DÉMARRAGE ---
    log.info(f"🚀 Démarrage de {settings.PROJECT_NAME}...")
    
    # 1. Connexion Base de Données
    try:
        initialize_firebase()
    except Exception as e:
        log.error(f"⚠️ Attention: Impossible de connecter Firebase. {e}")
    
    # 2. Enregistrement des Outils (Factory Pattern)
    # C'est ici que la magie opère : on charge Geometry2D, etc.
    register_application_tools()
    
    yield
    
    # --- CODE EXÉCUTÉ À L'ARRÊT ---
    log.info("🛑 Arrêt de NEUCLID API...")



# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend for the Neuclid neuro-symbolic AI platform.",
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# --- Middleware Configuration ---
app.add_middleware(
    CORSMiddleware,
     # ON CHANGE ICI : On met "*" pour dire "Tout le monde est accepté"
    allow_origins=["*"], 
    # allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Static Files Configuration ---
# This makes the generated images accessible via http://localhost:8000/static/...
app.mount("/static", StaticFiles(directory=settings.TEMP_BUILD_DIR), name="static")



# --- Include Routers ---
app.include_router(generation.router, prefix=settings.API_V1_STR)
app.include_router(compilation.router, prefix=settings.API_V1_STR)



@app.get("/")
async def root():
    """
    Health check endpoint.
    """
    return {
        "message": "Welcome to Neuclid API",
        "status": "running",
        "version": "0.1.0",
        "project": settings.PROJECT_NAME,
        "tools_loaded": True
    }


# ============== BLOC DE DÉBOGAGE À AJOUTER TEMPORAIREMENT ==============
from fastapi.routing import APIRoute

# On imprime toutes les routes connues par l'application au démarrage
print("--- DÉBUT DES ROUTES ENREGISTRÉES ---")
for route in app.routes:
    if isinstance(route, APIRoute):
        print(f"Path: {route.path} | Methods: {route.methods}")
print("--- FIN DES ROUTES ENREGISTRÉES ---")
# =========================================================================

if __name__ == "__main__":
    import uvicorn
    # Note: reload=True should be disabled in production
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)