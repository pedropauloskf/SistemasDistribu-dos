### lado passivo (server) ###
### CHORD RING ###

"""
O programa principal (ESSE AQUI) receberá como entrada o valor de n, escolherá portas distintas para
cada nó e disparará um processo filho para simular a execução de cada um dos nós,
montando o anel logico com identificadores consecutivos.

Simulação da interface de acesso aos nós: ́Depois de disparados os processos filhos, o programa principal deverá
ficar disponível para responder consultas sobre os nós da tabela e sua localização (IP e porta).
"""
import socket
import threading
from hashlib import sha1

import select

HOST = ''
PORT = 5000
ENCODING = "UTF-8"

ENTRADAS = []  # define entrada padrão
CONEXOES = {}  # armazena historico de conexoes
ID_ENDERECO = {}  # associa um id único a um endereço (conexão de cliente ip + porta)
NODES = []
NODENUMBER = 0

# Inicia o servidor e adiciona o socket do servidor nas entradas
def StartServer():
    global NODENUMBER
    NODENUMBER = int(input("Digite o numero 'n' (2^n): "))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen(2**NODENUMBER)  # espera por até 2^n conexões
    sock.setblocking(False)  # torna o socket não bloqueante na espera por conexões

    return sock


def instantiateRing():
    global NODENUMBER
    for i in range(NODENUMBER):
        # cria e inicia nova thread para gerar os nós
        newNode = threading.Thread(target=Processing, args=())
        newNode.start()
        # armazena a referencia da thread para usar com join()
        NODES.append(newNode)
    return

def hashing(key):
    return sha1(str.encode(key)).hexdigest()

# gerencia o recebimento de conexões de clientes, recebe o sock do server
def NewClient(sock):
    newSocket, endereco = sock.accept()
    print('Conectado com: ' + str(endereco))

    CONEXOES[endereco] = newSocket  # registra a nova conexão no dicionário de conexões
    if len(ID_ENDERECO) == 0:
        ID_ENDERECO[1] = endereco
    else:
        index = max(ID_ENDERECO, key=ID_ENDERECO.get) + 1
        ID_ENDERECO[index] = endereco

    return newSocket, endereco


# Processa as requisições do cliente
def Processing(clientSock, address):
    while True:
        msg = clientSock.recv(8192)

        if not msg:
            print(str(address) + '-> encerrou')
            del CONEXOES[address]
            del ID_ENDERECO[list(ID_ENDERECO.keys())[list(ID_ENDERECO.values()).index(address)]]
            clientSock.close()
            return

        msgStr = (str(msg, encoding=ENCODING))


def main():
    clients = []  # armazena as threads de cada client para dar join
    sock = StartServer()  # pega o socket do servidor
    print("### SERVER - ESPERANDO POR CONEXÕES ###")

    while True:
        leitura, escrita, excecao = select.select(ENTRADAS, [], [])  # listas do select

        # percorre cada objeto de leitura (conexão socket, entrada de teclado)
        for leitura_input in leitura:
            # significa que a leitura recebeu pedido de conexão
            if leitura_input == sock:
                clientSock, endr = NewClient(sock)

                # cria e inicia nova thread para atender o cliente
                newClientThread = threading.Thread(target=Processing, args=(clientSock, endr))
                newClientThread.start()
                # armazena a referencia da thread para usar com join()
                clients.append(newClientThread)


main()
