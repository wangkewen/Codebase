#!/bin/bash

mkdir vagrant_box
cd vagrant_box

sudo apt-get update
sudo apt-get upgrade
sudo apt-get install zip unzip

wget https://releases.hashicorp.com/vagrant/2.2.5/vagrant_2.2.5_linux_amd64.zip
sudo unzip vagrant_2.2.5_linux_amd64.zip
sudo mv vagrant /usr/bin
vagrant plugin install vagrant-disksize

os_codename=`lsb_release -c | awk -F : '{print$2}'`

if [ $os_codename = "trusty" ]
then 
  # Ubuntu 14.04
  # wget https://download.virtualbox.org/virtualbox/5.2.32/virtualbox-5.2_5.2.32-132073~Ubuntu~trusty_amd64.deb
  sudo bash -c 'echo "deb https://download.virtualbox.org/virtualbox/debian trusty contrib" >> /etc/apt/sources.list'
  wget -q https://www.virtualbox.org/download/oracle_vbox.asc -O- | sudo apt-key add -
  sudo apt-get update
  sudo apt-get install virtualbox-6.0
elif [ $os_codename = "xenial" ]
then
  # Ubuntu 16.04
  # wget https://download.virtualbox.org/virtualbox/5.2.32/virtualbox-5.2_5.2.32-132073~Ubuntu~xenial_amd64.deb
  sudo bash -c 'echo "deb https://download.virtualbox.org/virtualbox/debian xenial contrib" >> /etc/apt/sources.list'
  wget -q https://www.virtualbox.org/download/oracle_vbox_2016.asc -O- | sudo apt-key add -
  sudo apt-get update
  sudo apt-get install virtualbox-6.0
fi

# sudo apt-get install -f

vagrant init

# vagrant up

