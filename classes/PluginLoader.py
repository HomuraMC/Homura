import importlib
import os
from classes import log

logger = log.logger

class PluginLoader():
	def __init__(self):
		self.plugins = []

	def loadPlugins(self):
		for file in os.listdir("./plugins/"):
			base, ext = os.path.splitext(file)
			if ext == ".py":
				logger.info("Python Script {} is loading...".format(file))
				plpy = importlib.import_module("plugins.{}".format(base))
				isplugin = getattr(plpy, "HomuraMCPlugin", False)
				if isplugin == False:
					logger.warning("Python Script {} is Not HomuraMC Plugin!".format(file))
				else:
					self.plugins.append(plpy)
					logger.info("Python Script {} is Loading Successful.".format(plpy.HomuraMCPluginBackends.getPluginName()))
					"""
					What
					[14:42:03] INFO Python Script MyCoolPlugin.py is loading...
					[14:42:03] INFO Python Script MyCoolPlugin.py is Loading Successful.
					Traceback (most recent call last):
					File "/mnt/c/HomuraMC/Homura/main.py", line 164, in <module>
						self.plugins[plpy]["name"] = plpy.HomuraMCPluginBackends.getPluginName()
					TypeError: list indices must be integers or slices, not module
					self.plugins[plpy]["name"] = plpy.HomuraMCPluginBackends.getPluginName()
					self.plugins[plpy]["description"] = plpy.HomuraMCPluginBackends.getPluginDescription()
					self.plugins[plpy]["authors"] = plpy.HomuraMCPluginBackends.getPluginAuthors()
					self.plugins[plpy]["version"] = plpy.HomuraMCPluginBackends.getPluginVersion()
					"""
					if getattr(plpy.HomuraMCPlugin, "onLoad", False) != False:
						plpy.HomuraMCPlugin.onLoad()
		return True