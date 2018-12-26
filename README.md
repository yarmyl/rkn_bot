# rkn_bot

## Pre Install
```
sudo apt update
sudo apt install -y python3 python3-pip git
sudo su
pip3 install netaddr
exit
```
## Install
```
git clone https://github.com/yarmyl/rkn_bot.git
```

## Add systemd
```
echo "[Unit]
Description=RKN_Bot Application Service
Requires=networking.service
After=networking.service

[Service]
Type=simple
RemainAfterExit=yes
WorkingDirectory=[dir]/rkn_bot/
ExecStart=/usr/bin/python3 bot_init.py 
PIDFile=/run/bot.pid
Restart=always

[Install]
WantedBy=multi-user.target" > /etc/systemd/system/rkn_bot.service

systemctl enable rkn_bot
```
## Usage
```
usage: bot_init.py [-h] [--conf [CONF]]

optional arguments:
  -h, --help     show this help message and exit
  --conf [CONF]
```
## Registration

@BotFather This [instruction](https://core.telegram.org/bots) with commands in **commands** file

## Config

[CONF]
TOKEN=[your token]
UPDATE=https://github.com/yarmyl/black_nets/raw/master/black_nets.list
IPSET=black_list

## Start

systemctl start rkn_bot

## Proxy

use /autoinstall
