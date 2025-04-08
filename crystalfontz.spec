Name: crystalfontz
Version: 5.0.0
Release: 1
License: MPL-2.0
Summary: Serial client and Linux service for Crystalfontz LCD displays

URL: https://github.com/jfhbrook/crystalfontz
Source0: %{name}-%{version}.tar.gz
BuildArch: noarch

Requires: python-crystalfontz
Requires: python-sdbus

%description


%prep
%autosetup


%build
tar -xzf %{SOURCE0}


%install
mkdir -p %{buildroot}%{_prefix}/lib/systemd/system
mkdir -p %{buildroot}%{_bindir}
install -p -D -m 0644 systemd/crystalfontz.service %{buildroot}%{_prefix}/lib/systemd/system/crystalfontz.service
install -p -D -m 0644 dbus/org.jfhbrook.crystalfontz.conf %{buildroot}%{_prefix}/share/dbus-1/system.d/org.jfhbrook.crystalfontz.conf
install -p -m 755 bin/crystalfontz-dbus %{buildroot}%{_bindir}/crystalfontz

%check


%files
%{_prefix}/lib/systemd/system/crystalfontz.service
%{_prefix}/share/dbus-1/system.d/org.jfhbrook.crystalfontz.conf
%{_bindir}/crystalfontz

%changelog
* Tue Apr 08 2025 Josh Holbrook <josh.holbrook@gmail.com> 5.0.0-1
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


