# DBus Service

`crystalfontz` includes a dbus service, which can be started either through SystemD or directly through the command line.

## Starting the Service with SystemD

`crystalfontz` ships with a systemd unit that configures the service as a Dbus service. To set up the service, run:

```sh
sudo systemctl enable crystalfontz
sudo systemctl start crystalfontz  # optional
```

This unit will start on the `system` bus, under the root user.

## Running the Service Directly

The DBus service can be launched directly using `python3 -m crystalfontz.dbus.service`:

```sh
$ python3 -m crystalfontz.dbus.service --help
Usage: python3 -m crystalfontz.dbus.service [OPTIONS]

  Expose the Crystalfontz device as a DBus service.

Options:
  --global / --no-global          Load the global config file at
                                  /etc/crystalfontz.yaml (default true when
                                  called with sudo)
  -C, --config-file PATH          A path to a config file
  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Set the log level
  --user / --system               Connect to either the user or system bus
  --help                          Show this message and exit.
```

In most cases, this can be called without arguments. By default, the service will listen on the `system` bus and load the global config file (`/etc/crystalfontz.yml`) if launched as root; and otherwise listen on the `user` bus and load the user's config file (`~/.config/crystalfontz.yml`).
