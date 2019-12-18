from client import ClientConnect
from client import ServerConnect
class Client:
	def __init__(self, max_connections):
		
		self.sender_ip = None

		self.ClientConnect = ClientConnect(self)
		self.ClientConnect.daemon = True

		self.ServerConnect = ServerConnect(self)
		self.ServerConnect.daemon = True

		self.clientServer = ClientServer(self, "./")
		self.clientServer.daemon = True

		self.clients = []
		self.connected = 0
		self.maxConnections = max_connections
		self.currentVideo = None

	def set_sender_ip(self, sender_ip):
		self.sender_ip = sender_ip

	def set_current_video(self, video):
		self.currentVideo = video

	def get_current_video(self):
		return self.currentVideo