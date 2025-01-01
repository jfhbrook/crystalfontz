import asyncio

from crystalfontz.client import create_connection

async def main() -> None:
    client = await create_connection("/dev/ttyUSB0")

    pong = await client.ping(b"ping!")

    print(pong)

    versions = await client.versions()

    print(versions)

    print(await client.set_line_1("Hello"))
    print(await client.set_line_2("world!"))


asyncio.run(main())
