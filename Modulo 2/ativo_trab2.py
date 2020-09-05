### lado ativo (client) ###
import socket
import json

HOST = 'localhost'
PORTA = 5001
ENCODING = "UTF-32"


sock = socket.socket()

sock.connect((HOST,PORTA))

def close_connection():
	print("Finalizando conexão")
	sock.close()

def binary_to_dict(the_binary):
    #jsn = ''.join(chr(int(x, 2)) for x in the_binary.split())
    result = json.loads(the_binary.decode(ENCODING))
    return result
    #d = json.loads(jsn.decode('utf-8')) 
    	#json.loads(s.decode('utf-8'))
    #return d

print("### CLIENT ###")
while True:
	envio = input("Nome do arquivo: ")
	if (envio=="stop"):
		sock.close()
		break;
	sock.send(envio.encode(ENCODING))
	
	msg=sock.recv(4096)
	
	binary_to_dict(msg)
	print(str(msg,encoding=ENCODING))