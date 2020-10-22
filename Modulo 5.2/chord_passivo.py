### lado passivo (server) ###
### CHORD RING ###

'''
O programa principal (ESSE AQUI) receberá como entrada o valor de n, escolherá portas distintas para
cada nó e disparará um processo filho para simular a execução de cada um dos nós,
montando o anel logico com identificadores consecutivos.


Simulação da interface de acesso aos nós: ́Depois de disparados os processos filhos, o
programa principal deverá ficar disponível para responder consultas sobre os nós da tabela e sua localização (IP e porta).
'''

import json, select, socket, sys, threading

HOST = ''
PORT = 5000
ENCODING = "UTF-8"

ENTRADAS = [sys.stdin]  # define entrada padrão
CONEXOES = {}  # armazena historico de conexoes
ID_ENDERECO = {}  # associa um id único a um endereço (conexão de cliente ip + porta)


# Inicia o servidor e adiciona o socket do servidor nas entradas
def StartServer():
    numeroN = input("Digite o numero 'n' (2^n): ")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    #sock.listen(5)  # espera por até 5 conexões #TODO 2^n conexões serão suportadas
    sock.setblocking(False)  # torna o socket não bloqueante na espera por conexões
    ENTRADAS.append(sock)  # coloca o socket principal na lista de entradas de interesse

    instantiateRing(numeroN)

    return sock

def instantiateRing(numeroN):
    # 2^n
    return


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

            elif leitura_input == sys.stdin:  # entrada padrão, teclado
                cmd = input()
                if cmd == "--stop":  # solicitação para finalizar o servidor
                    for c in clients:
                        print("Ainda há clientes com conexões ativas")
                        # aguarda todas as threads terminarem, onde a magia do join acontece
                        c.join()
                    sock.close()
                    sys.exit()
                elif cmd == "--hist":  # mostra histórico de conexões do server
                    print(str(CONEXOES.keys()))


main()
