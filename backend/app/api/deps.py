from __future__ import annotations

from typing import cast

from fastapi import Request

from app.core.config import Settings, get_settings
from app.core.container import ServiceContainer


def get_container(request: Request) -> ServiceContainer:
    container = getattr(request.app.state, "container", None)
    if container is None:
        raise RuntimeError("Service container is not initialized")
    return cast(ServiceContainer, container)


def get_settings_dependency() -> Settings:
    return get_settings()
