#!/bin/bash
first=11
num=4
last=`expr $first + $num - 1`
writePid(){
    for i in $(seq $first $last)
    do
        echo "node$i write bg Pid"
        ssh node$i "~/cooldogs/writeBgPid.sh" &
    done
}
writePid

