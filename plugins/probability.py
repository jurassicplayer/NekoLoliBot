#!/usr/bin/env python

import template
import re, random

class IRCScript(template.IRCScript):
    print('loaded probability')
    def privmsg(self, user, channel, msg):
        if re.match('^-(eight|8)(-|)ball', msg, re.I):
            answers=['It is certain', 'It is decidedly so', 'Without a doubt', 'Yes definitely', 'You may rely on it', 'As I see it, yes', 'Most likely', 'Outlook good', 'Yes', 'Signs point to yes', 'Reply hazy try again', 'Ask again later', 'Better not tell you now', 'Cannot predict now', 'Concentrate and ask again', "Don't count on it", 'My reply is no', 'My sources say no', 'Outlook not so good', 'Very Doubtful']
            choice = random.choice(answers)
            self.sendMsg(channel, choice)
        dice = re.match('^-dice(roll|)(\s(?P<die>[1-9])|)$', msg, re.I)
        if dice:
            if dice.group('die'):
                number_of_die = int(dice.group('die'))
            else:
                number_of_die = 1
            string = ''
            for roll in range(0, number_of_die):
                a = random.randrange(1,7)
                string += str(a)+'   '
            self.sendMsg(channel, string)
        cf = re.match('^-coin(flip|toss|)(\s(?P<coins>[1-9])|)$', msg, re.I)
        if cf:
            if cf.group('coins'):
                number_of_coin = int(cf.group('coins'))
            else:
                number_of_coin = 1
            string = ''
            for roll in range(0, number_of_coin):
                a = random.randrange(1,3)
                if a == 1:
                    string += 'H   '
                elif a == 2:
                    string += 'T   '
            self.sendMsg(channel, string)
