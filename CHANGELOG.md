## 2025/04/08 Version 5.0.0-1
- API Changes:
  - **NEW:** `Receiver` class
    - A subclass of `asyncio.Queue`
  - `Client`:
    - **BREAKING:** `subscribe` and `unsubscribe` methods use new `Receiver` class
    - Emit unmatched exceptions on expecting receivers instead of resolving `client.closed`
    - `detect_baud_rate` exposes `timeout` and `retry_times` arguments
    - Document `detect_baud_rate`
  - **BREAKING:** `ClientProtocol`/`EffectClient`
    - `crystalfontz.protocol.ClientProtocol` type has been replaced by `crystalfontz.effects.EffectClient`
    - `EffectClient` enforces a smaller API than `ClientProtocol` did previously
  - **BREAKING:** `Response`:
    - `Response.from_bytes` accepts bytes as from packets, rather than `__init__`
    - `Response.__init__` accepts properties as arguments
  - **BREAKING:** `SpecialCharacter` API:
    - Rename `as_bytes` method to `to_bytes`
    - Store pixels as `List[List[bool]]` instead of `List[List[int]]`
  - `KeyState` includes `keypress: KeyPress` attribute
- CLI changes:
  - **BREAKING:** CLI now invoked through `python3 -m crystalfontz`
    - Optional unpackaged `crystalfontz` entry point at `./bin/crystalfontz`
  - Use `configurence` library
  - Respect `CRYSTALFONTZ_CONFIG_FILE` environment variable
  - Improve error reporting for timeouts
  - Client now respects CLI settings
    - Cause was the `Client` constructor being called twice
  - Additional commands accept bytes as arguments
    - `python3 -m crystalfontz line 1`
    - `python3 -m crystalfontz line 2`
    - `python3 -m crystalfontz send`
  - Help for `python3 -m crystalfontz listen` `--for` option
- **NEW:** Dbus support:
  - `crystalfontz.dbus.DbusInterface` dbus Interface class, implementing most commands
  - `crystalfontz.dbus.DbusClient` dbus client class
  - `crystalfontz.dbus.domain` API for mapping domain objects to dbus types
  - `python3 -m crystalfontz.dbus.service` dbus service CLI
    - Optional unpackaged `crystalfontz.dbus.service` entry point at `./bin/crystalfontz-service`
  - `python3 -m crystalfontz.dbus.client` dbus client CLI
    - Optional unpackaged `crystalfontz.dbus.client` entry point at `./bin/crystalfontz-dbus`
- Packaging and Releases:
  - `python-crystalfontz` COPR package spec
    - This has been moved from <https://github.com/jfhbrook/public>
  - **NEW:** `crystalfontz` COPR package
    - Depends on `python-crystalfontz` COPR package
    - Includes systemd unit for `python3 -m crystalfontz.dbus.service`
    - **BREAKING:** Includes shim bin `crystalfontz` -> `python3 -m crystalfontz.dbus.client`
  - Tito based release tagging
  - GitHub release
  - Improved PyPI classifiers
  - **BREAKING:** Release under MPL-2.0 license
- Integration tests:
  - Use `python-gak` plugin
  - Use snapshots
  - Leverage a config file at `./tests/fixtures/crystalfontz.yaml`
    - Can be overridden with `CRYSTALFONTZ_CONFIG_FILE` environment variable

## 2025/01/12 Version 4.0.0
- Fedora package on COPR: <https://copr.fedorainfracloud.org/coprs/jfhbrook/joshiverse/package/python-crystalfontz/>
- Client API Changes:
  - Rename `client.load_device` to `client.detect_device`
  - `client.dow_transaction`'s `data_to_write` argument defaults to empty bytes
  - New `client.test_connection` method
  - New `client.detect_baud_rate` method
- CLI Improvements and Features:
  - `crystalfontz ping` may receive encoded bytes
  - Support for `crystalfontz flash write`
  - Support for `crystalfontz dow transaction`
  - Support for `crystalfontz gpio write`
  - Support for `crystalfontz gpio read`
  - Support for `crystalfontz baud`
  - Support for `--output text` and `--output json`
  - New `crystalfontz config` command group
  - Global config loaded by default when command called with sudo
- Configuration Improvements and Features:
  - Export `Config` class used by CLI
  - Add `get`, `set` and `unset` methods to `Config` class

## 2025/01/09 Version 3.0.1

- Remove development dependencies from extras

## 2025/01/08 Version 3.0.0

- API changes:
  - Renamed `client` contextmanager to `connection`
  - Renamed `TemperatureReport`'s `idx` attribute to `index`
  - Moved `reset_invert` and `power_invert` from `ATXPowerSwitchFunction` to flags on `ATXPowerSwitchFunctionalitySettings`
  - Exposed `ClientProtocol` for developers of custom effects
- Retry and timeout related functionality:
  - Add response `timeout` option with 250ms default and per-method overrides
  - Add response `retry_times` option with 0 default and per-method overrides
- Command line changes and improvements:
  - Default port is now `/dev/ttyUSB0`
  - Renamed `crystalfontz atx` arg `--power-pulse-length-seconds` to `--power-pulse-length`
  - Add `--for SECONDS` option to `crystalfontz listen` and `crystalfontz effects` that closes the commands after a certain amount of time
  - Improved help text
- Docstrings, plus documentation hosted at <https://crystalfontz.readthedocs.io/>

## 2025/01/06 Version 2.0.0

- API changes:
  - Expose `pause` argument for marquee effect in client and CLI
  - Rename `client.poke` and `Poked` to `client.read_lcd_memory` and `LcdMemory` respectively
- Improved control flow and error handling:
  - Add `client.closed` future
  - Add `client` async contextmanager that awaits `client.closed`
  - Handle errors by surfacing them either in the command calls or through `client.closed`
- Refactor CLI command names
  - `read-lcd-memory` -> `lcd poke`
  - `send-command-to-lcd-controller` -> `lcd send`
  - `user-flash-area` -> `flash`
  - `store-boot-state` -> `store`
  - `clear-screen` -> `clear`
  - `set-line-1` -> `line 1`
  - `set-line-2` -> `line 2`
  - `special-character` -> `character`
  - `cursor set-position` -> `cursor position`
  - `cursor set-style` -> `cursor style`
  - `set-contrast` -> `constrast`
  - `set-backlight` -> `backlight`
  - `dow read-device-information` -> `dow info`
  - `temperature setup-reporting` -> `temperature reporting`
  - `temperature setup-live-display` -> `temperature display`
  - `keypad configure-reporting` -> `keypad reporting`
  - `set-atx-power-switch-functionality` -> `atx`
  - `configure-watchdog` -> `watchdog`
  - `read-status` -> `status`
  - `set-baud-rate` -> `baud`
- CLI improvements:
  - Byte CLI arguments are validated as being in range
  - Watchdog CLI argument allows "disable" and "disabled" values
  - Configure device model, hardware revision and firmware revison in CLI
  - Do not show stack trace on connection errors in CLI
- Support arbitrary multi-byte encodings in character ROM
- Build, package and CI housekeeping
  - Compile `requirements.txt` and `requirements_dev.txt`
  - Add CI pipeline
  - Support Python 3.11
  - Add PyPI classifiers
  - Updated documentation in README.md

## 2025/01/04 Version 1.0.0

- First version of `crystalfontz`
