import socket, select, sys, threading

connectionsList = {1: 5001, 2: 5002, 3: 5003, 4: 5004}

def main():
    myId = -1
    for ids in range(1,5):
        newReplicaThread = threading.Thread(target=ReplicaNode, args=(ids,) )
        newReplicaThread.start()

    while myId not in range(1,5):
        myId = int(input("\nDigite o numero da réplica a se conectar: \n"))

    #mySock = StartServer(myId)

    #PrintCommandList()

    #while True:
    #    command = input("Digite o comando: ")
    #    Processing(command, mySock)


class ReplicaNode:
    
    HOST = 'localhost'
    ENTRADAS = []#[sys.stdin]  # define entrada padrão
    
    # a classe ao ser instanciada, recebe os parametos
    def __init__(self, myId):
        self.x = 0
        self.myId = myId
        self.primaryCopy = False           #Variavel que diz quem esta com o chapeu para poder alterar X
        self.changesHistory = {}
        self.connectionsList = {1: 5001, 2: 5002, 3: 5003, 4: 5004}
        
        self.__startReplica()


    # Inicia o servidor e adiciona o socket do servidor nas entradas
    def StartServer(self):
        '''global HOST, connectionsList
        global ENTRADAS'''
        print("myId: %s, my port %i" %(self.myId, self.connectionsList[self.myId] ))

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port = int(self.connectionsList[self.myId])
        sock.bind((self.HOST, port ))
        sock.listen(5)  # espera por até 5 conexões
        #sock.setblocking(False)  # torna o socket não bloqueante na espera por conexões
        self.ENTRADAS.append(sock)
        return sock

    def SetPrimaryCopy():
        global primaryCopy
        primaryCopy = True

    # gerencia o recebimento de conexões de clientes, recebe o sock do server
    def NewClient(self,sock):
        newSocket, endereco = sock.accept()
        print('Conectado com: ' + str(endereco))



        return newSocket, endereco

    def PrintCommandList():
        print("--help - lista os comandos")
        print("--valor - valor de x nesta réplica")
        print("--historico - historico do valor de x")
        print("--alterar - altera o valor de x")
        print("--fim - finaliza esta replica")

    def Processing(self, command, mySock):
        if command == "--help":
            PrintCommandList()
        if command == "--valor":
            global x
            print(x)
        if command == "--historico":
            global changesHistory
            print(changesHistory)
        if command == "--alterar":
            Altera_X(mySock)
        if command == "--fim":
            exit()

    #TODO alterar valor de x em todas as replicas e atualizar historico de alterações
    def Altera_X(mySock):
        global myId
        mySock.connect((HOST, 5004 ))
        '''for i in connectionsList:
            if i != myId:
                print("Connecting to id %s, port %i" %(i, connectionsList[i]))
                mySock.connect((HOST, connectionsList[i]))
    '''

    def StartReplica(self):
        mySock = self.StartServer()
        print("### %s - ESPERANDO POR CONEXÕES ###" %(self.myId))
        newSocket, endereco = mySock.accept()
        #self.NewClient(mySock)
        '''while True:
            leitura, escrita, excecao = select.select(self.ENTRADAS, [], [])  # listas do select

            # percorre cada objeto de leitura (conexão socket, entrada de teclado)
            for leitura_input in leitura:
                # significa que a leitura recebeu pedido de conexão
                if leitura_input == mySock:
                    clientSock, endr = self.NewClient(mySock)

                    # cria e inicia nova thread para atender o cliente
                    #newClientThread = threading.Thread(target=Processing, args=(clientSock, endr))
                    #newClientThread.start()
                    
                    elif leitura_input == sys.stdin:  # entrada padrão, teclado
                    #cmd = input()
                    command = input("Digite o comando: ")
                    Processing(command, mySock)'''

    # Guarda uma referência do método para ser chamado log no init (instanciação) da classe
    __startReplica = StartReplica

if __name__ == "__main__":
    main()