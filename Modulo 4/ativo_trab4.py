### lado ativo (client) ###
import socket
import json

HOST = 'localhost'
PORTA = 5001
ENCODING = "UTF-8"

sock = socket.socket()

sock.connect((HOST, PORTA))

def CloseConnection():
    print("Finalizando conexão")
    sock.close()


def BinaryToDict(the_binary):
    result = json.loads(the_binary.decode(ENCODING))
    return result

# Cliente se torna server ao decidir se comunicar com alguém
def HandleP2P():
	return


print("### CLIENT ###")
while True:
    toSend = input("Nome(s) do(s) arquivo(s) separado(s) por espaço: ")
    if toSend == "stop":
        CloseConnection()
        break;
    if toSend == "":
    	print("Nada foi digitado")
    	continue
    sock.send(toSend.encode(ENCODING))

    msg = sock.recv(8192)

    resultDicts = BinaryToDict(msg)

    for eachDictionary in resultDicts:
        print("\"" + eachDictionary + "\": " + str(resultDicts[eachDictionary]))
