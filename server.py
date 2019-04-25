#!/usr/bin/python3

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

VERSION="0.02"
LIMIT=2048

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

##Function used to send a message to all clients, sock1 is used as an exception to avoid broken pipe error, sock2 is used
##to make an exception for another socket if needed.
def send_all(l,sock1,sock2,msg):
    for i in l:
        if i!=sock1 and i!=sock2:
            i.send(msg.encode("utf-8"))

##Function used to send a message to the clients in a given chanel
def send_cnl(chan,src,msg):
    for i in chan:
        if i!=src:
            i.send(msg.encode("utf-8"))
        
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
s.bind(('',1459))
s.listen(1)
##List of server and clients sockets
lsock=[s]
##Dictionnary of chat channels
lchan={}
##Dictionnary of all clients
lclt={}
while 1<2:
    reading,writing,exceptional=select.select(lsock,[],lsock)
    for i in reading:
        if i==s:
            news,addrnews=i.accept()
            #Prompt for a nickname, asks for a proper nickname as long as it's not given.
            temp=addrnews
            while addrnews==temp:
                news.send("Specify nickname with /NICK command.\n".encode("utf-8"))
                nick=news.recv(LIMIT).decode("utf-8")
                if nick[:5]==("NICK "):
                    given_nick=nick.partition(' ')[2].rstrip(' \n')
                    for k in lclt:
                        if lclt[k]==given_nick:
                            news.send("Nickname already taken.\n".encode("utf-8"))
                            break    
                    addrnews=given_nick
            lsock+=[news,]
            lclt[news]=addrnews
            news.send("List of channels:\n".encode("utf-8"))
            if len(lchan)!=0:
                for k in lchan:
                    news.send("{0}\n".format(k).encode("utf-8"))
            else:
                news.send("*No channels*\n".encode("utf-8"))
            news.send("Use /LIST command to display this list again.\nJoin a channel with /JOIN <channel_name> command before continuing.\n".encode("utf-8"))
            ##Prompts for a channel to join, asks again until a valid channel name is given.
            join_cnl=""
            while len(join_cnl)==0:
                join_cmd=news.recv(LIMIT).decode("utf-8")
                if join_cmd[:5]=="JOIN ":
                    join_cnl=join_cmd.partition(' ')[2].rstrip(' \n')
                    if len(join_cnl)!=0 and join_cnl not in lchan:
                        lchan[join_cnl]={}
                    lchan[join_cnl][news]=lclt[news]
                    send_cnl(lchan[join_cnl],i,"JOIN {0} {1}\n".format(join_cnl,lclt[news]))
        else:
            decmsg=i.recv(2042).decode("utf-8")
            ##Makes the client leave if he presses enter with no message
            if len(decmsg)<=1:
                    leave_addr=""
                    leave_msg="PART {0}\n".format(lclt[i])
                    i.close()
                    lsock.remove(i)
                    lclt.pop(i)
                    for k in lchan:
                        lchan[k].pop(i)
                    send_all(lsock,s,i,leave_msg)
                    break
            command, argument = decmsg.split(" ", 1)
            command=command.rstrip(' \n')
            argument = argument.rstrip(' \n')
            ##print(command)
            ##print(argument)
            ##Code for MSG feature: sending messages
            if command == "PRINT":
                if argument!="":
                    for k in lchan:
                        if i in lchan[k]:
                            send_cnl(lchan[k],i,argument)
            elif command == "MSG":
                nick_dest,msg=argument.split(' ',1)
                sock_dest=0
                for sock_clt in lclt:
                    if lclt[sock_clt]==nick_dest:
                        sock_dest=sock_clt
                        break
                for k in lchan:
                    if i in lchan[k] and sock_dest in lchan[k]:
                        sock_dest.send(msg.encode("utf-8"))
                        break
            ##Code for LIST feature: listing channels
            elif command == "WHO":
                for k in lchan:
                    if i in lchan[k]:
                        for r in lchan[k]:
                            i.send("{0}\n".format(lchan[k][r]).encode("utf-8"))
            elif command == "LIST":
                print(command)
                i.send("List of channels:\n".encode("utf-8"))
                for k in lchan:
                    i.send("{0}\n".format(k).encode("utf-8"))
            ##Code for KILL feature: removing a client from the chat
            elif command == "KILL":
                kck_addr=argument
                temp=0
                for k in lclt:
                    if lclt[k]==kck_addr:
                        k.send("Seeya\n".encode("utf-8"))
                        k.close()
                        lsock.remove(k)
                        temp=k
                lclt.pop(temp)
            ##Code for JOIN feature: joining a channel
            elif command == "JOIN":
                join_cnl=decmsg.partition(' ')[2].rstrip(' \n')
                if join_cnl not in lchan:
                    lchan[join_cnl]={}
                lchan[join_cnl][i]=lclt[i]
                send_cnl(lchan[join_cnl],i,"JOIN {0} {1}\n".format(join_cnl,lclt[i]))
            ##Code for PART feature: leaving a channel
            elif command == "KICK":
                kick_arg=argument
                kick_cnl=kick_arg.partition(' ')[0].rstrip(' \n')
                kick_nck=kick_arg.partition(' ')[2].rstrip(' \n')
                if kick_cnl!="default" and kick_cnl in lchan and i in lchan[kick_cnl]:
                    temp=0
                    for k in lchan[kick_cnl]:
                        if lchan[kick_cnl][k]==kick_nck:
                            temp=k
                    lchan[kick_cnl].pop(temp)
