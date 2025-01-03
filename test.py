import asyncio
import logging

from crystalfontz.character import SpecialCharacter, ROM
from crystalfontz.client import create_connection
from crystalfontz.report import NoopReportHandler, LoggingReportHandler

char = SpecialCharacter.from_str("""
        
 xxxxxx 
xx xx xx
xx xx xx 
xxxxxxxx
x xxxx x
xx    xx
 xxxxxx 
""")

ROM.set_encoding("☺", b"\x00")

async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    client = await create_connection("/dev/ttyUSB0", report_handler=NoopReportHandler())

    # await client.set_backlight(0.1)

    # for _ in range(10):
    #     print(await client.poll_keypad())
    #     await asyncio.sleep(5)

    # print(await client.poke(0x40))

    await client.clear_screen()

    await client.set_special_character_data(0x00, char)

    await client.send_data(0, 0, "☺")

    # marquee = client.marquee(0, "Josh is cool")

    # await marquee.run()

    # screensaver = client.screensaver("Josh!")

    # await screensaver.run()


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.create_task(main())
loop.run_forever()
