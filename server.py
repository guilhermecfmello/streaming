import socketserver
import sys
from canal import CanalThread        

class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):       
        # self.request is the TCP socket connected to the client
        data = str(self.request.recv(1024).strip(), 'utf-8')
        #print ("data=",data)
        codigo, canal_id = handle_request(data)

        ip_cliente = self.client_address[0]

        # Adicionar pessoa no canal
        if codigo == 10:

            # Procura o cliente em algum canal e retira ele caso tenha
            for _, canal in enumerate(CANAIS):
                if canal.remove_cliente(ip_cliente):
                    break

            CANAIS[canal_id].add_cliente(ip_cliente)

        # Listar pessoas de um canal
        if codigo == 11:
            canais_string = str(CANAIS[canal_id].clients)
            sys.stdout.write("Enviando lista de clientes do canal {} para o endereco {}.\n".format(
                canal_id, ip_cliente
            ))
            sys.stdout.flush()
            self.request.send(bytes(canais_string, encoding='utf-8'))

        # Remover pessoa no canal
        if codigo == 12:
            CANAIS[canal_id].remove_cliente(ip_cliente)

        # Numerar numero de pessoas em um canal
        if codigo == 13:
            num = str(CANAIS[canal_id].get_num_clients())
            sys.stdout.write("Enviando numero de clientes do canal {} para o endereco {}.\n".format(
                canal_id, ip_cliente
            ))
            sys.stdout.flush()
            self.request.send(bytes(num, encoding="utf-8"))

# Transforma uma string "XXC" em Código: XX Canal: C
def handle_request(request_string):
    cod   = request_string[0:2]
    canal = request_string[2]

    return int(cod), int(canal)

CANAIS = []
N = 2  # Quantidade de Canais

if __name__ == '__main__':
    # Deixa reutilizar a porta
    socketserver.TCPServer.allow_reuse_address = True

    # Cria os canais iniciais
    CANAIS = [CanalThread(i, "filme/") for i in range(N)]

    # Inicia os canais
    for i, canal in enumerate(CANAIS):
        canal.start()

    # Roda o servidor
    with socketserver.TCPServer(('', 6060), MyTCPHandler) as server:
        try:
            print("Starting server!")
            server.serve_forever()
        except KeyboardInterrupt:
            server.shutdown()
    
