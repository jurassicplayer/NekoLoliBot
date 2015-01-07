#!/usr/bin/env python

import template
import re, pickle, random
from dbmanager import databaseManager as dbm
from loli import loliManager as lm

# price, unit-per-price, sale price, 
itemdb = {
    'loli':       {'price': 1000, 'upp': 1,  'sale': 100},
    'an-pan':     {'price': 50,   'upp': 1,  'sale': 100},
    'candy':      {'price': 50,   'upp': 10, 'sale': 100},
    'dango':      {'price': 50,   'upp': 3,  'sale': 100},
    'meron-pan':  {'price': 50,   'upp': 1,  'sale': 100},
    'mochi':      {'price': 50,   'upp': 6,  'sale': 100},
    'pocky':      {'price': 50,   'upp': 20, 'sale': 100},
    'tea':        {'price': 50,   'upp': 1,  'sale': 100}
    }

class IRCScript(template.IRCScript):
    print('loaded tokens')
    def privmsg(self, user, channel, msg):
        if re.match('^-mine', msg, re.I):
            userdb = dbm.load_database(user);
            userdb, current_tokens = dbm.load_parameter(userdb, 'tokens', 0)
            weighted_random = ['low'] * 70 + ['med'] * 20 + ['high'] * 10
            weight = random.choice(weighted_random)
            if weight == 'low':
                profit = random.randint(2,15)
            elif weight == 'med':
                profit = random.randint(16,35)
            elif weight == 'high':
                profit = random.randint(40,55)
            userdb['tokens'] += profit
            dbm.save_database(user, userdb);
            self.sendMsg(channel, user + ' mined ' + str(profit) + ' tokens.')
        balanced = re.match('^-balance(\s(?P<target>[^\s]+)|)', msg, re.I)
        if balanced:
            if balanced.group('target') == 'me' or balanced.group('target') == None:
                target = user
            else:
                target = balanced.group('target')
            userdb = dbm.load_database(target);
            userdb, current_tokens = dbm.load_parameter(userdb, 'tokens', 0)
            self.sendMsg(channel, target + ' has ' + str(current_tokens) + ' tokens.')
        if re.match('^-store', msg, re.I):
            self.sendNotice(user, 'Welcome to the Flowercrest Department Store~!')
            for product in itemdb:
                self.sendNotice(user, product+': '+str(itemdb[product]['upp'])+' for '+str(itemdb[product]['price'])+' tokens.')
        
        purchasing = re.match('^-(buy|purchase)(\s(?P<quantity>0?[1-9]|[1-9][0-9])\s|\s)(?P<item>[^\s]+)(\s(?P<nick>[^\s]+)|)$', msg, re.I)
        if purchasing:
            if purchasing.group('item') in itemdb and purchasing.group('item') != 'loli' and purchasing.group('quantity') != None:
                self.sendMsg(channel, 'Purchased '+str(purchasing.group('quantity'))+' '+purchasing.group('item')+'(s).')
            elif purchasing.group('item') in itemdb and purchasing.group('item') != 'loli' and purchasing.group('quantity') == None:
                self.sendMsg(channel,'Purchased '+purchasing.group('item')+'.')
            elif purchasing.group('item') in itemdb and purchasing.group('item') == 'loli' and purchasing.group('quantity') != None:
                self.sendNotice(user, 'You can only purchase a single loli!')
            elif purchasing.group('item') in itemdb and purchasing.group('item') == 'loli' and purchasing.group('quantity') == None:
                if purchasing.group('nick'):
                    state, lolistats = lm.initialize_loli(user, purchasing.group('nick'))
                    if state == 'success':
                        self.sendNotice(user, '['+lolistats['name']+']: Please take care of me. *bow*')
                        self.sendMsg(channel, user+' has bought a new loli!')
                    elif state == 'failure':
                        self.sendNotice(user, 'You already have a loli~!')
                else:
                    self.sendNotice(user, "You need a name for your loli!")
            else:
                self.sendNotice(user, "I'm sorry, we don't have that item, maybe you can forward a request to management to put some in stock.")
