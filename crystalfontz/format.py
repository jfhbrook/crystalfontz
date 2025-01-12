from typing import Literal

OutputMode = Literal["text"] | Literal["json"]


def format_bytes(buffer: bytes) -> str:
    return str(buffer)[2:-1]
