from typing import ClassVar, Tuple

from crystalfontz.dbus.domain.base import (
    BytesM,
    BytesT,
    ModelM,
    ModelT,
    RevisionM,
    RevisionT,
    struct,
    t,
    Uint16M,
    Uint16T,
)
from crystalfontz.device import Device, DeviceStatus, lookup_device

WidthT = Uint16T


class WidthM(Uint16M):
    pass


HeightT = Uint16T


class HeightM(Uint16M):
    pass


DeviceT = Tuple[ModelT, RevisionT, RevisionT, WidthT, HeightT, WidthT, HeightT, Uint16T]


class DeviceM:
    t: ClassVar[str] = struct(
        ModelM, RevisionM, RevisionM, WidthM, HeightM, WidthM, HeightM, Uint16M
    )

    @staticmethod
    def pack(device: Device) -> DeviceT:
        return (
            device.model,
            device.hardware_rev,
            device.firmware_rev,
            device.lines,
            device.columns,
            device.character_width,
            device.character_height,
            device.n_temperature_sensors,
        )

    @staticmethod
    def unpack(device: DeviceT) -> Device:
        model = device[0]
        hardware_rev = device[1]
        firmware_rev = device[2]

        return lookup_device(model, hardware_rev, firmware_rev)


# Includes enough device info to unpack the status
DeviceStatusT = Tuple[ModelT, RevisionT, RevisionT, BytesT]


class DeviceStatusM:
    t: ClassVar[str] = t(ModelM, RevisionM, RevisionM, BytesM)

    @staticmethod
    def pack(_status: DeviceStatus) -> DeviceStatusT:
        raise NotImplementedError("pack")

    @staticmethod
    def unpack(_status: DeviceStatusT) -> DeviceStatus:
        raise NotImplementedError("unpack")
