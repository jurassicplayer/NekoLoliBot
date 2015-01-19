#!/usr/bin/env python

import template
import re, pickle
from database import databaseManager as dbm
from loli import loliManager as lm


userdb = dbm('user');

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
    print('loaded store')
    def privmsg(self, user, channel, msg):
        
        ## Store ##
        if re.match('^-store', msg, re.I):
            self.sendNotice(user, 'Welcome to the Flowercrest Department Store~!')
            for product in itemdb:
                self.sendNotice(user, product+': '+str(itemdb[product]['upp'])+' for '+str(itemdb[product]['price'])+' tokens.')

        ## Purchasing ##
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
                        self.sendMsg(channel, user+' has bought '+lolistats['name']+' the '+lolistats['deretype']+' '+lolistats['archetype']+'!')
                    elif state == 'failure':
                        self.sendNotice(user, 'You already have a loli~!')
                else:
                    self.sendNotice(user, "You need a name for your loli!")
            else:
                self.sendNotice(user, "I'm sorry, we don't have that item, maybe you can forward a request to management to put some in stock.")
