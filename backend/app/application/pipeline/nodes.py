from __future__ import annotations

from app.application.pipeline.state import PipelineState
from app.core.config import Settings
from app.infrastructure.audio.processing import extract_reference_clip
from app.infrastructure.llm.llama_summarizer import LlamaSummarizationService
from app.infrastructure.speech.coqui_voice_cloner import CoquiVoiceCloningService
from app.infrastructure.speech.faster_whisper_transcriber import WhisperTranscriptionService
from app.infrastructure.storage.file_store import FileStorageService


class PipelineNodes:
    """LangGraph nodes for transcription, summarization, and voice synthesis."""

    def __init__(
        self,
        settings: Settings,
        storage: FileStorageService,
        transcriber: WhisperTranscriptionService,
        summarizer: LlamaSummarizationService,
        voice_cloner: CoquiVoiceCloningService,
    ) -> None:
        self._settings = settings
        self._storage = storage
        self._transcriber = transcriber
        self._summarizer = summarizer
        self._voice_cloner = voice_cloner

    def transcribe(self, state: PipelineState) -> dict[str, object]:
        transcript_text = self._transcriber.transcribe(
            audio_path=state["audio_input_path"],
            language=self._settings.transcript_language,
        )
        return {"transcript_text": transcript_text}

    def summarize(self, state: PipelineState) -> dict[str, object]:
        transcript_text = state["transcript_text"]
        summary_text = self._summarizer.summarize(
            transcript=transcript_text,
            preferences=state["preferences"],
        )
        return {"summary_text": summary_text}

    def prepare_reference_clip(self, state: PipelineState) -> dict[str, object]:
        job_id = state["job_id"]
        reference_clip_path = self._storage.build_reference_clip_path(job_id)
        clip_path = extract_reference_clip(
            source_path=state["audio_input_path"],
            destination_path=reference_clip_path,
            seconds=self._settings.sample_clip_seconds,
        )
        return {"reference_clip_path": clip_path}

    def synthesize(self, state: PipelineState) -> dict[str, object]:
        output_path = self._storage.build_output_audio_path(state["job_id"])
        rendered_path = self._voice_cloner.synthesize(
            text=state["summary_text"],
            speaker_wav=state["reference_clip_path"],
            language=self._settings.transcript_language,
            output_path=output_path,
        )
        return {"output_audio_path": rendered_path}
