from typing import (
    ClassVar,
    List,
    Optional,
    Protocol,
    Self,
    Type,
    Union,
)


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


def array(of: Union[str, Type[TypeProtocol]]) -> str:
    return f"a{t(of)}"


class OptIntM:
    """
    Map optional positive integers to and from dbus types.

    This class treats values less than 0 (ie, -1) as representing None.
    """

    t: ClassVar[str] = "i"
    none: ClassVar[int] = -1

    @staticmethod
    def unpack(r: int) -> Optional[int]:
        return r if r >= 0 else None

    @classmethod
    def pack(cls: Type[Self], r: Optional[int]) -> int:
        return r if r is not None else cls.none


class OptFloatM:
    """
    Map optional positive floats to and from dbus types.

    This class treats values less than 0 (ie, -1.0) as representing None.
    """

    t: ClassVar[str] = "d"
    none: ClassVar[float] = -1.0

    @staticmethod
    def unpack(t: float) -> Optional[float]:
        return t if t >= 0 else None

    @classmethod
    def pack(cls: Type[Self], t: Optional[float]) -> float:
        return t if t is not None else cls.none


class AddressM:
    t: ClassVar[str] = "q"


class IndexM:
    t: ClassVar[str] = "q"


class PositionM:
    t: ClassVar[str] = "q"


class ByteM:
    t: ClassVar[str] = "y"


class BytesM:
    """
    Map bytes to and from dbus types.
    """

    t: ClassVar[str] = array(ByteM)

    @staticmethod
    def unpack(buff: List[int]) -> bytes:
        return bytes(buff)

    # TODO: This may not be what the dbus client expects...
    @staticmethod
    def pack(buff: bytes) -> List[int]:
        return list(buff)


class OptBytesM:
    """
    Map optional bytes to and from dbus types.
    """

    t: ClassVar[str] = array(ByteM)
    none: ClassVar[List[int]] = list()

    @staticmethod
    def unpack(buff: List[int]) -> Optional[bytes]:
        if not buff:
            return None
        return BytesM.unpack(buff)

    @classmethod
    def pack(cls: Type[Self], buff: Optional[bytes]) -> List[int]:
        if buff is None:
            return cls.none
        return BytesM.pack(buff)


class TimeoutM(OptFloatM):
    """
    Map timeout parameters to and from dbus types.

    TimeoutM is an alias for OptFloatM.
    """

    pass


class RetryTimesM(OptIntM):
    """
    Map retry times parameters to and from dbus types.

    RetryTimesM is an alias for OptFloatM.
    """

    pass


class OkM:
    t: ClassVar[str] = "b"
