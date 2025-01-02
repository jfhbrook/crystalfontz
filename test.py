import asyncio
import logging

from crystalfontz.client import create_connection
from crystalfontz.cursor import CursorStyle
from crystalfontz.report import LoggingReportHandler

async def main() -> None:
    logging.basicConfig(level=logging.DEBUG)

    client = await create_connection("/dev/ttyUSB0", report_handler=LoggingReportHandler())

    print(await client.versions())
    print(await client.clear_screen())
    print(await client.set_contrast(0.5))
    print(await client.set_backlight(10))
    # crystalfontz.error.UnknownResponseError: Unknown response (76, b'')
    print(await client.set_cursor_style(CursorStyle.BLINKING_UNDERSCORE))
    print(await client.set_cursor_position(1, 3))

    await asyncio.sleep(10)

    print(await client.reboot_lcd())


loop = asyncio.get_event_loop()
loop.create_task(main())
loop.run_forever()
