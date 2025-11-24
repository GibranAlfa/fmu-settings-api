"""Service for managing RMS projects through the RMS API."""

from runrms import get_rmsapi
from runrms.api import RmsApiProxy

from fmu_settings_api.models.rms import StratigraphicColumn, StratigraphicZone

from .project import ProjectService


class RmsService:
    """Service for handling RMS projects."""

    def __init__(self, project_service: ProjectService) -> None:
        """Initialize the RMS service with a project service."""
        self._project_service = project_service

    def open_rms_project(self, version: str = "14.2.2") -> RmsApiProxy:
        """Open an RMS project at the specified path.

        Args:
            version: RMS version to use (default: 14.2.2)

        Returns:
            RmsApiProxy: The opened RMS project proxy

        Raises:
            ValueError: If RMS project path is not set in config file
        """
        rms_project_path = self._project_service.rms_project_path
        if rms_project_path is None:
            raise ValueError("RMS project path is not set in config file.")

        rms_proxy = get_rmsapi(version=version)
        return rms_proxy.Project.open(rms_project_path, readonly=True)

    def get_strat_column(self, rms_project: RmsApiProxy) -> StratigraphicColumn:
        """Retrieve the stratigraphic column from the RMS project.

        Args:
            rms_project: The opened RMS project proxy

        Returns:
            StratigraphicColumn: The stratigraphic column with zones
        """
        zones = []
        for zone in rms_project.zones:
            strat_zone = StratigraphicZone(
                name=zone.name.get(),
                top=zone.horizon_above.name.get(),
                base=zone.horizon_below.name.get(),
            )
            zones.append(strat_zone)
        return StratigraphicColumn(zones=zones)
