#!/bin/bash
first=11
num=4
last=`expr $first + $num - 1`
collect(){
    if [ $# -ne 1 ]
    then
        echo "one argv label (pr2g_-1, pr2g1000, pr2g)"
        exit 1
    fi
    for i in $(seq $first $last)
    do
        echo "node$i collect cpu"
        ssh node$i "~/cooldogs/collectPid.sh $1" &
    done
}
collect $1

