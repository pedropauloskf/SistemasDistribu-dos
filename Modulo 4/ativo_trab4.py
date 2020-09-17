### lado ativo (client) ###
### BATE PAPO DISTRIBUÍDO ###
import socket, json, sys

HOST = 'localhost'
PORTA = 5001
ENCODING = "UTF-8"

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
    print(msgStr)
    return msgStr


def CommandList():
    print("Para ter acesso à lista de comandos, digite \"--help\":")
    print("--listar : Lista as conexões disponíveis para chat")
    print("--trocar : Troca o atual destinatário")
    print("stop : Encerra o cliente")

# Verifica se o cliente digitou algum comando ou mensagem a enviar
def ChooseAction(inputFromClient):
    if inputFromClient == "stop":
        CloseConnection()
    if inputFromClient == "":
        print("Nada foi digitado")
        return
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
        #okMsg = sock.recv(1024)
        okMsg = QuickReceiveAndPrint(sock,1024)
        if okMsg == "ok":
            print("Conversando agora com: %s" %changeTo)
        else:
            print("Conexão não localizada ")

    
print("### CLIENT ###")
CommandList()


def main():
    while True:    
        toSend = input()        
        ChooseAction(toSend)
        
        #msgRecv = sock.recv(8192)
        #print(str(msgRecv, encoding=ENCODING))

        '''resultDicts = BinaryToDict(msg)

        for eachDictionary in resultDicts:
            print("\"" + eachDictionary + "\": " + str(resultDicts[eachDictionary]))'''

main()