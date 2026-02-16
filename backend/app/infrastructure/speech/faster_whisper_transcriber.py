from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from app.core.config import Settings

if TYPE_CHECKING:
    from faster_whisper import WhisperModel


class WhisperTranscriptionService:
    """Local speech-to-text service built on faster-whisper."""

    def __init__(self, settings: Settings) -> None:
        self._model_size = settings.whisper_model_size
        self._compute_type = settings.whisper_compute_type
        self._model: WhisperModel | None = None

    def transcribe(self, audio_path: Path, language: str) -> str:
        model = self._get_model()
        segments, _ = model.transcribe(str(audio_path), language=language)

        text_chunks: list[str] = []
        for segment in segments:
            segment_text = str(getattr(segment, "text", "")).strip()
            if segment_text:
                text_chunks.append(segment_text)

        transcript = " ".join(text_chunks).strip()
        if not transcript:
            raise ValueError("Transcription result is empty")
        return transcript

    def _get_model(self) -> WhisperModel:
        if self._model is None:
            from faster_whisper import WhisperModel

            self._model = WhisperModel(self._model_size, compute_type=self._compute_type)
        return self._model
