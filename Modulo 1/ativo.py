import socket

HOST = 'localhost'
PORT = 3737
CLOSE_CONNECTION = 'qE2DJ3bNTyXk3w'

sock = socket.socket()

sock.connect((HOST, PORT))

while True:
    strMsg = input("Digite sua mensagem: \n")
    sock.send(strMsg.encode())

    res = sock.recv(1024)
    print(str(res, encoding='utf-8'))

    stop = False
    while not stop:
        ans = input("Deseja enviar uma nova mensagem? (S/N)")
        if ans == 'S':
            break
        elif ans == 'N':
            sock.send(CLOSE_CONNECTION.encode())
            print("Conexão Fechada")
            stop = True

    if stop:
        break

sock.close()
