#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import argparse
import configparser
import os
from netaddr import *
from subprocess import Popen, PIPE
import json


"""make buttons"""
def makeKeyboard(answers):
    return json.dumps({
        "resize_keyboard": True,
        "one_time_keyboard": True,
        "keyboard": [answers]
    })


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


"""read config file"""
def readToken(file_name):
    try:
        file = open(file_name, 'r')
    except:
        raise SystemExit("Fail to read token file")
    return file.read()


"""Arg Parser"""
def createParser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--conf', nargs='?')
    return parser


"""request to url"""
def req(url, method, data={}, req_method=0):
    if not req_method:
        r = requests.get(url+method, data=data)
    elif req_method == 1:
        headers = {
            'content-type': 'application/json',
            'Accept-Charset': 'UTF-8'
        }
        r = requests.post(url+method, data=data)
    else:
        print("Wrong method!")
    return r.json()


"""Read Settings"""
def getSettings(config):
    settings = dict()
    for section in config.sections():
        value = dict()
        for setting in config[section]:
            value.update({setting: config.get(section, setting)})
        settings.update({section: value})
    return settings


class Bot:

    """Manual"""
    HELP = [
        '/start - Enjoy\n',
        '/help - This message\n',
        '/show [cur|new|tor|w] - Show statistics by new or current rules\n',
        '/check - Check Difference between current and new rules\n',
        '/apply - Apply new rules\n',
        '/update - Update new rules\n',
        '/search [IP] [cur|new|tor|w] - Search IP in current and old rules\n',
        '/add [IP] [tor|w] - Add IP to list\n',
        '/del [IP] [tor|w] - Remove IP from list\n',
        '/showall [tow|w] - Show list'
    ]

    """Bot init"""
    def __init__(self, conf):
        self.__token = conf['token']
        self.__update = conf['update']
        self.__ipset = conf['ipset']
        self.__url = "https://api.telegram.org/bot" + self.__token + '/'
        self.rm_keyboard = json.dumps({"remove_keyboard": True})
        self.last_id = None
        self.updateRules()
        self.replyHi(self.getLastUpdate(self.getUpdates(None, 0)))
        if not self.checkToken():
            raise SystemExit("Bad token")

    """Check tocken bot"""
    def checkToken(self):
        return req(self.__url, "getMe")['ok']

    """reply sorry and hi"""
    def replyHi(self, data):
        if data.get('message'):
            self.sendMessage(
                "Hi, sorry, I'm alive",
                data['message']['chat']['id']
            )

    """Update new rules"""
    def updateRules(self):
        os.system('wget -O black_nets.list ' + self.__update)

    """Apply new rules"""
    def applyRules(self):
        os.system('cp black_nets.list cur.list')
        os.system('sudo ipset flush ' + self.__ipset)
        os.system(
            "cat cur.list | sed 's/^/add " + self.__ipset +
            " /g' > rules.list"
        )
        os.system('sudo ipset restore < rules.list')

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
            raise SystemExit("Fail to read file")
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
            raise SystemExit("Fail to read file")
        nets = []
        for net in file:
            nets.append(IPNetwork(net[:-1]))
        size = len(nets)
        nets.append(IPAddress(ip))
        return 1 if size == len(cidr_merge(nets)) else 0

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
        os.system('sudo ipset ' + cmd + ' ' + list + ' ' + ip)

    """Show full list"""
    def showAll(self, list):
        if list == 'w':
            file_name = 'white.list'
        elif list == 'tor':
            file_name = 'tor.list'
        try:
            file = open(file_name, 'r')
        except:
            raise SystemExit("Fail to read file")
        return file.read()

    """Get Update"""
    def getUpdates(self, offset=None, timeout=300):
        if not offset:
            if not self.last_id:
                offset = None
            offset = self.last_id
        data = req(
            self.__url,
            "getUpdates",
            {'timeout': timeout, 'offset': offset},
            1
        )['result']
        if data:
            self.last_id = int(self.getLastUpdate(data)['update_id']) + 1
        return data

    """Get Last Message in Update"""
    def getLastUpdate(self, data):
        if len(data) > 0:
            last_update = data[-1]
        else:
            last_update = {}
        return last_update

    """Send Message to chat_id"""
    def sendMessage(self, text, chat_id, board=None):
        return req(
            self.__url,
            "sendMessage",
            {'chat_id': chat_id, 'text': text, 'reply_markup': board},
            1
        )

    """Check coommand's list"""
    def checkList(self, str, chat_id, buttons):
        list = 0
        if str not in buttons:
            self.sendMessage(
                "Please select list",
                chat_id,
                makeKeyboard(buttons)
            )
            for elem in self.getUpdates():
                if elem.get('message').get('text') not in buttons:
                    return 0
                list = elem.get('message').get('text')
        else:
            list = str
        return list

    """Check command's tail"""
    def checkTail(self, str, chat_id, buttons):
        if isIP(str.split(' ')[0]):
            ip = str.split(' ')[0]
            if len(str.split(' ')) > 1:
                list = self.checkList(str.split(' ')[1], chat_id, buttons)
            else:
                list = self.checkList('', chat_id, buttons)
        else:
            self.sendMessage("Please enter IP", chat_id)
            for elem in self.getUpdates():
                if not isIP(elem.get('message').get('text')):
                    return (0, 0)
                ip = elem.get('message').get('text')
            list = self.checkList('', chat_id, buttons)
        return (ip, list)

    """Bot Brain"""
    def botBrain(self, text, chat_id):
        if text == "/help":
            self.sendMessage(
                ''.join(self.HELP),
                chat_id
            )
        elif text == "/start":
            self.sendMessage("Please, use /help", chat_id)
        elif text[:8] == "/showall":
            list = self.checkList(text[9:], chat_id, ["tor", "w"])
            if list:
                if self.showAll(list):
                    self.sendMessage(
                        self.showAll(list),
                        chat_id,
                        self.rm_keyboard
                    )
                else:
                    self.sendMessage(
                        "List is empty!",
                        chat_id,
                        self.rm_keyboard
                    )
            else:
                self.sendMessage("WTF?!", chat_id, self.rm_keyboard)
        elif text[:5] == "/show":
            list = self.checkList(
                text[6:],
                chat_id,
                ["cur", "new", "tor", "w"]
            )
            if list:
                self.sendMessage(
                    self.showRules(list),
                    chat_id,
                    self.rm_keyboard
                )
            else:
                self.sendMessage("WTF?!", chat_id, self.rm_keyboard)
        elif text == "/check":
            self.sendMessage(self.checkRules(), chat_id)
        elif text == "/apply":
            self.applyRules()
            self.sendMessage("It's Done!", chat_id)
        elif text == "/update":
            self.updateRules()
            self.sendMessage("It's Done!", chat_id, )
        elif text[:7] == "/search":
            ip, list = self.checkTail(
                text[8:],
                chat_id,
                ["cur", "new", "tor", "w"]
            )
            if ip:
                if list:
                    if self.searchIP(ip, list):
                        mess = "Yes"
                    else:
                        mess = "No"
                    self.sendMessage(mess, chat_id, self.rm_keyboard)
                    return 1
            self.sendMessage("WTF?!", chat_id, self.rm_keyboard)
        elif text[:4] == "/add":
            ip, list = self.checkTail(text[5:], chat_id, ["tor", "w"])
            if ip:
                if list:
                    if self.searchIP(ip, list):
                        self.sendMessage(
                            "Already exists",
                            chat_id,
                            self.rm_keyboard
                        )
                    else:
                        self.fixIP(ip, list, 'add')
                        self.sendMessage("Done!", chat_id, self.rm_keyboard)
                    return 1
            self.sendMessage("WTF?!", chat_id, self.rm_keyboard)
        elif text[:4] == "/del":
            ip, list = self.checkTail(text[5:], chat_id, ["tor", "w"])
            if ip:
                if list:
                    if self.searchIP(ip, list):
                        self.fixIP(ip, list, 'del')
                        self.sendMessage("Done!", chat_id, self.rm_keyboard)
                    else:
                        self.sendMessage(
                            "Nothing to delete!",
                            chat_id,
                            self.rm_keyboard
                        )
                    return 1
            self.sendMessage("WTF?!", chat_id, self.rm_keyboard)

    """Parse Messages in Update"""
    def parseMess(self, data):
        for mess in data:
            if mess.get('message'):
                self.botBrain(
                    mess['message']['text'],
                    mess['message']['chat']['id']
                )


def main():
    parser = createParser()
    namespace = parser.parse_args()
    parser = configparser.ConfigParser()
    parser.read(namespace.conf) \
        if namespace.conf else parser.read('token.conf')
    settings = getSettings(parser)
    bot = Bot(settings['CONF'])
    while 1:
        bot.parseMess(bot.getUpdates())


if __name__ == "__main__":
    main()
