class PlayerJoinEvent():
	def __init__(self,srvself):
		self.data = srvself
		self.message = f"§e{self.data.display_name} joined the game"
	def setJoinMessage(self,message):
		self.message = message
	def __string__(self):
		return f"PlayerJoinEvent[{self.data.display_name}({self.data.uuid})]"