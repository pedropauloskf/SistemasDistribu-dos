### lado ativo (client) ###
### BATE PAPO DISTRIBUÍDO ###
import json
import socket
import sys
import threading

HOST = 'localhost'
PORT = 5000
ENCODING = "UTF-8"

isOnChat = False
receiverID = -1
isActive = True
isAwaitingServer = False

sock = socket.socket()
sock.connect((HOST, PORT))
sock.settimeout(2)


# Encerra a conexão com o servidor
def CloseConnection():
    print("Finalizando conexão")
    sock.close()
    sys.exit()


# Converte de Binário para Dicionário
def BinaryToDict(the_binary):
    result = json.loads(the_binary.decode(ENCODING))
    return result


# Envio para o servidor
def QuickSend(socket, message):
    socket.send(message.encode(ENCODING))


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


# Separa a mensagem recebida do ID de envio
def unpackMsg(msgStr):
    idStart = msgStr.index('[[')
    idEnd = msgStr.index(']]')
    senderId = msgStr[idStart + 2:idEnd]
    msgContent = msgStr[idEnd + 2:]
    return senderId, msgContent


# Adiciona o ID de envio a mensagem ou ação
def packMsg(msgStr, msgType, requesterID=None):
    if msgType == 'action':
        return "[[" + msgStr + "]]"
    elif msgType == 'msg':
        global receiverID
        messagePrefix = "[[" + str(receiverID) + "]]"
        return messagePrefix + msgStr
    elif msgType == 'res':
        messagePrefix = "[[" + msgStr + "]]"
        return messagePrefix + str(requesterID)


# Verfica se algo relevante foi digitado
def ignoreInput(inputMsg):
    listToIgnore = [" ", "\\n", ""]
    return inputMsg not in listToIgnore


# Envia e recebe mensagem com prefixo do destinatário
def HandleP2PMessage2(clientSocket, messageToChat):
    try:
        QuickSend(clientSocket, packMsg(messageToChat, 'msg'))
    except:
        print("Não conseguimos enviar a mensagem: %s" % messageToChat)


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


# Realiza as ações apropriadas de acordo com a resposta a
# uma solicitação enviada ao servidor
def ServerResponse(responseId, msg):
    global receiverID, isOnChat, isAwaitingServer
    # Exibe a lista de clientes conectados
    if responseId == "--listar":
        print(msg + "\n")
        isAwaitingServer = False

    # Exibe a lista de clientes conectados e solicita a qual
    # deseja-se se conectar para solicitar ao servidor
    elif responseId == "--trocar":
        print(msg + "\n")
        changeTo = input("Digite o número referente a conexão que você deseja conversar: ")
        msg = packMsg('--troca', 'res', changeTo)
        receiverID = changeTo
        QuickSend(sock, msg)

    # Confirma que a conexão foi feita e inicializa o chat
    elif responseId == '--confirmar':
        isOnChat = True
        isAwaitingServer = False
        print("OK. Você agora pode conversar com {%s}\n" % receiverID)

    # Exibe a mensagem de negação da conexão
    elif responseId == '--negar':
        receiverID = -1
        isAwaitingServer = False
        print(msg)

    elif responseId == '--conexao':
        isAwaitingServer = True
        while True:
            res = input('{%s} deseja começar uma conversa. Aceitar? (S/N)' % msg)
            slc = int(msg[1:msg.index(':')])
            if res == 'S':
                isOnChat = True
                receiverID = slc
                QuickSend(sock, packMsg('--aceitar', 'res', slc))
                isAwaitingServer = False
                break
            elif res == 'N':
                QuickSend(sock, packMsg('--negar', 'res', slc))
                isAwaitingServer = False
                break
            else:
                print('Entrada inválida.')


# Thread que recebe as mensagens e respostas do servidor
def receiveMsgs():
    global isActive, sock
    while isActive:
        msg = QuickReceive(sock, 8192)
        if msg:
            headerStr, msgContent = unpackMsg(msg)
            if headerStr.find('--') == 0:
                ServerResponse(headerStr, msgContent)
            else:
                print("\nMensagem de {%s}: %s" % (headerStr, msgContent))
    return


# Thread que acompanha os inputs do usuário
def readInputAndSend():
    global isActive, sock, isOnChat, receiverID
    while isActive:
        if isAwaitingServer:
            continue
        elif not isOnChat:
            if receiverID == -1:
                toSend = input("Conversando com {Ninguém}, escolha alguém com \"--trocar\": \n ")
            else:
                continue
        else:
            toSend = input("Conversando com {%s}: " % receiverID)

        if ignoreInput(toSend):
            if toSend.find('--') == 0:
                ChooseAction(toSend)
            else:
                HandleP2PMessage2(sock, toSend)
    return


# Função main que inicializa as Threads
def main():
    print("### CLIENT ###")
    CommandList()

    receive = threading.Thread(target=receiveMsgs)
    receive.start()
    send = threading.Thread(target=readInputAndSend)
    send.start()

    while isActive:
        continue

    print("Encerrando cliente.")
    receive.join()
    send.join()
    CloseConnection()


main()
