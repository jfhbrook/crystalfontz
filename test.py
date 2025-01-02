import asyncio
import logging

from crystalfontz.client import create_connection
from crystalfontz.report import LoggingReportHandler

async def main() -> None:
    logging.basicConfig(level=logging.DEBUG)

    client = await create_connection("/dev/ttyUSB0", report_handler=LoggingReportHandler())

    print(await client.clear_screen())


loop = asyncio.get_event_loop()
loop.create_task(main())
loop.run_forever()
