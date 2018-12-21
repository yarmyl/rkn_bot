#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import argparse

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

class Bot:

    HELP = [
        '/start - Enjoy\n',
        '/help - This message\n'
    ]

    def __init__(self, token):
        self.__URL = "https://api.telegram.org/bot" + token + '/'
        self.__token = token
        self.last_id = None
        if not self.checkToken():
            raise SystemExit("Bad token")
        
    def checkToken(self):
         return req(self.__URL, "getMe")['ok']

    def getUpdates(self, offset=None, timeout=300):
        if not offset:
            if not self.last_id:
                offset = None
            offset = self.last_id
        data = req(
            self.__URL, 
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
            self.__URL,
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

    def parseMess(self, data):
        for mess in data:
            self.botBrain(mess['message']['text'], 
                mess['message']['chat']['id'])

def main():
    parser = createParser()
    namespace = parser.parse_args()
    bot = Bot(readToken(namespace.conf)[:-1]) if namespace.conf else Bot(readToken('token.conf')[:-1])
    while 1:
        bot.parseMess(bot.getUpdates())

if __name__ == "__main__":
    main()