#!/bin/bash

echo "ssh to first node then continue"

if [ $# -lt 1 ]
then
   echo "one parameter (number of first node)"
   exit 1
fi

# generate all public keys

first=$1
num=4
last=`expr $first + $num - 1`

for i in $(seq `expr $first + 1` $last)
do
    cat /etc/hosts | ssh node$i "sudo -- sh -c 'cat > /etc/hosts'"
done

for i in $(seq $first $last)
do
    ssh node$i "ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa"
    ssh node$i "cat ~/.ssh/id_rsa.pub > ~/.ssh/authorized_keys"
done

for i in $(seq `expr $first + 1`  $last)
do
    ssh node$i "cat ~/.ssh/authorized_keys" | cat >> ~/.ssh/authorized_keys
done

# copy accumulated public keys to other hosts

for i in $(seq `expr $first + 1` $last)
do
    scp ~/.ssh/authorized_keys node$i:~/.ssh/
done

