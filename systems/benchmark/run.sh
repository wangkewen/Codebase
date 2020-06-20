#!/bin/bash
echo "install sysbench..."
runCPUsys(){
  echo "run_"$1
  SECONDS=0
  sysbench --test=cpu --cpu-max-prime=200000 --num-threads=20 run
  dur=$SECONDS
  echo $dur" s"
}
runCPU(){
  SECONDS=0
  pxz -k -c WC1g_$1 > /dev/null 2>&1
  echo WC1g_$1
  dur=$SECONDS
  echo $dur" s"
  exit 0
}
runIO(){
  mkdir -p test_$1
  cd test_$1
  SECONDS=0
  #sysbench --test=fileio --num-threads=1 --file-total-size=3G --file-num=1 --file-test-mode=rndrw prepare
  sysbench --test=fileio --num-threads=1 --file-total-size=3G --file-num=1 --file-test-mode=seqwr run
  #sysbench --test=fileio --num-threads=1 --file-total-size=3G --file-num=1 --file-test-mode=rndwr cleanup
  dur=$SECONDS
  echo $dur" s"
}
runMem(){
  sysbench --test=memory --memory-oper=write --memory-access-mod=rnd --memory-total-size=12G run
}
testrun(){
    p=$1
    for i in $(seq 1 $1)
    do
      echo $i
      runCPU $i &
    done
}
runCPUsys abc

