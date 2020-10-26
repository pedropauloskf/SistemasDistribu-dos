### lado ativo (client) ###
### CHORD RING ###

import json, socket, sys, threading

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

sock = socket.socket()
sock.connect((HOST, PORT))
sock.settimeout(2)


# Encerra a conexão com o servidor
def CloseConnection():
    print("Finalizando conexão")
    sock.close()
    sys.exit()


# Envio para o servidor #TODO garantir que tudo foi enviado
def Send(socket, message):
    # socket.send(message.encode(ENCODING))
    return


# Recebimento do servidor
def QuickReceive(socket, size):
    try:
        msgRecv = socket.recv(size)
        msgStr = str(msgRecv, encoding=ENCODING)
        return msgStr
    except:
        return


# Imprime a lista de comandos para o usuário
def CommandList():
    print("Para ter acesso à lista de comandos, digite \"--help\":")
    print("--listar : Lista as conexões disponíveis para chat")
    print("--trocar : Troca o atual destinatário")
    print("--stop : Encerra o cliente")


# Verfica se algo relevante foi digitado
def ignoreInput(inputMsg):
    listToIgnore = [" ", "\\n", ""]
    return inputMsg not in listToIgnore


# Verifica se o cliente digitou algum comando
def ChooseAction(inputFromClient):
    global isActive, isAwaitingServer

    if inputFromClient == "--stop":
        isActive = False

    elif inputFromClient == "--help":
        CommandList()

    elif inputFromClient in ["--trocar", "--listar"]:
        QuickSend(sock, packMsg(inputFromClient, 'action'))
        isAwaitingServer = True

    else:
        print('Comando inválido. Se quiser a lista de comandos, digite --help')


def insere(noOrigem, chave, valor):
    return


def busca(idBusca, noOrigem, chave):
    return


# Função main que inicializa as Threads
def main():
    print("### CLIENT ###")
    CommandList()

    receive = threading.Thread(target=receiveMsgs)
    receive.start()

    while isActive:
        continue

    print("Encerrando cliente.")
    receive.join()
    send.join()
    CloseConnection()


main()
