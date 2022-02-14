import socket
import ssl
import threading

import RSA

from Crypto.PublicKey import RSA
from Crypto import Random


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
    def __init__(self,port,ip, conf):

        self.readconf(conf)
        self.running = False
        #TODO add funktion checking if parameters are right and key / cert are in the key folder
        self.ip = ip
        self.port = port
        if "." in self.ip:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Address Reuse enable
        #Enable TLS wrapper
        self.socket = ssl.wrap_socket(self.socket, server_side=True, keyfile=".\\Key\\MyKey.key", certfile=".\\Key\\MyCertificate.crt")

    def readconf(self, conf):
        self.configstring = '11100000'

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

            self.clientthreads.append(threading.Thread(target=self.clienthandler, args=([new_client,new_address],)))
            self.clientthreads[-1].start()  # Start newest thread


    def clienthandler(self, par):
        client = par[0]
        new_address = par[1]
        try:
            ### Config Byte section ###
            client.send(self.configstring.encode("utf-8"))  # sends config byte to server
            ###RSA Section###

            #Passwd Section###

            ###Nickname section####
            new_nickname = self.Connection_Handler.getclientnick(client).decode('utf-8').rstrip('\n')
            self.clients[client] = [new_nickname, new_address]  # May change for privacy reasons (IP)
            self.brodcast(f"new user {new_nickname} has connected\n".encode('utf-8'))
            client.send("hello, welcome to Server\n".encode('utf-8'))  # Welcome message
        except:
            print("Autohentication ERROR")
        while True:
            try:
                new_message = client.recv(1024)
                self.brodcast(f"{self.clients.get(client)[0]} : {new_message.decode('utf-8')} \n".encode("utf-8"))
            except :
                self.clients.pop(client)
                break

    def brodcast(self,message):
        if message: # do not brodcast empty string
            for client in self.clients:
                client.send(message)





