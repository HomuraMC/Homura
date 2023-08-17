from twisted.internet import reactor
from quarry.net.server import ServerFactory, ServerProtocol

from lognk import log
from colorama import Fore, Back, Style

import configparser
import sys
import os
from booltool import toBool

import time


ini = configparser.ConfigParser()
ini['HomuraMC'] = {'server_ip': '0.0.0.0','port': 25565,'motd': 'A Minecraft Server','token': "<How To Token Get: https://kqzz.github.io/mc-bearer-token/>",'eula': False}
if os.path.isfile("./Homura.ini") == False:
	with open('Homura.ini', 'w') as configfile:
		# 指定したconfigファイルを書き込み
		ini.write(configfile)

ini.read('./Homura.ini', 'UTF-8')
if toBool(ini['HomuraMC']['eula']) != True:
	log(Fore.RED + "You do not agree with the eula! The eula can be read at https://aka.ms/MinecraftEULA and to agree, set the eula to True in Homura.ini." + Fore.RESET,Fore.RED + "[error]" + Fore.RESET)
	print("Press Key to Continue...")
	input()
	sys.exit()


class HomuraServerProtocol(ServerProtocol):
	def close(self = None,kmsg = None):
		if (self != None) and (kmsg != None):
			ServerProtocol.close(self,kmsg)
			log(f"{Fore.RED}{self.display_name} is Kicked:{Fore.RESET} {kmsg}")
		else:
			ServerProtocol.close(self)
	def player_joined(self):
		# Call super. This switches us to "play" mode, marks the player as
		#   in-game, and does some logging.
		ServerProtocol.player_joined(self)

		# Send "Join Game" packet
		log(f"{self.display_name} is trying connect!")
		if self.protocol_version > 578:
			self.close("Outdated server! I'm still on 1.15.2")
		elif self.protocol_version < 578:
			self.close("Outdated client! I'm using 1.15.2")
		self.send_packet("join_game",
			self.buff_type.pack("iBqiB",
				0,							  # entity id
				3,							  # game mode
				0,							  # dimension
				0,							  # hashed seed
				0),							 # max players
			self.buff_type.pack_string("flat"), # level type
			self.buff_type.pack_varint(1),	  # view distance
			self.buff_type.pack("??",
				False,						  # reduced debug info
				True))						  # show respawn screen

		# Send "Player Position and Look" packet
		self.send_packet("player_position_and_look",
			self.buff_type.pack("dddff?",
				0,						 # x
				255,					   # y
				0,						 # z
				0,						 # yaw
				0,						 # pitch
				0b00000),				  # flags
			self.buff_type.pack_varint(0)) # teleport id

		# Start sending "Keep Alive" packets
		self.ticker.add_loop(20, self.update_keep_alive)

		# Announce player joined
		self.factory.send_chat(u"\u00a7e%s has joined." % self.display_name)
		log(f"{self.display_name} has joined.")

	def player_left(self):
		ServerProtocol.player_left(self)

		# Announce player left
		self.factory.send_chat(u"\u00a7e%s has left." % self.display_name)
		log(f"{self.display_name} has left.")

	def update_keep_alive(self):
		# Send a "Keep Alive" packet

		# 1.7.x
		if self.protocol_version <= 338:
			payload =  self.buff_type.pack_varint(0)

		# 1.12.2
		else:
			payload = self.buff_type.pack('Q', 0)

		self.send_packet("keep_alive", payload)

	def packet_chat_message(self, buff):
		# When we receive a chat message from the player, ask the factory
		# to relay it to all connected players
		p_text = buff.unpack_string()
		self.factory.send_chat("<%s> %s" % (self.display_name, p_text))
		log(f"<{self.display_name}> {p_text}")


class HomuraServerFactory(ServerFactory):
	protocol = HomuraServerProtocol
	motd = ini["HomuraMC"]["motd"]

	def send_chat(self, message):
		for player in self.players:
			player.send_packet("chat_message",player.buff_type.pack_chat(message) + player.buff_type.pack('B', 0) )
	

def main():

	# Create factory
	factory = HomuraServerFactory()

	# Listen
	factory.listen(ini['HomuraMC']['server_ip'],int(ini['HomuraMC']['port']))
	reactor.run()


if __name__ == "__main__":
	log("Homura v0.0.1 is Finished Loading!")
	main()