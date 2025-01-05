# crystalfontz

`crystalfontz` is a Python library and CLI for interacting with [Crystalfontz](https://www.crystalfontz.com/) LCD displays. While it has an eye for supporting multiple devices, it was developed against a CFA533.

## Usage

Here's a basic example:

```py
import asyncio

from crystalfontz import create_connection, SLOW_BAUD_RATE


async def main():
    client = await create_connection(
        "/dev/ttyUSB0",
        model="CFA533",
        baud_rate=SLOW_BAUD_RATE
    )

    await client.send_data(0, 0, "Hello world!")


asyncio.run(main())
```

This will write "Hello world!" on the first line of the LCD.

The client has methods for every command supported by the CFA533. I unfortunately ran out of steam before completing the documentation, but the code in [`crystalfontz.client`](./crystalfontz/client.py) combined with [the datasheet](./docs/CFA533-TMI-KU.pdf) should help fill in the gaps.

### Reporting

If configured, Crystalfontz devices will report the status of the keypad and/or [DOW](https://en.wikipedia.org/wiki/1-Wire)-based temperature sensors. To that end, `crystalfontz` contains a `ReportHandler` abstraction. For instance:

```py
import asyncio

from crystalfontz import create_connection, LoggingReportHandler, SLOW_BAUD_RATE

async def main():
    client = await create_connection(
        "/dev/ttyUSB0",
        model="CFA533",
        baud_rate=SLOW_BAUD_RATE,
        report_handler=LoggingReportHandler()
    )


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

## CLI

This library has a CLI, which you can run like so:

```sh
crystalfontz --help
Usage: crystalfontz [OPTIONS] COMMAND [ARGS]...

  Control your Crystalfontz LCD

Options:
  --global / --no-global          Load the global config file at
                                  /etc/crystalfontz.yaml
  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Set the log level
  --port TEXT                     The serial port the Crystalfontz LCD is
                                  connected to
  --baud [19200|115200]           The baud rate to use when connecting to the
                                  Crystalfontz LCD
  --help                          Show this message and exit.

Commands:
  clear-screen                    6 (0x06): Clear LCD Screen
  configure-watchdog              29 (0x1D): Enable/Disable and Reset...
  cursor                          Interact with the LCD cursor
  dow                             DOW (Dallas One-Wire) capabilities
  gpio                            Interact with GPIO pins
  keypad                          Interact with the keypad
  listen                          Listen for reports
  ping                            0 (0x00): Ping command
  power                           5 (0x05): Reboot LCD, Reset Host,...
  read-lcd-memory                 10 (0x0A): Read 8 Bytes of LCD Memory
  read-status                     30 (0x1E): Read Reporting & Status
  send                            31 (0x1F): Send Data to LCD
  send-command-to-lcd-controler   22 (0x16): Send Command Directly to...
  set-atx-power-switch-functionality
                                  28 (0x1C): Set ATX Power Switch...
  set-backlight                   14 (0x0E): Set LCD & Keypad Backlight
  set-baud-rate                   33 (0x21): Set Baud Rate
  set-contrast                    13 (0x0D): Set LCD Contrast
  set-line-1                      7 (0x07): Set LCD Contents, Line 1
  set-line-2                      8 (0x08): Set LCD Contents, Line 2
  special-character               Commands involving special characters
  store-boot-state                4 (0x04): Store Current State as...
  temperature                     Temperature reporting and live display
  user-flash-area                 Interact with the User Flash Area
  versions                        1 (0x01): Get Hardware & Firmware...
```

A lot of the functionality has been fleshed out. However, there are some issues:

1. I haven't thoroughly tested the CLI. I developed the CLI after getting the client mostly buttoned up, and didn't get around to running all the commands again. Some commands may have bugs.
2. Commands which take raw bytes as arguments are generally unimplemented. This is because Python and Click don't expose arguments as raw bytestrings. Implementing these commands will require developing a DSL for specifying non-ASCII bytes.
3. Setting special character data. Special character data needs to be loaded from files - either as specially formatted text or as bitmap graphics - and that functionality is currently not fleshed out. This will be added once those features are more mature.
4. Commands which imply persisting state across invocations. While there's a nascent implementation of a config file format, the mechanisms for persisting that kind of data aren't fully fleshed out. Related commands include:
  - Setting the baud rate - if you set the baud rate and don't save the new baud rate for future connections, you will have a bad time.
  - Setting encodings from unicode characters to special character code points. Once you add a special character to the LCD, you need to tell `crystalfontz` how to convert unicode characters passed into `send_data` into bytes 0x01 to 0x07.
5. GPIO pin functionality. These functions take object arguments and don't require special support, it was just low priority to implement them.

## Development

I use `uv` for managing dependencies, but also compile `requirements.txt` and `requirements_dev.txt` files that one can use instead. I also use `just` for task running, but if you don't have it installed you can run the commands manually.

There *are* some unit tests in `pytest`, but they mostly target more complex cases of marshalling/unmarshalling and calculating packet CRCs. The bulk of testing involves setting up `crystalfontz` on the computer that has the CFA533, running an ad-hoc script, and seeing what it does.

I have the start of an integration test framework in the [plusdeck](https://github.com/jfhbrook/plusdeck) project, that I'd like to spin out into a reusable package. If I get around to that, I'll likely implement a proper integration test suite for the Crystalfontz.

### Issues

There is a *really* long tail of things that I'd like to tackle for this library. Most of those things are captured in [GitHub Issues](https://github.com/jfhbrook/crystalfontz/issues).

## License

Apache-2.0, see ``LICENSE``.
