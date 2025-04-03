from typing import (
    ClassVar,
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


OptIntT = int


class OptIntM:
    """
    Map `Optional[int]` to and from `OptIntT` (`int`), where integer values
    are expected to be positive.

    None values are represented by negative values, namely `-1`.
    """

    t: ClassVar[str] = "x"
    none: ClassVar[OptIntT] = -1

    @staticmethod
    def unpack(r: OptIntT) -> Optional[int]:
        return r if r >= 0 else None

    @classmethod
    def pack(cls: Type[Self], r: Optional[int]) -> OptIntT:
        return r if r is not None else cls.none


OptFloatT = float


class OptFloatM:
    """
    Map `Optional[float]` to and from `OptFloatT` (`float`), where float values
    are expected to be positive.

    None values are represented by negative values, namely `-1.0`.
    """

    t: ClassVar[str] = "d"
    none: ClassVar[OptFloatT] = -1.0

    @classmethod
    def pack(cls: Type[Self], t: Optional[float]) -> OptFloatT:
        """
        Pack `Optional[float]` to `OptFloatT`.
        """

        return t if t is not None else cls.none

    @staticmethod
    def unpack(t: OptFloatT) -> Optional[float]:
        """
        Unpack `OptFloatT` to `Optional[float]`.
        """

        return t if t >= 0 else None


OptStrT = str


class OptStrM:
    """
    Map `Optional[str]` to and from `StrT` (`str`).

    None values are represented by an empty string.
    """

    t: ClassVar[str] = "s"
    none: ClassVar[str] = ""

    @classmethod
    def pack(cls: Type[Self], string: Optional[str]) -> OptStrT:
        """
        Pack `Optional[str]` to `OptStrT`.
        """

        return string or cls.none

    @classmethod
    def unpack(cls: Type[Self], string: OptStrT) -> Optional[str]:
        """
        Unpack `OptStrT` to `Optional[str]`.
        """

        return string if string != cls.none else None


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


class BytesM:
    t: ClassVar[str] = array(ByteM)


OptBytesT = bytes


class OptBytesM:
    """
    Map `Optional[bytes]` to and from `OptBytesT` (`bytes`).

    None values are represented by an empty bytestring.
    """

    t: ClassVar[str] = BytesM.t
    none: ClassVar[OptBytesT] = b""

    @classmethod
    def pack(cls: Type[Self], buff: Optional[bytes]) -> OptBytesT:
        """
        Pack `Optional[bytes]` to `OptBytesT`.
        """

        if buff is None:
            return cls.none
        return buff

    @staticmethod
    def unpack(buff: OptBytesT) -> Optional[bytes]:
        """
        Unpack `OptBytesT` to `Optional[bytes]`.
        """

        if not buff:
            return None
        return buff


ModelT = str


class ModelM:
    t: ClassVar[str] = "s"


RevisionT = str


class RevisionM(OptStrM):
    t: ClassVar[str] = OptStrM.t
    none: ClassVar[str] = OptStrM.none

    """
    Map `Optional[str]` to and from `RevisionT` (`str`).

    `RevisionM` is an alias for `OptStrM`.
    """


TimeoutT = float


class TimeoutM(OptFloatM):
    """
    Map `Optional[float]` to and from `TimeoutT` (`float`).

    `TimeoutM` is an alias for `OptFloatM`.
    """

    t: ClassVar[str] = OptFloatM.t
    none: ClassVar[float] = OptFloatM.none


RetryTimesT = int


class RetryTimesM(OptIntM):
    """
    Map `Optional[int]` to and from `RetryTimesT` (`int`).

    `RetryTimesM` is an alias for `OptIntM`.
    """

    t: ClassVar[str] = OptIntM.t
    none: ClassVar[int] = OptIntM.none


class OkM:
    t: ClassVar[str] = "b"
