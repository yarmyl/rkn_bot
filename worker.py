#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import configparser
import bot_class


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


"""Read Settings"""
def getSettings(config):
    settings = dict()
    for section in config.sections():
        value = dict()
        for setting in config[section]:
            value.update({setting: config.get(section, setting)})
        settings.update({section: value})
    return settings


def main():
    parser = createParser()
    namespace = parser.parse_args()
    parser = configparser.ConfigParser()
    parser.read(namespace.conf) \
        if namespace.conf else parser.read('token.conf')
    settings = getSettings(parser)
    bot = bot_class.Bot(settings)
    while 1:
        bot.startBrain()


if __name__ == "__main__":
    main()
