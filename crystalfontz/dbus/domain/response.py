from typing import ClassVar, Tuple

from crystalfontz.dbus.domain.base import (
    AddressM,
    AddressT,
    BytesM,
    BytesT,
    IndexM,
    IndexT,
    ModelM,
    ModelT,
    RevisionM,
    RevisionT,
    t,
    Uint16M,
    Uint16T,
)
from crystalfontz.dbus.domain.keys import KeyStatesM, KeyStatesT
from crystalfontz.response import (
    DowDeviceInformation,
    DowTransactionResult,
    KeypadPolled,
    LcdMemory,
    Pong,
    UserFlashAreaRead,
    Versions,
)

PongT = BytesT


class PongM:
    """
    Map a Pong (ie, a ping response) to and from dbus types.
    """

    t: ClassVar[str] = BytesM.t

    @staticmethod
    def pack(pong: Pong) -> PongT:
        return BytesM.pack(pong.response)

    @staticmethod
    def unpack(pong: BytesT) -> Pong:
        return Pong(BytesM.unpack(pong))


VersionsT = Tuple[ModelT, RevisionT, RevisionT]


class VersionsM:
    """
    Map versions to and from dbus types.
    """

    t: ClassVar[str] = t(ModelM, RevisionM, RevisionM)

    @staticmethod
    def pack(versions: Versions) -> VersionsT:
        return (versions.model, versions.hardware_rev, versions.firmware_rev)

    @staticmethod
    def unpack(versions: VersionsT) -> Versions:
        return Versions(*versions)


UserFlashAreaReadT = BytesT


class UserFlashAreaReadM:
    t: ClassVar[str] = BytesM.t

    @staticmethod
    def pack(res: UserFlashAreaRead) -> UserFlashAreaReadT:
        return BytesM.pack(res.data)

    @staticmethod
    def unpack(res: UserFlashAreaReadT) -> UserFlashAreaRead:
        return UserFlashAreaRead(BytesM.unpack(res))


LcdMemoryT = Tuple[AddressT, BytesT]


class LcdMemoryM:
    """
    Map LcdMemory to and from dbus types.
    """

    t: ClassVar[str] = t(AddressM, BytesM)

    @staticmethod
    def pack(memory: LcdMemory) -> LcdMemoryT:
        return (memory.address, BytesM.pack(memory.data))

    @staticmethod
    def unpack(obj: LcdMemoryT) -> LcdMemory:
        address, buff = obj
        return LcdMemory(address, BytesM.unpack(buff))


DowDeviceInformationT = Tuple[IndexT, BytesT]


class DowDeviceInformationM:
    """
    Map DowDeviceInformation to and from dbus types.
    """

    t: ClassVar[str] = t(IndexM, BytesM)

    @staticmethod
    def pack(info: DowDeviceInformation) -> DowDeviceInformationT:
        return (info.index, BytesM.pack(info.rom_id))

    @staticmethod
    def unpack(info: DowDeviceInformationT) -> DowDeviceInformation:
        index, rom_id = info
        return DowDeviceInformation(index, BytesM.unpack(rom_id))


DowTransactionResultT = Tuple[IndexT, BytesT, Uint16T]


class DowTransactionResultM:
    """
    Map DowTransactionResult to and from dbus types.
    """

    t: ClassVar[str] = t(IndexM, BytesM, Uint16M)

    @staticmethod
    def unpack(res: DowTransactionResultT) -> DowTransactionResult:
        index, data, crc = res
        return DowTransactionResult(index, BytesM.unpack(data), crc)

    @staticmethod
    def pack(res: DowTransactionResult) -> DowTransactionResultT:
        return (res.index, BytesM.pack(res.data), res.crc)


KeypadPolledT = KeyStatesT


class KeypadPolledM:
    """
    Map KeypadPolled to and from dbus types.
    """

    t: ClassVar[str] = KeyStatesM.t

    @staticmethod
    def pack(polled: KeypadPolled) -> KeyStatesT:
        return KeyStatesM.pack(polled.states)

    @staticmethod
    def unpack(polled: KeyStatesT) -> KeypadPolled:
        return KeypadPolled(KeyStatesM.unpack(polled))
