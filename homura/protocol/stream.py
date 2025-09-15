import asyncio


class Stream:
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        self.reader = reader
        self.writer = writer

        self.remoteAddress = writer.get_extra_info("peername")[0]
        self.remotePort = writer.get_extra_info("peername")[1]

    @property
    def remote(self):
        return f"{self.remoteAddress}:{self.remotePort}"

    async def drain(self):
        await self.writer.drain()

    def close(self):
        self.writer.close()

    async def waitClosed(self):
        await self.writer.wait_closed()

    async def read(self, n: int = -1):
        await self.reader.read(n)
