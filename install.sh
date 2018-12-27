#!/bin/bash

apt update
apt install -y python3 python3-pip git
pip3 install netaddr

echo "[Unit]
Description=RKN_Bot Application Service
Requires=networking.service
After=networking.service

[Service]
Type=simple
WorkingDirectory=`pwd`
ExecStart=/usr/bin/python3 bot_init.py
PIDFile=/run/bot.pid
Restart=always

[Install]
WantedBy=multi-user.target" > /etc/systemd/system/rkn_bot.service

systemctl enable rkn_bot
#systemctl start rkn_bot

touch cur.list tor.list white.list
echo "[CONF]
TOKEN=
UPDATE=https://github.com/yarmyl/black_nets/raw/master/black_nets.list
IPSET=black_list" > token.conf
