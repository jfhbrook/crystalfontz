# -*- coding: utf-8 -*-

import logging
import os
from pathlib import Path
from typing import Dict, Generator, List, Optional

import pytest

from tests.helpers import Cli, EnvFactory

logger = logging.getLogger(__name__)


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--system", action="store", default=False, help="Connect to the system bus"
    )


@pytest.fixture
def config_file() -> str:
    if "CRYSTALFONTZ_CONFIG_FILE" in os.environ:
        return os.environ["CRYSTALFONTZ_CONFIG_FILE"]
    path = Path(__file__).parent / "fixtures/crystalfontz.yaml"
    return str(path)


@pytest.fixture
def log_level() -> str:
    if "CRYSTALFONTZ_LOG_LEVEL" in os.environ:
        return os.environ["CRYSTALFONTZ_LOG_LEVEL"]
    return "INFO"


@pytest.fixture
def cli_env(config_file: str, log_level: str) -> EnvFactory:
    def factory(env: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        _env: Dict[str, str] = dict(os.environ)

        if env:
            _env.update(env)

        _env["CRYSTALFONTZ_CONFIG_FILE"] = config_file
        _env["CRYSTALFONTZ_LOG_LEVEL"] = log_level

        return _env

    return factory


@pytest.fixture
def cli(cli_env: EnvFactory) -> Cli:
    return Cli(["python3", "-m", "crystalfontz"], env=cli_env())


@pytest.fixture
def dbus_service(
    cli_env: EnvFactory, request: pytest.FixtureRequest
) -> Generator[None, None, None]:
    cli = Cli(["python3", "-m", "crystalfontz.dbus.service", "--user"], env=cli_env())

    if request.config.getoption("--system"):
        logger.info("Connecting to system bus")
        yield
        return

    with cli.bg():
        yield


@pytest.fixture
def dbus_cli(
    cli_env: EnvFactory, dbus_service: None, request: pytest.FixtureRequest
) -> Cli:
    argv: List[str] = [
        "python3",
        "-m",
        "crystalfontz.dbus.client",
        "--system" if request.config.getoption("--system") else "--user",
    ]

    if not request.config.getoption("--system"):
        argv.append("--user")

    return Cli(argv, env=cli_env())
