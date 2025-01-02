import asyncio
import logging

from crystalfontz.client import create_connection
from crystalfontz.report import LoggingReportHandler

async def main() -> None:
    logging.basicConfig(level=logging.DEBUG)

    client = await create_connection("/dev/ttyUSB0", report_handler=LoggingReportHandler())

    await client.load_device()

    for _ in range(10):
        print(await client.poll_keypad())
        await asyncio.sleep(1)

    print(await client.poke(0x40))

    marquee = client.marquee(0, "Josh is cool")

    f = asyncio.create_task(marquee.run())

    await asyncio.sleep(10)

    marquee.stop()

    await f

    screensaver = client.screensaver("Josh!")

    f = asyncio.create_task(screensaver.run())

    await f


loop = asyncio.get_event_loop()
loop.create_task(main())
loop.run_forever()
