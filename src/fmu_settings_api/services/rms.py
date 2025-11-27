"""Service for managing RMS projects through the RMS API."""

import os
from pathlib import Path

from runrms import get_rmsapi
from runrms.api import RmsApiProxy

from fmu_settings_api.models.rms import (
    Horizon,
    HorizonList,
    StratigraphicColumn,
    StratigraphicZone,
    Well,
    WellList,
)

from .project import ProjectService


def get_system_config_path() -> Path:
    """Get the path to the system runrms config based on KOMODO_RELEASE."""
    komodo_release = os.environ.get("KOMODO_RELEASE")
    if not komodo_release:
        raise RuntimeError("KOMODO_RELEASE environment variable is not set")
    return Path(
        f"/prog/res/komodo/{komodo_release}/root/lib/python3.11/site-packages/rms_sys/config/runrms.yml"
    )


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

        rms_proxy = get_rmsapi(
            version=version, config_path=str(get_system_config_path())
        )
        return rms_proxy.Project.open(str(rms_project_path), readonly=True)

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

    def get_horizons(self, rms_project: RmsApiProxy) -> HorizonList:
        """Retrieve all horizons from the RMS project.

        Args:
            rms_project: The opened RMS project proxy

        Returns:
            HorizonList: List of horizons in the project
        """
        horizons = []
        for horizon in rms_project.horizons:
            horizons.append(Horizon(name=horizon.name.get()))
        return HorizonList(horizons=horizons)

    def get_wells(self, rms_project: RmsApiProxy) -> WellList:
        """Retrieve all wells from the RMS project.

        Args:
            rms_project: The opened RMS project proxy

        Returns:
            WellList: List of wells in the project
        """
        wells = []
        for well in rms_project.wells:
            wells.append(Well(name=well.name.get()))
        return WellList(wells=wells)
