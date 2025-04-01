from typing import ClassVar, Dict

from crystalfontz.cursor import CursorStyle

CURSOR_STYLES: Dict[int, CursorStyle] = {style.value: style for style in CursorStyle}


class CursorStyleM:
    """
    Map a CursorStyle to and from dbus types.
    """

    t: ClassVar[str] = "q"

    @staticmethod
    def unpack(style: int) -> CursorStyle:
        return CURSOR_STYLES[style]

    @staticmethod
    def pack(style: CursorStyle) -> int:
        return style.value
