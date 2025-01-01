import asyncio

from crystalfontz.client import create_connection
from crystalfontz.response import KeyActivityReport

async def main() -> None:
    client = await create_connection("/dev/ttyUSB0")

    reports = client.subscribe(KeyActivityReport)

    while True:
        print(await reports.get())


asyncio.run(main())
