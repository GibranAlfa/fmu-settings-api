"""Models pertaining to the .fmu directory."""

from pathlib import Path

from fmu.settings.models.project_config import ProjectConfig
from pydantic import BaseModel, Field


class FMUDirPath(BaseModel):
    """Path where a .fmu directory may exist."""

    path: Path = Field(examples=["/path/to/project.2038.02.02"])
    """Absolute path to the directory which maybe contains a .fmu directory."""


class FMUProject(FMUDirPath):
    """Information returned when 'opening' an FMU Directory."""

    project_dir_name: str = Field(examples=["project.2038.02.02"])
    """The directory name, not the path, that contains the .fmu directory."""

    config: ProjectConfig
    """The configuration of an FMU project's .fmu directory."""


class GlobalConfigPath(BaseModel):
    """A relative path to a global config file, relative to the project root."""

    relative_path: Path = Field(examples=["relative_path/to/global_config_file"])
    """Relative path in the project to a global config file."""


class FMULockInfo(BaseModel):
    """Represents the contents of a project .fmu lock file."""

    pid: int = Field(examples=[12345])
    """Process ID of the lock holder."""

    hostname: str = Field(examples=["hostname.local"])
    """Hostname where the lock was acquired."""

    user: str = Field(examples=["username"])
    """User who acquired the lock."""

    acquired_at: float = Field(examples=[1_701_234_567.89])
    """Unix timestamp when the lock was acquired."""

    expires_at: float = Field(examples=[1_701_235_167.89])
    """Unix timestamp when the lock expires."""

    version: str | None = Field(default=None, examples=["0.3.0"])
    """Version of fmu-settings that created the lock, if provided."""


class FMULockStatus(BaseModel):
    """Represents the lock status of a project .fmu directory."""

    locked: bool = Field(examples=[True])
    """Whether the .fmu directory is currently locked."""

    lock: FMULockInfo | None = Field(default=None)
    """The lock information if the directory is locked."""
