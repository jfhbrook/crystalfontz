from typing import ClassVar, List, Tuple

from crystalfontz.dbus.map.base import array, BytesM, IndexM, struct, t
from crystalfontz.response import (
    DowDeviceInformation,
    DowTransactionResult,
    KeypadPolled,
    LcdMemory,
    Pong,
    UserFlashAreaRead,
    Versions,
)


class PongM:
    t: ClassVar[str] = BytesM.t

    @staticmethod
    def pack(pong: Pong) -> List[int]:
        return BytesM.pack(pong.response)


class VersionsM:
    t: ClassVar[str] = struct("sss")

    @staticmethod
    def unpack(versions: Tuple[str, str, str]) -> Versions:
        return Versions(*versions)

    @staticmethod
    def pack(versions: Versions) -> Tuple[str, str, str]:
        return (versions.model, versions.hardware_rev, versions.firmware_rev)


class UserFlashAreaReadM:
    t: ClassVar[str] = "y"

    @staticmethod
    def pack(res: UserFlashAreaRead) -> bytes:
        return res.data


class LcdMemoryM:
    t: ClassVar[str] = t("q", BytesM)

    @staticmethod
    def unpack(obj: Tuple[int, List[int]]) -> LcdMemory:
        address, buff = obj
        return LcdMemory(address, BytesM.unpack(buff))

    @staticmethod
    def pack(memory: LcdMemory) -> Tuple[int, List[int]]:
        return (memory.address, BytesM.pack(memory.data))


class DowDeviceInformationM:
    t: ClassVar[str] = t(IndexM, BytesM)

    @staticmethod
    def unpack(info: Tuple[int, List[int]]) -> DowDeviceInformation:
        index, rom_id = info
        return DowDeviceInformation(index, BytesM.unpack(rom_id))

    @staticmethod
    def pack(info: DowDeviceInformation) -> Tuple[int, List[int]]:
        return (info.index, BytesM.pack(info.rom_id))


class DowTransactionResultM:
    t: ClassVar[str] = t(IndexM, BytesM, "q")

    @staticmethod
    def unpack(res: Tuple[int, List[int], int]) -> DowTransactionResult:
        index, data, crc = res
        return DowTransactionResult(index, BytesM.unpack(data), crc)

    @staticmethod
    def pack(res: DowTransactionResult) -> Tuple[int, List[int], int]:
        return (res.index, BytesM.pack(res.data), res.crc)


class KeypadPolledM:
    t: ClassVar[str] = array(struct("bbb"))

    @staticmethod
    def pack(polled: KeypadPolled) -> List[Tuple[bool, bool, bool]]:
        raise NotImplementedError("pack")

    @staticmethod
    def unpack(polled: List[Tuple[bool, bool, bool]]) -> KeypadPolled:
        raise NotImplementedError("unpack")
