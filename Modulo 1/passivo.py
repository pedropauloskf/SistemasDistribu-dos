import socket

HOST = ''
PORT = 3737
CLOSE_CONNECTION = 'qE2DJ3bNTyXk3w'

sock = socket.socket()
sock.bind((HOST, PORT))

sock.listen(1)
print("Aguardando conexões")

newSock, endereco = sock.accept()
print('Conectado com: ', endereco)

while True:
    bMsg = newSock.recv(1024)
    strMsg = str(bMsg, encoding='utf-8')
    if strMsg == CLOSE_CONNECTION:
        print('Fechando conexão')
        break
    else:
        print(strMsg)
    newSock.send(bMsg)

newSock.close()

sock.close()