from typing import ClassVar, Tuple

from crystalfontz.character import SpecialCharacter
from crystalfontz.dbus.domain.device import ModelT, RevisionT
from crystalfontz.device import Device, lookup_device

SpecialCharacterT = Tuple[ModelT, RevisionT, RevisionT, bytes]


class SpecialCharacterM:
    t: ClassVar[str] = "t"

    @staticmethod
    def pack(character: SpecialCharacter, device: Device) -> SpecialCharacterT:
        return (
            device.model,
            device.hardware_rev,
            device.firmware_rev,
            character.to_bytes(device),
        )

    @staticmethod
    def unpack(character: SpecialCharacterT) -> SpecialCharacter:
        model, hardware_rev, firmware_rev, data = character

        device = lookup_device(model, hardware_rev, firmware_rev)

        return SpecialCharacter.from_bytes(data, device)
