from classes import HomuraServerProtocol

class HomuraMCPlugin():
	@staticmethod
	def onLoad():
		print("Loaded")
	@staticmethod
	def onJoinPlayer(self):
		self.factory.send_msg(f"[Server] Hello!", self.display_name)
		return "%s joined"
	@staticmethod
	def onQuitPlayer(self):
		return "%s leaved"