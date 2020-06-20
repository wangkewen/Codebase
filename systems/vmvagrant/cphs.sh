#!/bin/bash

download(){
    # download jdk, hadoop, spark pkgs

    if [ $# -lt 1 ]
    then
	echo "one parameter (remote pkg path)"
	exit 1
    fi

    cd

    if [ ! -d jdk1.7.0_72 ]
    then
	# wget https://download.oracle.com/otn/java/jdk/7u72-b14/jdk-7u72-linux-x64.tar.gz
	# tar -xzf jdk-7u72-linux-x64.tar.gz
	scp -r $1:~/jdk1.7.0_72 .
	scp -r $1:~/.bashrc .
	source ~/.bashrc
    fi

    if [ ! -d hadoop-2.7.3 ]
    then
	if [ ! -f hadoop-2.7.3.tar.gz ]
	then
	    wget https://archive.apache.org/dist/hadoop/common/hadoop-2.7.3/hadoop-2.7.3.tar.gz
	fi
	tar -xzf hadoop-2.7.3.tar.gz
	scp  $1:~/hadoop-2.7.3/starth.sh ~/hadoop-2.7.3/
	scp  $1:~/hadoop-2.7.3/stoph.sh ~/hadoop-2.7.3/
    fi

    if [ ! -d spark-2.1.0-bin-hadoop2.7 ]
    then
	if [ ! -f spark-2.1.0-bin-hadoop2.7.tgz ]
	then
	    wget https://archive.apache.org/dist/spark/spark-2.1.0/spark-2.1.0-bin-hadoop2.7.tgz
	fi
	tar -xzf spark-2.1.0-bin-hadoop2.7.tgz
	scp $1:~/spark-2.1.0-bin-hadoop2.7/starts.sh ~/spark-2.1.0-bin-hadoop2.7/
	scp $1:~/spark-2.1.0-bin-hadoop2.7/stops.sh ~/spark-2.1.0-bin-hadoop2.7/
	scp $1:~/spark-2.1.0-bin-hadoop2.7/stestnochange.jar ~/spark-2.1.0-bin-hadoop2.7/
        mkdir ~/spark-2.1.0-bin-hadoop2.7/sparkevents
    fi

    echo "------------------------------------"
    echo "hadoop config: etc/hadoop/core-site.xml, hdfs-site.xml, mapred-site.xml, yarn-site.xml, slaves, masters"

    echo "\n------------------------------------"
    echo "spark config: conf/spark-defaults.conf, spark-env.sh, slaves"

}


copy(){

    echo "ssh to first node"

    if [ $# -lt 1 ]
    then
	echo "two parameters (number of first node, copy from)"
	exit 1
    fi

    first=$1
    num=4
    last=`expr $first + $num - 1`

    # copy jdk
    for i in $(seq `expr $first + 1`  $last)
    do
	scp -r jdk1.7.0_72 node$i:~/
	scp .bashrc node$i:~/
	ssh node$i "source .bashrc"
    done

    # copy hadoop
    for i in $(seq `expr $first + 1`  $last)
    do
	scp -r hadoop-2.7.3 node$i:~/
    done

    # copy spark
    for i in $(seq `expr $first + 1`  $last)
    do
	scp -r spark-2.1.0-bin-hadoop2.7 node$i:~/
    done

}

clearmem() {

    if [ $# -lt 1 ]
    then
	echo "one parameter (number of first node)"
	exit 1
    fi

    first=$1
    num=4
    last=`expr $first + $num - 1`

    echo "#!/bin/bash" >> clearmem.sh
    echo "for i in \$(seq $first $last)" >> clearmem.sh
    echo "do" >> clearmem.sh
    echo "    ssh node\$i 'sudo /sbin/sysctl vm.drop_caches=3'" >> clearmem.sh
    echo "done" >> clearmem.sh

}

