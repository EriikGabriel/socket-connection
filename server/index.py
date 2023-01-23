import threading
import socket
import shutil
import os
import re

HOST = "127.0.0.1"
PORT = 8585
SIZE = 1024
SUCCESSFUL_SEND_UP_FILE_MESSAGE = "📝 - Arquivo '{}' gravado em disco!"
SUCCESSFUL_RECEIVE_UP_FILE_MESSAGE = "📝 - O arquivo '{}' foi obtido do disco!"
ERROR_RECEIVE_UP_FILE_MESSAGE = "📭 - Nenhum arquivo em disco!"
SUCCESSFUL_CREATE_SERVER_MESSAGE = "💬 - Servidor ('{}', {}) criado e ouvidoria estabelecida"
DISCONNECT_SERVER_MESSAGE = "🔐 - Fechando a conexão..."

clients = []

def main():
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1);

        if server:
            print(SUCCESSFUL_CREATE_SERVER_MESSAGE.format(HOST, PORT))

        server.bind((HOST, PORT))
        server.listen()
        print("🔎 - Esperando por eventos...")
    except:
        return print('❌ - Não foi possível iniciar o servidor!\n')

    while True:
        try:
            client, addr = server.accept()
            print('🌐 - Conectado em:', addr)

            clients.append(client)
            
            thread = threading.Thread(target=messagesTreatment, args=[client, addr])
            thread.start()
        except KeyboardInterrupt:
            clientUploadPath = os.path.join(os.path.abspath(".."), "client", "uploads")
            serverUploadPath =  os.path.join(os.path.abspath(".."), "server", "uploads")

            shutil.rmtree(clientUploadPath, ignore_errors=False, onerror=None)
            shutil.rmtree(serverUploadPath, ignore_errors=False, onerror=None)

            return print("\n" + DISCONNECT_SERVER_MESSAGE)
            

def messagesTreatment(client: socket, addr):
    while True:
        try:
            messageLength = int.from_bytes(client.recv(2), byteorder='big')
            msg = client.recv(messageLength).decode("utf-8");

            if msg == '': continue
            if not msg:
                print("SAIU")

            regex = r"data=(?P<data>.*), type=(?P<type>.*)."
            match = re.search(regex, msg)
            
            data = match.group(1)
            reqType = match.group(2)

            if reqType == "send":
                response = uploadFile(data)
                broadcast(response, client)
            if reqType == "receive":
                response = getFile(data)
                broadcast(response, client)
            if reqType == "exit":
                disconnect(client, addr)
        except:
            deleteClient(client)
            break


def broadcast(msg: str, client: socket):
    for clientItem in clients:
        if clientItem == client:
            try:
                clientItem.send(len(msg).to_bytes(2, byteorder='big'))
                clientItem.send(bytes(msg, "utf-8"))
            except:
                deleteClient(clientItem)


def deleteClient(client: socket):
    clients.remove(client)

def uploadFile(filePath: str):
    uploadPath = os.path.dirname(os.path.realpath(__file__)) + "/uploads"
    originalFilename = filePath.split("/")[-1]

    if not os.path.isdir(uploadPath):
        os.mkdir(uploadPath)
        
    for file in os.scandir(uploadPath):
        os.remove(file.path)
    shutil.copy2(filePath, uploadPath + "/" + originalFilename)

    print(SUCCESSFUL_SEND_UP_FILE_MESSAGE.format(originalFilename))

    return "Arquivo '" + originalFilename + "' gravado em disco!"

def getFile(clientPath: str): 
    clientUploadPath = os.path.join(clientPath, "uploads")
    serverUploadPath = os.path.dirname(os.path.realpath(__file__)) + "/uploads"

    filename = None

    if not os.path.isdir(clientUploadPath):
        os.mkdir(clientUploadPath)
    
    for file in os.scandir(clientUploadPath):
        os.remove(file.path)

    for file in os.scandir(serverUploadPath):
        shutil.copyfile(file.path, os.path.join(clientUploadPath, file.name))
        filename = file.name
    
    if filename:
        print(SUCCESSFUL_RECEIVE_UP_FILE_MESSAGE.format(filename))
        return "O arquivo '" + filename + "' foi obtido do disco!"
    else:
        print(ERROR_RECEIVE_UP_FILE_MESSAGE)
        return "Nenhum arquivo em disco!"

def disconnect(client: socket, addr):
    print('🔴 - Desconectado em:', addr)
    deleteClient(client)
    

main()