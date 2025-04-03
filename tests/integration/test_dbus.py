#!/usr/bin/env bash

import pytest

from tests.helpers import Cli


def test_backlight_contrast(crystalfontzctl: Cli, confirm) -> None:
    crystalfontzctl("backlight", "0.2")
    crystalfontzctl("contrast", "0.4")

    confirm("Did the backlight and contrast settings change?")


def test_display_clear(crystalfontzctl: Cli, confirm) -> None:
    crystalfontzctl("send", "0", "0", "Hello world!")

    confirm('Did the LCD display "Hello world!"?')

    crystalfontzctl("line", "1", "Line 1")
    crystalfontzctl("line", "2", "Line 2")

    confirm('Does the LCD display "Line 1" and "Line 2"?')

    crystalfontzctl("clear")

    confirm("Did the LCD clear?")


def test_cursor(crystalfontzctl: Cli, confirm) -> None:
    crystalfontzctl("cursor", "position", "1", "3")
    crystalfontzctl("cursor", "style", "BLINKING_BLOCK")

    confirm("Did the cursor move and start blinking?")


def test_ping(crystalfontzctl: Cli) -> None:
    pong: bytes = crystalfontzctl("ping", "pong").stdout.strip()

    assert pong == b"pong"


def test_status(crystalfontzctl: Cli, snapshot) -> None:
    assert crystalfontzctl("status").stdout.strip() == snapshot


def test_versions(crystalfontzctl: Cli, snapshot) -> None:
    assert crystalfontzctl("versions").stdout.strip() == snapshot


@pytest.mark.skip(reason="Privileged command")
def test_reboot(crystalfontzctl: Cli, confirm) -> None:
    crystalfontzctl("--timeout", "1.0", "power", "reboot-lcd")

    confirm("Did the LCD reboot?")


@pytest.mark.skip(reason="Privileged command")
def test_detect() -> None:
    raise NotImplementedError("test_detect")


@pytest.mark.skip(reason="Not implemented")
def test_listen() -> None:
    raise NotImplementedError("test_listen")


@pytest.mark.skip(reason="Not implemented")
def test_listen_for(crystalfontzctl: Cli) -> None:
    crystalfontzctl("listen", "--for", "1.0")


@pytest.mark.skip(reason="Not implemented")
def test_marquee() -> None:
    raise NotImplementedError("test_marquee")


@pytest.mark.skip(reason="Not implemented")
def test_screensaver() -> None:
    raise NotImplementedError("test_marquee")


@pytest.mark.skip(reason="Not implemented")
def test_read_user_flash() -> None:
    raise NotImplementedError("test_read_user_flash")


@pytest.mark.skip(reason="Not implemented")
def test_poll_keypad() -> None:
    raise NotImplementedError("test_poll_keypad")
