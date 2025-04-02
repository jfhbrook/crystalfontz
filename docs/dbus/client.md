# DBus Client CLI

Assuming `crystalfontzd` is running, you may interact with the service using `crystalfontzctl`:

```sh
$ crystalfontzctl --help
Usage: crystalfontzctl [OPTIONS] COMMAND [ARGS]...

  Control your Crystalfontz device.

Options:
  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Set the log level
  --output [text|json]            Output either human-friendly text or JSON
  --user / --no-user              Connect to the user bus
  --help                          Show this message and exit.

Commands:
  atx          28 (0x1C): Set ATX Power Switch Functionality
  backlight    14 (0x0E): Set LCD & Keypad Backlight
  baud         33 (0x21): Set Baud Rate
  character    Interact with special characters
  clear        6 (0x06): Clear LCD Screen
  config       Configure crystalfontz.
  contrast     13 (0x0D): Set LCD Contrast
  cursor       Interact with the LCD cursor
  dow          DOW (Dallas One-Wire) capabilities
  flash        Interact with the User Flash Area
  gpio         Interact with GPIO pins
  keypad       Interact with the keypad
  lcd          Interact directly with the LCD controller
  line         Set LCD contents for a line
  listen       Listen for key and temperature reports.
  ping         0 (0x00): Ping command
  power        5 (0x05): Reboot LCD, Reset Host, or Power Off Host
  send         31 (0x1F): Send Data to LCD
  status       30 (0x1E): Read Reporting & Status
  store        4 (0x04): Store Current State as Boot State
  temperature  Temperature reporting and live display
  versions     1 (0x01): Get Hardware & Firmware Version
  watchdog     29 (0x1D): Enable/Disable and Reset the Watchdog
```

The interface is similar to the vanilla `crystalfontz` CLI. However, there are a few differences:

1. By default, `crystalfontzctl` will connect to the `system` bus. To connect to the local bus, set the `--user` flag.
2. Configuration commands do not reload `crystalfontzctl`'s configuration. Instead, they will update the relevant config file, and show the differences between the file config and the service's loaded config.
3. If the config file isn't owned by the user, `crystalfontzctl` will attempt to run editing commands with `sudo`.
