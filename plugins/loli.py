#!/usr/bin/env python

import template
import re, pickle, random, logging
from database import databaseManager as dbm

class loliManager:
    def initialize_loli(user, lolinick):
        sadism =     random.randrange(0, 11)
        masochism =  10-sadism
        breakpoint = random.randrange(80, 100)
        hitpoints =  round(random.randrange(60, 91)*(1-2*(sadism/100)+2*(masochism/100)))
        attack =     random.randrange(20, 31)
        defense =    random.randrange(20, 31)
        crit =       random.randrange(1, 4)
        counter =    random.randrange(10, 21)
        dere =       random.choice(['Yandere']*2+['Deredere']*24+['Tsundere']*24+['Kuudere']*24+['Dandere']*24)
        accent =     random.choice([
            'Red tongue',
            "Philosopher's Stone",
            'Wrist Telecommunicator',
            'Flower Blossom',
            'Bionic Eye',
            'Halo',
            'Armguard',
            '',
            'Hammer',
            'Bunny Suit',
            "Cat's Bell",
            'Cowbell',
            'Exoskeleton',
            'Ahoge',
            '',
            'Staff',
            '',
            'Bent Spoon',
            'Petite Wings',
            'Megane',
            'Will-o-wisps',
            '',
            'Microphone',
            'Sickle',
            'Shield',
            'Wakizashi',
            '',
            'Magic Wand',
            'Headdress',
            'Roots',
            'Seashells',
            'Gohei',
            'Bandages',
            'Necronomicon',
            '',
            'Habit',
            'Syringe',
            'Zettai Ryouiki',
            'Club',
            'Talisman',
            'Otaku-ware',
            'Cap',
            'Pirate Hat',
            'Tarot Cards',
            'Lingerie',
            'Golem',
            'Shakujo',
            'Dagger',
            'Goblet',
            'Familiar',
            'Kansai-ben',
            'Snowflake',
            'Bloodied Clothes',
            'Nekomimi',
            'Twintails'
            ])
        archetype =  random.choice([
            'Akaname',
            'Alchemist',
            'Alien',
            'Alraune',
            'Android', 
            'Angel', 
            'Archer',
            'Assassin',
            'Blacksmith',
            'Bunnygirl',
            'Catgirl', 
            'Cowgirl'
            'Cyborg', 
            'Denpa', 
            'Dragon',
            'Druid',
            'Dryad',
            'ESPer',
            'Fairy',
            'Genius',
            'Ghost', 
            'Harpy',
            'Idol',
            'Kamaitachi',
            'Knight',
            'Kunoichi', 
            'Lamia', 
            'Mahou Shoujo', 
            'Maid',
            'Mandragora',
            'Mermaid', 
            'Miko',
            'Mummy',
            'Necromancer',
            'Nekomata',
            'Nun', 
            'Nurse', 
            'Ojou-sama',
            'Oni',
            'Onmyouji', 
            'Otaku', 
            'Otokonoko',
            'Pirate',
            'Seer',
            'Succubus',
            'Summoner',
            'Tengu',
            'Thief',
            'Vampire', 
            'Witch', 
            'Yankee',
            'Yuki-onna',
            'Zombie'
            ])
        age =        random.randrange(8, 14)
        ## A fag named dreamcore contributed to helping come up with these algorithms ##
        height =     round(122 + (age-8)*6 + random.randrange(0,6))  #cm
        weight =     round((height/100) * (height/100) * random.randrange(int(14+((age-8)*1.5/5)), int(18+((age-8)*3/5))))  #kg
        waist =      round( 56 + (age-8)*3 + ((height*weight/(height+weight))-(17+(age-8)*3)) + random.randrange(0,3))    # Smallest size 56-77
        bust =       round( 64 + (age-8)*3 + ((height*weight/(height+weight))-(17+(age-8)*3)) + random.randrange(0,3))     #random.randrange(waist-56+66, 86)  # Range from waist to upper limit
        hip =        round( 68 + (age-8)*3 + ((height*weight/(height+weight))-(17+(age-8)*3)) + random.randrange(0,3))    #random.randrange(waist-56+68, 89)  # Range from waist to upper limit
        loligenerator = {
            'name':         lolinick,
            'level':               1,
            'exp':                 0,
            'S':              sadism,
            'M':           masochism,
            'breakpoint': breakpoint,
            'affection':           0,
            'deretype':         dere,
            'accent':         accent,
            'archetype':   archetype,
            'maxhp':       hitpoints,
            'currenthp':   hitpoints,
            'atk':            attack,
            'def':           defense,
            'crit':             crit,
            'counter':       counter,
            'felled':              0,
            'fainted':             0,
            'age':               age,
            'height':         height,
            'weight':         weight,
            'bust':             bust,
            'waist':           waist,
            'hip':               hip
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
    def heal_loli(user, amount):
        userdb = dbm('user');
        userdb.load_database();
        userData, lolistats = userdb.load_parameter(user, 'loli', None);
        if lolistats:
            hp_lost = lolistats['maxhp'] - lolistats['currenthp']
            if hp_lost is 0:
                state = 'fullhp'
            elif hp_lost >= amount:
                lolistats['currenthp'] += amount
                userData['loli'] = lolistats
                userdb.save_database(user, userData)
                state = 'success'
            elif hp_lost < amount:
                lolistats['currenthp'] = lolistats['maxhp']
                userData['loli'] = lolistats
                userdb.save_database(user, userData)
                state = 'success'
        else:
            state = 'failure'
        return state
    def damage_loli(user, amount):
        userdb = dbm('user');
        userdb.load_database();
        userData, lolistats = userdb.load_parameter(user, 'loli', None);
        if lolistats:
            current_hp = lolistats['currenthp']
            if current_hp is 0:
                state = 'zerohp'
            elif current_hp > amount:
                lolistats['currenthp'] -= amount
                userData['loli'] = lolistats
                userdb.save_database(user, userData)
                state = 'success'
            elif current_hp <= amount:
                lolistats['currenthp'] = int('0')
                lolistats['fainted'] += 1
                userData['loli'] = lolistats
                userdb.save_database(user, userData)
                state = 'knockout'
        else:
            state = 'failure'
        return state
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
        if re.match('^!loli\srelease', msg, re.I):
            state = loliManager.release_loli(user);
            if state == 'success':
                self.sendMsg(channel, user+' has left his loli on the side of the road and drove off into the sunset!')
            elif state == 'failure':
                self.sendNotice(user, "You don't have a loli to release.")
        statsmsg = re.match('^!lolistat(\s(?P<user>[^\s]+)|)', msg, re.I)
        if statsmsg:
            if statsmsg.group('user') == 'me' or statsmsg.group('user') == None:
                target = user
            else:
                target = statsmsg.group('user')
            stats = loliManager.loli_stats(target);
            if stats:
                self.sendNotice(user, '[%s] %s the %s [Equip: %s]' % (stats['deretype'], stats['name'], stats['archetype'], stats['accent']))
                self.sendNotice(user, '[Age: %s][H: %s][W: %s][BWH: %s-%s-%s]' % (stats['age'], stats['height'], stats['weight'], stats['bust'], stats['waist'], stats['hip']))
                self.sendNotice(user, '[Lv: %s][Hp: %s/%s][S: %s][M: %s][Atk: %s][Def: %s][Crit: %s][Counter: %s]' % (stats['level'], stats['currenthp'], stats['maxhp'], stats['S'], stats['M'], stats['atk'], stats['def'], stats['crit'], stats['counter']))
                self.sendNotice(user, '[Felled: %s][Fainted: %s]' % (stats['felled'], stats['fainted']))
            else:
                self.sendNotice(user, "I can't seem to find the loli.")
        if re.match('^-revive', msg, re.I):
            state = loliManager.heal_loli(user, 999999999);
        if re.match('^-smite', msg, re.I):
            state = loliManager.damage_loli(user, 999999999);
