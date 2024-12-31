import asyncio

from crystalfontz.client import create_connection

async def main() -> None:
    client = await create_connection("/dev/ttyUSB0")

    for i in range(10):
        print(await client.reports.get())

    client.close()


asyncio.run(main())
