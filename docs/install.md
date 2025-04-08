# Install

`crystalfontz` is a Python package, and therefore can be installed [from PyPi](https://pypi.org/project/crystalfontz/), for instance with `pip`:

```sh
pip install crystalfontz
```

In addition, I have a Fedora package on COPR, which can be installed like so:

```sh
sudo dnf copr enable jfhbrook/joshiverse
sudo dnf install crystalfontz
```

The COPR package includes a script called `crystalfontz` that wraps `python3 -m crystalfontz.dbus.client`.
