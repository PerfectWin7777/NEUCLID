import os
from pathlib import Path
from typing import List, Union, Optional

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # --- Base ---
    PROJECT_NAME: str
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str

    # --- Paths ---
    # Logic to dynamically find the project root.
    # Since config.py is in neuclid/backend/src/config.py:
    # .parent (src) -> .parent (backend)
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    
    # Directory to store temporary files (PDFs/Images)
    TEMP_BUILD_DIR: Path = BASE_DIR / "temp_build"

    # --- CORS (Frontend URLs) ---
    # List of URLs allowed to call the API
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # --- Firebase ---
    FIREBASE_CREDENTIALS_PATH: str

    @property
    def GOOGLE_APPLICATION_CREDENTIALS(self) -> str:
        """Returns the absolute path to the Firebase JSON credentials file."""
        return str(self.BASE_DIR / self.FIREBASE_CREDENTIALS_PATH)

    # --- LLM Keys ---
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None

    # Pydantic configuration to read the .env file
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore" # Ignore .env variables not declared here
    )

# Unique settings instance
settings = Settings()

# Automatically create temp directory on startup if it doesn't exist
if not settings.TEMP_BUILD_DIR.exists():
    settings.TEMP_BUILD_DIR.mkdir(parents=True, exist_ok=True)