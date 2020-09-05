### lado passivo (server) ###
import socket
import re
import json

HOST = ''
PORTA = 5001

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.bind((HOST, PORTA))

sock.listen(1)

novoSock, endereco = sock.accept()
print("### SERVER ###")
print('Conectado com: ' + str(endereco))

dictionary = dict()
ENCODING = "UTF-32"

def ReadFile(file_path):
	try:
		file = open(file_path,"r")
		#print(file.read())
		return file

	except FileNotFoundError:
		print("Arquivo não encontrado")
	except:
		print("Algo errado com o arquivo")

	return None
	
def dict_to_binary(the_dict):
    str = json.dumps(the_dict)
    #binary = ' '.join(format(ord(letter), 'b') for letter in str)
    #return binary.encode('utf-8')
    return str.encode(ENCODING)

#Conta as palavras e adiciona ao dicionário
def Count_Words(words):
	print(words)
	for word in words:
		key = word.lower()
		if (key in dictionary):
			dictionary[key] +=1
		else:
			dictionary[key] = 1

# Le arquivos por linha, faz split, adiciona dict
def Processamento(arquivo_entrada):
	file = ReadFile(arquivo_entrada)
	if (file):
		for lines in file:
			words = re.findall(r"[\w']+",lines)
			Count_Words(words)
		return True
	else:
		return False
	

while True:
		msg = novoSock.recv(4096)
		if not msg: break
		if (Processamento(str(msg, encoding=ENCODING))):
			novoSock.send(dict_to_binary(dictionary))
			dictionary = dict()
		else:
			novoSock.send(b'Houve um problema ao tentar processar o arquivo')


		#print(str(msg, encoding='utf-8'))
		#novoSock.send(msg)

novoSock.close()
sock.close()
