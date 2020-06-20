#!/bin/bash
writeBgPid(){
    if [ -f "~/cooldogs/bgpid" ]
    then
        rm ~/cooldogs/bgpid
    fi
    ps -ef | grep spark | grep -v grep | awk '{print$2}' > ~/cooldogs/bgpid
}
writeBgPid

