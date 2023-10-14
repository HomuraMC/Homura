import configparser

from quarry.net.server import ServerProtocol

from . import log

ini = configparser.ConfigParser()
ini.read("./Homura.ini", "UTF-8")


class HomuraServerProtocol(ServerProtocol):
	global ini

	def close(self=None, kmsg=None):
		if (self != None) and (kmsg != None):
			ServerProtocol.close(self, kmsg)
			log.logger.warn(f"{self.display_name} is Kicked: {kmsg}")
		else:
			ServerProtocol.close(self)

	def player_joined(self):
		# Call super. This switches us to "play" mode, marks the player as
		#   in-game, and does some logging.
		ServerProtocol.player_joined(self)

		# Send "Join Game" packet
		log.logger.info(f"{self.display_name} is trying connect!")
		if self.protocol_version > 578:
			self.close("Outdated server! I'm still on 1.15.2")
		elif self.protocol_version < 578:
			self.close("Outdated client! I'm using 1.15.2")

		self.send_packet(
			"join_game",
			self.buff_type.pack(
				"iBqiB",
				0,  # entity id
				3,  # game mode
				0,  # dimension
				0,  # hashed seed
				0,
			),  # max players
			self.buff_type.pack_string("flat"),  # level type
			self.buff_type.pack_varint(1),  # view distance
			self.buff_type.pack("??", False, True),  # reduced debug info
		)  # show respawn screen

		# Send "Player Position and Look" packet
		self.send_packet(
			"player_position_and_look",
			self.buff_type.pack(
				"dddff?", 0, 255, 0, 0, 0, 0b00000  # x  # y  # z  # yaw  # pitch
			),  # flags
			self.buff_type.pack_varint(0),
		)  # teleport id

		# Start sending "Keep Alive" packets
		self.ticker.add_loop(20, self.update_keep_alive)

		# Announce player joined
		self.factory.send_chat("\u00a7e%s has joined." % self.display_name)
		log.logger.info(f"\033[033m{self.display_name} has joined.\033[0m")

		for plugin in plugins:
			self.plugin.HomuraMCPlugin.onJoinPlayer()
	def player_left(self):
		ServerProtocol.player_left(self)

		# Announce player left
		self.factory.send_chat("\u00a7e%s has left." % self.display_name)
		log(f"{self.display_name} has left.")

	def update_keep_alive(self):
		# Send a "Keep Alive" packet

		# 1.7.x
		if self.protocol_version <= 338:
			payload = self.buff_type.pack_varint(0)

		# 1.12.2
		else:
			payload = self.buff_type.pack("Q", 0)

		self.send_packet("keep_alive", payload)

	def packet_chat_message(self, buff):
		# When we receive a chat message from the player, ask the factory
		# to relay it to all connected players
		p_text = buff.unpack_string()
		if p_text == "/list":
			pltt = ""
			pll = 0
			pltt = self.factory.getPlayers()
			pll = self.factory.getPlayersCount()
			self.factory.send_msg(f"{pll} players online: {pltt}", self.display_name)
		else:
			self.factory.send_chat("<%s> %s" % (self.display_name, p_text))
			log.logger.info(f"<{self.display_name}> {p_text}")
