# Command Line Interface

This library has a CLI, which you can run like so:

```sh
$ python3 -m crystalfontz --help
Usage: crystalfontz [OPTIONS] COMMAND [ARGS]...

  Control your Crystalfontz device

Options:
  --global / --no-global          Load the global config file at
                                  /etc/crystalfontz.yaml
  -C, --config-file PATH          A path to a config file
  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Set the log level
  --port TEXT                     The serial port the device is connected to
  --model [CFA533|CFA633]         The model of the device
  --hardware-rev TEXT             The hardware revision of the device
  --firmware-rev TEXT             The firmware revision of the device
  --detect / --no-detect          When set, detect device version
  --output [text|json]            Output either human-friendly text or JSON
  --timeout FLOAT                 How long to wait for a response from the
                                  device before timing out
  --retry-times INTEGER           How many times to retry a command if a
                                  response times out
  --baud [19200|115200]           The baud rate to use when connecting to the
                                  device
  --help                          Show this message and exit.

Commands:
  atx          28 (0x1C): Set ATX Power Switch Functionality
  backlight    14 (0x0E): Set LCD & Keypad Backlight
  baud         33 (0x21): Set Baud Rate
  character    Interact with special characters
  clear        6 (0x06): Clear LCD Screen
  contrast     13 (0x0D): Set LCD Contrast
  cursor       Interact with the LCD cursor
  dow          DOW (Dallas One-Wire) capabilities
  effects      Run various effects, such as marquees
  flash        Interact with the User Flash Area
  gpio         Interact with GPIO pins
  keypad       Interact with the keypad
  lcd          Interact directly with the LCD controller
  line         Set LCD contents for a line
  listen       Listen for keypress and temperature reports
  ping         0 (0x00): Ping command
  power        5 (0x05): Reboot LCD, Reset Host, or Power Off Host
  send         31 (0x1F): Send Data to LCD
  status       30 (0x1E): Read Reporting & Status
  store        4 (0x04): Store Current State as Boot State
  temperature  Temperature reporting and live display
  versions     1 (0x01): Get Hardware & Firmware Version
  watchdog     29 (0x1D): Enable/Disable and Reset the Watchdog
```

## Byte Parameters

Some CLI parameters encode raw bytes. In these cases, the inputs support [the same escape sequences as Python's byte strings](https://docs.python.org/3/reference/lexical_analysis.html#escape-sequences). This includes hex numbers (`\xff`) and octal numbers (`\o333`). Note that unicode characters are parsed as utf-8.

## Output Format

This CLI supports two output formats: `text` and `json`. The former will output a human-readable format, and the latter will output JSON. When generating JSON output, bytes are encoded in base64.

## Installing the `crystalfontz` Shim

Included in this project is `./bin/crystalfontz`, a script that you can add to your PATH for convenience.
