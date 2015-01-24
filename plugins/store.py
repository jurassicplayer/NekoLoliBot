#!/usr/bin/env python

import template
import re, pickle
from database import databaseManager as dbm
from loli import loliManager as lm
from tokens import tokenManager as tm

itemdb = {
            'loli':       {'price': 1000, 'upp': 1,  'sale': 0},
            'an-pan':     {'price': 50,   'upp': 1,  'sale': 0},
            'candy':      {'price': 50,   'upp': 10, 'sale': 0},
            'dango':      {'price': 50,   'upp': 3,  'sale': 0},
            'meron-pan':  {'price': 50,   'upp': 1,  'sale': 0},
            'mochi':      {'price': 50,   'upp': 6,  'sale': 0},
            'pocky':      {'price': 50,   'upp': 20, 'sale': 0},
            'tea':        {'price': 50,   'upp': 1,  'sale': 0}
            }
   
class storeManager:
    def __init__(self, itemdb):
        self.userdb = dbm('user');
        # price, unit-per-price, sale price, 
        self.itemdb = itemdb
            
    def buy_item(self, user, item, quantity, *args):
        lolistat = None
        token = tm()
        if item in self.itemdb:
            sale_price = round((self.itemdb[item]['price'] - (self.itemdb[item]['price'] * self.itemdb[item]['sale'] / 100)) * quantity)
        if item != 'loli' and item in self.itemdb:
            tokenstate, current_tokens, amount = token.take_tokens(user, sale_price)
            if tokenstate == 'success':
                print('Give item')
                state = 2
            elif tokenstate == 'failure':
                print('Not enough tokens')
                state = 1
        elif item == 'loli' and quantity == 1:
            tokenstate, current_tokens, amount = token.take_tokens(user, sale_price)
            if tokenstate == 'success':
                try:
                    name = re.match('^[^\s]+', args[0], re.I)
                    state, lolistats = lm.initialize_loli(user, args[0])
                    if state == 'success':
                        lolistat = lolistats
                        print('Give the loli')
                    state = 3
                except:
                    token.give_tokens(user, sale_price)
                    print('Loli needs a name')
                    state = 4
            elif tokenstate == 'failure':
                print('Not enough tokens')
                state = 1
        elif item == 'loli' and quantity > 1:
            print('Not more than one loli')
            state = 5
        else:
            print('Item not in db')
            state = 6
        return state, lolistat
            
    def give_item(self, user, item, quantity):
        print('Give item')

    def set_sale(self, item, sale):
        if item in self.itemdb:
            self.itemdb[item]['sale'] = sale
            print('Set sale value')
        return self.itemdb

class IRCScript(template.IRCScript):
    print('loaded store')
    def privmsg(self, user, channel, msg):
        ## Store ##
        if re.match('^-store', msg, re.I):
            store = storeManager(itemdb)
            self.sendNotice(user, 'Welcome to the Flowercrest Department Store~!')
            for product in store.itemdb:
                if store.itemdb[product]['sale'] != 0:
                    sale_price = round(store.itemdb[product]['price'] - (store.itemdb[product]['price'] * store.itemdb[product]['sale'] / 100))
                    self.sendNotice(user, product+': '+str(store.itemdb[product]['upp'])+' on SALE for '+str(sale_price)+' tokens. ' + str(store.itemdb[product]['sale']) + '% off!')
                else:
                    sale_price = store.itemdb[product]['price']
                    self.sendNotice(user, product+': '+str(store.itemdb[product]['upp'])+' for '+str(sale_price)+' tokens.')

        ## Purchasing ##
        purchasing = re.match('^-(buy|purchase)(\s(?P<quantity>0?[1-9]|[1-9][0-9])\s|\s)(?P<item>[^\s]+)(\s(?P<nick>[^\s]+)|)$', msg, re.I)
        if purchasing:
            store = storeManager(itemdb)
            item = purchasing.group('item')
            if purchasing.group('quantity'):
                quantity = int(purchasing.group('quantity'))
            else:
                quantity = 1
            state, lolistats = store.buy_item(user, item, quantity, purchasing.group('nick'))
            if state == 1:
                self.sendNotice(user, "You don't have enough tokens!")
            elif state == 2:
                self.sendMsg(channel, 'Purchased '+str(quantity)+' '+purchasing.group('item')+'(s).')
            elif state == 3:
                if lolistats:
                    self.sendNotice(user, '['+lolistats['name']+']: Please take care of me. *bow*')
                    self.sendMsg(channel, user+' has bought '+lolistats['name']+' the '+lolistats['deretype']+' '+lolistats['archetype']+'!')
                else:
                    self.sendNotice(user, 'You already have a loli~!')
            elif state == 4:
                self.sendNotice(user, "You need a name for your loli!")
            elif state == 5:
                self.sendNotice(user, 'You can only purchase a single loli!')
            elif state == 6:
                self.sendNotice(user, "I'm sorry, we don't have that item, maybe you can forward a request to management to put some in stock.")

        discount = re.match('-sale\s(?P<item>\w+)\s(?P<amount>\d+)$', msg, re.I)
        if discount:
            store = storeManager(itemdb)
            new_itemdb = store.set_sale(discount.group('item'), int(discount.group('amount')))
            itemdb.update(new_itemdb)
