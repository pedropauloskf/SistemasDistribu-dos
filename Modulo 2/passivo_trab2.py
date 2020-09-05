### lado passivo (server) ###
import socket
import re
import json

HOST = ''
PORTA = 5000

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.bind((HOST, PORTA))

sock.listen(1)

novoSock, endereco = sock.accept()
print("### SERVER ###")
print('Conectado com: ' + str(endereco))

dictionary = dict()
ENCODING = "UTF_32"

# Lê arquivo
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
	
# Converte dicionário para binário
def dict_to_binary(the_dict):
	sortedDict = Sort_Dict(the_dict)
	#str = json.dumps(the_dict)
	str = json.dumps(sortedDict)
	return str.encode(ENCODING)

# retorna um novo dicionário com o sort de top10
def Sort_Dict(the_dict):
	sortedDict = dict()
	
	for i in range(10):
		max_key = max(the_dict, key=the_dict.get)
		sortedDict[max_key] = the_dict.pop(max_key,None)

	return sortedDict

# Conta as palavras e adiciona ao dicionário
def Count_Words(words):
	#print(words)
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
		msg = novoSock.recv(8192)
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
