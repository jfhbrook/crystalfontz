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


class NoneM:
    t: ClassVar[str] = ""


OptUintT = int


class OptUintM:
    """
    Map optional positive integers to and from dbus types.

    This class treats values less than 0 (ie, -1) as representing None.
    """

    t: ClassVar[str] = "i"
    none: ClassVar[OptUintT] = -1

    @staticmethod
    def unpack(r: OptUintT) -> Optional[int]:
        return r if r >= 0 else None

    @classmethod
    def pack(cls: Type[Self], r: Optional[int]) -> OptUintT:
        return r if r is not None else cls.none


OptPosFloatT = float


class OptPosFloatM:
    """
    Map optional positive floats to and from dbus types.

    This class treats values less than 0 (ie, -1.0) as representing None.
    """

    t: ClassVar[str] = "d"
    none: ClassVar[OptPosFloatT] = -1.0

    @staticmethod
    def unpack(t: OptPosFloatT) -> Optional[float]:
        return t if t >= 0 else None

    @classmethod
    def pack(cls: Type[Self], t: Optional[float]) -> OptPosFloatT:
        return t if t is not None else cls.none


Uint16T = int


class Uint16M:
    t: ClassVar[str] = "q"


AddressT = Uint16T


class AddressM(Uint16M):
    t: ClassVar[str] = Uint16M.t


ByteT = int


class ByteM:
    t: ClassVar[str] = "y"


IndexT = ByteT


class IndexM(ByteT):
    t: ClassVar[str] = ByteM.t


PositionT = Uint16T


class PositionM(ByteT):
    t: ClassVar[str] = ByteM.t


BytesT = List[int]


class BytesM:
    """
    Map bytes to and from dbus types.
    """

    t: ClassVar[str] = array(ByteM)

    @staticmethod
    def unpack(buff: BytesT) -> bytes:
        return bytes(buff)

    # TODO: This may not be what the dbus client expects...
    @staticmethod
    def pack(buff: bytes) -> BytesT:
        return list(buff)


OptBytesT = BytesT


class OptBytesM:
    """
    Map optional bytes to and from dbus types.
    """

    t: ClassVar[str] = BytesM.t
    none: ClassVar[BytesT] = list()

    @staticmethod
    def unpack(buff: BytesT) -> Optional[bytes]:
        if not buff:
            return None
        return BytesM.unpack(buff)

    @classmethod
    def pack(cls: Type[Self], buff: Optional[bytes]) -> BytesT:
        if buff is None:
            return cls.none
        return BytesM.pack(buff)


ModelT = str


class ModelM:
    t: ClassVar[str] = "s"


RevisionT = str


class RevisionM:
    t: ClassVar[str] = "s"
    none: ClassVar[str] = ""

    @classmethod
    def pack(cls: Type[Self], revision: Optional[str]) -> str:
        return revision or cls.none

    @classmethod
    def unpack(cls: Type[Self], revision: str) -> Optional[str]:
        return revision if revision != cls.none else None


TimeoutT = float


class TimeoutM(OptPosFloatM):
    """
    Map timeout parameters to and from dbus types.

    TimeoutM is an alias for OptFloatM.
    """

    pass


RetryTimesT = int


class RetryTimesM(OptUintM):
    """
    Map retry times parameters to and from dbus types.

    RetryTimesM is an alias for OptFloatM.
    """

    pass


class OkM:
    t: ClassVar[str] = "b"
