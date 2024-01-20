import importlib
import os
from classes import log

logger = log.logger

class PluginLoader():
	plugins = []

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
					PluginLoader.plugins.append(plpy)
					logger.info("Python Script {} is Loading Successful.".format(plpy.HomuraMCPluginBackends.getPluginName()))
					"""
					What
					[14:42:03] INFO Python Script MyCoolPlugin.py is loading...
					[14:42:03] INFO Python Script MyCoolPlugin.py is Loading Successful.
					Traceback (most recent call last):
					File "/mnt/c/HomuraMC/Homura/main.py", line 164, in <module>
						PluginLoader.plugins[plpy]["name"] = plpy.HomuraMCPluginBackends.getPluginName()
					TypeError: list indices must be integers or slices, not module
					PluginLoader.plugins[plpy]["name"] = plpy.HomuraMCPluginBackends.getPluginName()
					PluginLoader.plugins[plpy]["description"] = plpy.HomuraMCPluginBackends.getPluginDescription()
					PluginLoader.plugins[plpy]["authors"] = plpy.HomuraMCPluginBackends.getPluginAuthors()
					PluginLoader.plugins[plpy]["version"] = plpy.HomuraMCPluginBackends.getPluginVersion()
					"""
					if getattr(plpy.HomuraMCPlugin, "onLoad", False) != False:
						plpy.HomuraMCPlugin.onLoad()
		return True

	def reloadPlugins(self):
		for plugin in PluginLoader.plugins:
			log.logger.info(f"Plugin {plugin.HomuraMCPluginBackends.getPluginName()} reloading...")
			if getattr(plugin.HomuraMCPlugin,'onReloadPlugin',False) != False:
				plugin.HomuraMCPlugin.onReloadPlugin(self)
			importlib.reload(plugin)
			log.logger.info(f"Plugin {plugin.HomuraMCPluginBackends.getPluginName()} reload successful.")