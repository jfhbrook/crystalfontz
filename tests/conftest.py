# -*- coding: utf-8 -*-

import os
import subprocess
from typing import Dict, Optional, Protocol, Self

import pytest


class CliProtocol(Protocol):
    def __call__(self: Self, *argv: str, env=None) -> subprocess.CompletedProcess: ...


class EnvFactoryProtocol(Protocol):
    def __call__(
        self: Self, env: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]: ...


@pytest.fixture
def cli_env() -> EnvFactoryProtocol:
    def env_factory(env: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        _env: Dict[str, str] = dict(os.environ)

        if env:
            _env.update(env)

        if "CRYSTALFONTZ_LOG_LEVEL" not in _env:
            _env["CRYSTALFONTZ_LOG_LEVEL"] = "INFO"

        if "CRYSTALFONTZ_PORT" not in _env:
            _env["CRYSTALFONTZ_PORT"] = "/dev/ttyUSB0"

        return _env

    return env_factory


@pytest.fixture
def crystalfontz(cli_env) -> CliProtocol:
    def _cli(
        *argv: str, env: Optional[Dict[str, str]] = None
    ) -> subprocess.CompletedProcess:
        _env = cli_env(env)

        return subprocess.run(
            ["crystalfontz"] + list(argv), capture_output=True, check=True, env=_env
        )

    return _cli
