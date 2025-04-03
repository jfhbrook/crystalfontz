# -*- coding: utf-8 -*-

from contextlib import contextmanager
import os
import subprocess
from typing import Dict, Generator, List, Optional, Protocol, Self


class Cli:
    """
    A fixture for running CLI commands
    """

    def __init__(
        self: Self,
        command: str,
        argv: Optional[List[str]] = None,
        env: Optional[Dict[str, str]] = None,
    ) -> None:
        self.command: str = command
        self.argv: List[str] = argv or list()
        self.env: Dict[str, str] = env or dict(os.environ)

    def __call__(self: Self, *argv: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [self.command] + self.argv + list(argv),
            capture_output=True,
            check=True,
            env=self.env,
        )

    @contextmanager
    def bg(self: Self, *argv: str) -> Generator[None, None, None]:
        proc = subprocess.Popen(
            [self.command] + self.argv + list(argv),
            stderr=subprocess.DEVNULL,
            env=self.env,
        )

        yield

        proc.terminate()


class EnvFactory(Protocol):
    def __call__(
        self: Self, env: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]: ...
