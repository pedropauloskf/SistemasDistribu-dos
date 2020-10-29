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
import chord_node

from hashlib import sha1
# from chord_node import StartNode

import select

HOST = ''
PORT = 5000
ENCODING = "UTF-8"

ENTRADAS = []  # define entrada padrão
CONEXOES = {}  # armazena historico de conexoes
ID_ENDERECO = {}  # associa um id único a um endereço (conexão de cliente ip + porta)
NODES = []
N_NUMBER = 0

ENDERECOS_NOS_CHORD = {}  # dicionario de id do chord + porta
LISTA_INSTANCIAS = []


def log(msg):
    print('[SERVER] %s' % msg)

# Inicia o servidor e adiciona o socket do servidor nas entradas
def StartServer():
    global N_NUMBER
    N_NUMBER = int(input("Digite o numero 'n' (2^n): "))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen(2 ** N_NUMBER)  # espera por até 2^n conexões
    sock.setblocking(False)  # torna o socket não bloqueante na espera por conexões
    ENTRADAS.append(sock)

    return sock


def instantiateRing():
    global N_NUMBER, NODES, PORT, ENDERECOS_NOS_CHORD, LISTA_INSTANCIAS
    for i in range(2 ** N_NUMBER):

        ENDERECOS_NOS_CHORD[i] = PORT + i + 1

        fingerTable = []
        for j in range(N_NUMBER):
            pos = (i + 2**j) % 2**N_NUMBER
            fingerTable.append( PORT + 1 + pos )

        # cria e inicia nova thread para gerar os nós
        newNode = threading.Thread(target=chord_node.ChordNode, args=( PORT+i+1 , i , N_NUMBER, fingerTable ))
        newNode.start()

        # armazena a referencia da thread para usar com join()
        NODES.append(newNode)
    return


# Cada thread criada chamará este método que instanciará uma classe com as propriedades
def InstantiateChordNode(nodePort, nodeID, n_number):
    global LISTA_INSTANCIAS
    inst = chord_node.ChordNode(nodePort, nodeID, n_number)
    LISTA_INSTANCIAS.append(inst)

    log("debug: " + str((inst.NODE_ID, inst.NODE_PORT, inst.N_NUMBER)))


# Faz a hash da chave passada
def hashing(key):
    return sha1(str.encode(key)).hexdigest()


# gerencia o recebimento de conexões de clientes, recebe o sock do server
def NewClient(sock):
    newSocket, endereco = sock.accept()

    log('Conectado com: ' + str(endereco))

    CONEXOES[endereco] = newSocket  # registra a nova conexão no dicionário de conexões
    if len(ID_ENDERECO) == 0:
        ID_ENDERECO[1] = endereco
    else:
        index = max(ID_ENDERECO, key=ID_ENDERECO.get) + 1
        ID_ENDERECO[index] = endereco

    return newSocket, endereco


# Separa a mensagem recebida do header de envio
def unpackMsg(msgStr):
    headerStart = msgStr.index('[[')
    headerEnd = msgStr.index(']]')
    headerStr = msgStr[headerStart + 2:headerEnd]
    msgContent = msgStr[headerEnd + 2:]
    return headerStr, msgContent


# Adiciona o header de envio a mensagem ou ação
def packMsg(msgHeader, msgStr):
    messagePrefix = "[[" + str(msgHeader) + "]]"
    return messagePrefix + msgStr


# Verfica o comando enviado e o executa
def CommandList(sock, msg):
    headerStr, msgContent = unpackMsg(msg)

    # Comando de busca do endereço de um nó
    if headerStr == 'getAddr':
        addr = ENDERECOS_NOS_CHORD[int(msgContent)]
        res = packMsg('Addr', str(addr))
        sock.send(res.encode(ENCODING))

    # Comando de inicialização do Client para verificar o número total de nós
    elif headerStr == 'startClient':
        res = packMsg('N', str(2**N_NUMBER))
        sock.send(res.encode(ENCODING))


# Processa as requisições do cliente
def Processing(clientSock, address):
    global ENCODING, ENDERECOS_NOS_CHORD, N_NUMBER
    while True:
        msg = clientSock.recv(8192)

        if not msg:
            log(str(address) + '-> encerrou')

            del CONEXOES[address]
            del ID_ENDERECO[list(ID_ENDERECO.keys())[list(ID_ENDERECO.values()).index(address)]]
            clientSock.close()
            return

        msgStr = (str(msg, encoding=ENCODING))
        CommandList(clientSock, msgStr)


def main():
    sock = StartServer()  # pega o socket do servidor
    instantiateRing()

    log("### ESPERANDO POR CONEXÕES ###")

    while True:
        leitura, escrita, excecao = select.select(ENTRADAS, [], [])  # listas do select

        # percorre cada objeto de leitura (conexão socket, entrada de teclado)
        for leitura_input in leitura:
            # significa que a leitura recebeu pedido de conexão
            if leitura_input == sock:
                clientSock, endr = NewClient(sock)
                newClientThread = threading.Thread(target=Processing, args=(clientSock, endr))
                newClientThread.start()


main()
