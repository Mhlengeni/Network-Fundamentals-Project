##########################################################################
#                                                                        #
# Student Name: Mhlengeni Miya                                           #
# Student Number: 363729                                                 #
#                                                                        #
# ELEN4017 -- Networks Fundamentals                                      #
# Project 2023                                                           #
# Submission Date: 10/05/2023                                            #
#                                                                        #
# Online Multiplayer Reaction Game Using a Sychronization Protocol       #
#                                                                        #
##########################################################################

# server.py

"""Importing modules"""
import socket
import threading
import os
import random
import time

"""Declaring global variables"""
IP = socket.gethostbyname(socket.gethostname())
PORT = 21
ADDR = (IP,PORT)
SIZE = 1024
FORMAT = 'utf-8'

myClients = [] # Stores the client sockets
clientDelayTime = [] # Store the actual connection speed of each client
latency = [] # Stores the delays that should be applied to each client
answers = [] # Store answers from the clients
performanceTimes = [] # Store all the performance times for all the clients
winner = []
READY = 0 # At the beginning, no player has indicated they are ready to play
ANSWER = 0 # Stores the answer of the quiz

def connSpeed(client_time):
        """Calculate the connection speed of each client."""
        conn_time = time.time() - float(client_time)

        return conn_time

"""server class"""
# Creating a FTP Server class with multiple threads capability
class Server (threading.Thread):
    """A server class with basic functionality and some added functionalities."""
    def __init__(self, connection, addr, number1, number2):
        """Initialize Server's attributes."""
        threading.Thread.__init__(self) # Inherit all the methods of the super class
        self.connection = connection
        self.addr = addr
        self.clientDelayTime_ = 0
        self.number1 = number1
        self.number2 = number2
        self.threadAnswer = 0
        self.thread_performance_time = 0
        self.isUserValid = False
        self.loggedIn = False
        self.threadUsername = ""
        self.threadPassword = ""
        self.users = ["mhlengeni"] 
        self.passwords = ["miya1991"] 
        myClients.append(connection)

    def latency(self):
        indexOfMaxLat = clientDelayTime.index(max(clientDelayTime))
        bigLat = clientDelayTime[indexOfMaxLat]

        i = 0

        latency.clear() # Clear the list for it to be updated each time a client joins
        while i < len(clientDelayTime):
            delay = bigLat - clientDelayTime[i]
            print(f"Latency at index {i} = {clientDelayTime[i]}")
            latency.append(delay)
            i = i + 1

        print(latency)

    def sendMessage(self, msg):
        self.connection.send((msg + '\r\n').encode())

    def run(self):
        #Printing the IP and Port to demonstrate a new connection being made
        print(f"[NEW CONNECTION] {self.addr} connected.")

        # Sending welcome message to client
        welcomeMessage = self.welcomeMessage()
        self.sendMessage(welcomeMessage)

        # While loop permitting the exchange between Client Command and Server FTP
        #Protocol response
        sentinel = 0
        while sentinel <= 1:
            # Receiving of client data input determining the command and argument
            data = self.connection.recv(SIZE).decode()
            (f"[SERVER] received : {data}")
            data = data.split(" ")

            cmd = data[0]

            print(f"[SERVER] command received: {cmd}")

            cmd = cmd.rstrip()
            
            if cmd == "HELP":
                message = self.help()
                self.connection.send((message + '\r\n').encode())
            elif cmd == "PORT":
                port = data[1]
                message = self.port(port, self.connection)
                self.connection.send((message + '\r\n').encode())
            elif cmd == "ACCT":
                username = data[1]
                password = data[2]
                client_time = data[3]
                message = self.register(username, password, client_time)
                self.connection.send((message + '\r\n').encode())
            elif cmd == "USER":
                username = data[1]
                message = self.username(username)
                self.connection.send((message + '\r\n').encode())
            elif cmd == "PASS":
                password = data[1]
                message = self.password(password)
                self.connection.send((message + '\r\n').encode())  
            elif cmd == "PWD":
                message = self.pwd()
                self.connection.send((message + '\r\n').encode())     
            elif cmd == "QUIT":
                message = self.quit()
                self.connection.send((message + '\r\n').encode())
                self.loggedIn = False
                print(f"[SERVER] Client: {self.addr} disconnected")
                break
            elif cmd == "NOOP":
                message = self.NOOP()
                self.connection.send((message + '\r\n').encode())
            elif cmd == "READY":
                self.ready(myClients, clientDelayTime)
            elif cmd == "ANSWER":
                answer = int(data[1])
                client_send_time = float(data[2])
                recTime = time.time()
                print(answer)
                message = self.answer(answer, myClients, clientDelayTime, client_send_time, recTime)
            # If command entered wrong 
            else:
                message = "502 Command " +cmd+ " not implemented."
                self.connection.send((message + '\r\n').encode())
            print(f"[SERVER] ***************************************************")

    def ready(self, clients, latencies):
        """This function checks that all the connected clients have indicated that they are ready,
        and that there are at least two players that have joined before sending the game."""
        global READY 
        global ANSWER
        READY += 1

        if self.loggedIn: # If a player is not logged in, they can't play the game

            while READY < len(myClients): # Wait for all connected clients to indicate they are ready
                pass

            send_time = time.time()
            local_time = time.ctime(send_time)

            if READY == len(myClients) and len(myClients) > 1:
                message = f"What is the sum of " + str(self.number1) + " and " + str(self.number2) + "? \r\n"     
                message += f"Send time is: " + str(local_time) + " \r\n"  
        else:
            message = "You are not logged in. \r\n"

        self.sync(message, clients, latencies)

    def answer(self, answer, clients, latencies, client_time, recTime):
        global ANSWER
        global WIN

        answers.append(answer)
        self.threadAnswer = answer

        my_performance = recTime - client_time - self.clientDelayTime_
        self.thread_performance_time = my_performance
        performanceTimes.append(my_performance)

        while len(answers) < len(myClients): # Wait for all clients to answer the question
            pass

        if len(answers) == len(myClients):
            if self.threadAnswer == ANSWER and self.thread_performance_time == min(performanceTimes):
                message = "Correct! You win! \r\n"
                WIN = True
            elif self.threadAnswer == ANSWER and self.thread_performance_time != min(performanceTimes):
                message = "Correct, but you did not win. \r\n"
            else:
                message = "Wrong. \r\n"

        self.sync(message, clients, latencies)
    
    def NOOP(self):
        if self.loggedIn:    
            message = "200 OK"
        else:
            message = "530 Not logged in."

        return message

    def welcomeMessage(self):
        message = "220 Welcome to the server. Run command ACCT <yourusername> <yourpassword> to create a new account."

        return message

    def help(self):
        message = "214 help information:\n"
        message += "ACCT <yourusername> <yourpassword>: Create your user account.\n"
        message += "USER <yourusername>: User identification username, first command for logging in.\n"
        message += "PASS <yourpassword>: Takes the user's password, completes user's identification.\n"
        message += "QUIT: Terminate user, close control connection.\n"
        message += "READY: Send this command when your are ready to play.\n"
        message += "ANSWER: Captures your answer for the game and give you the results.\n"
        message += "NOOP: Check your connection."
        
        return message

    def register(self, username, password, client_time):
        
        if not self.loggedIn:
            delayTime = connSpeed(client_time)
            self.clientDelayTime_ = delayTime

            clientDelayTime.append(delayTime)
            print(clientDelayTime)

            self.latency()

            # create a text file to store user details if it does not exist in the directory
            if not os.path.exists("username_password.txt"):
                file = open("username_password.txt", "w") # open the file in write mode
                file.close()

            if username in open("username_password.txt", "r").read():
                message = "553 Username not available, try another one."
                return message

            file = open("username_password.txt","a")
            file.write(username)
            file.write(" ")
            file.write(password)
            file.write("\n")
            file.close()

            message = "332 Successfully registered."
        else:
            message = "530 You are already registered. \r\n"

        return message
    
    def sync(self, message, clients, latencies):
        indexOfMaxLat = clientDelayTime.index(max(clientDelayTime))
        delay = clientDelayTime[indexOfMaxLat]

        time.sleep(delay)

        for client in clients:
            if client == self.connection:
                client.sendall(message.encode())

    def username(self, username):
        print(f"The entered username is: {username}")
        new_username = username.rstrip()
        counter = 0
        numberOfUsers = len(self.users)
        for u in self.users:
            if u == new_username:
                self.isUserValid = True
                self.threadUsername = username
                message = "331 User name okay, need password."
                print("True")
                break
            elif u != new_username:
                counter = counter + 1
            elif counter == numberOfUsers:
                self.isUserValid == False
                message = "332 Need account for login. "+username+" not registered."
                print("False")

        if not self.isUserValid:
            for line in open("username_password.txt","r").readlines(): # Read the lines
                registeredUsername = line.split() # Split on the space, and store the results in a list of two strings
                if username == registeredUsername[0]:
                    self.threadUsername = username
                    self.isUserValid = True
                    message = "331 User name okay, need password."
                else:
                    message = "332 Need account for login."+username+" not registered."
                print(self.threadUsername)

        return message

      #FTP PASS functionality, determining validity of Client's Password
    def password(self, password):
        new_password = password.rstrip()
        counter = 0
        numberOfPass = len(self.passwords) # get the number of elements in the list
        if self.isUserValid:
            for p in self.passwords:
                if p == new_password:    
                    self.loggedIn = True
                    message = "230 Loggin successfully .\n"
                    break
                elif p != new_password:
                    counter = counter + 1
                elif counter == numberOfPass:
                    self.loggedIn == False
                    message = "530 incorrect password for "+self.threadUsername+".\n" 
                    break

        if not self.loggedIn and self.isUserValid:
            for line in open("username_password.txt","r").readlines(): # Read the lines
                userInfo = line.split() # Split on the space, and store the results in a list of two strings
                if self.threadUsername == userInfo[0] and password == userInfo[1]:
                    message = "230 User logged in, proceed."
                    self.loggedIn = True
                    break
                else:
                    message = "530 Not logged in. Incorrect password."

        return message

    def quit(self):
        message = "221 Logged out."
        return message

def main():
    print("[STARTING] Server is starting...")
    global ANSWER
    
    serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverSocket.bind(ADDR)
    serverSocket.listen()

    number1 = random.randint(1,50) 
    number2 = random.randint(1,50) 
    ANSWER = number1 + number2 # Store the answer in the global variable


    sentinel = 0

    while sentinel < 1:
        print ("[LISTENING] Server is listening...")
        connection, addr = serverSocket.accept()
        thread = Server(connection, addr, number1, number2)
        thread.start()        

if __name__ == '__main__':
    main()
