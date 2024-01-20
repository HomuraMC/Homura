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
from classes.Config import Config
from classes.lognk import log

reactor.suggestThreadPoolSize(50)

HomuraMCVersion = "v0.0.1"
HomuraMCConfigVersion = 1
HomuraMCConfigVersionStr = "v0.0.1"
logger = log.logger
download_jdk = download.download_jdk

defaultconf = {
	"config_version": HomuraMCConfigVersion,
	"server_ip": "0.0.0.0",
	"port": 25565,
	"motd": "A Minecraft Server",
	"max_players": 20,
	"server_icon": "server_icon_path_here",
	"eula": False,
}

config = Config()
if not os.path.isfile(os.path.join(os.path.dirname(__file__), "config.yml")):
	config.save(defaultconf)
config.load()

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



if Config.data["eula"] != True:
	logger.error(
		"You do not agree with the eula! The eula can be read at https://aka.ms/MinecraftEULA and to agree, set the eula to True in Homura.ini."
	)
	print("Press Key to Continue...")
	input()
	sys.exit()

pluginloader = PluginLoader()
pluginloader.loadPlugins()

logger.info("Loading spawn chunks, please wait...")

worlddata = WorldData()
worlddata.loadChunk()

logger.info("Spawn chunks succesfully loaded!")
for plugin in PluginLoader.plugins:
	if getattr(plugin.HomuraMCPlugin,'onSpawnChunkLoad',False) != False:
		plugin.HomuraMCPlugin.onSpawnChunkLoad()

class HomuraServerFactory(ServerFactory):
	protocol = HomuraServerProtocol
	motd = Config.data["motd"]
	force_protocol_version = 754
	max_players = int(Config.data["max_players"])
	if Config.data["server_icon"] == "":
		icon_path = None
	elif os.path.isfile(Config.data["server_icon"]) == False:
		icon_path = None
	else:
		icon_path = Config.data["server_icon"]

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
	factory.listen(Config.data["server_ip"], int(Config.data["port"]))
	reactor.run()


if __name__ == "__main__":
	main()
