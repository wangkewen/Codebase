#!/bin/bash
first=11
num=4
last=`expr $first + $num - 1`

mkCpugroup(){
    for i in $(seq $first $last)
    do
        echo "ssh node$i"
        ssh -t node$i "sudo mkdir -p /sys/fs/cgroup/cpu/spark"
        ssh -t node$i "sudo chmod -R 777 /sys/fs/cgroup/cpu/spark"
    done
}

mkMemgroup(){
    for i in $(seq $first $last)
    do
        echo "ssh node$i"
        ssh -t node$i "sudo mkdir -p /sys/fs/cgroup/memory/spark"
        ssh -t node$i "sudo chmod -R 777 /sys/fs/cgroup/memory/spark"
    done
}

changeCPU(){
    x=$(( 1000000 * $1 / 100 ))
    for i in $(seq $first $last)
    do
        echo "cpu, ssh node$i"
        ssh node$i "echo $x > /sys/fs/cgroup/cpu/spark/cpu.cfs_quota_us"
    done
}

changeCPUPeriod(){
    x=$(( 1000000 * $1))
    for i in $(seq $first $last)
    do
        echo "cpu, ssh node$i"
        ssh node$i "echo $x > /sys/fs/cgroup/cpu/spark/cpu.cfs_period_us"
    done
}

changeMem(){
    x=$(( 16 * 1024 * $1 / 100 ))
    echo $x
    for i in $(seq $first $last)
    do
        echo "mem, ssh node$i"
        ssh node$i "echo $x"M" > /sys/fs/cgroup/memory/spark/memory.limit_in_bytes"
    done
}

recoverAll(){
    for i in $(seq $first $last)
    do
        echo "cpu, ssh node$i"
        ssh node$i "echo -1 > /sys/fs/cgroup/cpu/spark/cpu.cfs_quota_us"
    done
}

dynamical(){
    for i in $(seq $first $last)
    do
        echo "node$i cpu dynamical"
        ssh node$i "~/cooldogs/dynamicalCPU.sh" &
    done
}

# changeCPU $1
# recoverAll
# dynamical
