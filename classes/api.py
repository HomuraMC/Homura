"""
Homura Plugin API (仮)
"""
import glob
import yaml
import os
from importlib import import_module
import pathlib

from protocol import HomuraServerProtocol
from lognk import log


class HomuraAPI:
    def __init__(self) -> None:
        plugins = glob.glob("./plugins/**/")
        self.commands = []
        self.factory = HomuraServerProtocol().factory
        self.logger = log.logger
        self.plugin = []
        self.pl = {}
        self.pl["name"] = []
        self.pl["path"] = []

        try:
            for plugin in plugins:
                with open(os.path.join(plugin, "plugin.yml"), encoding="utf-8") as f:
                    plconf = yaml.safe_load(f)
                if not plconf["config"]["name"] in self.pl["name"]:
                        path = os.path.join(plugin, plconf["config"]["main"])
                        module = (
                            path.replace(os.path.sep, ".")
                            .replace("./", "")
                            .replace("/", ".")
                            .replace(".py", "")
                        )
                        mdle = import_module(module)
                        self.plugin.append(mdle)
                        self.pl["name"].append(plconf["config"]["name"])
                        self.pl["path"].append(plugin)
                        mdle.plugin.on_load()
                else:
                    pli = self.pl["name"].index(plconf["config"]["name"])
                    
                    log.logger.error(f"This plugin cannot be loaded because it is a duplicate of {pathlib.Path(self.pl['path'][pli]).resolve()}.")
        except Exception as e:
            log.logger.exception("")

    def send_chat(self):
        self.factory.send_chat()

    def regist_command(self, name):
        self.commands.append(name)

    def command(self):
        pass

    def send_msg(self, text, player):
        self.factory.send_msg(text, player)

    class getLogger:
        debug = log.logger.debug
        info = log.logger.info
        warn = log.logger.warn
        error = log.logger.error
        critical = log.logger.critical