from typing import Optional

baud_rate_t = "q"
timeout_t = "d"
none_timeout = -1.0
retry_times_t = "i"
none_retry_times = -1


def load_timeout(d: float) -> Optional[float]:
    return d if d >= 0 else None


def load_retry_times(i: int) -> Optional[int]:
    return i if i >= 0 else None
