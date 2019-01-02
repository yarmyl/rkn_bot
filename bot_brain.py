#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from netaddr import *
from subprocess import Popen, PIPE


"""IP adress checking"""
def isIP(ip):
    arr = ip.split('.')
    if len(arr) == 4:
        for a in arr:
            if a.isdigit():
                if int(a) > 255 or int(a) < 0:
                    return 0
            else:
                return 0
    else:
        return 0
    return 1


class Brain:

    """Manual"""
    HELP = [
        '/start - Enjoy\n',
        '/help - This message\n',
        '/show [cur|new|tor|w] - Show statistics by new or current rules\n',
        '/check - Check Difference between current and new rules\n',
        '/apply - Apply new rules\n',
        '/update - Update new rules\n',
        '/search [cur|new|tor|w] [IP] - Search IP in current and old rules\n',
        '/add [tor|w] [IP] - Add IP to list\n',
        '/del [tor|w] [IP] - Remove IP from list\n',
        '/showall [tow|w] - Show list\n',
        '/autoinstall - Auto proxy install\n'
    ]

    """Argument Parser"""
    def parseArgs(self, text):
        arr = text.split(' ')
        args = arr[1:]
        ret = []
        for arg in args:
            if arg:
                ret.append(arg)
        return (ret, arr[0])

    """Brain init"""
    def __init__(self, conf):
        self.__update = conf['update']
        self.__ipset = conf['ipset']

    """Update new rules"""
    def updateRules(self):
        os.system('wget -O black_nets.list ' + self.__update)
        return "It's Done!"

    """Apply new rules"""
    def applyRules(self):
        os.system('cp black_nets.list cur.list')
        os.system('ipset flush ' + self.__ipset)
        os.system(
            "cat cur.list | sed 's/^/add " + self.__ipset +
            " /g' > rules.list"
        )
        os.system('ipset restore < rules.list')
        return "It's Done!"

    """Check Difference between current and new rules"""
    def checkRules(self):
        self.updateRules()
        out, err = Popen(
            'diff cur.list black_nets.list',
            shell=True,
            stdout=PIPE
        ).communicate()
        net_add = 0
        net_del = 0
        for str in out.decode("utf-8"):
            if str[0] == '>':
                net_add += 1
            elif str[0] == '<':
                net_del += 1
        return "Add {0[0]} nets and Del {0[1]} nets".format((net_add, net_del))

    """Show rules statistics"""
    def showRules(self, list):
        if list == 'cur':
            file_name = 'cur.list'
        elif list == 'w':
            file_name = 'white.list'
        elif list == 'tor':
            file_name = 'tor.list'
        else:
            file_name = 'black_nets.list'
        try:
            file = open(file_name, 'r')
        except:
            return "Fail to open file " + file_name
        count = 0
        size = 0
        for net in file:
            count += 1
            size += IPNetwork(net[:-1]).size
        return "{0:d} Networks and {2:d} IP-adressess in {1} list" \
            .format(count, list, size)

    """Search IP-address in list"""
    def searchIP(self, ip, list):
        if list == 'cur':
            file_name = 'cur.list'
        elif list == 'w':
            file_name = 'white.list'
        elif list == 'tor':
            file_name = 'tor.list'
        else:
            file_name = 'black_nets.list'
        try:
            file = open(file_name, 'r')
        except:
            return "Fail to open file " + file_name
        if not isIP(ip):
            return "It isn't IP-address"
        nets = []
        for net in file:
            nets.append(IPNetwork(net[:-1]))
        size = len(nets)
        nets.append(IPAddress(ip))
        return "Yes" if size == len(cidr_merge(nets)) else "No"

    """Tor auto install"""
    def autoInstall(self):
        os.system('./auto_install.sh')
        return "Done!"

    """Add or Del rules in ipset"""
    def fixIP(self, ip, list, cmd):
        if list == 'w':
            file_name = 'white.list'
            list = 'white'
        elif list == 'tor':
            file_name = 'tor.list'
            list = 'tor'
        if cmd == 'add':
            os.system('echo ' + ip + ' >> ' + file_name)
        elif cmd == 'del':
            os.system("sed -i '/^" + ip + "$/d' " + file_name)
        os.system('ipset ' + cmd + ' ' + list + ' ' + ip)
        return "Done!"

    """Show full list"""
    def showAll(self, list):
        if list == 'w':
            file_name = 'white.list'
        elif list == 'tor':
            file_name = 'tor.list'
        try:
            file = open(file_name, 'r')
        except:
            return "Fail to open file " + file_name
        return file.read()

    """Bot Brain"""
    def botBrain(self, text):
        args, cmd = self.parseArgs(text)
        if cmd == "/help":
            return (''.join(self.HELP), None)
        elif cmd == "/start":
            return ("Please, use /help", None)
        elif cmd == "/showall":
            if args:
                if args[0] in ["tor", "w"]:
                    return (self.showAll(args[0]), None)
                else:
                    return ("WTF?! Wrong Argument", None)
            else:
                return ("Select list", [["tor", "w"]])
        elif cmd == "/show":
            if args:
                if args[0] in ["tor", "w", "cur", "new"]:
                    return (self.showRules(args[0]), None)
                else:
                    return ("WTF?! Wrong Argument", None)
            else:
                return ("Select list", [["tor", "w", "cur", "new"]])
        elif cmd == "/check":
            return (self.checkRules(), None)
        elif cmd == "/apply":
            return (self.applyRules(), None)
        elif cmd == "/update":
            return (self.updateRules(), None)
        elif cmd == "/search":
            if args:
                if args[0] in ["tor", "w", "cur", "new"]:
                    if len(args) > 1:
                        return (self.searchIP(args[1], args[0]), None)
                    else:
                        return ("Please, Enter IP-address", "text")
                else:
                    return ("WTF?! Wrong Argument", None)
            else:
                return ("Select list", [["tor", "w", "cur", "new"]])
        elif cmd == "/add":
            if args:
                if args[0] in ["tor", "w"]:
                    if len(args) > 1:
                        if self.searchIP(args[1], args[0]) == "Yes":
                            return ("Already exists", None)
                        elif self.searchIP(args[1], args[0]) == "No":
                            return (self.fixIP(args[1], args[0], 'add'), None)
                        else:
                            return (self.searchIP(args[1], args[0]), None)
                    else:
                        return ("Please, Enter IP-address", "text")
                else:
                    return ("WTF?! Wrong Argument", None)
            else:
                return ("Select list", [["tor", "w"]])
        elif cmd == "/del":
            if args:
                if args[0] in ["tor", "w"]:
                    if len(args) > 1:
                        if self.searchIP(args[1], args[0]) == "Yes":
                            return (self.fixIP(args[1], args[0], 'del'), None)
                        elif self.searchIP(args[1], args[0]) == "No":
                            return ("Nothing to delete!", None)
                        else:
                            return (self.searchIP(args[1], args[0]), None)
                    else:
                        return ("Please, Enter IP-address", "text")
                else:
                    return ("WTF?! Wrong Argument", None)
            else:
                return ("Select list", [["tor", "w"]])
        elif cmd == "/autoinstall":
            return (self.autoInstall(), None)
        else:
            return ("Wrong Command!", None)
