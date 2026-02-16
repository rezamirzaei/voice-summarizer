from __future__ import annotations

import pytest
from app.domain.enums import Genre
from app.domain.models import JobPreferences
from pydantic import ValidationError


def test_job_preferences_accepts_valid_payload() -> None:
    preferences = JobPreferences(target_minutes=4, genre=Genre.ECONOMICAL)
    assert preferences.target_minutes == 4
    assert preferences.genre == Genre.ECONOMICAL


def test_job_preferences_rejects_invalid_minutes() -> None:
    with pytest.raises(ValidationError):
        JobPreferences(target_minutes=0, genre=Genre.GENERAL)
