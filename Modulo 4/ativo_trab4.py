### lado ativo (client) ###
### BATE PAPO DISTRIBUÍDO ###
import socket, json, sys

HOST = 'localhost'
PORTA = 5001
ENCODING = "UTF-8"

isOnchat = False
receiverID = -1

sock = socket.socket()
sock.connect((HOST, PORTA))

def CloseConnection():
    print("Finalizando conexão")
    sock.close()
    sys.exit()

# Converte de Binário para Dicionário
def BinaryToDict(the_binary):
    result = json.loads(the_binary.decode(ENCODING))
    return result

def QuickSend(socket, message):
    socket.send(message.encode(ENCODING))

def QuickReceive(socket, size):
    msgRecv = socket.recv(size)
    msgStr = str(msgRecv, encoding=ENCODING)
    return msgStr

def QuickReceiveAndPrint(socket, size):
    msgStr = QuickReceive(socket,size)
    print("\n"+msgStr)
    return msgStr

def CommandList():
    print("Para ter acesso à lista de comandos, digite \"--help\":")
    print("--listar : Lista as conexões disponíveis para chat")
    print("--trocar : Troca o atual destinatário")
    print("--stop : Encerra o cliente")

# Envia e recebe mensagem com prefixo do destinatário
# TODO send e recv para ver se tem mesagens para serem recebidas
def HandleP2PMessage(clientSocket, messageToChat):
    global isOnchat,receiverID
    messagePrefix = "[[" + receiverID + "]]"
    QuickSend(clientSocket, messagePrefix + messageToChat)
    thereIs = QuickReceive(clientSocket, 512)      # Verifica se há mensagens na fila
    if thereIs == "notOk":
        QuickReceiveAndPrint(clientSocket, 1024)

    while thereIs == "yes": # Enquanto houver mensagens na fila, recebe do server
        QuickReceiveAndPrint(clientSocket, 8192)
        thereIs = QuickReceive(clientSocket, 512)

# Verifica se o cliente digitou algum comando
def ChooseAction(inputFromClient):
    listToIgnore = [" ", "\\n", ""]

    if inputFromClient == "--stop":
        CloseConnection()

    if inputFromClient in listToIgnore:
        print("Nada foi digitado")

    if inputFromClient == "--help":
        CommandList()

    if inputFromClient == "--listar":
        QuickSend(sock,inputFromClient)
        QuickReceiveAndPrint(sock,8192)

    if inputFromClient == "--trocar":
        QuickSend(sock,inputFromClient)
        QuickReceiveAndPrint(sock,8192)
        changeTo = input("Digite o número referente a conexão que você deseja conversar: ")
        QuickSend(sock,changeTo)
        okMsg = QuickReceive(sock,1024)
        if okMsg == "ok":
            global receiverID
            receiverID = changeTo
            global isOnchat
            isOnchat = True
            print("OK\n")
        else:
            print(okMsg)

print("### CLIENT ###")
CommandList()

#def main():

while True:
    if receiverID == -1:
        toSend = input("Conversando com {Ninguém}, escolha alguém com \"--trocar\" \n ")
    else:    
        toSend = input("Conversando com {%s}: " %receiverID)
        HandleP2PMessage(sock,toSend)
    ChooseAction(toSend)
    
    #msgRecv = sock.recv(8192)
    #print(str(msgRecv, encoding=ENCODING))

    '''resultDicts = BinaryToDict(msg)

    for eachDictionary in resultDicts:
        print("\"" + eachDictionary + "\": " + str(resultDicts[eachDictionary]))'''

#main()


