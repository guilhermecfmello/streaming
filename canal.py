import threading
import socket as sk
import time
from os import listdir

WAIT_TIME   = 1.8
BUFFER_SIZE = 1024
PORTA_SAIDA = 9091

MAX_CLIENTES_CANAL = 3

class CanalThread(threading.Thread):
    def __init__(self, canal_id, path):
        threading.Thread.__init__(self)

        self.clients     = []
        self.canal_id    = canal_id
        self.path        = path
        self.curr_file   = 0
        self.total_files = len(listdir(self.path))

        self.nome_base   = listdir(self.path)[0].split('_')[0]

        print("[+] Nova thread iniciada para o canal {}".format(self.canal_id))
    
    def run(self):
        while True:
            tempo_inicial = time.time()

            for _, cliente in enumerate(self.clients):
                print("[*] Enviando canal {0} (arquivo {1}) para o cliente {2}.".format(
                    self.canal_id,
                    self.curr_file,
                    cliente
                ))
                self.enviar_video(cliente)

            tempo_final  = time.time()
            delta_tempo  = tempo_final - tempo_inicial
            tempo_espera = WAIT_TIME - delta_tempo

            if tempo_espera < 0:
                tempo_espera = 0

            time.sleep(tempo_espera)

            self.curr_file += 1
            if self.curr_file >= self.total_files:
                self.curr_file = 0
    
    def add_cliente(self, ip):
        
        # Se o canal ultrapassar o limite maximo de pessoas conectadas
        # Envia "00"
        if len(self.clients) >= MAX_CLIENTES_CANAL:
            with sk.socket(sk.AF_INET, sk.SOCK_STREAM) as tcp:
                tcp.connect((ip, PORTA_SAIDA))
                msg = "00"
                tcp.send(bytes(msg, encoding='utf-8'))
            return

        # Senao envia "10"
        msg = "10"
        with sk.socket(sk.AF_INET, sk.SOCK_STREAM) as tcp:
            tcp.connect((ip, PORTA_SAIDA))
            tcp.send(bytes(msg, encoding='utf-8'))

        self.clients.append(ip)
        print("{} inserido no canal {}".format(ip, self.canal_id))

    def remove_cliente(self, ip):
        if ip in self.clients:
            self.clients.remove(ip)
            print("{} removido do canal {}".format(ip, self.canal_id))
            return True
        return False

    def get_num_clients(self):
        return len(self.clients)

    def enviar_video(self, cliente):
        with sk.socket(sk.AF_INET, sk.SOCK_STREAM) as sk_client:
            sk_client.connect((cliente,  PORTA_SAIDA))

            nome_arq = self.path + "{}_{}.mkv".format(self.nome_base, format(self.curr_file, '05d'))

            # Envia o arquivo
            with open(nome_arq, 'rb') as up_file:
                send_read = up_file.read(BUFFER_SIZE)
                while send_read:
                    sk_client.send(send_read)
                    send_read = up_file.read(BUFFER_SIZE)

# End class
