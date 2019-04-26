#!/bin/bash

[ ! -f server.py ] && echo "File server.py not found!" && exit 0
[ ! -f client.py ] && echo "File client.py not found!" && exit 0

# command for client1 
function client1()
{
    echo "toto"
    echo "/JOIN mychannel"    # create it
    sleep 0.5                       # wait for message "pouet pouet"
    echo "/LEAVE"             # and leave it
    echo "/BYE"
}

# command for client2
function client2()
{
    echo "tutu"
    sleep 0.1
    echo "/JOIN mychannel"
    echo "pouet pouet"      # send a test message in channel
    sleep 0.2
    echo "/LEAVE"           # and leave it
    echo "/BYE"
}

# command for client3
function client3()
{
    echo "tata"
    echo "/JOIN anotherchannel"
    sleep 0.5                           # wait for nothing
    echo "/LEAVE"                 # and leave it
    echo "/BYE"
}


echo "=> start server"
python3 -u server.py |& sed -e "s/^/server0: /;" &
SERVER=$!
sleep 1
echo "=> start client1"
client1 | python3 -u client.py |& sed -e "s/^/client1: /;" &
CLIENT1=$!
echo "=> start client2"
client2 | python3 -u client.py |& sed -e "s/^/client2: /;" &
CLIENT2=$!
echo "=> start client3"
client3 | python3 -u client.py |& sed -e "s/^/client3: /;" &
CLIENT3=$!
trap "pkill -9 -P $$" EXIT  # kill all children at exit
wait $CLIENT1 $CLIENT2 $CLIENT3
echo "=> clients terminated."
# EOF
