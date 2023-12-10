import configparser
import os
import math
import builtins

from quarry.net.server import ServerProtocol
from quarry.data.data_packs import data_packs, dimension_types
from quarry.types.nbt import RegionFile, TagCompound, TagLongArray, TagRoot
from quarry.types.chunk import BlockArray, PackedArray
from quarry.net.protocol import Protocol
from quarry.types.registry import LookupRegistry
from twisted.internet import reactor

from .lognk import log
import importlib

ini = configparser.ConfigParser()
ini.read("./Homura.ini", "UTF-8")


class HomuraServerProtocol(ServerProtocol):
	global ini

	builtins.emptyHeight = TagRoot({"": TagCompound({
		"MOTION_BLOCKING": TagLongArray(PackedArray.empty_height())
	})})

	builtins.registry = LookupRegistry.from_jar(os.path.join(os.getcwd(), "assets", "registry", "server.jar"))

	class chunk:
		x = 0
		z = 0

	class player:
		x = 0
		z = 0

	def packet_login_start(self, buff):
		ServerProtocol.packet_login_start(self, buff)
		log.logger.info(f"{self.display_name} is trying connect!")

	def player_joined(self):
		ServerProtocol.player_joined(self)

		self.send_packet("join_game",
			self.buff_type.pack("i?BB",
				0, False, 1, 1),
			self.buff_type.pack_varint(1),
			self.buff_type.pack_string("chunks"),
			self.buff_type.pack_nbt(data_packs[self.protocol_version]),
			self.buff_type.pack_nbt(dimension_types[self.protocol_version, "minecraft:overworld"]),
			self.buff_type.pack_string("chunks"),
			self.buff_type.pack("q", 42),
			self.buff_type.pack_varint(0),
			self.buff_type.pack_varint(2),
			self.buff_type.pack("????", False, True, False, False))

		self.send_packet("player_position_and_look",
			self.buff_type.pack("dddff?",
				8, 200, 8, 0, 90, 0b00000),
			self.buff_type.pack_varint(0))
		builtins.sent_chunks[f'{self.uuid}'] = False
		builtins.counter[f'{self.uuid}'] = 0
		builtins.queue[f'{self.uuid}'] = []

		self.ticker.add_loop(20, self.update_keep_alive)
		self.ticker.add_loop(1, self.send_next_from_queue)	

		self.send_packet("player_info",
			self.buff_type.pack_varint(0),
			self.buff_type.pack_varint(1),
			self.buff_type.pack_uuid(self.uuid),

			self.buff_type.pack_string(self.display_name),
			self.buff_type.pack_varint(4),
			
			self.buff_type.pack_string("textures"),
			self.buff_type.pack_string("ewogICJ0aW1lc3RhbXAiIDogMTcwMjEyMzg4OTEyMCwKICAicHJvZmlsZUlkIiA6ICI1ODVjNWYzMjQwMjE0ZDc4OWU5MzAyZjEzYjVlMDI3MiIsCiAgInByb2ZpbGVOYW1lIiA6ICJuZW5ubmVrbzU3ODciLAogICJ0ZXh0dXJlcyIgOiB7CiAgICAiU0tJTiIgOiB7CiAgICAgICJ1cmwiIDogImh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvZDkxZDFmMzk3MWQxYzcyZDZjODAyNWJkMmJhOTYyM2YyNTY4ZTg4NWM2N2QwNjIzZGUwMmIyOTVhM2Q1OTI2YiIsCiAgICAgICJtZXRhZGF0YSIgOiB7CiAgICAgICAgIm1vZGVsIiA6ICJzbGltIgogICAgICB9CiAgICB9CiAgfQp9"),
			self.buff_type.pack("?",True),
			self.buff_type.pack_string("ZUGZvIdFgGhH9H2Rl0/ghfG6EJ7uc+COSYcJUi2+4Cus56dn1pdfwgzixsbhUBI1GEyxtAqhaSKy4dCfshWVG8lESm+BkXaQWdLdbnGv1+0cXQIglGjZrof35E5QziWcDLJRGr61Nxsqtf17bzBcKY5ssbdonzH9W5SmBc/Az0MKTbim0Bw50rpssQ0i5mde0uE4FEgip/uGuaEdBx3kd72Qod8pspYfPG0HQDbhFcvSl/GYb/2Jsb0pYE300Y9lmZrjeInqxLJBfKeK2e8HBOXn6gp8UBBn0zFpkKBjxXQEJ0rvBnLJxGEPEJo3rUVbD7/m4JU7OciwFkOga/qvP2ySIGZueQmZheABbKWOhNUWA62YceeWpfn+OlWizd3v+HD7U2XCO+bFZsws1wnH2BHuf4IpN3GXM0C7tRt6NJad0vO7dHg6HoOR7O7O0nRkS7hPXL2gLcVoEPwtEraF6aMG+9dY31eL5cQ8PiYWBx3gROIg2x62SjdJEy2pBwAn4i+0J2/UwgptHilFH3JHYyq7waNmYpiwOubnydDmAkQZcnXxRqtIQCwc9CT5mvXZGGqX4Ryvq/z4N/32S3UIeLWodpAxmyzZKd27FgMp0c2kJymQ2IlXQF8S3xUMziWeX5GeFx7mAftoW3IfU4DuyHpnRKBuVSQqanwYWID7mOw="),

			self.buff_type.pack_varint(2),
			self.buff_type.pack_varint(0),
			self.buff_type.pack("?",True),
			self.buff_type.pack_chat(self.display_name)
		)

		joinMessage = "\u00a7e%s has joined."
		for plugin in builtins.plugins:
			if getattr(plugin.HomuraMCPlugin,'onJoinPlayer',False) != False:
				joinMessage = plugin.HomuraMCPlugin.onJoinPlayer(self)
		# Announce player join
		self.factory.send_chat(joinMessage)
		#log.logger.info(f"\033[033m{self.display_name} has joined.\033[0m")

	def send_perimiter(self, size, thread=True):
		for x in range(-size, size + 1):
			for z in range(-size, size + 1):
				if x == -size or x == size or z == -size or z == size:
					if thread:
						reactor.callInThread(self.read_and_send_chunk, x * 16, z * 16)
					else:
						self.read_and_send_chunk(x * 16, z * 16)
				
	def send_empty_perimiter(self, size):
		for x in range(-size, size + 1):
			for z in range(-size, size + 1):
				if x == -size or x == size or z == -size or z == size:
					builtins.queue[f'{self.uuid}'].append([x, z, True, builtins.emptyHeight, [None]*16, [1]*256, []])

	def send_empty_full(self, size):
		for x in range(-size, size + 1):
			for z in range(-size, size + 1):
				if x == 0 and z == 0: continue
				builtins.queue[f'{self.uuid}'].append([x, z, True, builtins.emptyHeight, [None]*16, [1]*256, []])

	def player_left(self):
		ServerProtocol.player_left(self)
		del builtins.counter[f'{self.uuid}']
		del builtins.sent_chunks[f'{self.uuid}']
		del builtins.queue[f'{self.uuid}']
		quitMessage = "\u00a7e%s has joined."
		for plugin in builtins.plugins:
			if getattr(plugin.HomuraMCPlugin,'onQuitPlayer',False) != False:
				quitMessage = plugin.HomuraMCPlugin.onQuitPlayer(self)
		# Announce player left
		self.factory.send_chat(quitMessage)
		#log.logger.info(f"{self.display_name} has left.")


	def update_keep_alive(self):
		self.send_packet("keep_alive", self.buff_type.pack("Q", 0))

		if not builtins.sent_chunks[f'{self.uuid}']:
			if builtins.counter[f'{self.uuid}'] == 0:
				self.send_empty_full(4)
			if builtins.counter[f'{self.uuid}'] == 10:
				self.send_perimiter(2)
			if builtins.counter[f'{self.uuid}'] == 20:
				self.send_perimiter(0)
			
			builtins.counter[f'{self.uuid}'] += 1
		for plugin in builtins.plugins:
			if getattr(plugin.HomuraMCPlugin,'onKeepAlive',False) != False:
				plugin.HomuraMCPlugin.onKeepAlive(self)

	def send_next_from_queue(self):
		if len(builtins.queue[f'{self.uuid}']) == 0: return

		x, z, full, heightmap, sections, biomes, block_entities = builtins.queue[f'{self.uuid}'].pop()
		self.send_chunk(x, z, full, heightmap, sections, biomes, block_entities)
		
		for plugin in builtins.plugins:
			if getattr(plugin.HomuraMCPlugin,'onTick',False) != False:
				plugin.HomuraMCPlugin.onTick(self)

	def send_chunk(self, x, z, full, heightmap, sections, biomes, block_entities):
		sections_data = self.buff_type.pack_chunk(sections)

		biomes = [1] * 256
		for i in range(0, len(block_entities)):
			block_entities[i] = TagRoot({"": block_entities[i]})

		self.send_packet('chunk_data',
			self.buff_type.pack('ii?', x, z, full),
			self.buff_type.pack_chunk_bitmask(sections),
			self.buff_type.pack_nbt(heightmap),
			self.buff_type.pack_optional_varint(1023),
			self.buff_type.pack_array("I", biomes),
			self.buff_type.pack_varint(len(sections_data)),
			sections_data,
			self.buff_type.pack_varint(len(block_entities)),
			b"".join(self.buff_type.pack_nbt(entity) for entity in block_entities))

	def read_and_send_chunk(self, x, z):
		px = math.floor(x / 16)
		pz = math.floor(z / 16)

		rx, x = divmod(x, 512)
		rz, z = divmod(z, 512)
		cx, x = divmod(x, 16)
		cz, z = divmod(z, 16)

		if (str(rx) + ";" + str(rz)) in builtins.loaded_regions:
			region = builtins.loaded_regions[str(rx) + ";" + str(rz)]
		else:
			region = RegionFile(os.path.join("SendingChunks_1.16.5", "assets", "world", "region", "r.%d.%d.mca" % (rx, rz)))
			builtins.loaded_regions[str(rx) + ";" + str(rz)] = region

		try:
			if (str(rx) + ";" + str(rz) + "#" + str(cx) + ";" + str(cz)) in builtins.loaded_chunks:
				chunk = builtins.loaded_chunks[str(rx) + ";" + str(rz) + "#" + str(cx) + ";" + str(cz)].body.value["Level"].value
			else:
				chunk = region.load_chunk(cx, cz).body.value["Level"].value
		except ValueError as e:
			return
		except OSError as e:
			return

		sections = [None] * 16

		for section in chunk["Sections"].value:
			if 'Palette' in section.value:
				y = section.value["Y"].value
				if 0 <= y < 16:
					blocks = BlockArray.from_nbt(section, builtins.registry)
					block_light = None
					sky_light = None
					sections[y] = (blocks, block_light, sky_light)

		heightmap = TagRoot.from_body(chunk["Heightmaps"])
		biomes = chunk["Biomes"].value
		block_entities = chunk["TileEntities"].value
		biomes = [biome for biome in biomes]

		builtins.queue[f'{self.uuid}'].append([px, pz, True, heightmap, sections, biomes, block_entities])

	def update_chunks(self):
		if math.floor(self.player.x / 16) == self.chunk.x and math.floor(self.player.z / 16) == self.chunk.z:
			return

		self.read_and_send_chunk(math.floor(self.player.x / 16), math.floor(self.player.z / 16))

		self.chunk.x = math.floor(self.player.x / 16)
		self.chunk.z = math.floor(self.player.z / 16)
		for plugin in builtins.plugins:
			if getattr(plugin.HomuraMCPlugin,'onUpdateChunks',False) != False:
				plugin.HomuraMCPlugin.onUpdateChunks(self)

	def packet_player_position_and_look(self, buff):
		x, y, z, ry, rp, flag = buff.unpack('dddff?')

		self.player.x = x
		self.player.z = z
		for plugin in builtins.plugins:
			if getattr(plugin.HomuraMCPlugin,'onPlayerMove',False) != False:
				plugin.HomuraMCPlugin.onPlayerMove(self)

	def packet_chat_message(self, buff):
		# When we receive a chat message from the player, ask the factory
		# to relay it to all connected players
		p_text = buff.unpack_string()
		for plugin in builtins.plugins:
			if getattr(plugin.HomuraMCPlugin,'onChat',False) != False:
				plugin.HomuraMCPlugin.onChat(self,p_text)
		if p_text == "/list":
			pltt = ""
			pll = 0
			pltt = self.factory.getPlayers()
			pll = self.factory.getPlayersCount()
			self.factory.send_msg(f"{pll} players online: {pltt}", self.uuid)
		elif p_text == "/chest":
			self.open_gui(1,5,"Large chest")
		elif p_text == "/title":
			self.send_packet('title',
					self.buff_type.pack_varint(0),
					self.buff_type.pack_chat("§aHey"),
				)
		elif p_text == "/reloadplugins":
			log.logger.info("Reloading Plugins...")
			for plugin in builtins.plugins:
				if getattr(plugin.HomuraMCPlugin,'onReloadPlugin',False) != False:
					plugin.HomuraMCPlugin.onReloadPlugin(self)
				importlib.reload(plugin)
				log.logger.info(f"Plugin {plugin} reload successful.")
			log.logger.info("Reloading Successful!")
		else:
			self.factory.send_chat("<%s> %s" % (self.display_name, p_text))
			log.logger.info(f"<{self.display_name}> {p_text}")

	def packet_plugin_message(self, buff):
		p_channel_name = buff.unpack_string()
		p_channel_data = buff.read()
		# do something with the message
		log.logger.info(f"{self.display_name} pm> {p_channel_name}")

	def packet_tab_complete(self,buff):
		string, iscmd, haspos, pos = buff.unpack('s??q')
		x = pos >> 38
		y = pos << 52 >> 52 
		z = pos << 26 >> 38
		log.logger.info(f"{self.display_name} tab> {string}")
		self.send_packet('tab_complete',
				self.buff_type.pack_varint(2),
				self.buff_type.pack_string("Powered by HomuraMC"),
				self.buff_type.pack_string("HomuraMC by nennneko5787"),
			)

	def open_gui(self, winid:int, wintype:int, title:str, slots:int = 0, entityid:int = 0):
		if entityid == 0:
			self.send_packet('open_window',
					self.buff_type.pack_varint(winid),
					self.buff_type.pack_varint(wintype),
					self.buff_type.pack_chat(title),
					self.buff_type.pack_varint(slots)
				)
		else:
			self.send_packet('open_window',
					self.buff_type.pack_varint(winid),
					self.buff_type.pack_varint(wintype),
					self.buff_type.pack_chat(title),
					self.buff_type.pack_varint(slots),
					self.buff_type.pack_varint(entityid)
				)