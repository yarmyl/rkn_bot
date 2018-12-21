#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import argparse
import configparser
import os


def readToken(file_name):
    try:
        file = open(file_name, 'r')
    except:
        raise SystemExit("Fail to read token file")
    return file.read()

def createParser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--conf', nargs='?')
    return parser

def req(url, method, data=[], req_method=0):
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

def getSettings(config):
    settings = dict()
    for section in config.sections():
        value = dict()
        for setting in config[section]:
            value.update({setting: config.get(section, setting)})
        settings.update({section: value})
    return settings


class Bot:

    HELP = [
        '/start - Enjoy\n',
        '/help - This message\n',
        '/show [cur|new] - Show statistics by new or current rules\n',
        '/check - Check Difference between current and new rules\n',
        '/apply - Apply new rules\n',
        '/update - Update new rules\n',
        '/search [IP] [cur|new] - Search IP in current and old rules\n',
        '/add [IP] - Proxy IP to tor\n',
        '/del [IP] - Remove IP to tor\n'
    ]

    def __init__(self, conf):
        self.__token = conf['token']
        self.__update = conf['update']
        self.__ipset = conf['ipset']
        self.__url = "https://api.telegram.org/bot" + self.__token + '/'
        self.last_id = None
        self.updateRules()
        if not self.checkToken():
            raise SystemExit("Bad token")

    def checkToken(self):
         return req(self.__url, "getMe")['ok']

    def updateRules(self):
        os.system('wget -O black_nets.list ' + self.__update)
        
    def applyRules(self):
        os.system('cp black_nets.list cur.list')
        os.system('sudo ipset flush ' + self.__ipset)
        os.system("cat cur.list | sed 's/^/add " + self.__ipset + " /g' > rules.list")
        os.system('sudo ipset restore < rules.list')

    def checkRules(self):
        self.updateRules()
        os.system('diff black_nets.list cur.list')

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

    def getLastUpdate(self, data):
        if len(data) > 0:
            last_update = data[-1]
        else:
            last_update = data[len(data)]
        return last_update

    def sendMessage(self, text, chat_id):
        return req(
            self.__url,
            "sendMessage",
            {'chat_id': chat_id, 'text': text},
            1
        )

    def botBrain(self, text, chat_id):
        if text == "/help":
            self.sendMessage(
                ''.join(self.HELP),
                chat_id
            )
        elif text == "/start":
            self.sendMessage("Please, use /help", chat_id)
        elif text[:5] == "/show":
            pass
        elif text == "/check":
            self.checkRules()
        elif text == "/apply":
            self.applyRules()
            self.sendMessage("It's Done!", chat_id)
        elif text == "/update":
            self.updateRules()
            self.sendMessage("It's Done!", chat_id)
        elif text[:7] == "/search":
            pass
        elif text[:4] == "/add":
            pass
        elif text[:4] == "/del":
            pass

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
