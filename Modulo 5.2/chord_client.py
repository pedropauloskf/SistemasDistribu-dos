### lado ativo (client) ###
### CHORD RING ###

import socket
import sys
import uuid
from random import randint

import select

'''
Aplicação cliente: A aplicação cliente deverá permitir ao usuário realizar inserções de
pares chave/valor e consultas às chaves, indicando sempre um nó de origem. Os resultados
das consultas deverão exibir o valor da chave procurada e o nó onde ela foi
encontrada. As inserções e consultas deverão ser encaminhadas diretamente para o nó de
origem (SEM PASSAR pelo programa principal).
'''

HOST = 'localhost'
PORT = 5000
ENCODING = "UTF-8"
NODE_NUMBER = 0
CLIENT_ID = uuid.uuid4()

isActive = True

sock = socket.socket()
sock.connect((HOST, PORT))
sock.settimeout(2)


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


# Encerra a conexão com o servidor
def CloseConnection():
    print("Finalizando conexão")
    sock.close()
    sys.exit()


# Envio para o servidor #TODO garantir que tudo foi enviado
def Send(targetSocket, message):
    targetSocket.send(message.encode(ENCODING))
    return


# Recebimento do servidor
def QuickReceive(targetSocket, size):
    try:
        msgRecv = targetSocket.recv(size)
        msgStr = str(msgRecv, encoding=ENCODING)
        return msgStr
    except:
        return


# Envia e aguarda o recebimento
def SendAndReceive(targetSock, msg, size):
    Send(targetSock, msg)
    res = QuickReceive(targetSock, size)
    return res


# Verfica se algo relevante foi digitado
def ignoreInput(inputMsg):
    listToIgnore = [" ", "\\n", ""]
    return inputMsg in listToIgnore


# Imprime a lista de comandos para o usuário
def CommandList():
    print("Para ter acesso à lista de comandos, digite \"--help\":")
    print("--insert: Insere o par chave/valor na tabela")
    print("--search: retorna o valor referente a uma chave")
    print("--stop: Encerra o cliente")


# Verifica se o cliente digitou algum comando
def ChooseAction(inputFromClient):
    global isActive, NODE_NUMBER, CLIENT_ID

    if inputFromClient == "--stop":
        isActive = False

    if inputFromClient == "--help":
        CommandList()

    elif inputFromClient == "--insert":
        nodeToRequest = randint(0, NODE_NUMBER-1)
        key = input('Chave: ')
        value = input('Valor: ')
        insere(nodeToRequest, key, value)

    elif inputFromClient == "--search":
        nodeToRequest = randint(0, NODE_NUMBER-1)
        key = input('Chave: ')
        port = 5000 + NODE_NUMBER + randint(1, 10000)
        busca(port, nodeToRequest, key)

    else:
        print('Comando inválido. Se quiser a lista de comandos, digite --help')


# Função para solicitar o endereço do nó desejado
def getNodeAddr(noOrigem):
    global sock
    msgStr = SendAndReceive(sock, packMsg('getAddr', str(noOrigem)), 1024)
    header, port = unpackMsg(msgStr)
    if header == 'Addr':
        return int(port)


# Função de conecção com um nó para poder fazer uma requisição
def sendToNode(noOrigem, msg):
    port = getNodeAddr(noOrigem)
    nodeSock = socket.socket()
    nodeSock.connect((HOST, port))
    nodeSock.settimeout(2)

    Send(nodeSock, msg)
    nodeSock.close()
    return


# Função de inserção de um par chave/valor no Chord
def insere(noOrigem, chave, valor):
    msg = packMsg('insert', '%s-|-%s' % (chave, valor))
    sendToNode(noOrigem, msg)
    return


def awaitResponse(port):
    awaitSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    awaitSock.bind((HOST, port))
    awaitSock.listen(1)  # espera por até 2^n conexões
    awaitSock.setblocking(False)  # torna o socket não bloqueante na espera por conexões
    return awaitSock, port


# Função de busca de uma chave no Chord
def busca(idBusca, noOrigem, chave):
    clientSock, clientPort = awaitResponse(idBusca)
    print("Client port: " + str(clientPort))
    req = packMsg('lookup', '%s-|-%s' % (str(clientPort), chave))
    sendToNode(noOrigem, req)

    leitura, escrita, excecao = select.select([clientSock], [], [])
    for leitura_input in leitura:
        # significa que a leitura recebeu pedido de conexão
        if leitura_input == clientSock:
            newSocket, endereco = sock.accept()
            msg = newSocket.recv(8192)
            msgStr = msg.decode(ENCODING)
            header, val = unpackMsg(msgStr)

            if header == 'success':
                print("{%s: %s}" % (chave, val))
            else:
                print("Chave não encontrada")
    return


# Função main que inicializa as Threads
def main():
    global isActive, NODE_NUMBER
    print("### CLIENT ###")
    CommandList()

    # Solicitação do número N para definir o total de nós
    msgStr = SendAndReceive(sock, packMsg('startClient', ''), 1024)
    print("msg: " + msgStr)
    header, num = unpackMsg(msgStr)
    if header == 'N':
        NODE_NUMBER = int(num)

    while isActive:
        command = input('O que deseja fazer? ')
        if ignoreInput(command):
            print("Comando inválido. Tente Novamente.")
            continue
        ChooseAction(command)

    print("Encerrando cliente.")
    CloseConnection()


main()
