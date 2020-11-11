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
        newReplicaThread = threading.Thread(target=ReplicaNode, args=(ids,))
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
        # Variavel que diz quem esta com o chapeu para poder alterar X
        self.primaryCopyHolderId = 1
        self.changesHistory = []
        self.connectionsList = {1: 5001, 2: 5002, 3: 5003, 4: 5004}
        self.sock = None

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
        self.sock = sock

    @staticmethod
    def newClient(sock):
        newSocket, add = sock.accept()
        return newSocket, add

    def ConnectToReplica(self, replicaId):
        self.log('Iniciando conexão com réplica %s' % replicaId)
        sock = socket.socket()
        port = self.connectionsList[replicaId]
        sock.connect((self.HOST, port))
        self.log('Conectado com a réplica %s' % replicaId)
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

    def Confirm(self, sock):
        sock.send('[ACK]'.encode(self.ENCODING))

    def Deny(self, sock):
        sock.send('[DENY]'.encode(self.ENCODING))

    @staticmethod
    def PrintCommandList():
        print("--help - lista os comandos")
        print("--valor - valor de x nesta réplica")
        print("--historico - historico do valor de x")
        print("--alterar - altera o valor de x")
        print("--fim - finaliza esta replica")

    def ProcessCommand(self, command, mySock):
        if command == "--help":
            self.PrintCommandList()
        elif command == "--valor":
            print(self.x)
        elif command == "--historico":
            print(self.changesHistory)
        elif command == "--alterar":
            self.Altera_X(mySock)
        elif command == "--fim":
            self.saveChanges()
            self.connectedToClient = False
        else:
            print("Comando Inválido. Tente novamente.")

    def ClientConnection(self, clientSock):
        self.connectedToClient = True
        self.Confirm(clientSock)
        self.PrintCommandList()
        while self.connectedToClient:
            command = input("Digite o comando: ")
            self.ProcessCommand(command, self.sock)
        clientSock.send('[disconnect]'.encode(self.ENCODING))

    def ProcessMessage(self, msgStr, sock):
        headerEnd = msgStr.index(']')
        headerStr = msgStr[0:headerEnd + 1]
        msgContent = msgStr[headerEnd + 1:]

        if headerStr == "[ACK]":
            sock.close()
            return True

        if headerStr == "[DENY]":
            sock.close()
            return False

        if headerStr == "[connect]":
            self.ClientConnection(sock)

        if headerStr == "[changedX]":
            [replicaId, xValue] = msgContent.split('-|-')
            self.changesHistory.append({"replica": replicaId, "x": xValue})
            self.x = xValue

        if headerStr == "[changePrimary]":
            [former, new] = msgContent.split('-|-')
            if self.primaryCopyHolderId == former or 0:
                self.SetPrimaryCopyHolder(new)
                self.Confirm(sock)
            else:
                self.Deny(sock)

        if headerStr == "[getPrimary]":
            if self.primaryCopyHolderId == self.myId and not self.connectedToClient:
                # Impede que outra réplica peça a chave primária e confirma que o solicitante pode pegá-la
                self.SetPrimaryCopyHolder(0)
                self.Confirm(sock)
            else:
                # Nega-se a passar a chave primária
                self.Deny(sock)

    # Processa a nova conexão
    def Processing(self, clientSock, addr):
        msg = clientSock.recv(8192)

        if not msg:
            clientSock.close()
            return

        msgStr = str(msg, encoding=self.ENCODING)
        self.ProcessMessage(msgStr, clientSock)
        return

    # Informa outras réplicas para salvarem as mudanças em X
    def saveChanges(self):
        for i in range(1, 5):
            if i != self.myId:
                replicaSock = self.ConnectToReplica(i)
                msgStr = "[changedX]%s-|-%s" % (self.myId, self.x)
                replicaSock.send(msgStr.encode(self.ENCODING))
                replicaSock.close()

    def updateReplicasPrimary(self, former, new):
        counter = 0
        # Informa as outras réplicas de que devem atualizar quem possui a chavé primária
        for i in range(1, 5):
            if i != self.myId:
                replicaSock = self.ConnectToReplica(i)
                msgStr = "[changePrimary]%s-|-%s" % (former, new)
                replicaSock.send(msgStr.encode(self.ENCODING))
                reply = replicaSock.recv(2048)
                replyStr = str(reply, encoding=ENCODING)
                if self.ProcessMessage(replyStr, replicaSock):
                    counter += 1
        return counter == 3

    # Se definie como novo dono da chave primária e informa outras réplicas
    def isNewPrimaryHolder(self):
        formerPrimary = self.primaryCopyHolderId
        self.SetPrimaryCopyHolder(self.myId)
        success = self.updateReplicasPrimary(formerPrimary, self.primaryCopyHolderId)
        # Se não tiver a confirmação de que todas as réplicas fizeram a atualização
        # desfaz a mudança de propriedade da chave primária
        if not success:
            self.updateReplicasPrimary(self.primaryCopyHolderId, formerPrimary)

    def Altera_X(self, mySock):
        # Pega a chave primária para a réplica
        while not self.isPrimaryHolder():
            primarySock = self.ConnectToReplica(self.primaryCopyHolderId)
            msgStr = "[getPrimary]"
            primarySock.send(msgStr.encode(self.ENCODING))
            reply = primarySock.recv(2048)
            replyStr = str(reply, encoding=self.ENCODING)
            if self.ProcessMessage(replyStr, primarySock):
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
        self.StartServer()
        self.log("### %s ESPERANDO POR CONEXÕES ###" %(self.myId))

        while True:
            leitura, escrita, excecao = select.select(self.ENTRADAS, [], [])  # listas do select

            # percorre cada objeto de leitura (conexão socket, entrada de teclado)
            for leitura_input in leitura:
                # significa que a leitura recebeu pedido de conexão
                if leitura_input == self.sock:
                    clientSock, endr = self.NewClient(self.sock)

                    # Cria e inicia nova thread para atender o cliente
                    newClientThread = threading.Thread(target=self.Processing, args=(clientSock, endr))
                    newClientThread.start()

    # Guarda uma referência do método para ser chamado logo no init (instanciação) da classe
    __startReplica = StartReplica


if __name__ == "__main__":
    main()
