#!/usr/bin/env bash

import pytest

from tests.helpers import Cli


def test_backlight_contrast(cli: Cli, confirm) -> None:
    cli("backlight", "0.2")
    cli("contrast", "0.4")

    confirm("Did the backlight and contrast settings change?")


def test_send(cli: Cli, confirm) -> None:
    cli("send", "0", "0", "Hello world!")

    confirm('Did the LCD display "Hello world!"?')


def test_line(cli: Cli, confirm) -> None:
    cli("line", "1", "Line 1")
    cli("line", "2", "Line 2")

    confirm('Does the LCD display "Line 1" and "Line 2"?')


def test_clear(cli: Cli, confirm) -> None:
    cli("clear")

    confirm("Did the LCD clear?")


def test_cursor(cli: Cli, confirm) -> None:
    cli("cursor", "position", "1", "3")
    cli("cursor", "style", "BLINKING_BLOCK")

    confirm("Did the cursor move and start blinking?")


def test_ping(cli: Cli) -> None:
    pong: bytes = cli("ping", "pong").stdout.strip()

    assert pong == b"pong"


def test_status(cli: Cli, snapshot) -> None:
    assert cli("status").stdout.strip() == snapshot


def test_versions(cli: Cli, snapshot) -> None:
    assert cli("versions").stdout.strip() == snapshot


def test_reboot(cli: Cli, confirm) -> None:
    cli("--timeout", "1.0", "power", "reboot-lcd")

    confirm("Did the LCD reboot?")


@pytest.mark.skip
def test_detect() -> None:
    raise NotImplementedError("test_detect")


def test_listen(cli, confirm) -> None:
    with cli.bg("listen"):
        confirm("Mash some buttons. Are events showing up?")


def test_listen_for(cli: Cli) -> None:
    cli("listen", "--for", "1.0")


def test_marquee(cli, confirm) -> None:
    with cli.bg("effects", "marquee", "0", "Josh is cool"):
        confirm("Is the LCD showing a marquee effect?")


def test_marquee_for(cli: Cli) -> None:
    cli("effects", "--for", "1.0", "marquee", "1", "Josh is cool")


def test_screensaver(cli, confirm) -> None:
    with cli.bg("effects", "screensaver", "Josh!"):
        confirm("Is the LCD showing a screensaver effect?")


def test_screensaver_for(cli: Cli) -> None:
    cli("effects", "--for", "1.0", "screensaver", "Josh!")


def test_dance_party(cli, confirm) -> None:
    cli("clear")
    cli("send", "0", "0", "Carameldansen!!")
    with cli.bg("effects", "dance-party"):
        confirm("Is the LCD showing a dance party effect?")


@pytest.mark.skip
def test_read_user_flash() -> None:
    raise NotImplementedError("test_read_user_flash")


@pytest.mark.skip
def test_poll_keypad() -> None:
    raise NotImplementedError("test_poll_keypad")
