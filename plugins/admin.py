#!/usr/bin/env python

import template
import re, time

class IRCScript(template.IRCScript):
    print('loaded admin')
    def privmsg(self, user, channel, msg):
        pipe = re.match('^-pipe\s(?P<channel>#[^\s]+)\s(?P<message>.*)', msg, re.I)
        if pipe:
            if pipe.group('message').find('/me') !=-1:
                self.sendAction(pipe.group('channel'), pipe.group('message')[3:])
            elif pipe.group('message').find('-c') !=-1:
                self.sendIRC(pipe.group('message')[3:])
            else:
                self.sendMsg(pipe.group('channel'), pipe.group('message'))
