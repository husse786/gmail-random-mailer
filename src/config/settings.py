from __future__ import annotations

import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError


class Settings(BaseModel):
    openai_api_key: str = Field(..., min_length=1)
    openai_model: str = Field(default="gpt-4.1-mini", min_length=1)

    gmail_address: str = Field(..., min_length=1)
    gmail_app_password: str = Field(..., min_length=1)

    default_interval_seconds: int = Field(default=120, ge=10, le=3600)


def load_settings() -> Settings:
    """
    Lädt .env in die Prozess-ENV und validiert alle benötigten Werte.
    Wirft bei Fehlern eine klare Exception.
    """
    load_dotenv()  # lädt .env falls vorhanden

    try:
        return Settings(
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            gmail_address=os.getenv("GMAIL_ADDRESS", ""),
            gmail_app_password=os.getenv("GMAIL_APP_PASSWORD", ""),
            default_interval_seconds=int(os.getenv("DEFAULT_INTERVAL_SECONDS", "120")),
        )
    except ValidationError as e:
        # Kurz & klar: welche Variablen fehlen/invalid sind
        raise RuntimeError(f"Konfiguration ungültig oder unvollständig: {e}") from e