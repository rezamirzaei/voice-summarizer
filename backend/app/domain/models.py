from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import Genre, JobStatus


class JobPreferences(BaseModel):
    """User-provided summarization preferences."""

    model_config = ConfigDict(frozen=True, strict=True)

    target_minutes: int = Field(ge=1, le=120)
    genre: Genre


class JobRecord(BaseModel):
    """Internal job state."""

    model_config = ConfigDict(validate_assignment=True)

    id: UUID = Field(default_factory=uuid4)
    status: JobStatus = JobStatus.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    audio_input_path: Path
    reference_clip_path: Path | None = None
    output_audio_path: Path | None = None

    preferences: JobPreferences
    transcript_text: str | None = None
    summary_text: str | None = None
    error_message: str | None = None
