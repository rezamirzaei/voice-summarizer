from __future__ import annotations

from pathlib import Path
from uuid import UUID

import pytest
from app.domain.enums import Genre, JobStatus
from app.domain.models import JobPreferences
from app.infrastructure.jobs.manager import JobManager, JobNotFoundError


def test_job_manager_lifecycle(tmp_path: Path) -> None:
    manager = JobManager()
    audio_input_path = tmp_path / "source.wav"
    audio_input_path.write_bytes(b"demo")

    preferences = JobPreferences(target_minutes=3, genre=Genre.SOCIAL)
    job = manager.create_job(audio_input_path=audio_input_path, preferences=preferences)

    running = manager.mark_running(job.id)
    assert running.status == JobStatus.RUNNING

    output_audio_path = tmp_path / "output.wav"
    reference_clip_path = tmp_path / "reference.wav"
    completed = manager.mark_completed(
        job_id=job.id,
        transcript_text="transcript",
        summary_text="summary",
        output_audio_path=output_audio_path,
        reference_clip_path=reference_clip_path,
    )

    assert completed.status == JobStatus.COMPLETED
    assert completed.summary_text == "summary"
    assert completed.output_audio_path == output_audio_path
    assert completed.reference_clip_path == reference_clip_path


def test_job_manager_raises_for_unknown_id() -> None:
    manager = JobManager()
    with pytest.raises(JobNotFoundError):
        manager.mark_failed(
            job_id=UUID("00000000-0000-0000-0000-000000000000"), error_message="boom"
        )
