from __future__ import annotations

from pathlib import Path
from typing import NotRequired, TypedDict
from uuid import UUID

from app.domain.models import JobPreferences


class PipelineState(TypedDict):
    job_id: UUID
    audio_input_path: Path
    preferences: JobPreferences

    transcript_text: NotRequired[str]
    summary_text: NotRequired[str]
    reference_clip_path: NotRequired[Path]
    output_audio_path: NotRequired[Path]
