import base64
from typing import Literal

OutputMode = Literal["text"] | Literal["json"]


def format_bytes(buffer: bytes) -> str:
    return str(buffer)[2:-1]


def format_json_bytes(buffer: bytes) -> str:
    return base64.b64encode(buffer).decode("utf-8")
