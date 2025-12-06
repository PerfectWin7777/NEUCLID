import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles 

from src.config import settings
from src.firebase_setup import initialize_firebase


from src.api.v1 import geometry_router


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
log = logging.getLogger(__name__)

# --- LIFESPAN (Startup & Shutdown) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code executed on startup
    log.info("🚀 Starting NEUCLID API...")
    try:
        initialize_firebase()
    except Exception as e:
        log.error(f"Emergency shutdown: Unable to connect to database. {e}")
        # In prod, sys.exit(1)
    
    yield
    
    # Code executed on shutdown
    log.info("🛑 Stopping NEUCLID API...")



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
app.include_router(geometry_router.router, prefix=settings.API_V1_STR) 



@app.get("/")
async def root():
    """
    Health check endpoint.
    """
    return {
        "message": "Welcome to Neuclid API",
        "status": "running",
        "version": "0.1.0",
        "project": settings.PROJECT_NAME
    }

if __name__ == "__main__":
    import uvicorn
    # Note: reload=True should be disabled in production
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)