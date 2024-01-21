class PlayerQuitEvent():
	def __init__(self,srvself):
		self.data = srvself
		self.message = f"§e{self.data.display_name} leaved the game"
	def setQuitMessage(self,message):
		self.message = message
	def __string__(self):
		return f"PlayerQuitEvent[{self.data.display_name}({self.data.uuid})]"