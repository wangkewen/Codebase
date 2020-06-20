#!/bin/bash

vagrantssh() {

        if [ $# -lt 1 ]
        then
            echo "one parameter (number of first node)"
            exit 1
        fi

        first=$1
        num=3
        last=`expr $first + $num - 1`

        cd ~/vagrant_box

        for i in $(seq $first $last)
        do
            ssh-keygen -y -f ~/vagrant_box/.vagrant/machines/node$i/virtualbox/private_key | vagrant ssh node$i -c 'cat >> ~/.ssh/authorized_keys'
        done

}

vagrantssh $1

