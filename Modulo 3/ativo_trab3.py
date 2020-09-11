### lado ativo (client) ###
import socket
import json

HOST = 'localhost'
PORTA = 5001
ENCODING = "UTF-8"

sock = socket.socket()

sock.connect((HOST, PORTA))


def close_connection():
    print("Finalizando conexão")
    sock.close()


def binary_to_dict(the_binary):
    result = json.loads(the_binary.decode(ENCODING))
    return result


print("### CLIENT ###")
while True:
    toSend = input("Nome(s) do(s) arquivo(s) separado(s) por espaço: ")
    if toSend == "stop":
        sock.close()
        break;
    sock.send(toSend.encode(ENCODING))

    msg = sock.recv(8192)

    resultDicts = binary_to_dict(msg)

    for eachDictionary in resultDicts:
        print("\"" + eachDictionary + "\": " + str(resultDicts[eachDictionary]))
