"""
Configuration management for the Crystalfontz CLI.
"""

from typing import cast, Optional

from configurence import BaseConfig, config, field, global_file

from crystalfontz.baud import BaudRate, FAST_BAUD_RATE, SLOW_BAUD_RATE
from crystalfontz.client import DEFAULT_RETRY_TIMES, DEFAULT_TIMEOUT

APP_NAME = "crystalfontz"
GLOBAL_FILE = global_file(APP_NAME)
DEFAULT_PORT = "/dev/ttyUSB0"


def load_baud_rate(value: str) -> BaudRate:
    rate: int = int(value)

    if rate == SLOW_BAUD_RATE or rate == FAST_BAUD_RATE:
        return cast(BaudRate, rate)
    else:
        raise ValueError(
            f"{rate} is not a supported baud rate. "
            f"Supported baud rates are {SLOW_BAUD_RATE} and {FAST_BAUD_RATE}"
        )


@config(APP_NAME)
class Config(BaseConfig):
    """
    A configuration object. This class is typically used by the Crystalfontz CLI, but
    may also be useful for scripts or Jupyter notebooks using its configuration.
    """

    port: str = field(default=DEFAULT_PORT, env_var="PORT")
    model: str = field(default="CFA533", env_var="MODEL")
    hardware_rev: Optional[str] = field(default=None, env_var="HARDWARE_REV")
    firmware_rev: Optional[str] = field(default=None, env_var="FIRMWARE_REV")
    baud_rate: BaudRate = field(
        default=SLOW_BAUD_RATE, env_var="BAUD_RATE", load=load_baud_rate, dump=str
    )
    timeout: float = field(default=DEFAULT_TIMEOUT, env_var="TIMEOUT")
    retry_times: int = field(default=DEFAULT_RETRY_TIMES, env_var="RETRY_TIMES")
