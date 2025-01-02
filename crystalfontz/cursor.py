from enum import Enum


class CursorStyle(Enum):
    NONE = 0
    BLINKING_BLOCK = 1
    STATIC_UNDERSCORE = 2
    # NOTE: CFA633 shows a blinking block plus underscore, while CFA533 shows
    # no block but a blinking underscore
    BLINKING_UNDERSCORE = 3
