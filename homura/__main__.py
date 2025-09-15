import asyncio
from homura.server import Server
from homura.utils.log import setupLogging
import logging
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout

logger = logging.getLogger(__name__)

server = Server()


async def prompt():
    while not server.started:
        await asyncio.sleep(0)

    session = PromptSession()
    with patch_stdout():
        while True:
            fullCommand: str = await session.prompt_async("> ")
            command = fullCommand.split(" ")
            match command[0]:
                case "say":
                    logger.info(f"[Server] {' '.join(command[1:])}")
                case "stop":
                    await server.stop()
                    break
                case _:
                    logger.info("Command not found")


async def main():
    setupLogging()

    task = asyncio.create_task(prompt())

    try:
        await server.start()
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logger.error("An error occurred on server start up.", e)
        task.cancel()


if __name__ == "__main__":
    asyncio.run(main())
