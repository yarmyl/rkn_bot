#!/bin/bash

ipset -exist create black_list hash:net maxelem 300000
ipset -exist create white hash:ip
ipset -exist create tor hash:ip
iptables -t nat -A OUTPUT -p tcp -d 127.192.0.0/10 -j REDIRECT --to-port 9040
iptables -t nat -A OUTPUT -p udp --dport 53 -m string --hex-string "|056f6e696f6e00|" --algo bm -j REDIRECT --to-ports 5300
iptables -t nat -A OUTPUT -p tcp -m multiport --dports 80,443 -m set --match-set tor dst -j REDIRECT --to-port 9040
iptables -t nat -A OUTPUT -p tcp -m multiport --dports 80,443 -m set --match-set white dst -j REDIRECT --to-port 9040
iptables -t nat -A OUTPUT -p tcp -m multiport --dports 80,443 -m set --match-set black_list dst -j REDIRECT --to-port 9040
