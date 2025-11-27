"""Routes for interacting with RMS projects."""

from fastapi import APIRouter, HTTPException, status

from fmu_settings_api.deps.rms import OpenedRmsProjectDep, RmsServiceDep
from fmu_settings_api.deps.session import ProjectSessionDep
from fmu_settings_api.models.rms import (
    HorizonList,
    RMSVersion,
    StratigraphicColumn,
    WellList,
)
from fmu_settings_api.session import (
    add_rms_project_to_session,
    remove_rms_project_from_project_session,
)
from fmu_settings_api.v1.responses import GetSessionResponses

router = APIRouter(prefix="/rms", tags=["rms"])


@router.post(
    "/open",
    status_code=status.HTTP_200_OK,
    summary="Open an RMS project and store it in the session",
    responses=GetSessionResponses,
)
async def open_rms_project(
    rms_service: RmsServiceDep,
    project_session: ProjectSessionDep,
    rms_version: RMSVersion | None = None,
) -> dict[str, str]:
    """Open an RMS project and store it in the session.

    The RMS project path must be configured in the project's .fmu config file.
    Once opened, the project remains open in the session until explicitly closed
    or the session expires. This allows for efficient repeated access without
    reopening the project each time.

    Args:
        rms_service: RMS service instance
        project_session: Current project session
        rms_version: RMS version specification (default: 14.2.2)

    Returns:
        A success message
    """
    if rms_version is None:
        rms_version = RMSVersion()

    try:
        opened_project = rms_service.open_rms_project(version=rms_version.version)
        await add_rms_project_to_session(project_session.id, opened_project)
        return {"message": "RMS project opened successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to open RMS project: {str(e)}",
        ) from e


@router.delete(
    "/close",
    status_code=status.HTTP_200_OK,
    summary="Close the RMS project in the session",
    responses=GetSessionResponses,
)
async def close_rms_project(
    project_session: ProjectSessionDep,
) -> dict[str, str]:
    """Close the RMS project that is currently open in the session.

    This removes the RMS project reference from the session. The project
    should be closed when it is no longer needed to free up resources.

    Returns:
        A success message
    """
    try:
        await remove_rms_project_from_project_session(project_session.id)
        return {"message": "RMS project closed successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to close RMS project: {str(e)}",
        ) from e


@router.get(
    "/stratigraphic_column",
    response_model=StratigraphicColumn,
    summary="Get the stratigraphic column from the open RMS project",
    responses=GetSessionResponses,
)
async def get_stratigraphic_column(
    rms_service: RmsServiceDep,
    opened_rms_project: OpenedRmsProjectDep,
) -> StratigraphicColumn:
    """Retrieve the stratigraphic column from the currently open RMS project.

    This endpoint requires an RMS project to be open in the session.
    Use the POST /open endpoint first to open an RMS project.

    Returns:
        The stratigraphic column containing zones with their horizons
    """
    try:
        return rms_service.get_strat_column(opened_rms_project)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve stratigraphic column: {str(e)}",
        ) from e


@router.get(
    "/horizons",
    response_model=HorizonList,
    summary="Get all horizons from the open RMS project",
    responses=GetSessionResponses,
)
async def get_horizons(
    rms_service: RmsServiceDep,
    opened_rms_project: OpenedRmsProjectDep,
) -> HorizonList:
    """Retrieve all horizons from the currently open RMS project.

    This endpoint requires an RMS project to be open in the session.
    Use the POST /open endpoint first to open an RMS project.

    Returns:
        List of horizons in the project
    """
    try:
        return rms_service.get_horizons(opened_rms_project)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve horizons: {str(e)}",
        ) from e


@router.get(
    "/wells",
    response_model=WellList,
    summary="Get all wells from the open RMS project",
    responses=GetSessionResponses,
)
async def get_wells(
    rms_service: RmsServiceDep,
    opened_rms_project: OpenedRmsProjectDep,
) -> WellList:
    """Retrieve all wells from the currently open RMS project.

    This endpoint requires an RMS project to be open in the session.
    Use the POST /open endpoint first to open an RMS project.

    Returns:
        List of wells in the project
    """
    try:
        return rms_service.get_wells(opened_rms_project)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve wells: {str(e)}",
        ) from e
