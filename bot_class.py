#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import bot_brain


"""request to url"""
def req(url, method, data={}, req_method=0):
    if not req_method:
        r = requests.get(url+method, data=data)
    elif req_method == 1:
        r = requests.post(url+method, data=data)
    else:
        print("Wrong method!")
    return r.json()


class Bot:

    rm_keyboard = json.dumps({"remove_keyboard": True})

    """Bot init"""
    def __init__(self, conf):
        self.__token = conf['CONF']['token']
        self.__url = "https://api.telegram.org/bot" + self.__token + '/'
        self.last_id = None
        if not self.checkToken():
            raise SystemExit("Bad token")
        self.brain = bot_brain.Brain(conf['BRAIN'])
        self.queue = {}
        self.replyHi(self.parseMess(self.getUpdates(None, 0)))  # cap

    """make buttons"""
    def makeKeyboard(self, answers):
        if answers:
            return json.dumps({
                "resize_keyboard": True,
                "one_time_keyboard": True,
                "keyboard": answers
            })
        else:
            return self.rm_keyboard

    """Check tocken bot"""
    def checkToken(self):
        return req(self.__url, "getMe")['ok']

    """reply sorry and hi"""
    def replyHi(self, data):
        chats = set()
        for mess in data:
            chats.add(mess[1])
        for chat in chats:
            self.sendMessage(
                "Hi, sorry, I'm alive",
                chat
            )

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
    def sendMessage(self, text, chat_id, board=rm_keyboard, mess_id=None):
        return req(
            self.__url,
            "sendMessage",
            {
                'chat_id': chat_id,
                'text': text,
                'reply_markup': board,
                'reply_to_message_id': mess_id
            },
            1
        )

    """Parse Messages in Update"""
    def parseMess(self, data):
        messages = []
        for mess in data:
            if mess.get('message'):
                text = mess['message']['text']
                id = mess['message']['message_id']
                if self.queue.get(mess['message']['from']['id']):
                    head = self.queue.pop(mess['message']['from']['id'])
                    text = head[
                        mess['message']['chat']['id']
                    ][0] + ' ' + mess['message']['text']
                    id = head[
                        mess['message']['chat']['id']
                    ][1]
                messages.append(
                    [
                        text,
                        mess['message']['chat']['id'],
                        id,
                        mess['message']['from']['id']
                    ]
                )
        return messages

    """Listen and reply"""
    def startBrain(self):
        data = self.getUpdates()
        for mess in self.parseMess(data):
            message, board = self.brain.botBrain(mess[0])
            if board:
                self.queue[mess[3]] = {mess[1]: mess[::2]}
            if board == "text":
                self.sendMessage(
                    message,
                    mess[1],
                    mess_id=mess[2]
                )
            else:
                self.sendMessage(
                    message,
                    mess[1],
                    mess_id=mess[2],
                    board=self.makeKeyboard(board)
                )
