from __future__ import annotations

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from app.core.config import Settings
from app.domain.models import JobPreferences
from app.infrastructure.audio.processing import minutes_to_target_words


class LlamaSummarizationService:
    """Summarize transcript text with local Llama model via Ollama."""

    def __init__(self, settings: Settings) -> None:
        self._llm = ChatOllama(
            model=settings.ollama_model,
            base_url=settings.ollama_base_url,
            temperature=0.2,
        )
        self._prompt = ChatPromptTemplate.from_template(
            """
You are a specialist summarizer.
Create a concise spoken summary in plain language.

Constraints:
- Genre focus: {genre}
- Target length: around {target_words} words
- Keep factual accuracy and continuity
- Output only the summary text

Transcript:
{transcript}
""".strip()
        )

    def summarize(self, transcript: str, preferences: JobPreferences) -> str:
        if not transcript.strip():
            raise ValueError("Transcript is empty")

        target_words = minutes_to_target_words(preferences.target_minutes)
        chain = self._prompt | self._llm | StrOutputParser()
        summary = chain.invoke(
            {
                "genre": preferences.genre.value,
                "target_words": target_words,
                "transcript": transcript,
            }
        )
        cleaned = summary.strip()
        if not cleaned:
            raise ValueError("LLM generated an empty summary")
        return cleaned
