from abc import ABC
from dataclasses import dataclass
import logging
from typing import Any, Optional, Self, Set
import warnings

from crystalfontz.atx import AtxPowerSwitchFunctionalitySettings
from crystalfontz.character import CharacterRom, inverse, x_bar
from crystalfontz.error import DecodeError, DeviceLookupError
from crystalfontz.keys import KeyStates
from crystalfontz.temperature import unpack_temperature_settings

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
    .set_encoding(inverse, 244 + 9)
    .set_encoding(x_bar, 240 + 8)
)


class Device(ABC):
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
        raise NotImplementedError("contrast")

    def brightness(
        self: Self, lcd_brightness: float, keypad_brightness: Optional[float]
    ) -> bytes:
        raise NotImplementedError("brightness")

    def status(self: Self, data: bytes) -> DeviceStatus:
        raise NotImplementedError("status")


# INCOMPLETE
class CFA633(Device):
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
        return int(contrast * 200).to_bytes()

    def brightness(
        self: Self, lcd_brightness: float, keypad_brightness: Optional[float]
    ) -> bytes:
        assert_brightness_in_range("LCD", lcd_brightness)

        if keypad_brightness is not None:
            warnings.warn("CFA633 does not support keypad brightness")

        return int(lcd_brightness * 100).to_bytes()

    def status(self: Self, data: bytes) -> DeviceStatus:
        raise NotImplementedError("status")


@dataclass
class CFA533Status:
    temperature_sensors_enabled: Set[int]
    key_states: KeyStates
    atx_power_switch_functionality_settings: AtxPowerSwitchFunctionalitySettings
    watchdog_counter: int
    contrast: float
    brightness: float
    atx_sense_on_floppy: bool
    cfa633_contrast: float
    lcd_brightness: float


class CFA533(Device):
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
        return int(contrast * 50).to_bytes() + int(contrast * 255).to_bytes()

    def brightness(
        self: Self, lcd_brightness: float, keypad_brightness: Optional[float]
    ) -> bytes:
        assert_brightness_in_range("LCD", lcd_brightness)
        brightness = int(lcd_brightness * 100).to_bytes()

        # CFA533 can optionally accept a second parameter for keypad brightness
        if keypad_brightness is not None:
            assert_brightness_in_range("Keypad", keypad_brightness)
            brightness += int(keypad_brightness * 100).to_bytes()

        return brightness

    def status(self: Self, data: bytes) -> DeviceStatus:
        if len(data) != 15:
            raise DecodeError(f"Status expected to be 15 bytes, is {len(data)} bytes")
        # data[0] is reserved
        enabled = unpack_temperature_settings(data[1:5])
        key_states = KeyStates.from_bytes(b"\x00" + data[5:7])
        atx_power = AtxPowerSwitchFunctionalitySettings.from_bytes(data[7:8])
        watchdog_counter = data[8]
        contrast = data[9] / 255
        brightness = data[10] / 100
        atx_sense_on_floppy = bool(data[11])
        # data[12] is reserved
        cfa633_contrast = data[13] / 50
        lcd_brightness = data[14] / 100

        return CFA533Status(
            temperature_sensors_enabled=enabled,
            key_states=key_states,
            atx_power_switch_functionality_settings=atx_power,
            watchdog_counter=watchdog_counter,
            contrast=contrast,
            brightness=brightness,
            atx_sense_on_floppy=atx_sense_on_floppy,
            cfa633_contrast=cfa633_contrast,
            lcd_brightness=lcd_brightness,
        )


def lookup_device(
    model: str, hardware_rev: str = "<any>", firmware_rev: str = "<any>"
) -> Device:
    if model != "CFA533" or hardware_rev != "h1.4" or firmware_rev != "u1v2":
        logger.warning(
            f"{model}: {hardware_rev}, {firmware_rev} has not been "
            "tested and may have bugs."
        )

    if model == "CFA633":
        return CFA633()
    elif model == "CFA533":
        return CFA533()
    else:
        raise DeviceLookupError(f"Unknown device {model} {hardware_rev} {firmware_rev}")
