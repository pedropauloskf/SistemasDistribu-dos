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
    def __init__(self, nodePort, nodeID, N_Number, FingerTable):
        self.NODE_PORT = nodePort
        self.NODE_ID = nodeID
        self.N_NUMBER = N_Number
        self.ENTRADA_SELECT = []
        self.HASH_TABLE = {}  # armazena os pares chave/valor do nó
        self.FINGER_TABLE = FingerTable  # armazena o nó mais próximo a determinada distância
        self.LOG = True

        self.__startNode()

    # Log do nó
    def log(self, msg):
        if self.LOG:
            print('[Node %s] %s' % (self.NODE_ID, msg))

    def setFingerTable(self, fingerTable):
        self.FINGER_TABLE = fingerTable

    # Inicia o socket para receber novas conexões
    def startSocket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.HOST, self.NODE_PORT))
        sock.listen(self.N_NUMBER + 1)  # espera por até N + 1 conexões
        sock.setblocking(False)  # torna o socket não bloqueante na espera por conexões

        self.log("Start Socket " + str([self.HOST, self.NODE_PORT, self.N_NUMBER]))
        return sock

    # Faz a conexão com um outro nó
    def startConnection(self, port):
        self.log('Iniciando conexão com %s' % port)
        sock = socket.socket()
        sock.connect((self.HOST, port))
        self.log('Conectado')
        return sock

    # Encerra a conexão com um nó
    def closeConnection(self, sock):
        self.log('Encerrando conexão')
        sock.close()
        return

    # Aceita a conexão de um novo client
    @staticmethod
    def newClient(sock):
        newSocket, add = sock.accept()
        return newSocket, add

    # Faz a hash da chave passada
    @staticmethod
    def hashing(key):
        return sha1(str.encode(key)).hexdigest()

    # Verifica se a hash pertence ao nó em questão e retorna a hash ou o nó correto
    def checkHash(self, key):
        hashStr = self.hashing(key)
        nodeTotal = 2 ** self.N_NUMBER
        targetNode = int(hashStr, 16) % nodeTotal
        if targetNode == self.NODE_ID:
            return True, hashStr
        else:
            return False, targetNode

    # Verifica a distância entre dois nós especificados
    def distanceToTargetNode(self, target, num):
        nodeNum = self.NODE_ID + (2 ** num) % (2 ** self.N_NUMBER)
        targetDist = (target - self.NODE_ID) if (target > self.NODE_ID) else (
                target - self.NODE_ID + 2 ** self.N_NUMBER)
        nodeDist = (nodeNum - self.NODE_ID) if (nodeNum > self.NODE_ID) else (
                nodeNum - self.NODE_ID + 2 ** self.N_NUMBER)
        return targetDist - nodeDist

    # Função de redirecionamento da requisição, caso não seja o nó correto
    def redirectRequest(self, target, msgStr):
        nodeToConnect = -1
        nodePort = -1
        for i in range(len(self.FINGER_TABLE)):
            if self.distanceToTargetNode(target, i) < 0:
                nodeToConnect = i - 1
                nodePort = self.FINGER_TABLE[nodeToConnect]
                break
            elif i == len(self.FINGER_TABLE) - 1:
                nodeToConnect = i
                nodePort = self.FINGER_TABLE[nodeToConnect]

        self.log('Redirecionando request para node %s' % nodeToConnect)
        otherNodeSock = self.startConnection(nodePort)
        otherNodeSock.send(msgStr.encode(self.ENCODING))
        self.closeConnection(otherNodeSock)

    # Função de busca do valor associado a uma chave na tabela hash
    def lookUp(self, clientPort, key, msgStr):
        self.log('Verificando se a chave %s pertence ao nó' % key)
        isCorrectNode, data = self.checkHash(key)
        if isCorrectNode:
            try:
                self.log("Recuperando valor da chave")
                value = self.HASH_TABLE[data]
                msgToSend = self.packMsg("success", "%s-|-%s" % (self.NODE_ID, value))
            except:
                self.log("Chave %s não encontrada" % key)
                msgToSend = self.packMsg('fail', '')
            finally:
                clientSock = self.startConnection(int(clientPort))
                clientSock.send(msgToSend.encode(self.ENCODING))
                self.closeConnection(clientSock)

        else:
            self.redirectRequest(data, msgStr)

    # Função de inserção do par na tabela hash
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

    # # Verfica o comando enviado e o executa
    def checkCommand(self, msgStr):
        header, msg = self.unpackMsg(msgStr)

        if header == 'lookup':
            self.log('Recebido pedido de busca')
            ind = msg.index('-|-')
            self.lookUp(msg[:ind], msg[ind + 3:], msgStr)

        elif header == 'insert':
            self.log('Recebido pedido de inserção')
            ind = msg.index('-|-')
            self.insert(msg[:ind], msg[ind + 3:], msgStr)
        return

    # Processa o pedido feito pelo client
    def Processing(self, clientSock, addr):
        msg = clientSock.recv(8192)

        if not msg:
            clientSock.close()
            return

        msgStr = str(msg, encoding=self.ENCODING)
        self.checkCommand(msgStr)

    def StartNode(self):
        self.log("### Inicializando ###")
        nodeSock = self.startSocket()  # Cria o socket do nó
        self.ENTRADA_SELECT.append(nodeSock)  # appenda o socket na lista pro select
        self.log("### Pronto - Nó Chord Instanciado ###")

        while True:
            leitura, escrita, excecao = select.select(self.ENTRADA_SELECT, [], [])  # listas do select

            # percorre cada objeto de leitura (conexão socket, entrada de teclado)
            for leitura_input in leitura:
                # significa que a leitura recebeu pedido de conexão
                if leitura_input == nodeSock:
                    clientSock, endr = self.newClient(nodeSock)
                    newClientThread = threading.Thread(target=self.Processing, args=(clientSock, endr))
                    newClientThread.start()

    # Guarda uma referência do método para ser chamado log no init (instanciação) da classe
    __startNode = StartNode
