import asyncio

from crystalfontz.client import create_connection

async def main() -> None:
    client = await create_connection("/dev/ttyUSB0")
    print(await client.versions())


asyncio.run(main())
