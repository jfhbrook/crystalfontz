import asyncio

from crystalfontz.client import create_connection
from crystalfontz.response import KeyActivityReport

async def main() -> None:
    client = await create_connection("/dev/ttyUSB0")

    pong = await client.ping(b"ping!")
    
    print(pong)



asyncio.run(main())
