from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from threading import Lock
from uuid import UUID

from app.domain.enums import JobStatus
from app.domain.models import JobPreferences, JobRecord


class JobNotFoundError(KeyError):
    """Raised when a job id does not exist."""


class JobManager:
    """Thread-safe in-memory job registry."""

    def __init__(self) -> None:
        self._jobs: dict[UUID, JobRecord] = {}
        self._lock = Lock()

    def create_job(self, audio_input_path: Path, preferences: JobPreferences) -> JobRecord:
        job = JobRecord(audio_input_path=audio_input_path, preferences=preferences)
        with self._lock:
            self._jobs[job.id] = job
        return job.model_copy(deep=True)

    def list_jobs(self) -> list[JobRecord]:
        with self._lock:
            return [job.model_copy(deep=True) for job in self._jobs.values()]

    def get_job(self, job_id: UUID) -> JobRecord | None:
        with self._lock:
            job = self._jobs.get(job_id)
            return None if job is None else job.model_copy(deep=True)

    def mark_running(self, job_id: UUID) -> JobRecord:
        return self._update_job(job_id, status=JobStatus.RUNNING, error_message=None)

    def mark_completed(
        self,
        job_id: UUID,
        transcript_text: str,
        summary_text: str,
        output_audio_path: Path,
        reference_clip_path: Path,
    ) -> JobRecord:
        return self._update_job(
            job_id,
            status=JobStatus.COMPLETED,
            transcript_text=transcript_text,
            summary_text=summary_text,
            output_audio_path=output_audio_path,
            reference_clip_path=reference_clip_path,
            error_message=None,
        )

    def mark_failed(self, job_id: UUID, error_message: str) -> JobRecord:
        return self._update_job(job_id, status=JobStatus.FAILED, error_message=error_message)

    def _update_job(self, job_id: UUID, **updates: object) -> JobRecord:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                raise JobNotFoundError(str(job_id))

            merged = job.model_dump()
            merged.update(updates)
            merged["updated_at"] = datetime.now(UTC)
            updated = JobRecord.model_validate(merged)
            self._jobs[job_id] = updated
            return updated.model_copy(deep=True)
