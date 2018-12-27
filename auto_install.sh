#!/bin/bash

apt update

### install Docker

apt install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
apt-get update
apt-get install -y docker-ce

### install tor

git clone https://github.com/yarmyl/torproxy.git
cd torproxy
apt-get update && apt-get install ipset iptables
docker build -t tor .
cp ../iptables_rules.sh iptables_rules.sh

echo "[Unit]
Description=TorProxy Application Service
Requires=networking.service
Requires=docker.service
After=networking.service

[Service]
Type=simple
WorkingDirectory=`pwd`
ExecStart=/bin/bash run.sh
PIDFile=/run/torproxy.pid
Restart=always

[Install]
WantedBy=multi-user.target" > /etc/systemd/system/torproxy.service

systemctl enable torproxy
systemctl start torproxy
