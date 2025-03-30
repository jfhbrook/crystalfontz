from typing import Optional


class BaudRateM:
    t: str = "q"


class TimeoutM:
    t: str = "d"
    none: float = -1.0

    @staticmethod
    def load(d: float) -> Optional[float]:
        return d if d >= 0 else None


class RetryTimesM:
    t: str = "i"
    none: int = -1

    @staticmethod
    def load(i: int) -> Optional[int]:
        return i if i >= 0 else None
