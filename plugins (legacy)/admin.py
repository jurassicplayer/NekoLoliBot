#!/usr/bin/env python

import template
import re, time

class IRCScript(template.IRCScript):
    print('loaded admin')
    def privmsg(self, user, channel, msg):
        pipe = re.match('^\.p(?P<type>.)\s(?P<message>.*)', msg, re.I)
        if pipe:
            print(pipe.group('message'))
            print(channel)
            if pipe.group('type') == 'm':
                self.sendMsg(channel, pipe.group('message'))
            if pipe.group('type') == 'n':
                self.sendNotice(channel, pipe.group('message'))
            if pipe.group('type') == 'a':
                self.sendAction(channel, pipe.group('message'))
            if pipe.group('type') == 'c':
                print(pipe.group('message'))
                self.sendIRC(pipe.group('message'))
