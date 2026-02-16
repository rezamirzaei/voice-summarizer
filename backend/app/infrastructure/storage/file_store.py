from __future__ import annotations

from pathlib import Path
from uuid import UUID, uuid4

import aiofiles
from fastapi import UploadFile

from app.core.config import Settings


class FileStorageService:
    """Persist uploads and generated artifacts on local disk."""

    _ALLOWED_EXTENSIONS: tuple[str, ...] = (".wav", ".mp3", ".m4a", ".flac", ".ogg")

    def __init__(self, settings: Settings) -> None:
        self._uploads_dir = settings.uploads_dir
        self._outputs_dir = settings.outputs_dir

    async def save_uploaded_audio(self, upload: UploadFile) -> Path:
        filename = upload.filename or "audio.wav"
        suffix = Path(filename).suffix.lower() or ".wav"
        if suffix not in self._ALLOWED_EXTENSIONS:
            raise ValueError(f"Unsupported file extension: {suffix}")

        stored_path = self._uploads_dir / f"{uuid4()}{suffix}"
        await self._write_upload(upload, stored_path)
        return stored_path

    def build_reference_clip_path(self, job_id: UUID) -> Path:
        return self._outputs_dir / f"{job_id}_reference.wav"

    def build_transcript_path(self, job_id: UUID) -> Path:
        return self._outputs_dir / f"{job_id}.txt"

    def build_output_audio_path(self, job_id: UUID) -> Path:
        return self._outputs_dir / f"{job_id}.wav"

    def save_transcript(self, job_id: UUID, transcript_text: str) -> Path:
        transcript_path = self.build_transcript_path(job_id)
        transcript_path.parent.mkdir(parents=True, exist_ok=True)
        transcript_path.write_text(transcript_text, encoding="utf-8")
        return transcript_path

    @staticmethod
    async def _write_upload(upload: UploadFile, target: Path) -> None:
        target.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(target, "wb") as output:
            while True:
                chunk = await upload.read(1024 * 1024)
                if not chunk:
                    break
                await output.write(chunk)
        await upload.close()
