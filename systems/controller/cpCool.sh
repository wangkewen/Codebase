#!/bin/bash
cp(){
    if [ $# -lt 1 ]
    then
	echo "one parameter (number of first node) "
        exit 1
    fi
    second=`expr $1 + 1`
    last=`expr $1 + 4 - 1`
    for i in $(seq $second  $last)
    do
        ssh node$i 'mkdir ~/cooldogs'
        scp sysutil.py dynamic.py collectPid.sh newPid.sh  writeBgPid.sh  node$i:~/cooldogs/
        ssh node$i 'chmod -R 775 ~/cooldogs'
    done
}
cp $1
