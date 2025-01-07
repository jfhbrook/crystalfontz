from dataclasses import asdict, dataclass, field, fields, replace
import os
import os.path
from typing import Any, cast, Dict, Optional, Type

try:
    from typing import Self
except ImportError:
    Self = Any

from appdirs import user_config_dir
import yaml

from crystalfontz.baud import BaudRate, SLOW_BAUD_RATE

try:
    from yaml import CDumper as Dumper
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Dumper, Loader

"""
Configuration management for the Crystalfontz CLI.
"""

APP_NAME = "crystalfontz"

GLOBAL_FILE = f"/etc/{APP_NAME}.yaml"


def default_file() -> str:
    """
    Get the default file path for the crystalfontz CLI.
    """

    return os.path.join(user_config_dir(APP_NAME), f"{APP_NAME}.yaml")


DEFAULT_PORT = "/dev/ttyUSB0"


def _metadata(env_var: Optional[str] = None) -> Dict[str, Any]:
    return dict(env_var=env_var)


def _from_environment() -> Dict[str, Any]:
    env: Dict[str, Any] = dict()
    for f in fields(Config):
        if f.metadata and "env_var" in f.metadata:
            if f.metadata["env_var"] in os.environ:
                var: Any = os.environ[f.metadata["env_var"]]
                env[f.name] = cast(Any, f.type)(var)
    return env


@dataclass
class Config:
    """
    A config for the crystalfontz CLI.
    """

    port: str = field(
        default=DEFAULT_PORT, metadata=_metadata(env_var="CRYSTALFONTZ_PORT")
    )
    model: str = field(default="CFA533", metadata=_metadata("CRYSTALFONTZ_MODEL"))
    hardware_rev: Optional[str] = field(
        default=None, metadata=_metadata(env_var="CRYSTALFONTZ_HARDWARE_REV")
    )
    firmware_rev: Optional[str] = field(
        default=None, metadata=_metadata(env_var="CRYSTALFONTZ_FIRMWARE_REV")
    )
    baud_rate: BaudRate = field(
        default=SLOW_BAUD_RATE, metadata=_metadata(env_var="CRYSTALFONTZ_BAUD_RATE")
    )
    timeout: Optional[float] = field(
        default=None, metadata=_metadata(env_var="CRYSTALFONTZ_TIMEOUT")
    )
    retry_times: Optional[int] = field(
        default=None, metadata=_metadata(env_var="CRYSTALFONTZ_RETRY_TIMES")
    )
    file: Optional[str] = None

    @classmethod
    def from_environment(cls: Type[Self]) -> Self:
        """
        Load a config from the environment.
        """

        return cls(**_from_environment())

    @classmethod
    def from_file(
        cls: Type[Self],
        file: Optional[str] = None,
        load_environment: bool = False,
        create_file: bool = False,
    ) -> Self:
        """
        Load a config from a file.
        """

        _file: str = file or os.environ.get("CRYSTALFONTZ_CONFIG", default_file())

        found_file = False
        kwargs: Dict[str, Any] = dict(file=_file)
        try:
            with open(_file, "r") as f:
                found_file = True
                kwargs.update(yaml.load(f, Loader=Loader))
        except FileNotFoundError:
            try:
                with open(GLOBAL_FILE, "r") as f:
                    kwargs.update(yaml.load(f, Loader=Loader))
            except FileNotFoundError:
                pass

        if load_environment:
            kwargs.update(_from_environment())

        config = cls(**kwargs)

        if not found_file and create_file:
            config.to_file()

        return config

    def to_file(self, file: Optional[str] = None) -> "Config":
        """Save the config to a file."""

        file = file or self.file or default_file()

        with open(file, "w") as f:
            yaml.dump(asdict(self), f, Dumper=Dumper)

        return replace(self, file=file)
