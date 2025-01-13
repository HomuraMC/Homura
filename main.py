import asyncio
import sys
import time

from core import logger
from core.config import Config
from core.server import Server

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

HOMURAMC = "2024.08.16β"

startTime = time.time()
log = logger.get_module_logger("HomuraMC")

log.info(f"""Starting HomuraMC v{HOMURAMC}...""")

log.info("Loading properties from homura.yml")
config = Config().config
log.info("HomuraMC configuration file loaded successfully")


async def main():
    instance = Server()
    server = await asyncio.start_server(
        instance.run, config.listen.ip, config.listen.port
    )
    endTime = time.time()
    during = (endTime - startTime) * 1000
    during_s = during / 1000
    log.info(f"listening on {config.listen.ip}:{config.listen.port}")
    log.info(f"Done ({during_s}s)!")
    await server.serve_forever()


asyncio.run(main())
