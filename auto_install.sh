#!/bin/bash

cd "$(dirname "$0")"
### sudo sed -i 's/%sudo	ALL=(ALL:ALL) ALL/%sudo	ALL=(ALL) NOPASSWD:ALL/g' /etc/sudoers
touch cur.list tor.list white.list
sudo apt update

# install python
### sudo apt install -y python3 python3-pip git
### pip3 install netaddr

# install Docker
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
sudo apt-get update
sudo apt-get install -y docker-ce
### sudo usermod -aG docker $USERNAME

# install tor
git clone https://github.com/yarmyl/torproxy.git
cd torproxy
sudo docker build -t tor .
cd ../
sudo rm -r torproxy
sudo docker run --name tor --net host -d --restart tor
sudo ./iptables_rules.sh
