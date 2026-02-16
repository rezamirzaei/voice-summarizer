from enum import StrEnum


class Genre(StrEnum):
    GENERAL = "general"
    ECONOMICAL = "economical"
    SOCIAL = "social"
    TECHNICAL = "technical"
    NEWS = "news"


class JobStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
