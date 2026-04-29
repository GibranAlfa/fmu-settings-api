"""Service for managing mappings in .fmu and business logic."""

from pathlib import Path
from typing import Self

from fmu.datamodels.context.mappings import (
    DataSystem,
    MappingType,
    StratigraphyMappings,
)
from fmu.settings import ProjectFMUDirectory
from fmu.settings.models.mappings import Mappings


class MappingsService:
    """Service for handling mappings."""

    def __init__(self, fmu_dir: ProjectFMUDirectory) -> None:
        """Initialize the service with a project FMU directory."""
        self._fmu_dir = fmu_dir

    @property
    def fmu_dir_path(self) -> Path:
        """Returns the path to the .fmu directory."""
        return self._fmu_dir.path

    def list_stratigraphy_mappings(self: Self) -> StratigraphyMappings:
        """Get all the stratigraphy mappings in the FMU directory."""
        return self._fmu_dir.mappings.stratigraphy_mappings

    def update_stratigraphy_mappings(
        self: Self, stratigraphy_mappings: StratigraphyMappings
    ) -> StratigraphyMappings:
        """Save stratigraphy mappings to the mappings resource.

        All existing stratigraphy mappings will be overwritten.
        """
        return self._fmu_dir.mappings.update_stratigraphy_mappings(
            stratigraphy_mappings
        )

    def get_mappings(self, mapping_type: MappingType) -> Mappings:
        """Get mappings for a specific mapping type.

        Raises:
            ValueError: If mapping type is unsupported
        """
        if mapping_type == MappingType.stratigraphy:
            return Mappings(stratigraphy=self.list_stratigraphy_mappings())

        raise ValueError(f"Mapping type '{mapping_type}' is not yet supported")

    def get_mappings_by_source_system(
        self,
        mapping_type: MappingType,
        source_system: DataSystem,
    ) -> Mappings:
        """Get mappings filtered by mapping type and source system.

        Raises:
            ValueError: If mapping type is unsupported
        """
        if mapping_type == MappingType.stratigraphy:
            filtered_mappings = StratigraphyMappings(
                root=[
                    mapping
                    for mapping in self.list_stratigraphy_mappings()
                    if mapping.source_system == source_system
                ]
            )
            return Mappings(stratigraphy=filtered_mappings)

        raise ValueError(f"Mapping type '{mapping_type}' is not yet supported")

    def update_mappings_by_source_system(
        self,
        mapping_type: MappingType,
        source_system: DataSystem,
        mappings: StratigraphyMappings,
    ) -> None:
        """Replace mappings for a specific mapping type and source system.

        Raises:
            ValueError: If mapping type is unsupported
        """
        if mapping_type == MappingType.stratigraphy:
            if any(mapping.source_system != source_system for mapping in mappings):
                raise ValueError(
                    "All mappings in the request body must use the requested "
                    f"source system '{source_system.value}'"
                )

            try:
                other_mappings = [
                    mapping
                    for mapping in self.list_stratigraphy_mappings()
                    if mapping.source_system != source_system
                ]
            except FileNotFoundError:
                other_mappings = []

            self.update_stratigraphy_mappings(
                StratigraphyMappings(root=[*mappings, *other_mappings])
            )
            return

        raise ValueError(f"Mapping type '{mapping_type}' is not yet supported")
