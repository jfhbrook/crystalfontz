# crystalfontz

`crystalfontz` is a Python library and CLI for interacting with [Crystalfontz](https://www.crystalfontz.com/) LCD displays. While it has an eye for supporting multiple devices, it was developed against a CFA533.

## Install

`crystalfontz` is a Python package, and therefore can be installed [from PyPi](https://pypi.org/project/crystalfontz/), for instance with `pip`:

```sh
pip install crystalfontz
```

In addition, I have a Fedora package on COPR, which can be installed like so:

```sh
sudo dnf copr enable jfhbrook/joshiverse
sudo dnf install crystalfontz
```

## Usage

Here's a basic example:

```py
import asyncio

from crystalfontz import connection, SLOW_BAUD_RATE


async def main():
    # Will close the client on exit
    async with connection(
        "/dev/ttyUSB0",
        model="CFA533",
        baud_rate=SLOW_BAUD_RATE
    ) as client:
        await client.send_data(0, 0, "Hello world!")

asyncio.run(main())
```

This will write "Hello world!" on the first line of the LCD.

The client has methods for every command supported by the CFA533. For more documentation, refer to <https://crystalfontz.readthedocs.io> and [the CFA533 datasheet](./docs/CFA533-TMI-KU.pdf).

### Reporting

If configured, Crystalfontz devices will report the status of the keypad and/or [DOW](https://en.wikipedia.org/wiki/1-Wire)-based temperature sensors. To that end, `crystalfontz` contains a `ReportHandler` abstraction. For instance:

```py
import asyncio

from crystalfontz import create_connection, LoggingReportHandler, SLOW_BAUD_RATE

async def main():
    client = await create_connection(
        "/dev/ttyUSB0",
        model="CFA533",
        report_handler=LoggingReportHandler(),
        baud_rate=SLOW_BAUD_RATE
    )

    # Client will close if there's an error
    await client.closed


asyncio.run(main())
```

With factory settings for the CFA533, running this and then mashing the keypad will log keypad events to the terminal. To create your own behavior, subclass `ReportHandler` and pass an instance of your subclass into the `report_handler` argument.

## Support

### Devices

* `CFA533`: Most features have been tested with a real CFA533.
* `CFA633`: The CFA633 has **not** been tested. However, the documentation for the CFA533 includes some details on how the CFA633 differs from the CFA533, such that I have _ostensive_ support for it. Feel free to try it out, but be aware that it may have bugs.
* Other devices: Crystalfontz has other devices, but I haven't investigated them. As such, these other devices are currently unsupported. However, it's believed that it would be easy to add support for a device, by reading through its data sheet and implementing device-specific functionality in [`crystalfontz.device`](./crystalfontz/device.py).

### Features

The basic features have all been tested with a real CFA533. However, there are a number of features when have **not** been tested, as I'm not using them. These features tend to be related to the CFA533's control unit capabilities:

* ATX power supply control functionality
* DOW and temperature related functionality
* GPIO pin related functionality
* Watchdog timer

These features have been filled in, they type check, and they _probably_ work, mostly. But it's not viable for me to test them. If you're in a position where you need these features, give them a shot and let me know if they work for you!

### Timeouts and Retries

This library includes a default timeout for command responses, as well as the ability to retry. The default timeout is 250ms. This is the timeout recommended in the CFA533 documentation. By default the library does not retry commands - in practice, the CFA533 is *very* reliable, and so they were deemed unnecessary.

## CLI

This library has a CLI, which you can run like so:

```sh
crystalfontz --help
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

### Byte Parameters

Some CLI parameters encode raw bytes. In these cases, the inputs support [the same escape sequences as Python's byte strings](https://docs.python.org/3/reference/lexical_analysis.html#escape-sequences). This includes hex numbers (`\xff`) and octal numbers (`\o333`). Note that unicode characters are parsed as utf-8.

### Output Format

This CLI supports two output formats: `text` and `json`. The former will output a human-readable format, and the latter will output JSON. When generating JSON output, bytes are encoded in base64.

### Open Issues

A lot of the functionality has been fleshed out. However, there are some issues:

1. Setting special character data. Special character data needs to be loaded from files - either as specially formatted text or as bitmap graphics - and that functionality is currently not fleshed out. This will be added once those features are more mature.
2. Commands which imply persisting state across invocations. While there's a nascent implementation of a config file format, the mechanisms for persisting that kind of data aren't fully fleshed out. Related commands include:
  - Setting the baud rate - if you set the baud rate and don't save the new baud rate for future connections, you will have a bad time.
  - Setting encodings from unicode characters to special character code points. Once you add a special character to the LCD, you need to tell `crystalfontz` how to convert unicode characters passed into `send_data` into bytes 0x01 to 0x07.

## Development

I use `uv` for managing dependencies, but also compile `requirements.txt` and `requirements_dev.txt` files that one can use instead. I also use `just` for task running, but if you don't have it installed you can run the commands manually.

There *are* some unit tests in `pytest`, but they mostly target more complex cases of marshalling/unmarshalling and calculating packet CRCs. The bulk of testing involves setting up `crystalfontz` on the computer that has the CFA533, running the `./tests/integration.sh` script, and seeing what it does.

### Issues

There is a *really* long tail of things that I'd like to tackle for this library. Most of those things are captured in [GitHub Issues](https://github.com/jfhbrook/crystalfontz/issues).

## Changelog

See [`CHANGELOG.md`](./CHANGELOG.md).

## License

Apache-2.0, see [`LICENSE`](./LICENSE).
