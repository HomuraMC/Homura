from classes import HomuraServerProtocol

class HomuraMCPlugin():
	@staticmethod
	def onReady():
		print("aa")
	@staticmethod
	def onJoinPlayer(self):
		self.factory.send_msg(f"[Server] Hello There!", self.display_name)