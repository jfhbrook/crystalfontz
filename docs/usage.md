# Getting Started

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

The client has methods for every command supported by the CFA533. For more documentation, refer to <https://crystalfontz.readthedocs.io> and [the CFA533 datasheet](./CFA533-TMI-KU.pdf).

## Reporting

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

## Timeouts and Retries

This library includes a default timeout for command responses, as well as the ability to retry. The default timeout is 250ms. This is the timeout recommended in the CFA533 documentation. By default the library does not retry commands - in practice, the CFA533 is *very* reliable, and so they were deemed unnecessary.
