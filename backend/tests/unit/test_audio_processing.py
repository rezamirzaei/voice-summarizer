from __future__ import annotations

import pytest
from app.infrastructure.audio.processing import minutes_to_target_words


def test_minutes_to_target_words_uses_default_rate() -> None:
    assert minutes_to_target_words(minutes=3) == 435


def test_minutes_to_target_words_supports_custom_rate() -> None:
    assert minutes_to_target_words(minutes=2, words_per_minute=160) == 320


def test_minutes_to_target_words_rejects_invalid_values() -> None:
    with pytest.raises(ValueError):
        minutes_to_target_words(minutes=0)

    with pytest.raises(ValueError):
        minutes_to_target_words(minutes=2, words_per_minute=70)
