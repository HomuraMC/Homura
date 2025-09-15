import asyncio
import logging
from homura.exceptions import *
from homura.protocol.stream import Stream

logger = logging.getLogger(__name__)


class Server:
    def __init__(self):
        self.address = "0.0.0.0"
        self.port = 25565
        self.server = None
        self.started = False

    async def start(self):
        try:
            self.server = await asyncio.start_server(
                self.handleConnection, host=self.address, port=self.port
            )
        except OSError as e:
            if e.errno == 98:
                raise ServerBindingException(self.address, self.port)

            raise

        logger.info(f"Homura server is started at {self.address}:{self.port}")
        self.started = True

        await self.server.serve_forever()

    async def stop(self):
        self.server.close()
        await self.server.wait_closed()
        logger.info("Homura server closed. see you!")

    async def close(self, stream: Stream):
        try:
            await stream.drain()
        except (ConnectionResetError, BrokenPipeError):
            pass

        try:
            stream.close()
            await stream.waitClosed()
        except (ConnectionResetError, BrokenPipeError):
            pass

        logger.debug(f"Disconnected nicely from {stream.remote}")

        return False, stream

    async def handleConnection(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        stream = Stream(reader, writer)

        logger.info(f"Connection received from {stream.remote}")

        while True:
            try:
                # I'll write this code after school trip
                # await self.handlePacket(stream)
                raise CloseConnection
            except CloseConnection:
                break
            except (ConnectionResetError, BrokenPipeError):
                break

        await self.close(stream)
