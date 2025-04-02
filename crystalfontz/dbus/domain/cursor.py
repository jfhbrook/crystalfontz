from typing import ClassVar, Dict

from crystalfontz.cursor import CursorStyle

CursorStyleT = int

CURSOR_STYLES: Dict[int, CursorStyle] = {style.value: style for style in CursorStyle}


class CursorStyleM:
    """
    Map `CursorStyle` to and from `CursorStyleT` (`int`).
    """

    t: ClassVar[str] = "q"

    @staticmethod
    def pack(style: CursorStyle) -> CursorStyleT:
        """
        Pack `CursorStyle` to `CursorStyleT`.
        """

        return style.value

    @staticmethod
    def unpack(style: CursorStyleT) -> CursorStyle:
        """
        Unpack `CursorStyleT` to `CursorStyle`.
        """

        return CURSOR_STYLES[style]
