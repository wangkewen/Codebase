#!/bin/bash
newPid(){
    no_new=true
    count=0
    selPid=-1
    while [ $no_new = "true" ]
    do
        for i in `ps -ef | grep spark | grep -v grep | awk '{print$2}'`
        do
            no_new=false
            selPid=$i
            for j in `cat ~/cooldogs/bgpid`
            do
                if [ $i == $j ]
                then
                    no_new=true
                fi
            done
        done
        sleep 1
        count=$((count+1))
        echo $count
        if [ $count -ge "50" ]
        then
            exit 1
        fi
    done
    echo "collect "$selPid
    pid=$selPid
    # top -b -p $pid > ~/cooldogs/${pid}.out
    # python ~/cooldogs/sysutil.py $pid > ~/cooldogs/${pid}.out

    python ~/cooldogs/dynamic.py $pid $1
}
newPid $1


