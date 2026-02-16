from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.enums import Genre, JobStatus
from app.domain.models import JobRecord


class JobCreateResponse(BaseModel):
    job_id: UUID
    status: JobStatus


class JobStatusResponse(BaseModel):
    job_id: UUID
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    genre: Genre
    target_minutes: int
    summary_text: str | None = None
    error_message: str | None = None
    audio_url: str | None = None

    @classmethod
    def from_job(cls, job: JobRecord, audio_url: str | None = None) -> JobStatusResponse:
        return cls(
            job_id=job.id,
            status=job.status,
            created_at=job.created_at,
            updated_at=job.updated_at,
            genre=job.preferences.genre,
            target_minutes=job.preferences.target_minutes,
            summary_text=job.summary_text,
            error_message=job.error_message,
            audio_url=audio_url,
        )


class GenreListResponse(BaseModel):
    genres: list[Genre]


class CreateJobForm(BaseModel):
    target_minutes: int = Field(ge=1, le=120)
    genre: Genre
