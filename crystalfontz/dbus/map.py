from typing import ClassVar, Optional, Protocol, Type, Union


class TypeProtocol(Protocol):
    t: ClassVar[str]


def t(*args: Union[str, Type[TypeProtocol]]) -> str:
    type_ = ""

    for arg in args:
        if isinstance(arg, str):
            type_ += arg
        else:
            type_ += arg.t

    return type_


def struct(*args: Union[str, Type[TypeProtocol]]) -> str:
    return t("(", *args, ")")


class BaudRateM:
    t: ClassVar[str] = "q"


class TimeoutM:
    t: ClassVar[str] = "d"
    none: float = -1.0

    @staticmethod
    def load(d: float) -> Optional[float]:
        return d if d >= 0 else None


class RetryTimesM:
    t: ClassVar[str] = "i"
    none: int = -1

    @staticmethod
    def load(i: int) -> Optional[int]:
        return i if i >= 0 else None
