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

class ChordNode :

    HOST = ''
    MAIN_PORT = 5000
    #NODE_PORT = 0
    ENCODING = "UTF-8"

    #NODE_ID = -1
    #N_NUMBER = 0
    

    # a classe ao ser instanciada, recebe os parametos
    def __init__(self,nodePort,nodeID,N_Number):
        self.NODE_PORT = nodePort
        self.NODE_ID = nodeID
        self.N_NUMBER = N_Number
        self.ENTRADA_SELECT = []
        self.HASH_TABLE = {}  # armazena os pares chave/valor do nó
        self.FINGER_TABLE = []  # armazena o nó mais próximo a determinada distância

        self.__startNode()

    '''
    def setData(nodePort, nodeID):
        global NODE_ID, NODE_PORT
        NODE_ID = nodeID
        NODE_PORT = nodePort
        return
    '''

    def log(self,msg):
        #global NODE_ID
        print('[Node %s] %s' % (self.NODE_ID, msg))


    def startSocket(self):
        #global N_NUMBER, NODE_PORT, HOST
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.HOST, self.NODE_PORT))
        sock.listen(self.N_NUMBER + 1)  # espera por até N + 1 conexões
        sock.setblocking(False)  # torna o socket não bloqueante na espera por conexões
        self.log("Start Socket " + str([self.HOST,self.NODE_PORT,self.N_NUMBER]) )
        return sock


    def startConnection(port):
        sock = socket.socket()
        sock.connect((HOST, port))
        return sock


    def closeConnection(sock):
        sock.close()
        return


    def acknowledgeReady():
        mainSock = startConnection(MAIN_PORT)
        msg = 'ACK %s' % str(NODE_ID)
        mainSock.send(msg.encode(ENCODING))
        mainSock.recv(1024)
        closeConnection(mainSock)
        return


    def newClient(sock):
        newSocket, add = sock.accept()
        return newSocket, add


    def hashing(key):
        return sha1(str.encode(key)).hexdigest()


    def checkHash(key):
        global N_NUMBER
        hashStr = hashing(key)
        nodeTotal = 2 ** N_NUMBER
        targetNode = int(hashStr, 16) % nodeTotal
        if targetNode == NODE_ID:
            return True, hashStr
        else:
            return False, targetNode


    def distanceToTargetNode(target, num):
        global NODE_ID, N_NUMBER
        nodeNum = NODE_ID + (2**num) % (2**N_NUMBER)
        targetDist = (target - NODE_ID) if (target < NODE_ID) else (target - NODE_ID + 2**N_NUMBER)
        nodeDist = (nodeNum - NODE_ID) if (nodeNum < NODE_ID) else (nodeNum - NODE_ID + 2**N_NUMBER)

        return targetDist - nodeDist


    def redirectRequest(target, msgStr):
        global FINGER_TABLE
        nodeToConnect = -1
        for i in range(len(FINGER_TABLE)):
            if distanceToTargetNode(target, i) < 0:
                nodeToConnect = FINGER_TABLE[i - 1]
                break
            elif i == len(FINGER_TABLE) - 1:
                nodeToConnect = FINGER_TABLE[i]
        # TODO conectar com nodeToConnect e enviar requisição


    def lookUp(key, client, msgStr):
        isCorrectNode, data = checkHash(key)
        if isCorrectNode:
            value = HASH_TABLE[data]
            # TODO enviar valor diretamente de volta para o cliente
        else:
            redirectRequest(data, msgStr)


    def insert(key, value, msgStr):
        isCorrectNode, data = checkHash(key)
        if isCorrectNode:
            HASH_TABLE[data] = value
        else:
            redirectRequest(data, msgStr)


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


    def checkCommand(msgStr):
        header, msg = unpackMsg(msgStr)

        if header == 'lookup':
            ind = msg.index('-|-')
            lookUp(msg[:ind], msg[ind+3:], msgStr)
        elif header == 'insert':
            ind = msg.index('-|-')
            insert(msg[:ind], msg[ind+3:], msgStr)
        elif header == 'check':
            a = 3

        return

    # 
    # def StartNode(nodeId, port):
    def StartNode(self):
        #setData(port, nodeId)
        self.ENTRADA_SELECT.append(self.startSocket())  # cria o socket do nó e appenda na lista pro select
        self.log("### Pronto - Nó Chord Instanciado ###")
        #acknowledgeReady()

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

    def PreencheFinger(self,FingerTable):
        self.FINGER_TABLE = FingerTable