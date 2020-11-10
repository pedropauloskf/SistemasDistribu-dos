import socket, select, sys, threading, time

connectionsList = {1: 5001, 2: 5002, 3: 5003, 4: 5004}
HOST = ''
ENCODING = "UTF-8"

def startReplicaConnection(replicaId):
    replicaSock = socket.socket()
    port = connectionsList[replicaId]
    replicaSock.connect((HOST, port))

    return replicaSock

def startReplicas():
    for ids in range(1, 5):
        newReplicaThread = threading.Thread(target=ReplicaNode, args=ids)
        newReplicaThread.start()

def main():
    connected = False
    startReplicas()

    replicaSock = None

    while True:
        if not connected:
            replicaId = int(input("\nDigite o numero da réplica a se conectar: \n"))
            replicaSock = startReplicaConnection(replicaId)
            replicaSock.send('[connect]'.encode(ENCODING))
            msg = replicaSock.recv(1024)
            msgStr = str(msg, encoding=ENCODING)
            if msgStr == '[ACK]':
                connected = True
            else:
                print('[MAIN] Não foi possível conectar-se a réplica solicitada. Tente novamente.')
        else:
            if replicaSock:
                msg = replicaSock.recv(1024)
                msgStr = str(msg, encoding=ENCODING)
                if msgStr == '[disconnect]':
                    replicaSock.close()
                    connected = False

class ReplicaNode:
    HOST = ''
    ENTRADAS = []  # [sys.stdin]  # define entrada padrão
    ENCODING = "UTF-8"

    # a classe ao ser instanciada, recebe os parametos
    def __init__(self, myId):
        self.connectedToClient = False
        self.x = 0
        self.myId = myId
        self.primaryCopyHolderId = 1
        # Variavel que diz quem esta com o chapeu para poder alterar X
        self.changesHistory = []
        self.connectionsList = {1: 5001, 2: 5002, 3: 5003, 4: 5004}

        self.__startReplica()

    def log(self, message):
        print('[Replica %s] %s' % (self.myId, message))

    # Inicia o servidor e adiciona o socket do servidor nas entradas
    def StartServer(self):
        self.log("Conectado a porta: %i" % self.connectionsList[self.myId])

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port = int(self.connectionsList[self.myId])
        sock.bind((self.HOST, port))
        sock.listen(5)  # espera por até 5 conexões
        # sock.setblocking(False)  # torna o socket não bloqueante na espera por conexões
        self.ENTRADAS.append(sock)
        return sock

    @staticmethod
    def newClient(sock):
        newSocket, add = sock.accept()
        return newSocket, add

    def ConnectToReplica(self, id):
        self.log('Iniciando conexão com réplica %s' % id)
        sock = socket.socket()
        port = self.connectionsList[id]
        sock.connect((self.HOST, port))
        self.log('Conectado')
        return sock

    def SetPrimaryCopyHolder(self, holderId):
        self.primaryCopyHolderId = holderId

    def isPrimaryHolder(self):
        return self.primaryCopyHolderId == self.myId

    # gerencia o recebimento de conexões de clientes, recebe o sock do server
    def NewClient(self, sock):
        newSocket, endereco = sock.accept()
        self.log('Conectado com: ' + str(endereco))

        return newSocket, endereco

    def PrintCommandList(self):
        print("--help - lista os comandos")
        print("--valor - valor de x nesta réplica")
        print("--historico - historico do valor de x")
        print("--alterar - altera o valor de x")
        print("--fim - finaliza esta replica")

    def ProcessCommand(self, command, mySock):
        if command == "--help":
            self.PrintCommandList()
        if command == "--valor":
            print(self.x)
        if command == "--historico":
            print(self.changesHistory)
        if command == "--alterar":
            self.Altera_X(mySock)
        if command == "--fim":
            exit()

    def ProcessMessage(self, msgStr, sock):
        headerEnd = msgStr.index(']')
        headerStr = msgStr[1:headerEnd]
        msgContent = msgStr[headerEnd + 1:]

        if headerStr == "[ACK]":
            sock.close()

        if headerStr == "[changedX]":
            [replicaId, xValue] = msgContent.split('-|-')
            self.changesHistory.append({"replica": replicaId, "x": xValue})

        if headerStr == "[changePrimary]":
            [former, new] = msgContent.split('-|-')
            if self.primaryCopyHolderId == former or 0:
                self.SetPrimaryCopyHolder(new)

        if headerStr == "[getPrimary]":
            if self.primaryCopyHolderId == self.myId:
                # TODO responder com ACK e bloquear mudança pra outro
                self.SetPrimaryCopyHolder(0)
            else:
                # TODO Negar mudança

    # Processa a nova conexão
    def Processing(self, clientSock, addr):
        msg = clientSock.recv(8192)

        if not msg:
            clientSock.close()
            return

        msgStr = str(msg, encoding=self.ENCODING)
        self.ProcessMessage(msgStr, clientSock)

    # Informa outras réplicas para salvarem as mudanças em X
    def saveChanges(self):
        for i in range(1, 5):
            if i != self.myId:
                replicaSock = self.ConnectToReplica(i)
                msgStr = "[changedX]%s-|-%s" % (self.myId, self.x)
                replicaSock.send(msgStr.encode(self.ENCODING))
                replicaSock.close()

    # Se definie como novo dono da chave primária e informa outras réplicas
    def isNewPrimaryHolder(self):
        self.SetPrimaryCopyHolder(self.myId)
        for i in range(1, 5):
            if i != self.myId:
                replicaSock = self.ConnectToReplica(i)
                msgStr = "[changePrimary]%s" % self.myId
                replicaSock.send(msgStr.encode(self.ENCODING))
                replicaSock.close()

    def Altera_X(self, mySock):
        # Pega a chave primãria para a réplica
        if not self.isPrimaryHolder:
            primarySock = self.ConnectToReplica(self.primaryCopyHolderId)
            msgStr = "[getPrimary]"
            while not self.isPrimaryHolder:
                primarySock.send(msgStr.encode(self.ENCODING))
                reply = primarySock.recv(2048)
                replyStr = str(reply, encoding=self.ENCODING)
                if replyStr == "[ACK]":
                    primarySock.close()
                    self.isNewPrimaryHolder()
                else:
                    time.sleep(2)

        # Faz a escrita em X
        try:
            val = int(input("Novo valor para X: "))
            self.x = val
            self.changesHistory.append({"replica": self.myId, "x": val})
        except ValueError:
            print("Valor inválido. Tente Novamente.")

    def StartReplica(self):
        mySock = self.StartServer()
        self.log("### ESPERANDO POR CONEXÕES ###" % self.myId)

        while True:
            leitura, escrita, excecao = select.select(self.ENTRADAS, [], [])  # listas do select

            # percorre cada objeto de leitura (conexão socket, entrada de teclado)
            for leitura_input in leitura:
                # significa que a leitura recebeu pedido de conexão
                if leitura_input == mySock:
                    clientSock, endr = self.NewClient(mySock)

                    # Cria e inicia nova thread para atender o cliente
                    newClientThread = threading.Thread(target=self.Processing, args=(clientSock, endr))
                    newClientThread.start()

                # entrada padrão, teclado
                elif leitura_input == sys.stdin:
                    command = input("Digite o comando: ")
                    self.ProcessCommand(command, mySock)

    # Guarda uma referência do método para ser chamado logo no init (instanciação) da classe
    __startReplica = StartReplica


if __name__ == "__main__":
    main()
