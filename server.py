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
##Dictionnary used to manage admins
ladmin={}

##Function used to send a message to all clients, sock1 is used as an exception to avoid broken pipe error, sock2 is used
##to make an exception for another socket if needed.
def send_all(l,sock1,sock2,msg):
    for i in l:
        if i!=sock1 and i!=sock2:
            i.send(msg.encode("utf-8"))

##Function used to send a message to the clients in a given channel
def send_cnl(chan,src,msg):
    for i in chan:
        if i!=src:
            i.send(msg.encode("utf-8"))

##Function that checks whether the given socket is in a channel
def in_a_cnl(sock):
    for chan in lchan:
        if sock in lchan[chan]:
            return True
    return False

##Function that returns the current channel of a client, given their socket
def current_cnl(sock):
    for chan in lchan:
        if sock in lchan[chan]:
            return chan
    return ""
        
while 1<2:
    reading,writing,exceptional=select.select(lsock,[],lsock)
    for i in reading:
        if i==s:
            news,addrnews=i.accept()
            lsock+=[news,]
            lclt[news]="*Nick_pending*"
            ##news.send("Specify nickname with /NICK command.\n".encode("utf-8"))
        else:
            decmsg=i.recv(2042).decode("utf-8")
            command, argument = decmsg.split(" ", 1)
            command=command.rstrip(' \n')
            argument = argument.rstrip(' \n')
            ##print(command)
            ##print(argument)
            ##Code for sending messages in a channel, no command on the client's side
            if command == "PRINT":
                if argument!="":
                    for k in lchan:
                        if i in lchan[k]:
                            send_cnl(lchan[k],i,lclt[i]+" : "+argument)
            elif command == "HELP":
                i.send("* /HELP: print this message\n* /LIST: list all available channels on server\n* /JOIN <channel>: join (or create) a channel\n* /LEAVE: leave current channel\n* /WHO: list users in current channel\n* <message>: send a message in current channel\n* /MSG <nick> <message>: send a private message in current channel\n* /BYE: disconnect from server\n* /KICK <nick>: kick user from current channel [admin]\n* /REN <channel>: change the current channel name [admin]\n".encode("utf-8"))
            ##Code for MSG feature: sending private message to another client in the same channel
            elif command == "MSG":
                nick_dest,msg=argument.split(' ',1)
                sock_dest=0
                for sock_clt in lclt:
                    if lclt[sock_clt]==nick_dest:
                        sock_dest=sock_clt
                        break
                for k in lchan:
                    if i in lchan[k] and sock_dest in lchan[k]:
                        sock_dest.send(("<DM> "+lclt[i]+" : "+msg).encode("utf-8"))
                        break
            ##Code for LIST feature: listing channels
            elif command == "WHO":
                for k in lchan:
                    if i in lchan[k]:
                        for r in lchan[k]:
                            if r==ladmin[k][0]:
                                i.send("@{0}@\n".format(lchan[k][r]).encode("utf-8"))
                            else:
                                i.send("{0}\n".format(lchan[k][r]).encode("utf-8"))
            ##Code for LIST feature: displaying the list of channels
            elif command == "LIST":
                ##i.send("List of channels:\n".encode("utf-8"))
                if len(lchan)!=0:
                    for k in lchan:
                        i.send("{0}\n".format(k).encode("utf-8"))
                ##else:
                ##    i.send("*No channels*\n".encode("utf-8"))
            ##Code for NICK feature: choosing a name for a client
            elif command == "NICK":
                if argument != "":
                    bad_nick=False
                    for clt in lclt:
                        if argument==lclt[clt]:
                            bad_nick=True
                            break
                    if bad_nick:
                        break
                    ##    i.send("Nickname already taken.\n".encode("utf-8"))
                    else:
                        if lclt[i]=="*Nick_pending*":
                            ##i.send("List of channels:\n".encode("utf-8"))
                            if len(lchan)!=0:
                                for k in lchan:
                                    i.send("{0}\n".format(k).encode("utf-8"))
                            else:
                                break
                                ##i.send("*No channels*\n".encode("utf-8"))
                            ##i.send("Use /LIST command to display this list again.\nJoin a channel with /JOIN <channel_name> command before continuing.\nUse /HELP to display a list of commands.\n".encode("utf-8"))
                        for chan in lchan:
                            if i in lchan[chan]:
                                lchan[chan][i]=argument
                        lclt[i]=argument
            ##Code for JOIN feature: joining a channel
            elif command == "JOIN":
                if lclt[i]=="*Nick_pending*":
                    break
                    ##i.send("Choose a nickname before joining a channel\n".encode("utf-8"))
                else:
                    if argument != "":
                        if argument not in lchan:
                            lchan[argument]={}
                            ladmin[argument]=[]
                        lchan[argument][i]=lclt[i]
                        ladmin[argument].append(i)
                        ##send_cnl(lchan[argument],i,"JOIN {0} {1}\n".format(argument,lclt[i]))
            ##Code fo LEAVE feature: leaving a channel
            elif command == "LEAVE":
                for k in lchan:
                    if i in lchan[k]:
                        lchan[k].pop(i)
                        ladmin[k].remove(i)
                        if len(ladmin[k])==0:
                            lchan.pop(k)
                        break
                ##i.send("Use /JOIN command to join another channel or /BYE command to disconnect from the server.\n".encode("utf-8"))
            ##Code for BUY feature: disconnecting from the server.
            elif command == "BYE":
                if in_a_cnl(i):
                    break
                    ##i.send("Use /LEAVE command to leave your current channel before disconnecting from the server.\n")
                else:
                    ##leave_msg="BYE {0}!\n".format(lclt[i])
                    i.close()
                    lsock.remove(i)
                    lclt.pop(i)
                    ##send_all(lsock,s,i,leave_msg)
            ##Code for KICK feature: forcibly removing a client from a channel.
            elif command == "KICK":
                if argument != "":
                    chan=current_cnl(i)
                    if chan!="":
                        if i==ladmin[chan][0]:
                            for clt in lchan[chan]:
                                if lchan[chan][clt]==argument:
                                    lchan[chan].pop(clt)
                                    ladmin[chan].remove(clt)
                                    ##clt.send("Kicked from {0} by admin.\n".format(chan).encode("utf-8"))
                                    break
                        ##else:
                        ##    i.send("Error: This is an admin command.\n".encode("utf-8"))
                    ##else:
                    ##    i.send("You are not in any channel.\n".encode("utf-8"))
                ##else:
                ##    i.send("Error: No nickname provided.\n".encode("utf-8"))
            ##Code for REN feature: changing the name of a channel
            elif command == "REN":
                if argument !="":
                    chan=current_cnl(i)
                    if chan!="":
                        if i==ladmin[chan][0]:
                            lchan[argument]=lchan.pop(chan)
                            ladmin[argument]=ladmin.pop(chan)
                        ##else:
                        ##    i.send("Error: This is an admin command.\n".encode("utf-8"))
                    ##else:
                    ##    i.send("You are not in any channel.\n".encode("utf-8"))
                ##else:
                ##    i.send("Error: No channel name provided.\n".encode("utf-8"))
                
