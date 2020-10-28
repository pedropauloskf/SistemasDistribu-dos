### lado ativo (client) ###
### CHORD RING ###

import socket
import sys
import uuid
from random import randint

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
        busca(CLIENT_ID, nodeToRequest, key)

    else:
        print('Comando inválido. Se quiser a lista de comandos, digite --help')


def insere(noOrigem, chave, valor):
    return


def busca(idBusca, noOrigem, chave):
    return


# Função main que inicializa as Threads
def main():
    global isActive, NODE_NUMBER
    print("### CLIENT ###")
    CommandList()

    # Solicitação do número N para definir o total de nós
    msgStr = SendAndReceive(sock, '[[startClient]]', 1024)
    header, num = unpackMsg(msgStr)
    if header == 'N':
        NODE_NUMBER = num

    while isActive:
        command = input('O que deseja fazer? ')
        if ignoreInput(command):
            print("Comando inválido. Tente Novamente.")
            continue
        ChooseAction(command)

    print("Encerrando cliente.")
    CloseConnection()


main()
