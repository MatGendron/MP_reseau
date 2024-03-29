#!/usr/bin/python3

###########
# MODULES #
###########

import socket
import select
import threading
import sys
import signal

####################
# GLOBAL VARIABLES #
####################

LOCALHOST=("127.0.0.1",1459)
USAGE="""USAGE :
  -h | --help
    display this help
  -v | --version
    display the version
  --verbose
    display some text during the run
"""

VERSION="0.03"
LIMIT=2048
verbose=False

def ERROR(s):
    print("Error : ", s)
    sys.exit(0)

###################
# PARSE ARGUMENTS #
###################
    
argv = sys.argv
argc = len(sys.argv)
for i in range(1,argc):
    if argv[i] in ("--verbose"):
        i+=1
        verbose=True
    elif argv[i] in ("-h", "--help"):
        print(USAGE)
        sys.exit(0)
    elif argv[i] in ("-v", "--version"):
        print("Version " + VERSION)
        sys.exit(0)


########
# CODE #
########

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
s.bind(('',1459))
s.listen(1)
##List of server and clients sockets
lsock=[s,sys.stdin]
##Dictionnary of chat channels
lchan={}
##Dictionnary of all clients
lclt={}
##Dictionnary of users in channels used to determine admin
lcnlusr={}
##Dictionnary used to manage admins
ladmin={}
##List of banned adresses
lban=[]

##Function used to send a message to all clients, sock1 is used as an exception to avoid broken pipe error, sock2 is used
##to make an exception for another socket if needed.
def send_all(l,sock1,sock2,msg):
    for i in l:
        if i!=sock1 and i!=sock2 and i!=sys.stdin:
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

##Signal_handler
def signal_handler(sig,frame):
    for clt in lclt:
        clt.close()
    s.close()
    sys.exit(0)

        
while 1<2:
    signal.signal(signal.SIGINT, signal_handler)
    reading,writing,exceptional=select.select(lsock,[],lsock)
    for i in reading:
        if i==s:
            news,addrnews=i.accept()
            ipnews,portnews=addrnews
            if ipnews not in lban:
                lsock+=[news,]
                lclt[news]="*Nick_pending*"
                news.send("Choose a nickname before joining a channel.".encode("utf-8"))
            else:
                news.send("You are banned from this server.".encode("utf-8"))
                news.close()
        elif i==sys.stdin:
            line=i.readline()
            if len(line) >0 and line[0]=='/':
                line=line[1:-1]+" \n"
                command,argument=line.split(" ", 1)
                command=command.rstrip(' \n')
                argument=argument.rstrip(' \n')
                if command == "USERS":
                    for clt in lclt:
                        print(lclt[clt])
                if command == "SOCKETS":
                    for clt in lclt:
                        print(clt)
                if command == "KILL":
                    sock_kill=0
                    for clt in lclt:
                        if lclt[clt]==argument:
                            sock_kill=clt
                            break
                    leave_msg="{0} IS DED!".format(lclt[sock_kill])
                    sock_kill.close()
                    lsock.remove(sock_kill)
                    lclt.pop(sock_kill)
                    send_all(lsock,s,sock_kill,leave_msg)
                if command == "BAN":
                    sock_ban=0
                    for clt in lclt:
                        if lclt[clt]==argument:
                            sock_ban=clt
                            break
                    ip_ban,port_ban=sock_ban.getpeername()
                    lban.append(ip_ban)
                    leave_msg="{0} HAS BEEN FORSAKEN!".format(lclt[sock_ban])
                    sock_ban.close()
                    lsock.remove(sock_ban)
                    lclt.pop(sock_ban)
                    send_all(lsock,s,sock_ban,leave_msg)
        else:
            decmsg=i.recv(2042).decode("utf-8")
            if decmsg=="":
                #force quit
                if verbose: print(lclt[i], "Has forcefully quit.")
                if in_a_cnl(i):
                    #LEAVE
                    for k in lchan:
                        if i in lchan[k]:
                            lchan[k].pop(i)
                            lcnlusr[k].remove(i)
                            if len(lcnlusr[k])==0:
                                lchan.pop(k)
                            break
                command="BYE"
                argument=""
            else:
                command, argument = decmsg.split(" ", 1)
            command=command.rstrip(' \n')
            argument = argument.rstrip(' \n')
            ##print(command)
            ##print(argument)
            ##Code for sending messages in a channel, no command on the client's side
            if command == "BYE":
                if in_a_cnl(i):
                    i.send("Use /LEAVE command to leave your current channel before disconnecting from the server.".encode("utf-8"))
                else:
                    leave_msg="BYE {0}!".format(lclt[i])
                    i.close()
                    lsock.remove(i)
                    lclt.pop(i)
                    send_all(lsock,s,i,leave_msg)
            elif lclt[i]=="*Nick_pending*":
                if command=="PRINT" and argument!="" and argument != "*Nick_pending*":
                    bad_nick=False
                    for clt in lclt:
                        if argument==lclt[clt]:
                            bad_nick=True
                            break
                    if bad_nick:
                        i.send("Nickname already taken.".encode("utf-8"))
                    else:
                        lclt[i]=argument
                        reply = "List of channels:\n"
                        if len(lchan)!=0:
                            for k in lchan:
                                reply += "{0}\n".format(k)
                        else:
                            reply += "*No channels*\n"
                        reply += "Use /LIST command to display this list again.\nJoin a channel with /JOIN <channel_name> command before continuing.\nUse /HELP to display a list of commands."
                        i.send(reply.encode("utf-8"))
                else:
                    i.send("Invalid nickname.".encode("utf-8"))
            elif command == "PRINT":
                if argument!="":
                    for k in lchan:
                        if i in lchan[k]:
                            send_cnl(lchan[k],i,lclt[i]+" : "+argument)
            elif command == "HELP":
                i.send("* /HELP: print this message\n* /LIST: list all available channels on server\n* /JOIN <channel>: join (or create) a channel\n* /LEAVE: leave current channel\n* /WHO: list users in current channel\n* <message>: send a message in current channel\n* /MSG <nick> <message>: send a private message in current channel\n* /BYE: disconnect from server\n* /KICK <nick>: kick user from current channel [admin]\n* /REN <channel>: change the current channel name [admin]".encode("utf-8"))
            ##Code for MSG feature: sending private message to another client in the same channel
            elif command == "MSG":
                lnick_dest,msg=argument.split(' ',1)
                lnick_dest=lnick_dest.split(';')
                lsock_dest=[]
                for sock_clt in lclt:
                    if lclt[sock_clt] in lnick_dest:
                        lsock_dest.append(sock_clt)
                for k in lchan:
                    if i in lchan[k]:
                        for sock_dest in lsock_dest:
                            if sock_dest in lchan[k]:
                                sock_dest.send(("<DM> "+lclt[i]+" : "+msg).encode("utf-8"))
                        break
            ##Code for LIST feature: listing channels
            elif command == "WHO":
                if in_a_cnl(i):
                    for k in lchan:
                        if i in lchan[k]:
                            for r in lchan[k]:
                                if r==lcnlusr[k][0]:
                                    i.send("@{0}@\n".format(lchan[k][r]).encode("utf-8"))
                                else:
                                    i.send("{0}\n".format(lchan[k][r]).encode("utf-8"))
                else: 
                    i.send("You are not in a channel.".encode("utf-8"))
            ##Code for LIST feature: displaying the list of channels
            elif command == "LIST":
                i.send("List of channels:\n".encode("utf-8"))
                if len(lchan)!=0:
                    for k in lchan:
                        i.send("{0}\n".format(k).encode("utf-8"))
                else:
                    i.send("*No channels*\n".encode("utf-8"))
            ##Code for NICK feature: choosing a name for a client
            elif command == "NICK":
                if argument != "" and argument != "*Nick_pending*":
                    bad_nick=False
                    for clt in lclt:
                        if argument==lclt[clt]:
                            bad_nick=True
                            break
                    if bad_nick:
                        i.send("Nickname already taken.".encode("utf-8"))
                    else:
                        for chan in lchan:
                            if i in lchan[chan]:
                                lchan[chan][i]=argument
                        lclt[i]=argument
                else:
                    i.send("Invalid nickname.".encode("utf-8"))
            ##Code for JOIN feature: joining a channel
            elif command == "JOIN":
                if lclt[i]=="*Nick_pending*":
                    i.send("Choose a nickname before joining a channel".encode("utf-8"))
                else:
                    if argument != "":
                        if argument not in lchan:
                            lchan[argument]={}
                            lcnlusr[argument]=[]
                        lchan[argument][i]=lclt[i]
                        lcnlusr[argument].append(i)
                        i.send("Successfully joined {0}.".format(argument).encode("utf-8"))
                        send_cnl(lchan[argument],i,"JOIN {0} {1}".format(argument,lclt[i]))
            ##Code fo LEAVE feature: leaving a channel
            elif command == "LEAVE":
                if in_a_cnl(i):
                    for k in lchan:
                        if i in lchan[k]:
                            lchan[k].pop(i)
                            lcnlusr[k].remove(i)
                            if len(lcnlusr[k])==0:
                                lchan.pop(k)
                            break
                    i.send("Use /JOIN command to join another channel or /BYE command to disconnect from the server.".encode("utf-8"))
                else:
                    i.send("Error: You are not in any channel.".encode("utf-8"))
            ##Code for BUY feature: disconnecting from the server.
            elif command == "BYE":
                if in_a_cnl(i):
                    i.send("Use /LEAVE command to leave your current channel before disconnecting from the server.".encode("utf-8"))
                else:
                    i.send("BYE!".encode("utf-8"))
                    leave_msg="BYE {0}!".format(lclt[i])
                    i.close()
                    lsock.remove(i)
                    lclt.pop(i)
                    send_all(lsock,s,i,leave_msg)
            ##Code for KICK feature: forcibly removing a client from a channel.
            elif command == "KICK":
                if argument != "":
                    chan=current_cnl(i)
                    if chan!="":
                        if i==lcnlusr[chan][0]:
                            for clt in lchan[chan]:
                                if lchan[chan][clt]==argument:
                                    lchan[chan].pop(clt)
                                    lcnlusr[chan].remove(clt)
                                    send_cnl(lchan[chan],0,"{0} has been kicked.".format(argument))
                                    clt.send("Kicked from {0} by admin.".format(chan).encode("utf-8"))
                                    break
                        else:
                            i.send("Error: This is an admin command.".encode("utf-8"))
                    else:
                        i.send("You are not in any channel.".encode("utf-8"))
                else:
                    i.send("Error: No nickname provided.".encode("utf-8"))
            ##Code for REN feature: changing the name of a channel
            elif command == "REN":
                if argument !="":
                    chan=current_cnl(i)
                    if chan!="":
                        if i==lcnlusr[chan][0]:
                            lchan[argument]=lchan.pop(chan)
                            lcnlusr[argument]=lcnlusr.pop(chan)
                        else:
                            i.send("Error: This is an admin command.".encode("utf-8"))
                    else:
                        i.send("You are not in any channel.".encode("utf-8"))
                else:
                    i.send("Error: No channel name provided.".encode("utf-8"))
                
