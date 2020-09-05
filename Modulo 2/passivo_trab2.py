### lado passivo (server) ###
import socket
import re
import json

HOST = ''
PORTA = 5000

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, PORTA))
sock.listen(1)

dictionary = dict()
ENCODING = "UTF-8"


# Lê arquivo
def read_file(file_path):
    try:
        file = open(file_path, "r")
        # print(file.read())
        return file

    except FileNotFoundError:
        print("Arquivo não encontrado: %s" % (file_path))
        return None
    except:
        print("Algo errado com o arquivo")
        return None


# Converte dicionário para binário
def dict_to_binary(the_dict):
    str = json.dumps(the_dict)
    return str.encode(ENCODING)


# retorna um novo dicionário com o sort de top10
def sort_dict(the_dict):
    sortedDict = dict()

    for i in range(10):
        max_key = max(the_dict, key=the_dict.get)
        sortedDict[max_key] = the_dict.pop(max_key, None)

    return sortedDict


# Conta as palavras e adiciona ao dicionário
def count_words(words):
    # print(words)
    for word in words:
        key = word.lower()
        if (key in dictionary):
            dictionary[key] += 1
        else:
            dictionary[key] = 1


# Le arquivos por linha, faz split, adiciona dict
def processing(file):
    file = read_file(file)
    if file:
        for lines in file:
            words = re.findall(r"[\w']+", lines)
            count_words(words)
        return True
    else:
        return False


def separate_files(message_from_client):
    return message_from_client.split(' ')


def new_client():
    newSocket, endereco = sock.accept()
    print('Conectado com: ' + str(endereco))
    return newSocket


print("### SERVER ###")
newSocket = new_client()

while True:
    msg = newSocket.recv(8192)
    if not msg:
        newSocket.close()
        newSocket = new_client()
        continue

    # pega os resultados finais em um único dicionário
    resultDict = dict()

    # lista de nomes dos arquivos
    fileList = separate_files(str(msg, encoding=ENCODING))

    for file in fileList:

        # Processa as palavras, inserindo no dicionário final
        if processing(file):
            resultDict[file] = sort_dict(dictionary)
            dictionary = dict()
        else:
            if file == " ": continue
            msgToSend = "Houve um problema ao tentar processar o %s" % (file)
            resultDict[file] = msgToSend

    # Enviar um único dicionário, com os erros ou êxitos
    newSocket.send(dict_to_binary(resultDict))

sock.close()
