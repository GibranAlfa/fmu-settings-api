"""RMS service dependencies."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from runrms.api import RmsApiProxy

from fmu_settings_api.services.rms import RmsService

from .project import ProjectServiceDep
from .session import ProjectSessionDep


async def get_rms_service(
    project_service: ProjectServiceDep,
) -> RmsService:
    """Returns an RmsService instance.

    Args:
        project_service: The project service

    Returns:
        RmsService: The RMS service instance
    """
    return RmsService(project_service)


RmsServiceDep = Annotated[RmsService, Depends(get_rms_service)]


async def get_opened_rms_project(
    project_session: ProjectSessionDep,
) -> RmsApiProxy:
    """Returns the opened RMS project from the session.

    Args:
        project_session: The current project session

    Returns:
        RmsApiProxy: The opened RMS project proxy

    Raises:
        HTTPException: If no RMS project is open in the session
    """
    if project_session.rms_project is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "No RMS project is currently open. Please open an RMS project first."
            ),
        )
    return project_session.rms_project


RmsProjectDep = Annotated[RmsApiProxy, Depends(get_opened_rms_project)]
