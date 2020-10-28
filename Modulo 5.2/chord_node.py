### nó (server) ###
### CHORD RING ###

"""
Processo do nó que armazenará os pares de {chave: valor} em uma tabela hash e receberá solicitações de consulta e
inserção desses pares
"""

import socket
import threading
from hashlib import sha1

import select


class ChordNode:
    HOST = ''
    MAIN_PORT = 5000
    ENCODING = "UTF-8"

    # a classe ao ser instanciada, recebe os parametos
    def __init__(self, nodePort, nodeID, N_Number):
        self.NODE_PORT = nodePort
        self.NODE_ID = nodeID
        self.N_NUMBER = N_Number
        self.ENTRADA_SELECT = []
        self.HASH_TABLE = {}  # armazena os pares chave/valor do nó
        self.FINGER_TABLE = []  # armazena o nó mais próximo a determinada distância
        self.LOG = True

        self.__startNode()

    def log(self, msg):
        if self.LOG:
            print('[Node %s] %s' % (self.NODE_ID, msg))

    def startSocket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.HOST, self.NODE_PORT))
        sock.listen(self.N_NUMBER + 1)  # espera por até N + 1 conexões
        sock.setblocking(False)  # torna o socket não bloqueante na espera por conexões

        self.log("Start Socket " + str([self.HOST, self.NODE_PORT, self.N_NUMBER]))
        return sock

    def startConnection(self, port):
        self.log('Iniciando conexão com %s' % port)
        sock = socket.socket()
        sock.connect((self.HOST, port))
        self.log('Conectado')
        return sock

    def closeConnection(self, sock):
        self.log('Encerrando conexão')
        sock.close()
        return

    def acknowledgeReady(self):
        mainSock = self.startConnection(self.MAIN_PORT)
        msg = 'ACK %s' % str(self.NODE_ID)
        mainSock.send(msg.encode(self.ENCODING))
        mainSock.recv(1024)
        self.closeConnection(mainSock)
        return

    @staticmethod
    def newClient(sock):
        newSocket, add = sock.accept()
        return newSocket, add

    @staticmethod
    def hashing(key):
        return sha1(str.encode(key)).hexdigest()

    def checkHash(self, key):
        hashStr = self.hashing(key)
        nodeTotal = 2 ** self.N_NUMBER
        targetNode = int(hashStr, 16) % nodeTotal
        if targetNode == self.NODE_ID:
            return True, hashStr
        else:
            return False, targetNode

    def distanceToTargetNode(self, target, num):
        nodeNum = self.NODE_ID + (2 ** num) % (2 ** self.N_NUMBER)
        targetDist = (target - self.NODE_ID) if (target < self.NODE_ID) else (target - self.NODE_ID + 2 ** self.N_NUMBER)
        nodeDist = (nodeNum - self.NODE_ID) if (nodeNum < self.NODE_ID) else (nodeNum - self.NODE_ID + 2 ** self.N_NUMBER)

        return targetDist - nodeDist

    def redirectRequest(self, target, msgStr):
        nodeToConnect = -1
        for i in range(len(self.FINGER_TABLE)):
            if self.distanceToTargetNode(target, i) < 0:
                nodeToConnect = self.FINGER_TABLE[i - 1]
                break
            elif i == len(self.FINGER_TABLE) - 1:
                nodeToConnect = self.FINGER_TABLE[i]
        self.log('Redirecionando request para node %s' % nodeToConnect)
        # TODO conectar com nodeToConnect e enviar requisição

    def lookUp(self, key, client, msgStr):
        self.log('Verificando se a chave %s pertence ao nó' % key)
        isCorrectNode, data = self.checkHash(key)
        if isCorrectNode:
            self.log("Recuperando valor da chave")
            value = self.HASH_TABLE[data]
            # TODO enviar valor diretamente de volta para o cliente
        else:
            self.redirectRequest(data, msgStr)

    def insert(self, key, value, msgStr):
        self.log('Verificando se a chave %s pertence ao nó' % key)
        isCorrectNode, data = self.checkHash(key)
        if isCorrectNode:
            self.log('Salvando chave %s no nó' % key)
            self.HASH_TABLE[data] = value
        else:
            self.redirectRequest(data, msgStr)

    # Separa a mensagem recebida do header de envio
    @staticmethod
    def unpackMsg(msgStr):
        headerStart = msgStr.index('[[')
        headerEnd = msgStr.index(']]')
        headerStr = msgStr[headerStart + 2:headerEnd]
        msgContent = msgStr[headerEnd + 2:]
        return headerStr, msgContent

    # Adiciona o header de envio a mensagem ou ação
    @staticmethod
    def packMsg(msgHeader, msgStr):
        messagePrefix = "[[" + str(msgHeader) + "]]"
        return messagePrefix + msgStr

    def checkCommand(self, msgStr):
        header, msg = self.unpackMsg(msgStr)

        if header == 'lookup':
            ind = msg.index('-|-')
            self.lookUp(msg[:ind], msg[ind + 3:], msgStr)
        elif header == 'insert':
            ind = msg.index('-|-')
            self.insert(msg[:ind], msg[ind + 3:], msgStr)
        elif header == 'check':
            a = 3
        return

    def StartNode(self):
        self.log("### Inicializando ###")
        self.ENTRADA_SELECT.append(self.startSocket())  # cria o socket do nó e appenda na lista pro select
        self.log("### Pronto - Nó Chord Instanciado ###")

        '''
        ############# Programa main fica bloqueado neste while True #############

        while True:
            leitura, escrita, excecao = select.select(self.ENTRADA_SELECT, [], [])  # listas do select

            # significa que a leitura recebeu pedido de conexão
            if nodeSock in leitura:
                clientSock, add = newClient(nodeSock)

                msg = clientSock.recv(8192)
                msgStr = (str(msg, encoding=ENCODING))

                checkCommand(msgStr)
    '''

    # Guarda uma referência do método para ser chamado log no init (instanciação) da classe
    __startNode = StartNode

    def PreencheFinger(self, FingerTable):
        self.FINGER_TABLE = FingerTable
