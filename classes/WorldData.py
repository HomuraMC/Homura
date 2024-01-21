import os
from quarry.types.nbt import RegionFile
from quarry.types.nbt import RegionFile, TagCompound, TagLongArray, TagRoot
from quarry.types.chunk import BlockArray, PackedArray
from quarry.types.registry import LookupRegistry
from .lognk import log
logger = log.logger

class WorldData():
	emptyHeight = TagRoot({"": TagCompound({
		"MOTION_BLOCKING": TagLongArray(PackedArray.empty_height())
	})})
	registry = LookupRegistry.from_jar(os.path.join(os.getcwd(), "assets", "registry", "server.jar"))

	sent_chunks = {}
	counter = {}

	loaded_regions = {}
	loaded_chunks = {}

	queue = {}

	def loadChunk(self):
		for x in range(-10, 11):
			for z in range(-10, 11):
				x2 = x * 16
				z2 = z * 16

				rx, x2 = divmod(x2, 512)
				rz, z2 = divmod(z2, 512)
				cx, x2 = divmod(x2, 16)
				cz, z2 = divmod(z2, 16)

				logger.info(f"Chunk({x2},{z2}) loading...")

				if (str(rx) + ";" + str(rz)) in WorldData.loaded_regions:
					region = WorldData.loaded_regions[str(rx) + ";" + str(rz)]
				else:
					region = RegionFile(
						os.path.join(
							os.getcwd(), "assets", "world", "region", "r.%d.%d.mca" % (rx, rz)
						)
					)
					WorldData.loaded_regions[str(rx) + ";" + str(rz)] = region

				try:
					if not (str(cx) + ";" + str(cz)) in WorldData.loaded_chunks:
						WorldData.loaded_chunks[
							str(rx) + ";" + str(rz) + "#" + str(cx) + ";" + str(cz)
						] = region.load_chunk(cx, cz)
					logger.info(f"Chunk({x2},{z2}) loading successful")
				except ValueError as e:
					logger.error(f"Chunk({x2},{z2}) loading error (ValueError)")
					continue
				except OSError as e:
					logger.error(f"Chunk({x2},{z2}) loading error (OSError)")
					continue
		return True