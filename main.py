from twisted.internet import reactor
from quarry.net.server import ServerFactory

import configparser
import sys
import os

from classes import toBool
from classes import log
from classes import HomuraServerProtocol

HomuraMCVersion = "v0.0.1"
HomuraMCConfigVersion = "1"
HomuraMCConfigVersionStr = "v0.0.1"

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

if os.path.isfile("./Homura.ini") == False:
    with open("Homura.ini", "w") as configfile:
        defaultini.write(configfile)

ini = configparser.ConfigParser()
ini.read("./Homura.ini", "UTF-8")
isConfigVer = "config_version" in ini["HomuraMC"]
if (isConfigVer == False) or (
    ini["HomuraMC"]["config_version"] != HomuraMCConfigVersion
):
    log.logger.info(
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
    with open("Homura.ini", "w") as configfile:
        ini.write(configfile)
        log.logger.info(
            f"The configuration file (Homura.ini) is Updated to {HomuraMCConfigVersionStr}!",
            "[info]",
        )
else:
    isserverip = "server_ip" in ini["HomuraMC"]
    if isserverip == False:
        ini["HomuraMC"]["server_ip"] = defaultini["HomuraMC"]["server_ip"]
        log.logger.warn(
            "The value of server_ip, which for some reason was not there, has been corrected to {}.".format(
                defaultini["HomuraMC"]["server_ip"]
            )
        )
    isport = "port" in ini["HomuraMC"]
    if isport == False:
        ini["HomuraMC"]["port"] = defaultini["HomuraMC"]["port"]
        log.logger.warn(
            "The value of port, which for some reason was not there, has been corrected to .".format(
                defaultini["HomuraMC"]["port"]
            )
        )
    ismotd = "motd" in ini["HomuraMC"]
    if ismotd == False:
        ini["HomuraMC"]["motd"] = defaultini["HomuraMC"]["motd"]
        log.logger.warn(
            "The value of motd, which for some reason was not there, has been corrected to .".format(
                defaultini["HomuraMC"]["motd"]
            )
        )
    ismaxplayers = "max_players" in ini["HomuraMC"]
    if ismaxplayers == False:
        ini["HomuraMC"]["max_players"] = defaultini["HomuraMC"]["max_players"]
        log.logger.warn(
            "The value of max_players, which for some reason was not there, has been corrected to .".format(
                defaultini["HomuraMC"]["max_players"]
            )
        )
    iseula = "eula" in ini["HomuraMC"]
    if iseula == False:
        ini["HomuraMC"]["eula"] = defaultini["HomuraMC"]["eula"]
        log.logger.warn(
            "The value of eula, which for some reason was not there, has been corrected to .".format(
                defaultini["HomuraMC"]["eula"]
            )
        )
    isservericon = "server_icon" in ini["HomuraMC"]
    if isservericon == False:
        ini["HomuraMC"]["server_icon"] = defaultini["HomuraMC"]["eula"]
        log.logger.warn(
            "The value of server_icon, which for some reason was not there, has been corrected to .".format(
                defaultini["HomuraMC"]["server_icon"]
            )
        )
    with open("Homura.ini", "w") as configfile:
        ini.write(configfile)

if toBool(ini["HomuraMC"]["eula"]) != True:
    log.logger.error(
        "You do not agree with the eula! The eula can be read at https://aka.ms/MinecraftEULA and to agree, set the eula to True in Homura.ini."
    )
    print("Press Key to Continue...")
    input()
    sys.exit()


class HomuraServerFactory(ServerFactory):
    protocol = HomuraServerProtocol
    motd = ini["HomuraMC"]["motd"]
    force_protocol_version = 578
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
                player.buff_type.pack_chat(message) + player.buff_type.pack("B", 0),
            )

    def send_msg(self, message, name):
        for player in self.players:
            if player.display_name == name:
                player.send_packet(
                    "chat_message",
                    player.buff_type.pack_chat(message) + player.buff_type.pack("B", 0),
                )

    def getPlayers(self):
        pltt = ""
        for player in self.players:
            pltt = f"{pltt},{player.display_name}"
        return pltt

    def getPlayersCount(self):
        return len(self.players)


def main():
    # Create factory
    factory = HomuraServerFactory()

    # Listen
    factory.listen(ini["HomuraMC"]["server_ip"], int(ini["HomuraMC"]["port"]))
    reactor.run()


if __name__ == "__main__":
    log(f"Homura {HomuraMCVersion} is Finished Loading!")
    main()
