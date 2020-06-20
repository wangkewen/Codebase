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
                if [ $i = $j ]
                then
                    no_new=true
                fi
            done
            if [ $no_new = "false" ]
            then
                if [ $1 = "mem" ]
                then
                    echo "memory "
                    echo $i > /sys/fs/cgroup/memory/spark/cgroup.procs
                elif [ $1 = "cpu" ]
                then
                    echo "cpu "
                    echo $i > /sys/fs/cgroup/cpu/spark/cgroup.procs
                fi
            fi
        done
        sleep 1
        count=$((count+1))
        echo $count
        if [ $count -ge "50" ]
        then
            exit 1
        fi
    done
echo $selPid
}   
newPid $1

