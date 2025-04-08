# Install

`crystalfontz` is released as a PyPI package, a series of COPR packages, and a GitHub release.

## Python Package

`crystalfontz` is a Python package, and therefore can be installed [from PyPi](https://pypi.org/project/crystalfontz/), for instance with `pip`:

```sh
pip install crystalfontz
```

This package contains the Python library, with the CLIs exposed with Python's `-m` flag (ie. `python3 -m crystalfontz`).

## COPR Packages

I package `crystalfontz` for Fedora on COPR. It can be installed like so:

```sh
sudo dnf copr enable jfhbrook/joshiverse
sudo dnf install crystalfontz
```

This package installs the Python package via `python-crystalfontz`, configures the systemd service, and includes a bin called `crystalfontz` that wraps `python3 -m crystalfontz.dbus.client`.

## GitHub Release

`crystalfontz` is also published as a GitHub release:

<https://github.com/jfhbrook/crystalfontz/releases>

These releases simply contain packaged source code, and will mostly be useful for package authors.
