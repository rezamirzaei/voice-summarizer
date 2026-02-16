from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from app.core.config import Settings

if TYPE_CHECKING:
    from TTS.api import TTS


class CoquiVoiceCloningService:
    """Clone speaker voice using Coqui XTTS and a reference clip."""

    def __init__(self, settings: Settings) -> None:
        self._model_name = settings.tts_model_name
        self._use_gpu = settings.tts_use_gpu
        self._model: TTS | None = None

    def synthesize(self, text: str, speaker_wav: Path, language: str, output_path: Path) -> Path:
        if not text.strip():
            raise ValueError("Summary text cannot be empty")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        model = self._get_model()
        model.tts_to_file(
            text=text,
            speaker_wav=str(speaker_wav),
            language=language,
            file_path=str(output_path),
        )
        return output_path

    def _get_model(self) -> TTS:
        if self._model is None:
            try:
                from TTS.api import TTS
            except ModuleNotFoundError as exc:
                raise RuntimeError(
                    "Coqui TTS is not installed in this environment. "
                    "Use the Docker deployment for full voice cloning support."
                ) from exc

            self._model = TTS(model_name=self._model_name, progress_bar=False, gpu=self._use_gpu)
        return self._model
