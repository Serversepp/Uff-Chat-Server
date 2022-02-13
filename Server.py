import socket
import ssl
import threading

import RSA


class Connection_Handler():
    def __init__(self,socket):
        self.socket = socket

    def waitforclient(self):
        self.socket.listen(0)
        return self.socket.accept()

    def getclientnick(self, Client):
        #Client.send("nick".encode('UTF-8'))
        return Client.recv(1024)
        #TODO check if nick already in use

class Server:
    def __init__(self,port,ip):
        self.running = False
        #TODO add funktion checking if parameters are right and key / cert are in the key folder
        self.ip = ip
        self.port = port
        if "." in self.ip:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        #self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Address Reuse enable
        # Enable TLS wrapper
        #self.socket = ssl.wrap_socket(self.socket, server_side=True, keyfile=".\\Key\\key.pem"
        #                                      , certfile=".\\Key\\key.pem")


    def runserver(self):
        self.clients = {}
        self.loginfailes = []
        self.blacklist = []
        self.clientthreads = []

        #TODO read config file
        self.running = True
        self.socket.bind((self.ip, self.port))  # bind uses Touple as parameter
        self.Connection_Handler = Connection_Handler(self.socket)


        while self.running:
            new_client, new_address = self.Connection_Handler.waitforclient() # Waits until new client connects returns client and address
            #TODO may move to new thread
            try:
                new_nickname = self.Connection_Handler.getclientnick(new_client).decode('utf-8').rstrip('\n')
                self.clients[new_client] = [new_nickname, new_address]  # May change for privacy reasons (IP)
                self.brodcast(f"new user {new_nickname} has connected\n".encode('utf-8'))
                new_client.send("hello, welcome to Server\n".encode('utf-8'))  # Welcome message

                self.clientthreads.append(threading.Thread(target=self.clienthandler, args=(new_client,)))
                self.clientthreads[-1].start()  # Start newest thread
            except :
                print("Autohentication ERROR")

    def clienthandler(self, client):
        while True:
            try:
                new_message = client.recv(1024)
                self.brodcast(f"{self.clients.get(client)[0]} : {new_message.decode('utf-8')} \n".encode("utf-8"))
            except :
                self.clients.pop(client)
                break

    def brodcast(self,message):
        for client in self.clients:
            print("NEUE NACHRICHT", message)
            client.send(message)





