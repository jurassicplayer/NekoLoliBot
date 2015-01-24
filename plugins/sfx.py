#!/usr/bin/env python

import template
import re, random

zombie_sfx = [
    'Graagh!',
    'Urrrggh!',
    'Auuugh!',
    'Uuhhhhg!',
    'Mazzagrh!',
    'Zgaarah!',
    'Hnzmzgnnzb!',
    'OOARRGH!',
    '*nom nom nom*',
    'Uunnnnggg!',
    'Wrookkk!',
    'Shlukkk!'  
    ]
ghost_sfx = [
    'Whoo-oo-oo-oo~!',
    'Hyu-dorodoro~!',
    'Boo!',
    'Ooo-oo-oo~! Spooky!',
    'Kowaii~',
    'Whoaaargh~!',
    'Uunnggg~!',
    'Oooaaggghhh~!',
    'Ghhaaaaaa~!'
    ]
laugh_sfx = [
    'Eeh-he-heh~',
    'Hah-ha-ha~',
    'Pfuu-hu-hu~',
    'Ufu-fu-fu~',
    'Uwa-ha-ha~',
    'Aha-ha-ha~',
    'Mhm-hm-hm~',
    'Oho-ho-ho~',
    'Hoh-ho-ho~',
    'Ni-shi-shi-shi~',
    'Ka ka~',
    'Nya-ha-ha~',
    'Ku-ku-ku~',
    'Doh-ho-ho~'
    ]

class IRCScript(template.IRCScript):
    print('loaded sfx')
    def privmsg(self, user, channel, msg):
        if re.match('.*(zombie|undead|ghoul).*', msg, re.I):
            replying = random.choice(['reply']*3+['']*7)
            if 'reply' in replying:
                reply = random.choice(zombie_sfx)
                self.sendMsg(channel, reply)
        if re.match('.*ghost.*', msg, re.I):
            replying = random.choice(['reply']*3+['']*7)
            if 'reply' in replying:
                reply = random.choice(ghost_sfx)
                self.sendMsg(channel, reply)
        if re.match('.*(hah|HUE|kek|kuku|fufu|lolo|lel|rofl|lulz).*', msg, re.I):
            replying = random.choice(['reply']*3+['']*7)
            if 'reply' in replying:
                reply = random.choice(laugh_sfx)
                self.sendMsg(channel, reply)
