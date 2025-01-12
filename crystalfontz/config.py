"""
Configuration management for the Crystalfontz CLI.
"""

from dataclasses import asdict, dataclass, field, fields, replace
import logging
import os
import os.path
from pathlib import Path
from typing import Any, Callable, cast, Dict, NoReturn, Optional, Type

try:
    from typing import Self
except ImportError:
    Self = Any

from appdirs import user_config_dir
import yaml

from crystalfontz.baud import BaudRate, FAST_BAUD_RATE, SLOW_BAUD_RATE
from crystalfontz.client import DEFAULT_RETRY_TIMES, DEFAULT_TIMEOUT

try:
    from yaml import CDumper as Dumper
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Dumper, Loader

logger = logging.getLogger(__name__)

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
    A configuration object. This class is typically used by the Crystalfontz CLI, but
    may also be useful for scripts or Jupyter notebooks using its configuration.
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
    timeout: float = field(
        default=DEFAULT_TIMEOUT, metadata=_metadata(env_var="CRYSTALFONTZ_TIMEOUT")
    )
    retry_times: int = field(
        default=DEFAULT_RETRY_TIMES,
        metadata=_metadata(env_var="CRYSTALFONTZ_RETRY_TIMES"),
    )
    _file: Optional[str] = None

    @property
    def file(self: Self) -> str:
        """
        The configuration file path.
        """
        return self._file or default_file()

    @classmethod
    def from_environment(cls: Type[Self]) -> Self:
        """
        Load configuration from the environment.
        """

        logger.debug("Loading config from environment...")
        return cls(**_from_environment())

    @classmethod
    def from_file(
        cls: Type[Self],
        file: Optional[str] = None,
        load_environment: bool = False,
        create_file: bool = False,
    ) -> Self:
        """
        Load configuration from a file. Optionally load environment overrides and
        optionally create the file.
        """

        _file: str = file or os.environ.get("CRYSTALFONTZ_CONFIG", default_file())

        found_file = False
        kwargs: Dict[str, Any] = dict(_file=_file)
        try:
            with open(_file, "r") as f:
                found_file = True
                logger.debug(f"Loading config from {_file}...")
                kwargs.update(yaml.load(f, Loader=Loader))
        except FileNotFoundError:
            try:
                with open(GLOBAL_FILE, "r") as f:
                    logger.debug(f"Loading config from {GLOBAL_FILE}...")
                    kwargs.update(yaml.load(f, Loader=Loader))
            except FileNotFoundError:
                pass

        if load_environment:
            logger.debug("Loading environment overrides...")
            kwargs.update(_from_environment())

        config = cls(**kwargs)

        if not found_file and create_file:
            config.to_file()

        return config

    def _assert_has(self: Self, name: str) -> None:
        if not hasattr(self, name) or name.startswith("_"):
            raise ValueError(f"Unknown configuration parameter {name}")

    def get(self: Self, name: str) -> Any:
        """
        Get a configuration parameter by name.
        """

        self._assert_has(name)
        return getattr(self, name)

    def set(self: Self, name: str, value: str) -> None:
        """
        Set a configuration parameter by name and string value.
        """

        self._assert_has(name)

        setters: Dict[Any, Callable[[str, str], None]] = {
            str: self._set_str,
            Optional[str]: self._set_str,
            bool: self._set_bool,
            BaudRate: self._set_baud_rate,
            float: self._set_float,
            Optional[float]: self._set_float,
            int: self._set_int,
            Optional[int]: self._set_int,
        }
        for f in fields(self):
            if f.name == name:
                if f.type in setters:
                    setters[f.type](name, value)
                    return
                else:
                    raise ValueError(f"Unknown type {f.type}")

    def _set_str(self: Self, name: str, value: str) -> None:
        setattr(self, name, value)

    def _set_bool(self: Self, name: str, value: str) -> None:
        if value.lower() in {"true", "yes", "y", "1"}:
            setattr(self, name, True)
        elif value.lower() in {"false", "no", "n", "0"}:
            setattr(self, name, False)
        else:
            raise ValueError(f"Can not convert {value} to bool")

    def _set_baud_rate(self: Self, name: str, value: str) -> None:
        rate: int = int(value)
        if rate == SLOW_BAUD_RATE or rate == FAST_BAUD_RATE:
            setattr(self, name, rate)
        else:
            raise ValueError(
                f"{rate} is not a supported baud rate. "
                f"Supported baud rates are {SLOW_BAUD_RATE} and {FAST_BAUD_RATE}"
            )

    def _set_float(self: Self, name: str, value: str) -> None:
        setattr(self, name, float(value))

    def _set_int(self: Self, name: str, value: str) -> None:
        setattr(self, name, int(value))

    def unset(self: Self, name: str) -> None:
        """
        Unset an optional parameter.
        """

        self._assert_has(name)

        unsetters: Dict[Any, Callable[[str], None]] = {
            str: self._parameter_required,
            Optional[str]: self._unset,
            bool: self._parameter_required,
            BaudRate: self._parameter_required,
            float: self._parameter_required,
            Optional[float]: self._unset,
            int: self._parameter_required,
            Optional[int]: self._unset,
        }

        for f in fields(self):
            if f.name == name:
                if f.type in unsetters:
                    unsetters[f.type](name)
                    return
                else:
                    raise ValueError(f"Unknown type {f.type}")

    def _parameter_required(self: Self, name: str) -> NoReturn:
        raise ValueError(f"{name} is a required configuraiton parameter")

    def _unset(self: Self, name: str) -> None:
        setattr(self, name, None)

    def as_dict(self: Self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if not k.startswith("_")}

    def to_file(self: Self, file: Optional[str] = None) -> Self:
        """
        Save the configuration to a file.
        """

        file = file or self.file

        os.makedirs(Path(file).parent, exist_ok=True)

        with open(file, "w") as f:
            yaml.dump(self.as_dict(), f, Dumper=Dumper)

        logger.info(f"Wrote configuration to {file}.")

        return replace(self, _file=file)

    def __repr__(self: Self) -> str:
        return yaml.dump(self.as_dict(), Dumper=Dumper)
