#!/usr/bin/python3

"""
Ecrit par le prof au tableau (algo)

CLIENT.PY
=========
socket(v4, TCP)
connect
select([s, sys.stdin])
  if s in read...
    d = s.recv(1024)
    print(d)
  if s in exceptional...
    s.close()
  if s = sys.stdin
    l = s.recv(...)
    l.split()
    .....COMMAND PARSE 2

SERVEUR.PY
==========
socket(v4, TCP)
listen(so)
[serv]
select
  if s in read...
    if s = serv
    c = s.accept()
  else
    s.recv()
    parse command
    envoyer MSG à tous les autres ml du channel
"""
###########
# MODULES #
###########

import socket
import select
import threading
import sys

####################
# GLOBAL VARIABLES #
####################

LOCALHOST=("127.0.0.1",1459)
USAGE="""USAGE :
  -h | --help
    display this help
  -v | --version
    display the version
  -a | --addr
    change the address (by default localhost)
"""
VERSION="0.01"
LIMIT=2048
address = LOCALHOST

def ERROR(s):
    print("Error : ", s)
    exit()

###################
# PARSE ARGUMENTS #
###################
    
argv = sys.argv
argc = len(sys.argv)
for i in range(1,argc):
    if argv[i] in ("-a", "--addr"):
        i+=1
        if i >= argc:
            ERROR(argv[i-1] + " needs an argument")
        address = (argv[i], address[1])
    elif argv[i] in ("-h", "--help"):
        print(USAGE)
        exit()
    elif argv[i] in ("-v", "--version"):
        print("Version " + VERSION)
        exit()


########
# CODE #
########

# Create socket
s = socket.socket()
s.connect(address)

liste = [s, sys.stdin]

cmdlist=["HELP","LIST","JOIN","WHO","MSG","BYE","KICK","REN"]

# Main loop
while True:
    reading, writing, exceptional = select.select(liste,[],[])
    for r in reading:
        if r in exceptional:
            r.close()
            ##exit()
        elif r!=sys.stdin:
            d=r.recv(LIMIT).decode("utf-8")
            print(d)
        else:
            msg=r.readline()
            if msg.rstrip(' \n') != "":
                if msg[0]=='/':
                    msg=msg[1:]+" "
                    command, argument=msg.split(" ",1)
                    command=command.rstrip(' \n')
                    if command in cmdlist:
                        s.send(msg.encode("utf-8"))
                else:
                    msg="PRINT "+msg
                    s.send(msg.encode("utf-8"))

"""
            l.split(" ", 1)
            l[0] == "MSG"
            l[1] == "<nick> <message>"
            l[1].split(" ", 1)
"""
