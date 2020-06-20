#!/bin/bash
first=11
num=4
last=`expr $first + $num - 1`
restrict(){
    if [ $# -ne 1 ]
    then
        echo "one argv (cpu, mem)"
        exit 1
    fi
    for i in $(seq $first $last)
    do
        echo "node$i restrict $1"
        ssh node$i "~/cooldogs/newPid.sh $1" &
    done
}
restrict $1

