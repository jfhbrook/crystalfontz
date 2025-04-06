"""
Manage a DBus service configuration.

Configuration for the DBus service is a little different than for the serial client.
This is because the DBus service doesn't live reload a config after it changes. In
other words, if you edit the config file, the DBus service's loaded config will
show drift.

This is captured in the `StagedConfig` class, which holds both the config as served
by the live DBus service, and the config as loaded from the same file. These are
called the "active" and "target" config, respectively.
"""

from dataclasses import asdict, dataclass, fields
import json
from typing import Any, Dict, Generic, Literal, Self, TypeVar

import yaml

try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper

from crystalfontz.config import Config

StageType = Literal["set"] | Literal["unset"] | None
T = TypeVar("T")


@dataclass
class StagedAttr(Generic[T]):
    """
    A staged attribute. Shows both the active and target value, and how the value is
    expected to change when applied.

    Attributes:
        type (StageType): The type of staged change. Either "set", "unset" or None.
        active (T): The attribute value from the active config.
        target (T): The attribute value from the target config.
    """

    type: StageType
    active: T
    target: T

    def __repr__(self: Self) -> str:
        target: str = (
            self.target if type(self.target) is str else json.dumps(self.target)
        )

        if self.type is None:
            return target

        active: str = (
            self.active if type(self.active) is str else json.dumps(self.active)
        )

        return f"{active} ~> {target}"


class StagedConfig:
    """
    A staged configuration. Shows both the active and target configurations, and how
    the attributes are expected to change.

    Attributes:
        active_config (Config): The active configuration, as loaded from the live
                                DBus service.

        target_config (Config): The target configuration, as loaded from the service's
                                config file.
        dirty (bool): When true, there is drift between the active and target config.
    """

    def __init__(self: Self, active_config: Config, target_config: Config) -> None:
        # The configuration currently loaded by the service
        self.active_config: Config = active_config
        # The configuration as per the file
        self.target_config: Config = target_config
        self.dirty = False

    def reload_target(self: Self) -> None:
        """
        Reload the target config from file.
        """

        self.target_config = Config.from_file(self.file)
        self._check_config_dirty()

    def _check_attr_dirty(self: Self, name: str) -> None:
        if self.target_config.get(name) != self.active_config.get(name):
            self.dirty = True

    def _check_config_dirty(self: Self) -> None:
        for f in fields(self.target_config):
            self._check_attr_dirty(f.name)

    @property
    def file(self: Self) -> str:
        """
        The path to the config file.
        """

        file = self.target_config.file
        assert file is not None, "Target config must be from a file"
        return file

    def get(self: Self, name: str) -> StagedAttr[Any]:
        """
        Get the staged status of an attribute.
        """

        active_attr = self.active_config.get(name)
        target_attr = self.target_config.get(name)

        type_: StageType = None
        if active_attr != target_attr:
            if target_attr is None:
                type_ = "unset"
            else:
                type_ = "set"

        return StagedAttr(type=type_, active=active_attr, target=target_attr)

    def set(self: Self, name: str, value: str) -> None:
        """
        Stage a new value for an attribute.
        """

        self.target_config.set(name, value)
        self._check_attr_dirty(name)

    def unset(self: Self, name: str) -> None:
        """
        Stage the unsetting of a value for an attribute.
        """

        self.target_config.unset(name)
        self._check_attr_dirty(name)

    def as_dict(self: Self) -> Dict[str, Any]:
        d: Dict[str, Any] = dict()

        for f in fields(self.target_config):
            d[f.name] = asdict(self.get(f.name))

        return d

    def __repr__(self: Self) -> str:
        d: Dict[str, Any] = dict()

        for f in fields(self.target_config):
            d[f.name] = repr(self.get(f.name))

        dump = yaml.dump(d, Dumper=Dumper)
        return "\n".join(
            [f"~ {line}" if "~>" in line else f"  {line}" for line in dump.split("\n")]
        )

    def to_file(self: Self) -> None:
        """
        Save the target config to file.
        """

        self.target_config.to_file()
