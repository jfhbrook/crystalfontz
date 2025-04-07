#!/usr/bin/env bash

import pytest

from tests.helpers import Cli


def test_backlight_contrast(dbus_cli: Cli, confirm) -> None:
    dbus_cli("backlight", "0.2")
    dbus_cli("contrast", "0.4")

    confirm("Did the backlight and contrast settings change?")


def test_send(dbus_cli: Cli, confirm) -> None:
    dbus_cli("send", "0", "0", "Hello world!")

    confirm('Did the LCD display "Hello world!"?')


def test_line(dbus_cli: Cli, confirm) -> None:
    dbus_cli("line", "1", "Line 1")
    dbus_cli("line", "2", "Line 2")

    confirm('Does the LCD display "Line 1" and "Line 2"?')


def test_clear(dbus_cli: Cli, confirm) -> None:
    dbus_cli("clear")

    confirm("Did the LCD clear?")


def test_cursor(dbus_cli: Cli, confirm) -> None:
    dbus_cli("cursor", "position", "1", "3")
    dbus_cli("cursor", "style", "BLINKING_BLOCK")

    confirm("Did the cursor move and start blinking?")


def test_ping(dbus_cli: Cli) -> None:
    pong: bytes = dbus_cli("ping", "pong").stdout.strip()

    assert pong == b"pong"


def test_status(dbus_cli: Cli, snapshot) -> None:
    assert dbus_cli("status").stdout.strip() == snapshot


def test_versions(dbus_cli: Cli, snapshot) -> None:
    assert dbus_cli("versions").stdout.strip() == snapshot


def test_reboot(dbus_cli: Cli, confirm) -> None:
    dbus_cli("--timeout", "1.0", "power", "reboot-lcd")

    confirm("Did the LCD reboot?")


@pytest.mark.skip
def test_detect() -> None:
    raise NotImplementedError("test_detect")


def test_listen(dbus_cli, confirm) -> None:
    with dbus_cli.bg("listen", quiet=False):
        confirm("Mash some buttons. Are events showing up?")


def test_listen_for(dbus_cli: Cli) -> None:
    dbus_cli("listen", "--for", "1.0")


def test_marquee(dbus_cli, confirm) -> None:
    with dbus_cli.bg("effects", "marquee", "0", "Josh is cool"):
        confirm("Is the LCD showing a marquee effect?")


def test_marquee_for(dbus_cli: Cli) -> None:
    dbus_cli("effects", "--for", "1.0", "marquee", "1", "Josh is cool")


def test_screensaver(dbus_cli, confirm) -> None:
    with dbus_cli.bg("effects", "screensaver", "Josh!"):
        confirm("Is the LCD showing a screensaver effect?")


def test_screensaver_for(dbus_cli: Cli) -> None:
    dbus_cli("effects", "--for", "1.0", "screensaver", "Josh!")


def test_dance_party(dbus_cli, confirm) -> None:
    dbus_cli("clear")
    dbus_cli("send", "0", "0", "Carameldansen!!")
    with dbus_cli.bg("effects", "dance-party"):
        confirm("Is the LCD showing a dance party effect?")


@pytest.mark.skip
def test_read_user_flash() -> None:
    raise NotImplementedError("test_read_user_flash")


@pytest.mark.skip
def test_poll_keypad() -> None:
    raise NotImplementedError("test_poll_keypad")
