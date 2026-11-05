"""Sumo service and query parameter dependencies."""

from typing import Annotated

from fastapi import Depends, Query

from fmu_settings_api.services.sumo import SumoService


def get_sumo_service() -> SumoService:
    """Return a Sumo service."""
    return SumoService()


SumoServiceDep = Annotated[SumoService, Depends(get_sumo_service)]


def get_sumo_force_refresh(
    force_refresh: Annotated[
        bool,
        Query(description="Invalidate cached Microsoft access tokens before login."),
    ] = False,
) -> bool:
    """Return whether the Sumo login must refresh cached access tokens."""
    return force_refresh


SumoForceRefreshDep = Annotated[bool, Depends(get_sumo_force_refresh)]
