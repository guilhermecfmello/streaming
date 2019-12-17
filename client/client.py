import socket
import threading
import sys

class Receptor(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        self._stopped = False

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sk_server:
            sk_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            sk_server.bind(('', 9091))
            sk_server.listen(1)

            file_num = 0

            while not self._stopped:
                content, address = sk_server.accept()

                # Recebe o nome do arquivo
                nome = "{}.mkv".format(file_num)
                sys.stdout.write("Recebendo '{}' de {}.\n".format(nome, address[0]))
                sys.stdout.flush()

                # Recebe o arquivo
                with open(nome, 'wb') as down_file:
                    recv_read = content.recv(BUFFER_SIZE)
                    while recv_read:
                        down_file.write(recv_read)
                        recv_read = content.recv(BUFFER_SIZE)

                content.close()
                file_num += 1



    def stop(self):
        self._stopped = True

# IP e porta do servidor
TCP_HOST    = 'localhost'  # IP
TCP_PORT    = 6060         #porta
BUFFER_SIZE = 1024 # Normally 1024

dest = (TCP_HOST, TCP_PORT)

msg = None

recep = Receptor()
# recep.daemon = True

while True:
    msg = input()
    #tcp.connect(dest)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp:

        tcp.connect(dest)

        print("Enviado:", msg)

        # Sair do canal
        if msg[0:2] == '12':
            recep.stop()
            recep.join()
            recep = Receptor()
            
        tcp.send(bytes(msg, encoding='utf-8'))

        # Entrou em um canal
        if msg[0:2] == '10':

            # Recebe a mensagem de resposta
            #   "10" -> conectcou
            #   "00" -> nao conectou
            message = ""
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sk_server:
                sk_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                sk_server.bind(('', 9091))
                sk_server.listen(1)

                content, address = sk_server.accept()

                received_msg = content.recvmsg(BUFFER_SIZE)
                message = str(received_msg[0], 'utf-8')

            if message == "00":
                print("Limite de canais conectados excedidos.")
            elif not recep.is_alive():
                recep.start()

        # lista de clientes conectados
        if msg[0:2] == '11':
            print(str(tcp.recv(BUFFER_SIZE), 'utf-8'))

        # quantidade de clientes conectados
        if msg[0:2] == '13':
            print(str(tcp.recv(BUFFER_SIZE), 'utf-8'))

        tcp.shutdown(socket.SHUT_RDWR)
