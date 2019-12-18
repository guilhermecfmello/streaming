import socket
import socketserver
import _thread
import threading
import vlc
import glob
import os
import sys
import time
from canal import *
# from clientObj import Client
from threading import Lock

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


class ServerConnect(threading.Thread):
	def __init__(self, client):
		threading.Thread.__init__(self)
		self.client = client

	def run(self):
		self._stopped = False

		# instance = vlc.Instance()
		# media_player = instance.media_player_new()
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sk_server:
			sk_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

			sk_server.bind(('', 9091))
			sk_server.listen(1)
			sk_server.settimeout(3)

			print("SERVER RECEIVER STARTED")

			file_num = 0

			while not self._stopped:
				try:
					content, address = sk_server.accept()

				except socket.timeout as e:
					print("Error on server, ip: {} error: {}".format(self.client.sender_ip, e))
					sys.exit()

				nome = "{}.wmv".format(file_num)
				sys.stdout.write("Received file '{}' from {}.\n".format(nome, address[0]))
				sys.stdout.flush()

				# Recebe o arquivo
				with open(nome, 'wb') as down_file:
					recv_read = content.recv(BUFFER_SIZE)
					while recv_read:
						down_file.write(recv_read)
						recv_read = content.recv(BUFFER_SIZE)


				# media = instance.media_new(nome)
				# media.parse()
				# media_player.set_media(media)
				# media_player.play()

				for _, cliente in enumerate(self.client.clients):
					print("Client {0} | File: {1}".format(
						cliente,
						nome
					))
					with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sk_client:
						sk_client.connect((cliente, 9092))
						with open(nome, 'rb') as up_file:
							send_read = up_file.read(BUFFER_SIZE)
							while send_read:
								sk_client.send(send_read)
								send_read = up_file.read(BUFFER_SIZE)
					self.client.set_current_video(nome)
					print(client.currentVideo)

				self.client.set_current_video(nome)
				time.sleep(3.9)

				content.close()
				file_num += 1

	def stop(self):
		self._stopped = True

class ClientConnect(threading.Thread):
	def __init__(self, client):
		threading.Thread.__init__(self)
		self.client = client

	def run(self):
		self._stopped = False

		socketserver.TCPServer.allow_reuse_address = True
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sk_server:
			sk_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

			print("Waiting for client")

			sk_server.bind(('', 9092))
			sk_server.listen(1)
			sk_server.settimeout(3)

			print("Client receiver started")

			file_num = 0

			while not self._stopped:
				try:
					content, address = sk_server.accept()

				except socket.timeout as e:
					_thread.interrupt_main()

					if self.client.ClientConnect.is_alive():
						self.client.ClientConnect.stop()

					if self.client.ServerConnect.is_alive():
						self.client.ServerConnect.stop()
					print("Error on server, ip: {} error: {}".format(self.client.sender_ip, e))

					client2 = Client(self.client.maxConnections)
					dest2 = (TCP_HOST, TCP_PORT)
					# connect(dest2, "100", client2)
					conecta(TCP_HOST, TCP_PORT, BUFFER_SIZE, dest, msg, client)
					sys.exit()

				nome = "{}.wmv".format(file_num)
				
				sys.stdout.write("Received file '{}' from {}.\n".format(nome, address[0]))
				sys.stdout.flush()

				# Recebe o arquivo
				with open(nome, 'wb') as down_file:
					recv_read = content.recv(BUFFER_SIZE)
					while recv_read:
						down_file.write(recv_read)
						recv_read = content.recv(BUFFER_SIZE)

				for _, cliente in enumerate(self.client.clients):
					print("Client {0} | File: {1}".format(
						cliente,
						nome
					))
					with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sk_client:
						sk_client.connect((cliente, 9092))

						with open(nome, 'rb') as up_file:
							send_read = up_file.read(BUFFER_SIZE)
							while send_read:
								sk_client.send(send_read)
								send_read = up_file.read(BUFFER_SIZE)
				self.client.set_current_video(nome)

	def stop(self):
		self._stopped = True


class Player():
	def __init__(self, path):
		self.vlc_instance = vlc.Instance('--quiet')
		self.player = self.vlc_instance.media_player_new()
		self.path = path
		self.vetor = []

	def listMovies(self):
		os.chdir("./")
		for file in glob.glob("*.wmv"):
			self.vetor.append(file)
		return self.vetor

	def play(self, file):
		# _000040.wmv
		media = self.vlc_instance.media_new(self.path + file)
		self.player.set_media(media)
		self.player.play()


class ExibeVideos(threading.Thread):
	def __init__(self, client):
		threading.Thread.__init__(self)
		Player.__init__(self, "./")
		self.client = client

	def run(self):
		while True:
			if self.client.currentVideo is not None:
				nomeMovie = self.client.currentVideo
				Player.play(self, nomeMovie)
				time.sleep(3.9)
			

	def stop(self):
		self.client.currentVideo = None



TCP_HOST = '127.0.0.1'   # IP
TCP_PORT = 6060  			# porta


BUFFER_SIZE = 1024  # Normally 1024
MAX_CONNECTIONS = 2

dest = (TCP_HOST, TCP_PORT)

msg = None

client = Client(MAX_CONNECTIONS)
ServerConnect = ServerConnect(client)
ClientConnect = ClientConnect(client)

ServerConnect.daemon = True

def conecta(TCP_HOST, TCP_PORT, BUFFER_SIZE, dest, msg, client):
	while True:
		msg = input()
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp:
			print(TCP_HOST)
			tcp.connect(dest)

			print("Command:", msg)

			if msg[0:2] == '12':
				client.ServerConnect.stop()
				client.ServerConnect.join()
				x.stop()

			tcp.send(bytes(msg, encoding='utf-8'))

			if msg[0:2] == '10':
				#   "10" -> success
				#   "00" -> not connected
				with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sk_server:
					sk_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

					sk_server.bind(('', 9091))
					sk_server.listen(1)

					content, address = sk_server.accept()

					received_msg = content.recv(BUFFER_SIZE)
					message = str(received_msg, 'utf-8')

					print("RECEIVED MESSAGE: " + message)
				# Erro ao entrar no canal, deve-se conectar a cliente
				if message == "00":
					print("Limite de canais conectados ao servidor excedidos.")

					with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp2:
						tcp2.connect((TCP_HOST, 6060))
						teste = "11" + msg[-1]
						tcp2.send(bytes(teste, encoding='utf-8'))

						clients_ip = str(tcp2.recv(BUFFER_SIZE), 'utf-8')
						clients_ip = handle_ip_list(clients_ip)

					client_ip = None
					# client_ip = str(client_ip)
					socketserver.TCPServer.allow_reuse_address = True
					for ip in clients_ip:
						with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp3:
							print("IP TENTANDO CONECTAR: ", ip)
							tcp3.connect((ip, 9093))
							tcp3.send(bytes("10", encoding='utf-8'))
							resp = str(tcp3.recv(BUFFER_SIZE), 'utf-8')
							# print("RESPOSTA: ", resp)
							if resp == "OK":
								print("DEU BOM!")
								client_ip = ip
								break

							tcp3.close()

					if client_ip is None:
						client_ip = get_available_client(clients_ip)

					socketserver.TCPServer.allow_reuse_address = True
					with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp2:
						print("CLIENTE IP: ", client_ip)

						tcp2.connect((client_ip, 9095))
						tcp2.sendall(bytes("teste", encoding='utf-8'))
						tcp2.close()

					client.set_sender_ip(client_ip)
					client.ClientConnect.start()

					client.clientServer.start()
					x = ExibeVideos(client)

					while True:
						code = input()

						socketserver.TCPServer.allow_reuse_address = True
						with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp2:
							print("AAA ---", client_ip)
							tcp2.connect((client_ip, 9093))
							tcp2.send(bytes(code, encoding='utf-8'))

							if code == "11":
								print(str(tcp2.recv(BUFFER_SIZE), 'utf-8'))

							else:
								print("Comando Invalido!")

				elif not ServerConnect.is_alive():
					client.set_sender_ip(TCP_HOST)
					client.ServerConnect.start()

					print("##### AAA #####")

					client.clientServer.start()

					x = ExibeVideos(client)
					x.start()

			# lista de clientes conectados
			if msg[0:2] == '11':
				print(str(tcp.recv(BUFFER_SIZE), 'utf-8'))

			# quantidade de clientes conectados
			if msg[0:2] == '13':
				print(str(tcp.recv(BUFFER_SIZE), 'utf-8'))

			tcp.shutdown(socket.SHUT_RDWR)

def connect(dest, msg, client):

	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp:
		tcp.connect((TCP_HOST, TCP_PORT))
		tcp.send(bytes("100", encoding='utf-8'))

		socketserver.TCPServer.allow_reuse_address = True
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp2:
			tcp2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

			tcp2.bind(('', 9091))
			tcp2.listen(1)

			content, address = tcp2.accept()

			received_msg = content.recv(BUFFER_SIZE)
			message = str(received_msg, 'utf-8')

		# Erro ao entrar no canal, deve-se conectar a cliente
		if message == "00":
			print("Limite de canais conectados ao servidor excedidos.")

			with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp2:
				tcp2.connect((TCP_HOST, 6060))
				teste = "11" + msg[-1]
				tcp2.send(bytes(teste, encoding='utf-8'))

				clients_ip = str(tcp2.recv(BUFFER_SIZE), 'utf-8')
				clients_ip = handle_ip_list(clients_ip)

			client_ip = None
			socketserver.TCPServer.allow_reuse_address = True
			for ip in clients_ip:
				with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp3:
					print("Request connection from: ", ip)
					tcp3.connect((ip, 9093))
					tcp3.send(bytes("10", encoding='utf-8'))
					resp = str(tcp3.recv(BUFFER_SIZE), 'utf-8')

					if resp == "OK":
						client_ip = ip
						break

					tcp3.close()

			if client_ip is None:
				client_ip = get_available_client(clients_ip)

			socketserver.TCPServer.allow_reuse_address = True
			with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp2:
				print("CLIENTE IP: ", client_ip)
				tcp2.connect((client_ip, 9095))
				tcp2.sendall(bytes("teste", encoding='utf-8'))
				tcp2.close()

			client.set_sender_ip(client_ip)
			client.ClientConnect.start()
			client.clientServer.start()

			while True:
				code = input()

				socketserver.TCPServer.allow_reuse_address = True
				with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp2:
					print("AAA ---", client_ip)
					tcp2.connect((client_ip, 9093))
					tcp2.send(bytes(code, encoding='utf-8'))

					if code == "11":
						print(str(tcp2.recv(BUFFER_SIZE), 'utf-8'))

					else:
						print("Comando Invalido!")

		elif not client.ServerConnect.is_alive():
			client.set_sender_ip(TCP_HOST)
			client.ServerConnect.start()

			client.clientServer.start()

	while True:
		msg = input()
		# tcp.connect(dest)
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp:
			print(TCP_HOST)
			tcp.connect(dest)

			print("Enviado:", msg)

			# Sair do canal
			if msg[0:2] == '12':
				client.ServerConnect.stop()
				client.ServerConnect.join()
				x.stop()

			tcp.send(bytes(msg, encoding='utf-8'))

			# Entrou em um canal
			if msg[0:2] == '10':
				# Recebe a mensagem de resposta
				#   "10" -> conectcou
				#   "00" -> nao conectou
				# message = ""
				with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sk_server:
					sk_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

					sk_server.bind(('', 9091))
					sk_server.listen(1)

					content, address = sk_server.accept()

					received_msg = content.recv(BUFFER_SIZE)
					message = str(received_msg, 'utf-8')

				if message == "00":
					# AQUI É ONDE O CLIENTE PROCURA OUTRO CLIENTE PARA RECEBER OS ARQUIVOS
					print("Limite de canais conectados ao servidor excedidos.")


					with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp2:
						tcp2.connect((TCP_HOST, 6060))
						teste = "11" + msg[-1]
						tcp2.send(bytes(teste, encoding='utf-8'))

						clients_ip = str(tcp2.recv(BUFFER_SIZE), 'utf-8')
						clients_ip = handle_ip_list(clients_ip)

					client_ip = None
					socketserver.TCPServer.allow_reuse_address = True
					for ip in clients_ip:
						with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp3:
							print("Request connection from: ", ip)
							tcp3.connect((ip, 9093))
							tcp3.send(bytes("10", encoding='utf-8'))
							resp = str(tcp3.recv(BUFFER_SIZE), 'utf-8')
							if resp == "OK":
								client_ip = ip
								break
							tcp3.close()

					if client_ip is None:
						client_ip = get_available_client(clients_ip)

					socketserver.TCPServer.allow_reuse_address = True
					with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp2:
						print("CLIENT: ", client_ip)
						tcp2.connect((client_ip, 9095))
						tcp2.sendall(bytes("teste", encoding='utf-8'))
						tcp2.close()

					client.set_sender_ip(client_ip)
					client.ClientConnect.start()

					client.clientServer.start()

					while True:
						code = input()

						socketserver.TCPServer.allow_reuse_address = True
						with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp2:
							tcp2.connect((client_ip, 9093))
							tcp2.send(bytes(code, encoding='utf-8'))
							if code == "11":
								print(str(tcp2.recv(BUFFER_SIZE), 'utf-8'))

							else:
								print("Comando Invalido!")

				elif not ServerConnect.is_alive():
					client.set_sender_ip(TCP_HOST)
					client.ServerConnect.start()


					client.clientServer.start()

			# Lista de clientes conectados
			if msg[0:2] == '11':
				print(str(tcp.recv(BUFFER_SIZE), 'utf-8'))

			# Quantidade de clientes conectados
			if msg[0:2] == '13':
				print(str(tcp.recv(BUFFER_SIZE), 'utf-8'))

			tcp.shutdown(socket.SHUT_RDWR)

def handle_ip_list(ip_list):
	cont = len(ip_list)
	i = 0
	teste = ''
	ips = []
	while i < cont:
		if ip_list[i] == ',' or ip_list[i] == ']':
			ips.append(teste)
			teste = ''

		else:
			if ip_list[i] != ' ' and ip_list[i] != '[' and ip_list[i] != "'":
				teste += ip_list[i]

		i += 1

	return ips

def get_available_client(clients_ip):
	normal = None
	for ip in clients_ip:
		if is_available(ip):
			normal = ip
			break

	if normal is not None:
		return normal

	for ip in clients_ip:
		clients_list = get_clients_list(ip)
		normal = get_available_client(clients_list)
		if normal is not None:
			return normal

def is_available(ip):
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp:
		tcp.connect((ip, 9093))
		tcp.send(bytes("10", encoding='utf-8'))
		resp = str(tcp.recv(BUFFER_SIZE), 'utf-8')

		if resp == "OK":
			return True

		else:
			return False

def get_clients_list(ip):
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp:
		tcp.connect((ip, 9093))
		tcp.send(bytes("11", encoding='utf-8'))
		resp = str(tcp.recv(BUFFER_SIZE), 'utf-8')

	clients_list = handle_ip_list(resp)

	return clients_list

conecta(TCP_HOST, TCP_PORT, BUFFER_SIZE, dest, msg, client)
# connect(dest, msg, client)

