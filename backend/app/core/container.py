from __future__ import annotations

from dataclasses import dataclass

from app.application.orchestrator import JobOrchestrator
from app.application.pipeline.graph import SummarizationPipeline
from app.application.pipeline.nodes import PipelineNodes
from app.core.config import Settings
from app.infrastructure.jobs.manager import JobManager
from app.infrastructure.llm.llama_summarizer import LlamaSummarizationService
from app.infrastructure.speech.coqui_voice_cloner import CoquiVoiceCloningService
from app.infrastructure.speech.faster_whisper_transcriber import WhisperTranscriptionService
from app.infrastructure.storage.file_store import FileStorageService


@dataclass(frozen=True, slots=True)
class ServiceContainer:
    settings: Settings
    storage: FileStorageService
    jobs: JobManager
    orchestrator: JobOrchestrator


def build_container(settings: Settings) -> ServiceContainer:
    storage = FileStorageService(settings)
    jobs = JobManager()

    transcriber = WhisperTranscriptionService(settings)
    summarizer = LlamaSummarizationService(settings)
    voice_cloner = CoquiVoiceCloningService(settings)

    nodes = PipelineNodes(
        settings=settings,
        storage=storage,
        transcriber=transcriber,
        summarizer=summarizer,
        voice_cloner=voice_cloner,
    )
    pipeline = SummarizationPipeline(nodes)

    orchestrator = JobOrchestrator(
        pipeline=pipeline,
        storage=storage,
        job_manager=jobs,
    )

    return ServiceContainer(
        settings=settings,
        storage=storage,
        jobs=jobs,
        orchestrator=orchestrator,
    )
