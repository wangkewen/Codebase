#! /bin/bash
first=11
num=4
last=`expr $first + $num - 1`
check(){
   for i in $(seq $first $last)
   do
       echo "node"$i
       ssh node$i "cat /sys/fs/cgroup/cpu/spark/cpu.cfs_quota_us"
   done
}

check

