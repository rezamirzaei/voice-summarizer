from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.api.deps import get_container, get_settings_dependency
from app.api.schemas.jobs import (
    CreateJobForm,
    GenreListResponse,
    JobCreateResponse,
    JobStatusResponse,
)
from app.core.config import Settings
from app.core.container import ServiceContainer
from app.domain.enums import Genre, JobStatus
from app.domain.models import JobPreferences

router = APIRouter(prefix="/jobs", tags=["jobs"])
TARGET_MINUTES_FORM = Form(...)
GENRE_FORM = Form(...)
AUDIO_FILE_FORM = File(...)
CONTAINER_DEPENDENCY = Depends(get_container)
SETTINGS_DEPENDENCY = Depends(get_settings_dependency)


@router.get("/genres", response_model=GenreListResponse)
def list_genres() -> GenreListResponse:
    return GenreListResponse(genres=list(Genre))


def validate_form(
    target_minutes: int = TARGET_MINUTES_FORM,
    genre: Genre = GENRE_FORM,
    settings: Settings = SETTINGS_DEPENDENCY,
) -> CreateJobForm:
    form = CreateJobForm(target_minutes=target_minutes, genre=genre)
    if not settings.min_target_minutes <= form.target_minutes <= settings.max_target_minutes:
        raise HTTPException(
            status_code=422,
            detail=(
                f"target_minutes must be between {settings.min_target_minutes} and "
                f"{settings.max_target_minutes}"
            ),
        )
    return form


FORM_DEPENDENCY = Depends(validate_form)


@router.post("", response_model=JobCreateResponse, status_code=202)
async def create_job(
    background_tasks: BackgroundTasks,
    form: CreateJobForm = FORM_DEPENDENCY,
    audio_file: UploadFile = AUDIO_FILE_FORM,
    container: ServiceContainer = CONTAINER_DEPENDENCY,
) -> JobCreateResponse:
    try:
        audio_input_path = await container.storage.save_uploaded_audio(audio_file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    preferences = JobPreferences(
        target_minutes=form.target_minutes,
        genre=form.genre,
    )
    job = container.jobs.create_job(
        audio_input_path=audio_input_path,
        preferences=preferences,
    )

    background_tasks.add_task(container.orchestrator.process_job, job.id)

    return JobCreateResponse(job_id=job.id, status=job.status)


@router.get("/{job_id}", response_model=JobStatusResponse)
def get_job_status(
    job_id: UUID,
    container: ServiceContainer = CONTAINER_DEPENDENCY,
) -> JobStatusResponse:
    job = container.jobs.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    audio_url: str | None = None
    if job.status == JobStatus.COMPLETED and job.output_audio_path is not None:
        audio_url = f"{container.settings.api_prefix}/jobs/{job.id}/audio"

    return JobStatusResponse.from_job(job=job, audio_url=audio_url)


@router.get("/{job_id}/audio")
def download_audio(
    job_id: UUID,
    container: ServiceContainer = CONTAINER_DEPENDENCY,
) -> FileResponse:
    job = container.jobs.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != JobStatus.COMPLETED or job.output_audio_path is None:
        raise HTTPException(status_code=409, detail="Audio is not ready")
    if not job.output_audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")

    return FileResponse(
        path=job.output_audio_path,
        media_type="audio/wav",
        filename=f"summary-{job.id}.wav",
    )
