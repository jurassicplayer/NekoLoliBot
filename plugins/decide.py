#!/usr/bin/env python

import template
import re, random

class IRCScript(template.IRCScript):
    print('loaded decide')
    def privmsg(self, user, channel, msg):
        decisions = re.match('^-decide\s(?P<choices>.*)', msg, re.I)
        if decisions:
            choices = decisions.group('choices').split('|')
            result = random.choice(choices)
            self.sendMsg(channel, "I'd go with "+result)
