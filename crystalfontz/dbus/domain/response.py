from typing import ClassVar, Tuple

from crystalfontz.dbus.domain.base import (
    AddressM,
    AddressT,
    ByteM,
    BytesM,
    ByteT,
    IndexM,
    IndexT,
    ModelM,
    ModelT,
    RevisionM,
    RevisionT,
    struct,
    t,
    Uint16M,
    Uint16T,
)
from crystalfontz.dbus.domain.gpio import (
    GpioSettingsM,
    GpioSettingsT,
    GpioStateM,
    GpioStateT,
)
from crystalfontz.dbus.domain.keys import (
    KeyActivityM,
    KeyActivityT,
    KeyStatesM,
    KeyStatesT,
)
from crystalfontz.response import (
    DowDeviceInformation,
    DowTransactionResult,
    GpioRead,
    KeyActivityReport,
    KeypadPolled,
    LcdMemory,
    Pong,
    TemperatureReport,
    UserFlashAreaRead,
    Versions,
)

PongT = bytes


class PongM:
    """
    Map `Pong` to and from `PongT` (`bytes`).
    """

    t: ClassVar[str] = BytesM.t

    @staticmethod
    def pack(pong: Pong) -> PongT:
        """
        Pack `Pong` to `PongT`.
        """

        return pong.response

    @staticmethod
    def unpack(pong: PongT) -> Pong:
        """
        Unpack `PongT` to `Pong`.
        """

        return Pong(pong)


VersionsT = Tuple[ModelT, RevisionT, RevisionT]


class VersionsM:
    """
    Map `Versions` to and from `VersionsT` (`Tuple[str, str, str]`).
    """

    t: ClassVar[str] = t(ModelM, RevisionM, RevisionM)

    @staticmethod
    def pack(versions: Versions) -> VersionsT:
        return (versions.model, versions.hardware_rev, versions.firmware_rev)

    @staticmethod
    def unpack(versions: VersionsT) -> Versions:
        """
        Unpack `VersionsT` to `Versions`.
        """

        return Versions(*versions)


UserFlashAreaReadT = bytes


class UserFlashAreaReadM:
    """
    Map `UserFlashAreaRead` to and from `UserFlashAreaReadT` (`bytes`).
    """

    t: ClassVar[str] = BytesM.t

    @staticmethod
    def pack(res: UserFlashAreaRead) -> UserFlashAreaReadT:
        return res.data

    @staticmethod
    def unpack(res: UserFlashAreaReadT) -> UserFlashAreaRead:
        """
        Unpack `UserFlashAreaReadT` to `UserFlashAreaRead`.
        """

        return UserFlashAreaRead(res)


LcdMemoryT = Tuple[AddressT, bytes]


class LcdMemoryM:
    """
    Map `LcdMemory` to and from `LcdMemoryT` (`Tuple[int, bytes]`).
    """

    t: ClassVar[str] = t(AddressM, BytesM)

    @staticmethod
    def pack(memory: LcdMemory) -> LcdMemoryT:
        return (memory.address, memory.data)

    @staticmethod
    def unpack(obj: LcdMemoryT) -> LcdMemory:
        """
        Unpack `LcdMemoryT` to `LcdMemory`.
        """

        address, buff = obj
        return LcdMemory(address, buff)


DowDeviceInformationT = Tuple[IndexT, int]


class DowDeviceInformationM:
    """
    Map `DowDeviceInformation` to and from `DowDeviceInformationT`
    (`Tuple[int, int]`).
    """

    t: ClassVar[str] = t(IndexM, "t")

    @staticmethod
    def pack(info: DowDeviceInformation) -> DowDeviceInformationT:
        return (info.index, info.rom_id)

    @staticmethod
    def unpack(info: DowDeviceInformationT) -> DowDeviceInformation:
        """
        Unpack `DowDeviceInformation` to `DowDeviceInformationT`.
        """

        index, rom_id = info
        return DowDeviceInformation(index, rom_id)


DowTransactionResultT = Tuple[IndexT, bytes, Uint16T]


class DowTransactionResultM:
    """
    Map `DowTransactionResult` to and from `DowTransactionResultT`
    (`Tuple[int, bytes, int]`).
    """

    t: ClassVar[str] = t(IndexM, BytesM, Uint16M)

    @staticmethod
    def pack(res: DowTransactionResult) -> DowTransactionResultT:
        return (res.index, res.data, res.crc)

    @staticmethod
    def unpack(res: DowTransactionResultT) -> DowTransactionResult:
        """
        Unpack `DowTransactionResultT` to `DowTransactionResult`.
        """

        index, data, crc = res
        return DowTransactionResult(index, data, crc)


KeypadPolledT = KeyStatesT


class KeypadPolledM:
    """
    Map `KeypadPolled` to and from `KeypadPolledT`
    (`Tuple[KeyStateT, KeyStateT, KeyStateT, KeyStateT, KeyStateT, KeyStateT]`,
    where `KeyStateT = Tuple[bool, bool, bool]`).
    """

    t: ClassVar[str] = KeyStatesM.t

    @staticmethod
    def pack(polled: KeypadPolled) -> KeyStatesT:
        return KeyStatesM.pack(polled.states)

    @staticmethod
    def unpack(polled: KeypadPolledT) -> KeypadPolled:
        """
        Unpack `KeypadPolledT` to `KeypadPolled`.
        """

        return KeypadPolled(KeyStatesM.unpack(polled))


GpioReadT = Tuple[IndexT, GpioStateT, ByteT, GpioSettingsT]


class GpioReadM:
    """
    Map `GpioRead` to and from `GpioReadT`
    (`Tuple[int, Tuple[bool, bool, bool], int, int]`).
    """

    t: ClassVar[str] = t(IndexM, struct(GpioStateM), ByteM, GpioSettingsM)

    @staticmethod
    def pack(gpio_read: GpioRead) -> GpioReadT:
        return (
            gpio_read.index,
            GpioStateM.pack(gpio_read.state),
            gpio_read.requested_level,
            GpioSettingsM.pack(gpio_read.settings),
        )

    @staticmethod
    def unpack(gpio_read: GpioReadT) -> GpioRead:
        """
        Unpack `GpioReadT` to `GpioRead`.
        """

        index, state, requested_level, settings = gpio_read
        return GpioRead(
            index=index,
            state=GpioStateM.unpack(state),
            requested_level=requested_level,
            settings=GpioSettingsM.unpack(settings),
        )


KeyActivityReportT = KeyActivityT


class KeyActivityReportM:
    """
    Map `KeyActivityReport` to and from `KeyActivityReportT`
    """

    t: ClassVar[str] = KeyActivityM.t

    @staticmethod
    def pack(report: KeyActivityReport) -> KeyActivityReportT:
        return KeyActivityM.pack(report.activity)

    @staticmethod
    def unpack(report: KeyActivityReportT) -> KeyActivityReport:
        return KeyActivityReport(KeyActivityM.unpack(report))


TemperatureReportT = Tuple[IndexT, float, float]


class TemperatureReportM:
    """
    Map `TemperatureReport` to and from `KeyActivityReportT`
    """

    t: ClassVar[str] = t(IndexM, "dd")

    @staticmethod
    def pack(report: TemperatureReport) -> TemperatureReportT:
        return (report.index, report.celsius, report.fahrenheit)

    @staticmethod
    def unpack(report: TemperatureReportT) -> TemperatureReport:
        index, celsius, fahrenheit = report
        return TemperatureReport(index, celsius, fahrenheit)
