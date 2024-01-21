import configparser
import os
import math
from .PluginLoader import PluginLoader
from .WorldData import WorldData

from quarry.net.server import ServerProtocol
from quarry.data.data_packs import data_packs, dimension_types
from quarry.types.nbt import RegionFile, TagCompound, TagLongArray, TagRoot
from quarry.types.chunk import BlockArray, PackedArray
from quarry.net.protocol import Protocol
from twisted.internet import reactor

from .lognk import log
from .Config import Config

from .events.PlayerJoinEvent import PlayerJoinEvent
from .events.PlayerQuitEvent import PlayerQuitEvent


class HomuraServerProtocol(ServerProtocol):
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
				8, 63, 8, 0, 90, 0b00000),
			self.buff_type.pack_varint(0))
		WorldData.sent_chunks[f'{self.uuid}'] = False
		WorldData.counter[f'{self.uuid}'] = 0
		WorldData.queue[f'{self.uuid}'] = []

		self.ticker.add_loop(20, self.update_keep_alive)
		self.ticker.add_loop(1, self.send_next_from_queue)	

		event = PlayerJoinEvent(self)

		for plugin in PluginLoader.plugins:
			if getattr(plugin.HomuraMCPlugin,'onJoinPlayer',False) != False:
				plugin.HomuraMCPlugin.onJoinPlayer(self,event)
		# Announce player join
		self.factory.send_chat(event.message)
		log.logger.info(event.message)

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
					WorldData.queue[f'{self.uuid}'].append([x, z, True, WorldData.emptyHeight, [None]*16, [1]*256, []])

	def send_empty_full(self, size):
		for x in range(-size, size + 1):
			for z in range(-size, size + 1):
				if x == 0 and z == 0: continue
				WorldData.queue[f'{self.uuid}'].append([x, z, True, WorldData.emptyHeight, [None]*16, [1]*256, []])

	def player_left(self):
		ServerProtocol.player_left(self)
		del WorldData.counter[f'{self.uuid}']
		del WorldData.sent_chunks[f'{self.uuid}']
		del WorldData.queue[f'{self.uuid}']

		event = PlayerQuitEvent(self)

		for plugin in PluginLoader.plugins:
			if getattr(plugin.HomuraMCPlugin,'onQuitPlayer',False) != False:
				plugin.HomuraMCPlugin.onQuitPlayer(self,event)
		# Announce player left
		self.factory.send_chat(event.message)
		log.logger.info(event.message)


	def update_keep_alive(self):
		self.send_packet("keep_alive", self.buff_type.pack("Q", 0))

		if not WorldData.sent_chunks[f'{self.uuid}']:
			if WorldData.counter[f'{self.uuid}'] == 0:
				self.send_empty_full(4)
			if WorldData.counter[f'{self.uuid}'] == 10:
				self.send_perimiter(2)
			if WorldData.counter[f'{self.uuid}'] == 20:
				self.send_perimiter(0)
			
			WorldData.counter[f'{self.uuid}'] += 1
		for plugin in PluginLoader.plugins:
			if getattr(plugin.HomuraMCPlugin,'onKeepAlive',False) != False:
				plugin.HomuraMCPlugin.onKeepAlive(self)

	def send_next_from_queue(self):
		if len(WorldData.queue[f'{self.uuid}']) == 0: return

		x, z, full, heightmap, sections, biomes, block_entities = WorldData.queue[f'{self.uuid}'].pop()
		self.send_chunk(x, z, full, heightmap, sections, biomes, block_entities)
		
		for plugin in PluginLoader.plugins:
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

		if (str(rx) + ";" + str(rz)) in WorldData.loaded_regions:
			region = WorldData.loaded_regions[str(rx) + ";" + str(rz)]
		else:
			region = RegionFile(os.path.join("SendingChunks_1.16.5", "assets", "world", "region", "r.%d.%d.mca" % (rx, rz)))
			WorldData.loaded_regions[str(rx) + ";" + str(rz)] = region

		try:
			if (str(rx) + ";" + str(rz) + "#" + str(cx) + ";" + str(cz)) in WorldData.loaded_chunks:
				chunk = WorldData.loaded_chunks[str(rx) + ";" + str(rz) + "#" + str(cx) + ";" + str(cz)].body.value["Level"].value
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
					blocks = BlockArray.from_nbt(section, WorldData.registry)
					block_light = None
					sky_light = None
					sections[y] = (blocks, block_light, sky_light)

		heightmap = TagRoot.from_body(chunk["Heightmaps"])
		biomes = chunk["Biomes"].value
		block_entities = chunk["TileEntities"].value
		biomes = [biome for biome in biomes]

		WorldData.queue[f'{self.uuid}'].append([px, pz, True, heightmap, sections, biomes, block_entities])

	def update_chunks(self):
		if math.floor(self.player.x / 16) == self.chunk.x and math.floor(self.player.z / 16) == self.chunk.z:
			return

		self.read_and_send_chunk(math.floor(self.player.x / 16), math.floor(self.player.z / 16))

		self.chunk.x = math.floor(self.player.x / 16)
		self.chunk.z = math.floor(self.player.z / 16)
		for plugin in PluginLoader.plugins:
			if getattr(plugin.HomuraMCPlugin,'onUpdateChunks',False) != False:
				plugin.HomuraMCPlugin.onUpdateChunks(self)

	def packet_player_position_and_look(self, buff):
		x, y, z, ry, rp, flag = buff.unpack('dddff?')

		self.player.x = x
		self.player.z = z
		for plugin in PluginLoader.plugins:
			if getattr(plugin.HomuraMCPlugin,'onPlayerMove',False) != False:
				plugin.HomuraMCPlugin.onPlayerMove(self)

	def packet_chat_message(self, buff):
		# When we receive a chat message from the player, ask the factory
		# to relay it to all connected players
		p_text = buff.unpack_string()
		for plugin in PluginLoader.plugins:
			if getattr(plugin.HomuraMCPlugin,'onChat',False) != False:
				plugin.HomuraMCPlugin.onChat(self,p_text)
		if p_text == "/list":
			pltt = ""
			pll = 0
			pltt = self.factory.getPlayers()
			pll = self.factory.getPlayersCount()
			self.factory.send_msg(f"{pll} players online: {pltt}", self.uuid)
		elif p_text == "/chest":
			self.open_gui(1,5,"Large chest",1)
		elif p_text == "/title":
			self.send_packet('title',
					self.buff_type.pack_varint(0),
					self.buff_type.pack_chat("§aHey"),
				)
		elif p_text == "/reloadplugins":
			log.logger.info("Reloading Plugins...")
			pluginloader = PluginLoader()
			pluginloader.reloadPlugins()
			log.logger.info("Reloading Successful!")
		else:
			self.factory.send_chat("<%s> %s" % (self.display_name, p_text))
			log.logger.info(f"<{self.display_name}> {p_text}")

	def packet_plugin_message(self, buff):
		p_channel_name = buff.unpack_string()
		p_channel_data = buff.read()
		# do something with the message
		log.logger.info(f"{self.display_name} pm> {p_channel_name}")
		for plugin in PluginLoader.plugins:
			if getattr(plugin.HomuraMCPlugin,'onPluginMessage',False) != False:
				quitMessage = plugin.HomuraMCPlugin.onPluginMessage(self,buff)

	def packet_tab_complete(self,buff):
		string, iscmd, haspos = buff.unpack('s??')
		x,y,z = buff.unpack_position()
		log.logger.info(f"{self.display_name} tab> {string}")
		self.send_packet('tab_complete',
				self.buff_type.pack_varint(2),
				self.buff_type.pack_string("Powered by HomuraMC"),
				self.buff_type.pack_string("HomuraMC by nennneko5787"),
			)

	def packet_player_digging(self,buff):
		status = buff.unpack_varint()
		x,y,z = buff.unpack_position()
		face = buff.unpack('b')
		log.logger.info(f"{self.display_name} block digging: {status},({x},{y},{z}),{face}")

	def packet_player_block_placement(self,buff):
		status = buff.unpack_varint()
		x,y,z = buff.unpack_position()
		face, cpx, cpy, cpz, inside = buff.unpack('bfff?')
		log.logger.info(f"{self.display_name} block placement: {status},({x},{y},{z}),{face},({cpx},{cpy},{cpz}),{inside}")
	
	def packet_entity_action(self,buff):
		entity = buff.unpack_varint()
		action = buff.unpack_varint()
		jump_boost = buff.unpack_varint()
		log.logger.info(f"{self.display_name} entity action: {entity},{action},{jump_boost}")

	def packet_player_abilities(self,buff):
		flag = buff.unpack('b')
		log.logger.info(f"{self.display_name} player abilities: {flag}")

	def packet_client_settings(self,buff):
		locale,view_distance = buff.unpack('x5sb')
		chat_mode = buff.unpack_varint()
		chat_colors,displayed_skin_parts, = buff.unpack('?B')
		main_hand = buff.unpack_varint()
		log.logger.info(f"{self.display_name} client settings: {locale},{view_distance},{chat_mode},{chat_colors},{displayed_skin_parts},{main_hand}")

	# Short (???)
	# def packet_advancement_tab(self,buff):
	#	action = buff.unpack_varint()
	#	tab = buff.unpack_optional(buff.unpack_varint())
	#	log.logger.info(f"{self.display_name} advancement tab: {action},{tab}")

	def open_gui(self, winid:int, wintype:int, title:str, slots:int = 0, entityid:int = -1):
		if entityid == -1:
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