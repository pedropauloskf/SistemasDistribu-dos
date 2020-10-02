### lado passivo (server) ###
### BATE PAPO DISTRIBUÍDO ###
import socket, select, re, json, sys, threading

HOST = ''
PORTA = 5001
ENCODING = "UTF-8"

ENTRADAS = [sys.stdin] # define entrada padrão
CONEXOES = {} # armazena historico de conexoes
ID_ENDERECO = {} # associa um id único a um endereço (conexão de cliente ip + porta)


# Inicia o servidor e adiciona o socket do servidor nas entradas
def StartServer():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORTA))
    sock.listen(5)  # espera por até 5 conexões
    sock.setblocking(False)  # torna o socket não bloqueante na espera por conexões
    ENTRADAS.append(sock)  # coloca o socket principal na lista de entradas de interesse
    return sock


# Converte dicionário para binário
def DictToBinary(the_dict):
    str = json.dumps(the_dict)
    return str.encode(ENCODING)


# gerencia o recebimento de conexões de clientes, recebe o sock do server
def NewClient(sock):
    newSocket, endereco = sock.accept()
    print('Conectado com: ' + str(endereco))

    CONEXOES[newSocket] = endereco # registra a nova conexão no dicionário de conexões
    if len(ID_ENDERECO) == 0:
        ID_ENDERECO[1] = endereco
    else:
        indice = max(ID_ENDERECO, key=ID_ENDERECO.get)+1
        ID_ENDERECO[max(ID_ENDERECO, key=ID_ENDERECO.get)+1] = endereco
    
    return newSocket, endereco


# Recebe algum comando vindo do cliente
def CommandList(clientSock, msgStr):
    if msgStr == "--listar":
        clientSock.send(str(ID_ENDERECO).encode(ENCODING))
        return
    if msgStr == "--trocar":
        clientSock.send(str(ID_ENDERECO).encode(ENCODING))
        addressIdStr = clientSock.recv(1024)

        try:
            addressIdInt = int(addressIdStr)
        except:
            print("Id do destinatário não é um número")
            clientSock.send("Id do destinatário não é um número".encode())
            return 0

        if addressIdInt not in ID_ENDERECO:
            clientSock.send(("Conexão não encontrada [%s]" % (addressIdInt)).encode(ENCODING))
        else:
            try:
                if CONEXOES[clientSock] ==  ID_ENDERECO[addressIdInt]:
                    clientSock.send("\nUsuário tentando conversar consigo mesmo".encode(ENCODING))
                    return 0
            except:
                clientSock.send(b"not ok")
                return 0

            clientSock.send(b"ok")
            return addressIdInt


# Processa as requisições do cliente
def Processing(clientSock, address):
    dictionaryFull = {}
    while True:
        msg = clientSock.recv(8192)

        if not msg:
            print(str(address) + '-> encerrou')
            del CONEXOES[clientSock]
            del ID_ENDERECO[list(ID_ENDERECO.keys())[list(ID_ENDERECO.values()).index(address)]]
            clientSock.close()
            return

        msgStr = (str(msg, encoding=ENCODING)) 

        # Verifica o comando solicitado e recebe o ID da conexão que se deseja fazer, 0 se for um ID inválido ou None caso seja o comando de listar conexões
        commandResponse = CommandList(clientSock, msgStr)

        try:
            if commandResponse != None:
                if commandResponse != 0:
                    print("Nova conexão entre clientes solicitada. Socket remetente: {%s}, Socket destino: {%s}" %(str(address), str(ID_ENDERECO[commandResponse])))
                    clientSock.send(b"yes") # Remetente espera uma flag "yes" para saber se há mensagens na fila
                    clientSock.send() # TODO Envia mensagens na fila para o remetente
                    clientSock.send() # TODO Envia a mensagem para o destinatário
                else:
                    print("id de destinatário recebido de { {%s} } não é um número válido" %(str(address)))
                    clientSock.send(b"notOk") # Informa ao cliente que não há mensagens na fila e algo está errado
                    clientSock.send(str("id de destinatário recebido não é um número válido"))
            else:
                print("Socket {%s} solicitou listagem de conexões ativas" %(str(address)))
        except:
            print("deu ruim")
            continue


def main():
    clientes = []  # armazena as threads de cada client para dar join
    sock = StartServer()  # pega o socket do servidor
    print("### SERVER - ESPERANDO POR CONEXÕES ###")

    while True:
        leitura, escrita, excecao = select.select(ENTRADAS, [], [])  # listas do select

        for leitura_input in leitura:  # percorre cada objeto de leitura (conexão socket, entrada de teclado)
            if leitura_input == sock:  # significa que a leitura recebeu pedido de conexão
                clientSock, endr = NewClient(sock)
                
                # cria e inicia nova thread para atender o cliente
                newClientThread = threading.Thread(target=Processing, args=(clientSock, endr))
                newClientThread.start()
                clientes.append(newClientThread)  # armazena a referencia da thread para usar com join()

            elif leitura_input == sys.stdin:  # entrada padrão, teclado
                cmd = input()
                if cmd == "--stop":  # solicitação para finalizar o servidor
                    for c in clientes:
                        print("Ainda há clientes com conexões ativas")
                        c.join()  # aguarda todas as threads terminarem, onde a magia do join acontece
                    sock.close()
                    sys.exit()
                elif cmd == "--hist":  # mostra histórico de conexões do server
                    print(str(CONEXOES.values()))


main()
