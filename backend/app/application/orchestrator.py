from __future__ import annotations

from uuid import UUID

from app.application.pipeline.graph import SummarizationPipeline
from app.infrastructure.jobs.manager import JobManager
from app.infrastructure.storage.file_store import FileStorageService


class JobOrchestrator:
    """Run full summarization jobs and update lifecycle state."""

    def __init__(
        self,
        pipeline: SummarizationPipeline,
        storage: FileStorageService,
        job_manager: JobManager,
    ) -> None:
        self._pipeline = pipeline
        self._storage = storage
        self._job_manager = job_manager

    def process_job(self, job_id: UUID) -> None:
        job = self._job_manager.mark_running(job_id)

        try:
            final_state = self._pipeline.run(
                {
                    "job_id": job.id,
                    "audio_input_path": job.audio_input_path,
                    "preferences": job.preferences,
                }
            )
            transcript_text = final_state["transcript_text"]
            summary_text = final_state["summary_text"]
            output_audio_path = final_state["output_audio_path"]
            reference_clip_path = final_state["reference_clip_path"]

            self._storage.save_transcript(job.id, transcript_text)
            self._job_manager.mark_completed(
                job_id=job.id,
                transcript_text=transcript_text,
                summary_text=summary_text,
                output_audio_path=output_audio_path,
                reference_clip_path=reference_clip_path,
            )
        except Exception as exc:
            self._job_manager.mark_failed(job.id, str(exc))
