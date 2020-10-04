### lado passivo (server) ###
### BATE PAPO DISTRIBUÍDO ###
import json
import select
import socket
import sys
import threading

HOST = ''
PORT = 5000
ENCODING = "UTF-8"

ENTRADAS = [sys.stdin]  # define entrada padrão
CONEXOES = {}  # armazena historico de conexoes
ID_ENDERECO = {}  # associa um id único a um endereço (conexão de cliente ip + porta)


# Inicia o servidor e adiciona o socket do servidor nas entradas
def StartServer():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen(5)  # espera por até 5 conexões
    sock.setblocking(False)  # torna o socket não bloqueante na espera por conexões
    ENTRADAS.append(sock)  # coloca o socket principal na lista de entradas de interesse
    return sock


# Converte dicionário para binário
def DictToBinary(the_dict):
    txt = json.dumps(the_dict)
    return txt.encode(ENCODING)


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

def getSocketbyID(clientId):
    address = ID_ENDERECO[int(clientId)]  # Pega o endereço do destinatário
    return CONEXOES[address]  # Recupera o socket do destinatário


# Recebe algum comando vindo do cliente
def CommandList(clientSock, address, headerStr):
    if headerStr == "--listar":
        msg = packMsg('--listar', str(ID_ENDERECO)).encode(ENCODING)
        clientSock.send(msg)
        return

    if headerStr == "--trocar":
        msg = packMsg('--trocar', str(ID_ENDERECO)).encode(ENCODING)
        clientSock.send(msg)
        addressIdStr = clientSock.recv(1024)
        try:
            addressIdInt = int(addressIdStr)
        except:
            print("Id do destinatário não é um número")
            msg = packMsg('--negar', "Id do destinatário não é um número").encode(ENCODING)
            clientSock.send(msg)
            return 0

        if addressIdInt not in ID_ENDERECO:
            msg = packMsg('--negar', "Conexão não encontrada [%s]" % addressIdInt).encode(ENCODING)
            clientSock.send(msg)
            return 0
        else:
            try:
                if address == ID_ENDERECO[addressIdInt]:
                    msg = packMsg('--negar', "Usuário tentando conversar consigo mesmo").encode(ENCODING)
                    clientSock.send(msg)
                    return 0
            except:
                msg = packMsg('--negar',
                              "Ocorreu um erro e não foi possível estabelecer a conexão").encode(ENCODING)
                clientSock.send(msg)
                return 0

            conf = packMsg('--conexao', str(address)).encode(ENCODING)
            targetSock = getSocketbyID(addressIdInt)
            targetSock.send(conf)
            res = clientSock.recv(1024)
            headerRes, headerMsg = unpackMsg(str(res, encoding=ENCODING))

            if headerRes == '--aceitar':
                msg = packMsg('--confirmar', str(addressIdInt)).encode(ENCODING)
                clientSock.send(msg)
                return addressIdInt

            elif headerRes == '--negar':
                msg = packMsg('--negar', '').encode(ENCODING)
                clientSock(msg)
                return -1


# Verifica se a mensagem é um comando ou uma mensagem para outro cliente
def checkIfCommand(msgStr):
    try:
        if msgStr.index('--') == 0:
            return True
    except:
        pass
    return False


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
        headerStr, msgContent = unpackMsg(msgStr)

        # Verifica se a mensagem é um comando do cliente
        if checkIfCommand(headerStr):
            # Verifica o comando solicitado e recebe o ID da conexão que se deseja fazer,
            # 0 se for um ID inválido ou None caso seja o comando de listar conexões
            commandResponseId = CommandList(clientSock, address, headerStr)
            try:
                if commandResponseId is not None:
                    if commandResponseId != 0:
                        print(commandResponseId)
                        print(ID_ENDERECO[commandResponseId])
                        print(
                            "Nova conexão entre clientes solicitada. Socket remetente: {%s}, "
                            "Socket destino: {%s}"
                            % (str(address), str(ID_ENDERECO[commandResponseId]))
                        )
                    else:
                        print(
                            "{%s} solicitou nova conexão, porém id de destinatário recebido "
                            "não é um número válido"
                            % (str(address))
                        )
                else:
                    print("Socket {%s} solicitou listagem de conexões ativas" % (str(address)))
            except:
                print("Problemas ao executar o comando '%s' solicitado por {%s}"
                      % (headerStr, str(address)))
                continue
        else:
            try:
                targetAdd = ID_ENDERECO[int(headerStr)]  # Pega o endereço do destinatário
                targetSock = getSocketbyID(int(headerStr))
                targetSock.send(msgStr.encode(ENCODING))
                print('Encaminhando mensagem de %s para %s' % (str(address), str(targetAdd)))
            except:
                print('Erro ao encaminhar mensagem de %s' % (str(address)))


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
