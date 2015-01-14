#!/usr/bin/env python

import template
import re, pickle, random, logging
from database import databaseManager as dbm

class loliManager():
    def initialize_loli(user, lolinick):
        sadism =     random.randrange(0, 11)
        masochism =  10-sadism
        breakpoint = random.randrange(80, 100)
        hitpoints =  round(random.randrange(60, 91)*(1-2*(sadism/100)+2*(masochism/100)))
        attack =     random.randrange(20, 31)
        defense =    random.randrange(20, 31)
        crit =       random.randrange(1, 4)
        counter =    random.randrange(10, 21)
        arch =       random.choice(['Yandere']*4+['Deredere']*24+['Tsundere']*24+['Kuudere']*24+['Dandere']*24)
        age =        random.randrange(8, 14)
        ## A fag named dreamcore contributed to helping come up with these algorithms ##
        height =     122 + (age-8)*6 + random.randrange(0,6)
        weight =     int(((height/100)(height/100)) * random.randrange(14-20))
        bust =       random.randrange(68, 86)  #Fix
        waist =      random.randrange(56, 77)  #Fix
        hip =        random.randrange(68, 89)  #Fix
        loligenerator = {
            'name':         lolinick,
            'level':               1,
            'exp':                 0,
            'S':              sadism,
            'M':           masochism,
            'breakpoint': breakpoint,
            'affection':           0,
            'archetype':        arch,
            'maxhp':       hitpoints,
            'currenthp':   hitpoints,
            'atk':            attack,
            'def':           defense,
            'crit':             crit,
            'counter':       counter,
            'felled':              0,
            'fainted':             0,
            'bust':             bust,
            'waist':           waist,
            'hip':               hip,
            'height':         height,
            'weight':         weight
            }
        userdb = dbm('user');
        userdb.load_database();
        userData, lolistats = userdb.load_parameter(user, 'loli', loligenerator);
        if lolistats != loligenerator:
            state = 'failure'
            lolistats = userData['loli']
            logging.info('**lm** <%s> Tried to generate a loli, but failed.' % user)
        else:
            userdb.save_database(user, userData);
            state = 'success'
            logging.info('**lm** <%s> Generated a loli' % user)
        return state, lolistats
    def release_loli(user):
        userdb = dbm('user');
        userdb.load_database();
        userData, lolistats = userdb.load_parameter(user, 'loli', None);
        try: 
            del userData['loli']
            userdb.save_database(user, userData);
            state = 'success'
            logging.info('**lm** <%s> Released a loli.' % user)
        except KeyError:
            state = 'failure'
            logging.info('**lm** <%s> Tried to release a loli, but failed.' % user)
        return state
    def loli_stats(user):
        userdb = dbm('user');
        userdb.load_database();
        userData, lolistats = userdb.load_parameter(user, 'loli', None);
        return lolistats

class IRCScript(template.IRCScript):
    print('loaded loli')
    def privmsg(self, user, channel, msg):
        if re.match('^-release\sloli', msg, re.I):
            state = loliManager.release_loli(user);
            if state == 'success':
                self.sendMsg(channel, user+' has left his loli on the side of the road and drove off into the sunset!')
            elif state == 'failure':
                self.sendNotice(user, "You don't have a loli to release.")
        statsmsg = re.match('^-stats(\s(?P<user>[^\s]+)|)', msg, re.I)
        if statsmsg:
            if statsmsg.group('user') == 'me' or statsmsg.group('user') == None:
                target = user
            else:
                target = statsmsg.group('user')
            stats = loliManager.loli_stats(target);
            if stats:
                self.sendNotice(user, '['+stats['archetype']+'] '+stats['name']+'    Lv'+str(stats['level']))
                self.sendNotice(user, 'S: '+str(stats['S'])+'          M: '+str(stats['S']))
                self.sendNotice(user, 'Hp: '+str(stats['currenthp'])+'/'+str(stats['maxhp']))
                self.sendNotice(user, 'Atk: '+str(stats['atk'])+'       Def: '+str(stats['def']))
                self.sendNotice(user, 'Crit: '+str(stats['crit'])+'       Counter: '+str(stats['counter']))
                self.sendNotice(user, 'Felled: '+str(stats['felled'])+'     Fainted: '+str(stats['fainted']))
            else:
                self.sendNotice(user, "I can't seem to find the loli.")
