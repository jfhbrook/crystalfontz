import asyncio

from crystalfontz.client import create_connection

async def main() -> None:
    conn = await create_connection("/dev/ttyUSB0")
    print(conn)


asyncio.run(main())
