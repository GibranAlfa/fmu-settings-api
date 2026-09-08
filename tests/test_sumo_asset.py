"""Tests for the Sumo asset response model."""

import pytest
from pydantic import TypeAdapter, ValidationError

from fmu_settings_api.models.project import SumoAsset


@pytest.mark.parametrize(
    "assets",
    [{"Drogon": ["read", "write"]}, {}, {"Drogon": [], "Other": ["read"]}],
)
def test_sumo_asset_response(assets: dict[str, list[str]]) -> None:
    """Parse asset permissions and serialize without an extra wrapper."""
    response = TypeAdapter(SumoAsset).validate_python(assets)

    assert response.root == assets
    assert response.model_dump(mode="json") == assets


@pytest.mark.parametrize("permissions", ["read", [1], None])
def test_sumo_asset_rejects_invalid_permissions(permissions: object) -> None:
    """Require a list of strings for each asset's permissions."""
    with pytest.raises(ValidationError):
        TypeAdapter(SumoAsset).validate_python({"Drogon": permissions})
