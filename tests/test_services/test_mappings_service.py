"""Tests for the MappingsService."""

from collections.abc import Callable

import pytest
from fmu.datamodels.context.mappings import (
    DataSystem,
    MappingType,
    RelationType,
    StratigraphyIdentifierMapping,
    StratigraphyMappings,
)
from fmu.settings._fmu_dir import ProjectFMUDirectory
from fmu.settings.models.mappings import Mappings

from fmu_settings_api.services.mappings import MappingsService


@pytest.fixture
def mappings_service(fmu_dir: ProjectFMUDirectory) -> MappingsService:
    """Returns a MappingsService instance."""
    return MappingsService(fmu_dir)


def test_get_mappings_returns_stratigraphy(
    mappings_service: MappingsService,
    fmu_dir: ProjectFMUDirectory,
    make_stratigraphy_mappings: Callable[[], StratigraphyMappings],
) -> None:
    """Test fetching stratigraphy mappings returns the mappings resource model."""
    stratigraphy_mappings = make_stratigraphy_mappings()
    fmu_dir.mappings.update_stratigraphy_mappings(stratigraphy_mappings)

    assert mappings_service.get_mappings(MappingType.stratigraphy) == Mappings(
        stratigraphy=stratigraphy_mappings
    )


def test_get_mappings_unsupported_type(
    mappings_service: MappingsService,
) -> None:
    """Test unsupported mapping types raise ValueError on read."""
    with pytest.raises(ValueError, match="not yet supported"):
        mappings_service.get_mappings(MappingType.wellbore)


def test_get_mappings_by_source_system_unsupported_type(
    mappings_service: MappingsService,
) -> None:
    """Test unsupported mapping types raise ValueError on filtered read."""
    with pytest.raises(ValueError, match="not yet supported"):
        mappings_service.get_mappings_by_source_system(
            MappingType.wellbore,
            DataSystem.rms,
        )


def test_update_mappings_by_source_system_replaces_existing_stratigraphy(
    mappings_service: MappingsService,
    fmu_dir: ProjectFMUDirectory,
    make_stratigraphy_mapping: Callable[..., StratigraphyIdentifierMapping],
) -> None:
    """Test updates replace only the stored stratigraphy source partition."""
    initial_mappings = StratigraphyMappings(
        root=[
            make_stratigraphy_mapping(
                "TopVolantis",
                "TopVolantis",
                RelationType.primary,
                source_system=DataSystem.rms,
                target_system=DataSystem.rms,
            ),
            make_stratigraphy_mapping(
                "TopHugin",
                "TopHugin",
                RelationType.primary,
                source_system=DataSystem.simulator,
                target_system=DataSystem.simulator,
            ),
            make_stratigraphy_mapping(
                "TopHugin",
                "HUGIN GP. Top",
                RelationType.primary,
                source_system=DataSystem.simulator,
                target_system=DataSystem.smda,
            ),
        ]
    )
    replacement_mappings = StratigraphyMappings(
        root=[
            make_stratigraphy_mapping(
                "TopViking",
                "TopViking",
                RelationType.primary,
                source_system=DataSystem.rms,
                target_system=DataSystem.rms,
            ),
            make_stratigraphy_mapping(
                "TopViking",
                "VIKING GP. Top",
                RelationType.primary,
                source_system=DataSystem.rms,
                target_system=DataSystem.smda,
            ),
        ]
    )

    fmu_dir.mappings.update_stratigraphy_mappings(initial_mappings)

    mappings_service.update_mappings_by_source_system(
        MappingType.stratigraphy,
        DataSystem.rms,
        replacement_mappings,
    )

    assert fmu_dir.mappings.stratigraphy_mappings == StratigraphyMappings(
        root=[
            replacement_mappings[0],
            replacement_mappings[1],
            initial_mappings[1],
            initial_mappings[2],
        ]
    )


def test_update_mappings_by_source_system_creates_mappings_file_if_missing(
    mappings_service: MappingsService,
    fmu_dir: ProjectFMUDirectory,
    make_stratigraphy_mapping: Callable[..., StratigraphyIdentifierMapping],
) -> None:
    """Test first-time mapping updates create mappings.json instead of failing."""
    mappings_path = fmu_dir.mappings.path
    assert not mappings_path.exists()

    primary = make_stratigraphy_mapping(
        "TopVolantis",
        "TopVolantis",
        RelationType.primary,
        source_system=DataSystem.rms,
        target_system=DataSystem.rms,
    )
    cross_system = make_stratigraphy_mapping(
        "TopVolantis",
        "VOLANTIS GP. Top",
        RelationType.primary,
        source_system=DataSystem.rms,
        target_system=DataSystem.smda,
    )
    mappings = StratigraphyMappings(root=[primary, cross_system])

    mappings_service.update_mappings_by_source_system(
        MappingType.stratigraphy,
        DataSystem.rms,
        mappings,
    )

    assert mappings_path.exists()
    assert fmu_dir.mappings.stratigraphy_mappings == mappings


def test_update_mappings_by_source_system_supports_unmappable(
    mappings_service: MappingsService,
    fmu_dir: ProjectFMUDirectory,
    make_stratigraphy_mapping: Callable[..., StratigraphyIdentifierMapping],
) -> None:
    """Test source partition updates support unmappable cross-system mappings."""
    primary = make_stratigraphy_mapping(
        "TopUnmapped",
        "TopUnmapped",
        RelationType.primary,
        source_system=DataSystem.rms,
        target_system=DataSystem.rms,
    )
    unmappable = make_stratigraphy_mapping(
        "TopUnmapped",
        None,
        RelationType.unmappable,
        source_system=DataSystem.rms,
        target_system=DataSystem.smda,
    )
    mappings = StratigraphyMappings(root=[primary, unmappable])

    mappings_service.update_mappings_by_source_system(
        MappingType.stratigraphy,
        DataSystem.rms,
        mappings,
    )

    assert fmu_dir.mappings.stratigraphy_mappings == mappings
    assert mappings_service.get_mappings_by_source_system(
        MappingType.stratigraphy, DataSystem.rms
    ) == Mappings(stratigraphy=mappings)


def test_update_mappings_by_source_system_unsupported_type(
    mappings_service: MappingsService,
) -> None:
    """Test unsupported mapping types raise ValueError on write."""
    with pytest.raises(ValueError, match="not yet supported"):
        mappings_service.update_mappings_by_source_system(
            MappingType.wellbore,
            DataSystem.rms,
            StratigraphyMappings(root=[]),
        )


def test_update_mappings_by_source_system_rejects_mismatched_source_system(
    mappings_service: MappingsService,
    make_stratigraphy_mapping: Callable[..., StratigraphyIdentifierMapping],
) -> None:
    """Test updates reject mappings outside the requested source partition."""
    mismatched_mappings = StratigraphyMappings(
        root=[
            make_stratigraphy_mapping(
                "TopHugin",
                "TopHugin",
                RelationType.primary,
                source_system=DataSystem.simulator,
                target_system=DataSystem.simulator,
            )
        ]
    )

    with pytest.raises(ValueError, match="requested source system 'rms'"):
        mappings_service.update_mappings_by_source_system(
            MappingType.stratigraphy,
            DataSystem.rms,
            mismatched_mappings,
        )
