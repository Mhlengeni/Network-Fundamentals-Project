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

# Client

"""Importing modules"""
import socket
from time import time
import random
from poorconn import delay_before_sending, make_socket_patchable # Simulate poor connection

"""Declaring global variables"""
IP = socket.gethostbyname(socket.gethostname())
PORT = 21
ADDR = (IP,PORT)
SIZE = 1024
FORMAT = 'utf-8'

def client_socket(): # Simulating latency, the socket delays by 1 to 5 seconds
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s = make_socket_patchable(s)
    delay = random.randint(1,2)
    delay_before_sending(s, delay, SIZE)
    return s

def main():
    # Making a client socket connection
    client = client_socket()
    client.connect(ADDR)
    #While loop enabling clients to send Command and argument to Server.
    while True:
        message = client.recv(SIZE).decode(FORMAT)
        print(message)
        
        msg = input("> ")
        msg = msg.split(" ")
        cmd = msg[0].upper()
        if cmd == "HELP":
            client.send(cmd.encode(FORMAT))
        elif cmd == "QUIT":
            client.send(cmd.encode(FORMAT))
            recv_msg = client.recv(SIZE).decode(FORMAT)
            print(recv_msg)
            break
        elif cmd == "ACCT":
            curr_time = str(time())
            client.send(f"{cmd} {msg[1]} {msg[2]} {curr_time}".encode(FORMAT))
        elif cmd == "START":
            client.send(cmd.encode(FORMAT))
        elif cmd == "READY": 
            client.send(cmd.encode(FORMAT))
        elif cmd == "ANSWER":
            answer = input("Enter your answer: ")
            send_time = str(time())
            client.send(f"{cmd} {answer} {send_time}".encode(FORMAT))
        elif cmd == "USER":
            client.send(f"{cmd} {msg[1]}".encode(FORMAT))
        elif cmd == "PASS":
            client.send(f"{cmd} {msg[1]}".encode(FORMAT))
        elif cmd == "NOOP":
            client.send(cmd.encode(FORMAT))
        else :
            client.send(f"{cmd}".encode(FORMAT))

    client.close()
    
if __name__ == "__main__":
    main()