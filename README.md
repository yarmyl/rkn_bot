# rkn_bot

## Install
```
git clone https://github.com/yarmyl/rkn_bot.git
cd rkn_bot
sudo ./install.sh
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

## Config in token.conf
```
[CONF]
TOKEN=[your token]
[BRAIN]
UPDATE=https://github.com/yarmyl/black_nets/raw/master/black_nets.list
IPSET=black_list
```
## Start
```
systemctl start rkn_bot
```
## Proxy

first time use */autoinstall*

## Troubles

sometimes You may need this rule
```
iptables -t nat -A OUTPUT -p udp --dport 53 -j REDIRECT --to-ports 5300
```
redirect all DNS packets to Tor
