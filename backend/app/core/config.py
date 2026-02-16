from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        populate_by_name=True,
    )

    app_name: str = Field(default="Voice Summarize Platform", alias="APP_NAME")
    api_prefix: str = Field(default="/api/v1", alias="API_PREFIX")

    uploads_dir: Path = Field(default=Path("data/uploads"), alias="UPLOADS_DIR")
    outputs_dir: Path = Field(default=Path("data/outputs"), alias="OUTPUTS_DIR")

    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="llama3", alias="OLLAMA_MODEL")

    whisper_model_size: str = Field(default="small", alias="WHISPER_MODEL_SIZE")
    whisper_compute_type: str = Field(default="int8", alias="WHISPER_COMPUTE_TYPE")
    transcript_language: str = Field(default="en", alias="TRANSCRIPT_LANGUAGE")

    tts_model_name: str = Field(
        default="tts_models/multilingual/multi-dataset/xtts_v2",
        alias="TTS_MODEL_NAME",
    )
    tts_use_gpu: bool = Field(default=False, alias="TTS_USE_GPU")
    coqui_tos_agreed: bool = Field(default=False, alias="COQUI_TOS_AGREED")

    min_target_minutes: int = Field(default=1, alias="MIN_TARGET_MINUTES", ge=1)
    max_target_minutes: int = Field(default=20, alias="MAX_TARGET_MINUTES", le=120)
    sample_clip_seconds: int = Field(default=25, alias="SAMPLE_CLIP_SECONDS", ge=3, le=120)

    cors_origins: Annotated[tuple[str, ...], NoDecode] = Field(
        default=("http://localhost:8080",),
        alias="CORS_ORIGINS",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _parse_cors_origins(cls, value: object) -> tuple[str, ...]:
        if isinstance(value, str):
            return tuple(origin.strip() for origin in value.split(",") if origin.strip())
        if isinstance(value, tuple):
            return value
        if isinstance(value, list):
            return tuple(str(item) for item in value)
        raise TypeError("CORS_ORIGINS must be a comma-separated string or list")


def ensure_directories(settings: Settings) -> None:
    """Create storage directories if they do not exist."""

    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    settings.outputs_dir.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    ensure_directories(settings)
    return settings
