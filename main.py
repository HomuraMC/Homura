import configparser
import sys
import os

from twisted.internet import reactor
from quarry.net.server import ServerFactory

from classes import toBool
from classes import log
from classes import HomuraServerProtocol
from classes import download
from classes.WorldData import WorldData
from classes.PluginLoader import PluginLoader

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
	#	 "Homura cannot determine CPU architecture. Therefore, if the wrong java is downloaded, please download java again from setup.py."
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

pluginloader = PluginLoader()
pflag = pluginloader.loadPlugins()

logger.info("Loading spawn chunks, please wait...")

worlddata = WorldData()
wflag = worlddata.loadChunk()

logger.info("Spawn chunks succesfully loaded!")
for plugin in PluginLoader.plugins:
	if getattr(plugin.HomuraMCPlugin,'onSpawnChunkLoad',False) != False:
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
				player.buff_type.pack_chat(message) + player.buff_type.pack("B", 0) + player.buff_type.pack_uuid(player.uuid),
			)

	def send_msg(self, message, uuid):
		for player in self.players:
			if player.uuid == uuid:
				player.send_packet(
					"chat_message",
					player.buff_type.pack_chat(message) + player.buff_type.pack("B", 0) + player.buff_type.pack_uuid(player.uuid),
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
