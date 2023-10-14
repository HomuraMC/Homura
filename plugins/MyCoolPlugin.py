from classes import HomuraServerProtocol

class HomuraMCPlugin():
	@staticmethod
	def onStart(self):
		print("aa")
	@staticmethod
	def onJoinPlayer(self):
		self.factory.send_msg(f"[Server] Hello There!", self.display_name)