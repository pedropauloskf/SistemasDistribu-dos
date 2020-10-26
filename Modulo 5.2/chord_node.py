### nó (server) ###
### CHORD RING ###

"""
Processo do nó que armazenará os pares de {chave: valor} em uma tabela hash
"""

import socket
import threading
from hashlib import sha1

import select

HOST = ''
ENCODING = "UTF-8"

NODE_ID = -1
NODENUMBER = 0
HASH_TABLE = {}    # armazena os pares chave/valor do nó
FINGER_TABLE = []  # armazena o nó mais próximo a determinada distância


def StartNode(port):
    global NODENUMBER
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, port))
    sock.listen(NODENUMBER)  # espera por até 2^n conexões
    sock.setblocking(False)  # torna o socket não bloqueante na espera por conexões

    return sock


def main(nodeId, port):
    global NODE_ID
    NODE_ID = nodeId
    sock = StartNode(port)  # pega o socket do servidor
    print("### Node %s ###" % str(NODE_ID))


main()
