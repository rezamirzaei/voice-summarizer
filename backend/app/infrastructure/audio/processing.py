from __future__ import annotations

from pathlib import Path


def minutes_to_target_words(minutes: int, words_per_minute: int = 145) -> int:
    """Estimate a concise spoken summary length in words."""

    if minutes < 1:
        raise ValueError("minutes must be >= 1")
    if words_per_minute < 80:
        raise ValueError("words_per_minute must be >= 80")
    return minutes * words_per_minute


def extract_reference_clip(source_path: Path, destination_path: Path, seconds: int) -> Path:
    """Extract the first N seconds from source audio as a WAV speaker reference."""

    if seconds < 1:
        raise ValueError("seconds must be >= 1")

    from pydub import AudioSegment

    audio = AudioSegment.from_file(source_path)
    clipped = audio[: seconds * 1000]
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    clipped.export(destination_path, format="wav")
    return destination_path
