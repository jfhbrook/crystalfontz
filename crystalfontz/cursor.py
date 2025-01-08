from enum import Enum


class CursorStyle(Enum):
    """
    A cursor style, as set with command 12 (0x0C): Set LCD Cursor Style.

    - **NONE**:  No cursor.
    - **BLINKING_BLOCK**: Blinking block cursor.
    - **STATIC_UNDERSCORE**: Static underscore cursor.
    - **BLINKING_UNDERSCORE**: Blinking underscore cursor. On the CFA633, this
      represents a blinking block plus an underscore.
    """

    NONE = 0
    BLINKING_BLOCK = 1
    STATIC_UNDERSCORE = 2
    BLINKING_UNDERSCORE = 3
