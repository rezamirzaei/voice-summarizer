from __future__ import annotations

from pathlib import Path

from app.core.config import Settings, ensure_directories


def test_settings_parse_cors_and_create_dirs(tmp_path: Path) -> None:
    uploads = tmp_path / "uploads"
    outputs = tmp_path / "outputs"

    settings = Settings(
        UPLOADS_DIR=uploads,
        OUTPUTS_DIR=outputs,
        CORS_ORIGINS=("http://localhost:8080", "http://localhost:3000"),
    )
    ensure_directories(settings)

    assert settings.cors_origins == ("http://localhost:8080", "http://localhost:3000")
    assert uploads.exists()
    assert outputs.exists()
