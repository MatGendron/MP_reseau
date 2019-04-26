#!/bin/bash

[ ! -f server.py ] && echo "File server.py not found!" && exit 0
[ ! -f client.py ] && echo "File client.py not found!" && exit 0

# command for client1 
function client1()
{
    echo "toto"
    sleep 0.2       # 200 ms
    echo "/BYE"
}

# command for client2
function client2()
{
    echo "tutu"
    sleep 0.2       # 200 ms
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
trap "pkill -9 -P $$" EXIT  # kill all children at exit
wait $CLIENT1 $CLIENT2
echo "=> clients terminated."
# EOF
