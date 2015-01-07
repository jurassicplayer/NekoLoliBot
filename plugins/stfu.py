#!/usr/bin/env python

import template
import re, time


class IRCScript(template.IRCScript):
    print('loaded stfu')
    def privmsg(self, user, channel, msg):
        stfu = re.match('^!stfu(\s(?P<time>\d+)((?P<unit>[s|m|h])|)|)$', msg, re.I)
        if stfu:
            if stfu.group('time') and stfu.group('unit'):
                delay = int(stfu.group('time'))
                if stfu.group('unit') == 'h' and delay <= 2:
                    sleeper = delay*60*60
                elif stfu.group('unit') == 'm' and delay <= 120:
                    sleeper = delay*60
                elif stfu.group('unit') == 's' and delay <= 7200:
                    sleeper = delay
                else:
                    sleeper = None
            elif stfu.group('time') and stfu.group('unit') != 1:
                delay = int(stfu.group('time'))
                if delay > 7200:
                    sleeper = None
                else:
                    sleeper = delay
            else:
                sleeper = 1800
            if sleeper:
                self.sendMsg(channel, "Fine! I didn't want to listen to you anyways! ヾ( ･`⌓´･)ﾉﾞ")
                self.part(channel)
                time.sleep(sleeper)
                self.join(channel)
                time.sleep(2)
                self.sendMsg(channel, "I'm sorry, I didn't mean what I said earlier. .·´¯`(>▂<)´¯`·.")
            else:
                self.sendMsg(channel, "I don't have to listen to you!")
