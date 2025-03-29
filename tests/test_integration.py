#!/usr/bin/env bash

import subprocess
from typing import Protocol, Self

import pytest


class CliProtocol(Protocol):
    def __call__(self: Self, *argv: str, env=None) -> subprocess.CompletedProcess: ...


def test_backlight_contrast(crystalfontz: CliProtocol, confirm) -> None:
    crystalfontz("backlight", "0.2")
    crystalfontz("contrast", "0.4")

    confirm("Did the backlight and contrast settings change?")


def test_display_clear(crystalfontz: CliProtocol, confirm) -> None:
    crystalfontz("send", "0", "0", "Hello world!")

    confirm('Did the LCD display "Hello world!"?')

    crystalfontz("line", "1", "Line 1")
    crystalfontz("line", "2", "Line 2")

    confirm('Does the LCD display "Line 1" and "Line 2"?')

    crystalfontz("clear")

    confirm("Did the LCD clear?")


def test_cursor(crystalfontz: CliProtocol, confirm) -> None:
    crystalfontz("cursor", "position", "1", "3")
    crystalfontz("cursor", "style", "BLINKING_BLOCK")

    confirm("Did the cursor move and start blinking?")


def test_ping(crystalfontz: CliProtocol) -> None:
    pong: bytes = crystalfontz("ping", "pong").stdout.strip()

    assert pong == b"pong"


def test_status(crystalfontz: CliProtocol, snapshot) -> None:
    assert crystalfontz("status").stdout.strip() == snapshot


def test_versions(crystalfontz: CliProtocol, snapshot) -> None:
    assert crystalfontz("versions").stdout.strip() == snapshot


@pytest.mark.skip
def test_reboot(crystalfontz: CliProtocol, confirm) -> None:
    # TODO: This test failed due to a timeout issue. This is probably an
    # easy fix - simply increasing the timeout. But it raises a bigger issue
    # with how timeouts are treated in the crystalfontz project...
    crystalfontz("power", "reboot-lcd")

    confirm("Did the LCD reboot?")


@pytest.mark.skip
def test_detect() -> None:
    raise NotImplementedError("test_detect")


def test_listen(cli_env, confirm) -> None:
    listen = subprocess.Popen(["crystalfontz", "listen"], env=cli_env())

    confirm("Mash some buttons. Are events showing up?")

    listen.terminate()


def test_listen_for(crystalfontz: CliProtocol) -> None:
    crystalfontz("listen", "--for", "1.0")


def test_marquee(cli_env, confirm) -> None:
    marquee = subprocess.Popen(
        ["crystalfontz", "effects", "marquee", "1", "Josh is cool"], env=cli_env()
    )

    confirm("Is the LCD showing a marquee effect?")

    marquee.terminate()


def test_marquee_for(crystalfontz: CliProtocol) -> None:
    crystalfontz("effects", "--for", "1.0", "marquee", "1", "Josh is cool")


def test_screensaver(cli_env, confirm) -> None:
    screensaver = subprocess.Popen(
        ["crystalfontz", "effects", "screensaver", "Josh!"], env=cli_env()
    )

    confirm("Is the LCD showing a screensaver effect?")

    screensaver.terminate()


def test_screensaver_for(crystalfontz: CliProtocol) -> None:
    crystalfontz("effects", "--for", "1.0", "screensaver", "Josh!")


@pytest.mark.skip
def test_read_user_flash() -> None:
    raise NotImplementedError("test_read_user_flash")


@pytest.mark.skip
def test_poll_keypad() -> None:
    raise NotImplementedError("test_poll_keypad")
