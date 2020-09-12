### lado passivo (server) ###
import socket, select, re, json, sys, threading

HOST = ''
PORTA = 5001

ENCODING = "UTF-8"

# define entrada padrão
ENTRADAS = [sys.stdin]

# armazena historico de conexoes
CONEXOES = {}


# Inicia o servidor e adiciona o socket do servidor nas entradas
def StartServer():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORTA))
    sock.listen(5)  # espera por até 5 conexões
    sock.setblocking(False)  # torna o socket não bloqueante na espera por conexões
    ENTRADAS.append(sock)  # coloca o socket principal na lista de entradas de interesse
    return sock


# Lê arquivo
def ReadFile(file_path):
    try:
        file = open(file_path, "r")
        # print(file.read())
        return file

    except FileNotFoundError:
        print("Arquivo não encontrado: [%s]" % (file_path))
        return None
    except:
        print("Algo errado com o arquivo")
        return None


# Converte dicionário para binário
def DictToBinary(the_dict):
    str = json.dumps(the_dict)
    return str.encode(ENCODING)


# retorna um novo dicionário com o sort de top10
def SortDict(the_dict):
    sortedDict = dict()

    for i in range(10):
        max_key = max(the_dict, key=the_dict.get)
        sortedDict[max_key] = the_dict.pop(max_key, None)

    return sortedDict


# Conta as palavras e adiciona ao dicionário
def CountWords(words, dictionaryFull):
    # print(words)
    for word in words:
        key = word.lower()
        if key in dictionaryFull:
            dictionaryFull[key] += 1
        else:
            dictionaryFull[key] = 1


# Le arquivos por linha, faz split, chama func CountWords
def ReadAndSplit(file, dictionaryFull):
    file = ReadFile(file)
    if file:
        for lines in file:
            words = re.findall(r"[\w']+", lines)
            CountWords(words, dictionaryFull)
        return True
    else:
        return False


# Processa as requisições do cliente
def Processing(clientSock, address):
    dictionaryFull = {}
    while True:
        msg = clientSock.recv(8192)
        if not msg:
            print(str(address) + '-> encerrou')
            clientSock.close()
            return

        # pega os resultados finais em um único dicionário
        resultDict = dict()

        # lista de nomes dos arquivos recebido pelo cliente
        fileList = (str(msg, encoding=ENCODING)).split(' ')

        for file in fileList:
            # Processa as palavras, inserindo no dicionário final
            if ReadAndSplit(file, dictionaryFull):
                resultDict[file] = SortDict(dictionaryFull)
                dictionaryFull = {}
            else:  # adiciona ao dicionário de resultado final a mensagem com erro
                if file == " " or file == "\\n": continue
                msgToSend = "Houve um problema ao tentar processar [%s]" % file
                resultDict[file] = msgToSend

        # Enviar um único dicionário, com os erros ou êxitos
        clientSock.send(DictToBinary(resultDict))


# gerencia o recebimento de conexões de clientes, recebe o sock do server
def NewClient(sock):
    newSocket, endereco = sock.accept()
    print('Conectado com: ' + str(endereco))

    # registra a nova conexão no dicionário de conexões
    CONEXOES[newSocket] = endereco

    return newSocket, endereco


def main():
    clientes = []  # armazena as threads para cada client para dar join
    sock = StartServer()  # pega o socket do servidor
    print("### SERVER - ESPERANDO POR CONEXÕES ###")

    while True:
        leitura, escrita, excecao = select.select(ENTRADAS, [], [])  # listas do select

        for leitura_input in leitura:  # percorre cada objeto de leitura (conexão socket, entrada de teclado)
            if leitura_input == sock:  # significa que a leitura recebeu pedido de conexão
                clientSock, endr = NewClient(sock)

                # cria e inicia nova thread para atender o cliente
                newClientThread = threading.Thread(target=Processing, args=(clientSock, endr))
                newClientThread.start()
                clientes.append(newClientThread)  # armazena a referencia da thread para usar com join()

            elif leitura_input == sys.stdin:  # entrada padrão, teclado
                cmd = input()
                if cmd == "fim":  # solicitação para finalizar o servidor
                    for c in clientes:
                        print("Ainda há clientes com conexões ativas")
                        c.join()  # aguarda todas as threads terminarem, onde a magia do join acontece
                    sock.close()
                    sys.exit()
                elif cmd == "hist":  # mostra histórico de conexões do server
                    print(str(CONEXOES.values()))


main()
