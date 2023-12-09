import configparser
import sys
import os
import importlib
import builtins

from twisted.internet import reactor
from quarry.net.server import ServerFactory
from quarry.types.nbt import RegionFile
import requests
from tqdm import tqdm

from classes import toBool
from classes import log
from classes import HomuraServerProtocol
from classes import download

reactor.suggestThreadPoolSize(50)

HomuraMCVersion = "v0.0.1"
HomuraMCConfigVersion = "1"
HomuraMCConfigVersionStr = "v0.0.1"
logger = log.logger
download_jdk = download.download_jdk

defaultini = configparser.ConfigParser()
defaultini["HomuraMC"] = {
    "config_version": HomuraMCConfigVersion,
    "server_ip": "0.0.0.0",
    "port": 25565,
    "motd": "A Minecraft Server",
    "max_players": 20,
    "server_icon": "server_icon_path_here",
    "eula": False,
}

if not os.path.isfile(os.path.join(os.path.dirname(__file__), "Homura.ini")):
    with open(
        os.path.join(os.path.dirname(__file__), "Homura.ini"), "w", encoding="utf-8"
    ) as configfile:
        defaultini.write(configfile)

if not os.path.exists(os.path.join(os.path.dirname(__file__), "assets/java")):
    logger.warning("Java16 not found. downloading...")
    # logger.warning(
    #     "Homura cannot determine CPU architecture. Therefore, if the wrong java is downloaded, please download java again from setup.py."
    # )
    download_jdk()
    logger.info("Download of server jar has been completed.")

if not os.path.isfile(
    os.path.join(os.path.dirname(__file__), "assets/registry/server.jar")
):
    logger.warning("server.jar not found. downloading...")
    download.download_sjar()
    logger.info("Download of server jar has been completed.")

ini = configparser.ConfigParser()
ini.read(os.path.join(os.path.dirname(__file__), "Homura.ini"), "UTF-8")
isConfigVer = "config_version" in ini["HomuraMC"]
if (isConfigVer == False) or (
    ini["HomuraMC"]["config_version"] != HomuraMCConfigVersion
):
    logger.info(
        f"The configuration file (Homura.ini) is an outdated version! The configuration file is updated to {HomuraMCConfigVersionStr}...",
    )

    ini["HomuraMC"]["config_version"] = HomuraMCConfigVersion
    isserverip = "server_ip" in ini["HomuraMC"]
    if isserverip == False:
        ini["HomuraMC"]["server_ip"] = defaultini["HomuraMC"]["server_ip"]
    isport = "port" in ini["HomuraMC"]
    if isport == False:
        ini["HomuraMC"]["port"] = defaultini["HomuraMC"]["port"]
    ismotd = "motd" in ini["HomuraMC"]
    if ismotd == False:
        ini["HomuraMC"]["motd"] = defaultini["HomuraMC"]["motd"]
    ismaxplayers = "max_players" in ini["HomuraMC"]
    if ismaxplayers == False:
        ini["HomuraMC"]["max_players"] = defaultini["HomuraMC"]["max_players"]
    iseula = "eula" in ini["HomuraMC"]
    if iseula == False:
        ini["HomuraMC"]["eula"] = defaultini["HomuraMC"]["eula"]
    isservericon = "server_icon" in ini["HomuraMC"]
    if isservericon == False:
        ini["HomuraMC"]["server_icon"] = defaultini["HomuraMC"]["eula"]
    with open("Homura.ini", "w", encoding="utf-8") as configfile:
        ini.write(configfile)
        logger.info(
            f"The configuration file (Homura.ini) is Updated to {HomuraMCConfigVersionStr}!",
        )
else:
    isserverip = "server_ip" in ini["HomuraMC"]
    if isserverip == False:
        ini["HomuraMC"]["server_ip"] = defaultini["HomuraMC"]["server_ip"]
        logger.warn(
            "The value of server_ip, which for some reason was not there, has been corrected to {}.".format(
                defaultini["HomuraMC"]["server_ip"]
            )
        )
    isport = "port" in ini["HomuraMC"]
    if isport == False:
        ini["HomuraMC"]["port"] = defaultini["HomuraMC"]["port"]
        logger.warn(
            "The value of port, which for some reason was not there, has been corrected to .".format(
                defaultini["HomuraMC"]["port"]
            )
        )
    ismotd = "motd" in ini["HomuraMC"]
    if ismotd == False:
        ini["HomuraMC"]["motd"] = defaultini["HomuraMC"]["motd"]
        logger.warn(
            "The value of motd, which for some reason was not there, has been corrected to .".format(
                defaultini["HomuraMC"]["motd"]
            )
        )
    ismaxplayers = "max_players" in ini["HomuraMC"]
    if ismaxplayers == False:
        ini["HomuraMC"]["max_players"] = defaultini["HomuraMC"]["max_players"]
        logger.warn(
            "The value of max_players, which for some reason was not there, has been corrected to .".format(
                defaultini["HomuraMC"]["max_players"]
            )
        )
    iseula = "eula" in ini["HomuraMC"]
    if iseula == False:
        ini["HomuraMC"]["eula"] = defaultini["HomuraMC"]["eula"]
        logger.warn(
            "The value of eula, which for some reason was not there, has been corrected to .".format(
                defaultini["HomuraMC"]["eula"]
            )
        )
    isservericon = "server_icon" in ini["HomuraMC"]
    if isservericon == False:
        ini["HomuraMC"]["server_icon"] = defaultini["HomuraMC"]["eula"]
        logger.warn(
            "The value of server_icon, which for some reason was not there, has been corrected to .".format(
                defaultini["HomuraMC"]["server_icon"]
            )
        )
    with open("Homura.ini", "w", encoding="utf-8") as configfile:
        ini.write(configfile)

if toBool(ini["HomuraMC"]["eula"]) != True:
    logger.error(
        "You do not agree with the eula! The eula can be read at https://aka.ms/MinecraftEULA and to agree, set the eula to True in Homura.ini."
    )
    print("Press Key to Continue...")
    input()
    sys.exit()

builtins.plugins = []
for file in os.listdir("./plugins/"):
    base, ext = os.path.splitext(file)
    if ext == ".py":
        logger.info("Python Script {} is loading...".format(file))
        plpy = importlib.import_module("plugins.{}".format(base))
        isplugin = getattr(plpy, "HomuraMCPlugin", False)
        if isplugin == False:
            logger.warning("Python Script {} is Not HomuraMC Plugin!".format(file))
        else:
            builtins.plugins.append(plpy)
            logger.info("Python Script {} is Loading Successful.".format(file))
            if getattr(plpy.HomuraMCPlugin, "onLoad", False) != False:
                plpy.HomuraMCPlugin.onLoad()

builtins.sent_chunks = {}
builtins.counter = {}

builtins.loaded_regions = {}
builtins.loaded_chunks = {}

builtins.queue = []

logger.info("Loading spawn chunks, please wait...")

for x in range(-10, 11):
    for z in range(-10, 11):
        x2 = x * 16
        z2 = z * 16

        rx, x2 = divmod(x2, 512)
        rz, z2 = divmod(z2, 512)
        cx, x2 = divmod(x2, 16)
        cz, z2 = divmod(z2, 16)

        if (str(rx) + ";" + str(rz)) in builtins.loaded_regions:
            region = builtins.loaded_regions[str(rx) + ";" + str(rz)]
        else:
            region = RegionFile(
                os.path.join(
                    os.getcwd(), "assets", "world", "region", "r.%d.%d.mca" % (rx, rz)
                )
            )
            builtins.loaded_regions[str(rx) + ";" + str(rz)] = region

        try:
            if not (str(cx) + ";" + str(cz)) in builtins.loaded_chunks:
                builtins.loaded_chunks[
                    str(rx) + ";" + str(rz) + "#" + str(cx) + ";" + str(cz)
                ] = region.load_chunk(cx, cz)
        except ValueError as e:
            continue
        except OSError as e:
            continue

logger.info("Spawn chunks succesfully loaded!")
for plugin in builtins.plugins:
    if getattr(plugin.HomuraMCPlugin, "onSpawnChunkLoad", False) != False:
        plugin.HomuraMCPlugin.onSpawnChunkLoad()


class HomuraServerFactory(ServerFactory):
    protocol = HomuraServerProtocol
    motd = ini["HomuraMC"]["motd"]
    force_protocol_version = 754
    max_players = int(ini["HomuraMC"]["max_players"])
    if ini["HomuraMC"]["server_icon"] == "":
        icon_path = None
    elif os.path.isfile(ini["HomuraMC"]["server_icon"]) == False:
        icon_path = None
    else:
        icon_path = ini["HomuraMC"]["server_icon"]

    def send_chat(self, message):
        for player in self.players:
            player.send_packet(
                "chat_message",
                player.buff_type.pack_chat(message)
                + player.buff_type.pack("B", 0)
                + player.buff_type.pack_uuid(player.uuid),
            )

    def send_msg(self, message, name):
        for player in self.players:
            if player.display_name == name:
                player.send_packet(
                    "chat_message",
                    player.buff_type.pack_chat(message)
                    + player.buff_type.pack("B", 0)
                    + player.buff_type.pack_uuid(player.uuid),
                )

    def getPlayers(self):
        pltt = ""
        for player in self.players:
            pltt = f"{player.display_name},"
        return pltt

    def getPlayersCount(self):
        return len(self.players)


def main():
    # Create factory
    factory = HomuraServerFactory()

    # Listen
    logger.info(f"Homura {HomuraMCVersion} is Finished Loading!")
    factory.listen(ini["HomuraMC"]["server_ip"], int(ini["HomuraMC"]["port"]))
    reactor.run()


if __name__ == "__main__":
    main()
