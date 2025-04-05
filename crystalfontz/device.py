from abc import ABC
from dataclasses import asdict, dataclass
import logging
import textwrap
from typing import Any, Dict, Optional, Self, Set, Type
import warnings

from crystalfontz.atx import AtxPowerSwitchFunctionalitySettings
from crystalfontz.character import CharacterRom, inverse, x_bar
from crystalfontz.error import DecodeError, DeviceLookupError
from crystalfontz.keys import KeyStates
from crystalfontz.temperature import (
    pack_temperature_settings,
    unpack_temperature_settings,
)

logger = logging.getLogger(__name__)

# Device status is specific to not just the model, but the hardware and
# firmware revisions as well. Rather than forcing the user to check the
# return type, we just make this API unsafe.
DeviceStatus = Any


def assert_contrast_in_range(contrast: float) -> None:
    if contrast < 0:
        raise ValueError(f"Contrast {contrast} < 0")
    elif contrast > 1:
        raise ValueError(f"Contrast {contrast} > 1")


def assert_brightness_in_range(name: str, brightness: float) -> None:
    if brightness < 0:
        raise ValueError(f"{name} brightness {brightness} < 0")
    elif brightness > 1:
        raise ValueError(f"{name} brightness {brightness} > 1")


#
# This ROM encoding is based on page 44 of CFA533-TMI-KU.pdf.
#
# However, it is *incomplete*, mostly because I don't know katakana and only
# know a smattering of Greek. Unknown characters are filled in with spaces.
# Some characters that *are* filled out are best guesses.
#
# NOTE: ASCII characters generally share their code points with true ASCII.
# TODO: Does this ROM match another encoding which contains both katakana and
# Greek letters?
# NOTE: The first column in the ROM is reserved for custom characters.
#

CFA533_CHARACTER_ROM = (
    CharacterRom(
        """
   0@P`p   ―  α 
  !1AQaq  。ア  ä 
  "2BRbr  「 ツ βθ
  #3CScs  」ウ  ε∞
  $4DTdt  、エ  μΩ
  %5EUeu  ・オ  σü
  &6FVfv  ヲカ  ρΣ
  '7GWgw  アキ   π
  (8HXhx  イク  √ 
  )9IYiy  ゥケ    
  *:JZjz  エコ     
  +;K[k{  オサ    
  ,<L¥l|  ヤシ  ¢ 
  -=M]m}  ユヌ  £÷
  .>N^n→  ヨセ  ñ 
  /?O_o←  ツソ °ö█
"""  # noqa: W291, W293
    )
    .set_special_character_range(0, 7)
    .set_encoding(inverse, 224 + 9)
    .set_encoding(x_bar, 240 + 8)
)


class Device(ABC):
    """
    An abstract device. Subclasses of Device contain parameter and methods
    particular to a given model, hardware revision and firmware revision.
    """

    model: str = "<unknown>"
    hardware_rev: str = "<unknown>"
    firmware_rev: str = "<unknown>"

    lines: int = 2
    columns: int = 16
    character_width: int = 6
    character_height: int = 8
    character_rom: CharacterRom = CFA533_CHARACTER_ROM
    n_temperature_sensors: int = 0

    def contrast(self: Self, contrast: float) -> bytes:
        """
        Set the contrast of the device. This is device-dependent.
        """
        raise NotImplementedError("contrast")

    def brightness(
        self: Self, lcd_brightness: float, keypad_brightness: Optional[float]
    ) -> bytes:
        """
        Set the brightness of the device's LCD and keypad. This is device-dependent.
        """

        raise NotImplementedError("brightness")

    def status(self: Self, data: bytes) -> DeviceStatus:
        """
        Parse the status included in a device response into a status object.
        This is highly device-dependent.
        """

        raise NotImplementedError("status")


@dataclass
class CFA533Status:
    """
    The status of a CFA533. This status is based on h1.4, u1v2.
    """

    temperature_sensors_enabled: Set[int]
    key_states: KeyStates
    atx_power_switch_functionality_settings: AtxPowerSwitchFunctionalitySettings
    watchdog_counter: int
    contrast: float
    keypad_brightness: float
    atx_sense_on_floppy: bool
    cfa633_contrast: float
    lcd_brightness: float

    @classmethod
    def from_bytes(cls: Type[Self], data: bytes) -> Self:
        if len(data) != 15:
            raise DecodeError(f"Status expected to be 15 bytes, is {len(data)} bytes")
        # data[0] is reserved
        enabled = unpack_temperature_settings(data[1:5])
        key_states = KeyStates.from_bytes(b"\x00" + data[5:7])
        atx_power = AtxPowerSwitchFunctionalitySettings.from_bytes(data[7:8])
        watchdog_counter = data[8]
        contrast = data[9] / 255
        keypad_brightness = data[10] / 100
        atx_sense_on_floppy = bool(data[11])
        # data[12] is reserved
        cfa633_contrast = data[13] / 50
        lcd_brightness = data[14] / 100

        return cls(
            temperature_sensors_enabled=enabled,
            key_states=key_states,
            atx_power_switch_functionality_settings=atx_power,
            watchdog_counter=watchdog_counter,
            contrast=contrast,
            keypad_brightness=keypad_brightness,
            atx_sense_on_floppy=atx_sense_on_floppy,
            cfa633_contrast=cfa633_contrast,
            lcd_brightness=lcd_brightness,
        )

    def to_bytes(self: Self, device: Device) -> bytes:
        data = b"\00"

        enabled = pack_temperature_settings(self.temperature_sensors_enabled, device)
        key_states = self.key_states.to_bytes()[1:]
        atx_power = self.atx_power_switch_functionality_settings.to_bytes()[0]
        watchdog_counter = self.watchdog_counter
        contrast = int(self.contrast * 255)
        keypad_brightness = int(self.keypad_brightness * 100)
        atx_sense_on_floppy = int(self.keypad_brightness)
        reserved = 0x00
        cfa633_contrast = int(self.cfa633_contrast * 50)
        lcd_brightness = int(self.lcd_brightness * 100)

        data += enabled
        data += key_states
        data += bytes(
            [
                atx_power,
                watchdog_counter,
                contrast,
                keypad_brightness,
                atx_sense_on_floppy,
                reserved,
                cfa633_contrast,
                lcd_brightness,
            ]
        )

        return data

    def as_dict(self: Self) -> Dict[str, Any]:
        atx = self.atx_power_switch_functionality_settings.as_dict()
        return dict(
            temperature_sensors_enabled=list(self.temperature_sensors_enabled),
            key_states=asdict(self.key_states),
            atx_power_switch_functionality_settings=atx,
            watchdog_counter=self.watchdog_counter,
            contrast=self.contrast,
            keypad_brightness=self.keypad_brightness,
            atx_sense_on_floppy=self.atx_sense_on_floppy,
            cfa633_contrast=self.cfa633_contrast,
            lcd_brightness=self.lcd_brightness,
        )

    def __repr__(self: Self) -> str:
        repr_ = "CFA533 Status:\n"
        repr_ += ("-" * (len(repr_) - 1)) + "\n"

        enabled = ", ".join(
            [f"{e}" for e in sorted(list(self.temperature_sensors_enabled))]
        )
        repr_ += "Temperature sensors enabled: " + enabled + "\n"

        repr_ += "Key states:\n"
        repr_ += textwrap.indent(repr(self.key_states), "  ") + "\n"

        repr_ += "ATX Power Switch Functionality Settings:\n"
        repr_ += (
            textwrap.indent(repr(self.atx_power_switch_functionality_settings), "  ")
            + "\n"
        )

        repr_ += f"Watchdog Counter: {self.watchdog_counter}\n"
        repr_ += f"Contrast: {self.contrast}\n"
        repr_ += f"Contrast (CFA633 Compatible): {self.cfa633_contrast}\n"
        repr_ += "Backlight:\n"
        repr_ += f"  Keypad Brightness: {self.keypad_brightness}\n"
        repr_ += f"  LCD Brightness: {self.lcd_brightness}"

        return repr_


class CFA533(Device):
    """
    A CFA533 device.
    """

    model = "CFA533"
    hardware_rev = "h1.4"
    firmware_rev = "u1v2"

    lines: int = 2
    columns: int = 16
    character_width: int = 6
    character_height: int = 8
    character_rom: CharacterRom = CFA533_CHARACTER_ROM
    n_temperature_sensors: int = 32

    def contrast(self: Self, contrast: float) -> bytes:
        # CFA533 supports "enhanced contrast". The first byte is ignored and
        # the second byte can accept the full range.
        # CFA533 also supports "legacy contrast", but with a max value of 50.
        return int(contrast * 50).to_bytes(1, "big") + int(contrast * 200).to_bytes(
            1, "big"
        )

    def brightness(
        self: Self, lcd_brightness: float, keypad_brightness: Optional[float]
    ) -> bytes:
        assert_brightness_in_range("LCD", lcd_brightness)
        brightness = int(lcd_brightness * 100).to_bytes(1, "big")

        # CFA533 can optionally accept a second parameter for keypad brightness
        if keypad_brightness is not None:
            assert_brightness_in_range("Keypad", keypad_brightness)
            brightness += int(keypad_brightness * 100).to_bytes(1, "big")

        return brightness

    def status(self: Self, data: bytes) -> DeviceStatus:
        return CFA533Status.from_bytes(data)


class CFA633(Device):
    """
    A CFA633 device.

    This device is partially documented in the CFA533 datasheet, and therefore
    has nominal support. However, it is completely untested and is likely to
    have bugs.
    """

    model: str = "CFA633"
    hardware_rev: str = "h1.5c"
    firmware_rev: str = "k1.7"

    lines: int = 2
    columns: int = 16
    character_width: int = 6
    character_height: int = 8
    character_rom: CharacterRom = CFA533_CHARACTER_ROM
    n_temperature_sensors: int = 0

    def contrast(self: Self, contrast: float) -> bytes:
        # CFA633 supports a contrast setting between 0 and 200.
        assert_contrast_in_range(contrast)
        return int(contrast * 200).to_bytes(1, "big")

    def brightness(
        self: Self, lcd_brightness: float, keypad_brightness: Optional[float]
    ) -> bytes:
        assert_brightness_in_range("LCD", lcd_brightness)

        if keypad_brightness is not None:
            warnings.warn("CFA633 does not support keypad brightness")

        return int(lcd_brightness * 100).to_bytes(1, "big")

    def status(self: Self, data: bytes) -> DeviceStatus:
        raise NotImplementedError("status")


def lookup_device(
    model: str, hardware_rev: Optional[str] = None, firmware_rev: Optional[str] = None
) -> Device:

    def version() -> str:
        v = f"{model}"
        if hardware_rev:
            v += f": {hardware_rev}"
            if firmware_rev:
                v += f", {firmware_rev}"
        return v

    def select(
        cls: Type[Device],
        hw_rev: Optional[str] = None,
        fw_rev: Optional[str] = None,
        untested: bool = False,
        dangerous: bool = False,
    ) -> Device:
        nonlocal hardware_rev
        nonlocal firmware_rev

        if hw_rev:
            logger.debug(f"Defaulting to hardware revision {hw_rev}")
            hardware_rev = hw_rev
        if fw_rev:
            logger.debug(f"Defaulting to firmware revison {fw_rev}")
            firmware_rev = fw_rev

        logger.info(f"Selected device {version()}")
        if untested:
            message = f"{version()} has not been tested and may have bugs."
            if dangerous:
                warnings.warn(message)
            else:
                logger.warning(message)

        device = cls()
        device.model = model
        device.hardware_rev = hardware_rev or device.hardware_rev
        device.firmware_rev = firmware_rev or device.firmware_rev
        return device

    if model == "CFA533":
        if hardware_rev is None:
            return select(CFA533, hw_rev="h1.4", fw_rev="u1v2")
        if hardware_rev != "h1.4":
            return select(CFA533, untested=True)
        if firmware_rev is None:
            return select(CFA533, fw_rev="u1v2", untested=True)
        elif firmware_rev != "u1v2":
            return select(CFA533, untested=True)
        return CFA533()
    elif model == "CFA633":
        return select(CFA633, untested=True, dangerous=True)
    else:
        raise DeviceLookupError(f"Unknown device {version()}")
