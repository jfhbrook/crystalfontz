#!/usr/bin/env bash

import subprocess
from typing import Protocol, Self


class CliProtocol(Protocol):
    def __call__(self: Self, *argv: str, env=None) -> subprocess.CompletedProcess: ...


def test_cli(crystalfontz: CliProtocol, cli_env, confirm) -> None:
    crystalfontz("backlight", "0.2")
    crystalfontz("contrast", "0.4")

    confirm("Did the backlight and contrast settings change?")

    crystalfontz("send", "0", "0", "Hello world!")

    confirm('Did the LCD display "Hello world!"?')

    crystalfontz("line", "1" "Line 1")
    crystalfontz("line", "2", "Line 2")

    confirm('Does the LCD display "Line 1" and "Line 2"?')

    crystalfontz("clear")

    confirm("Did the LCD clear?")

    crystalfontz("cursor", "position", "1", "3")
    crystalfontz("cursor", "style", "BLINKING_BLOCK")

    confirm("Did the cursor move and start blinking?")

    pong: str = crystalfontz("ping", "pong").stdout.strip()

    assert pong == "pong"

    crystalfontz("status")
    crystalfontz("versions")
    crystalfontz("--detect", "ping", "hello")

    crystalfontz("power", "reboot-lcd")

    confirm("Did the LCD reboot?")

    listen = subprocess.Popen(["crystalfontz", "listen"], env=cli_env())

    confirm("Mash some buttons. Are events showing up?")

    listen.terminate()

    marquee = subprocess.Popen(
        ["crystalfontz", "effects", "marquee", "1", "Josh is cool"], env=cli_env()
    )

    confirm("Is the LCD showing a marquee effect?")

    marquee.terminate()

    screensaver = subprocess.Popen(
        ["crystalfontz", "effects", "screensaver", "Josh!"], env=cli_env()
    )

    confirm("Is the LCD showing a screensaver effect?")

    screensaver.terminate()

    crystalfontz("listen", "--for", "1.0")
    crystalfontz("effects", "--for", "1.0", "marquee", "1", "Josh is cool")
    crystalfontz("effects", "--for", "1.0", "screensaver", "Josh!")


# TODO: read user flash
# TODO: keypad poll
# TODO: keypad reporting
