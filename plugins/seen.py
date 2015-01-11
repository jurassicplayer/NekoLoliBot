#!/usr/bin/env python

import template
import re, time
from dbmanager import databaseManager as dbm

def update_seen(user):
    userdb = dbm.load_database(user);
    userdb, lastseen = dbm.load_parameter(userdb, 'last_seen', None);
    current_time = (int(time.strftime('%j'))*24*60*60)+(int(time.strftime('%H'))*60*60)+(int(time.strftime('%M'))*60)+int(time.strftime('%S'))
    userdb['last_seen'] = current_time
    dbm.save_database(user, userdb);

def last_seen(user):
    userdb = dbm.load_database(user);
    userdb, lastseen = dbm.load_parameter(userdb, 'last_seen', None);
    current_time = (int(time.strftime('%j'))*24*60*60)+(int(time.strftime('%H'))*60*60)+(int(time.strftime('%M'))*60)+int(time.strftime('%S'))
    if lastseen:
        diff_in_sec = current_time - lastseen
        days = int(diff_in_sec/24/60/60)
        hours = int(diff_in_sec/60/60 - days*24)
        minutes = int(diff_in_sec/60 - days*24*60 - hours*60)
        seconds = int(diff_in_sec - days*24*60*60 - hours*60*60 - minutes*60)
        diff = ''
        if days >= 1:
            diff += str(days)+' day(s) '
        if hours >= 1:
            diff += str(hours)+'h '
        if minutes >= 1:
            diff += str(minutes)+'m '
        if seconds >=1:
            diff += str(seconds)+'s '
    else:
        diff = None
    return diff

class IRCScript(template.IRCScript):
    print('loaded seen')
    def privmsg(self, user, channel, msg): 
        try:
            if user.find('.') !=-1 or user.find('py-ctcp') !=-1:
                pass
            else:
                update_seen(user);
        except AttributeError:
            pass
        seen = re.match('^.seen\s(?P<user>[^\s]+)', msg, re.I)
        if seen:
            lastseen = last_seen(seen.group('user'));
            if lastseen and (seen.group('user') == user) or (seen.group('user') == 'me'):
                self.sendMsg(channel, "If you keep asking me that, the last time you will be seen will be in the hospital.")
            elif lastseen and (seen.group('user') == self.nick) or (seen.group('user') == 'yourself') or (seen.group('user') == 'you'):
                self.sendMsg(channel, "I'm going to slap you if you keep this up.")
            elif lastseen and seen.group('user') != user:
                self.sendMsg(channel, seen.group('user')+' was last seen '+str(lastseen)+'ago.')
            else:
                self.sendMsg(channel, "I haven't seen them. Maybe I forgot.")
    def action(self, user, channel, msg): 
        if user.find('.') !=-1 or user.find('py-ctcp') !=-1:
            pass
        else:
            update_seen(user);
    def userJoined(self, user, channel):
        if user.find('.') !=-1 or user.find('py-ctcp') !=-1:
            pass
        else:
            update_seen(user);
