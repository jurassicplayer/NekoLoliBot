#!/usr/bin/env python

import template
import random, re

class Persistent:
    def __init__(self):
        self.global_result = 'hurrdurr'
        self.local_result = 'derp perp'
persist = Persistent()


class IRCScript(template.IRCScript):
    def privmsg(self, origin, target, msg):
        decisions = re.match('^-decide\s(?P<choices>.*)', msg, re.I)
        if decisions:
            choices = decisions.group('choices').split('|')
            result = random.choice(choices)
            self.sendMsg(target, "I'd go with "+result)
