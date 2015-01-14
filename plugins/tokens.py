#!/usr/bin/env python

import template
import re, pickle, random
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

def mine(user):
    userdb.load_database();
    userData, current_tokens = userdb.load_parameter(user, 'tokens', int("0"))
    weighted_random = ['low'] * 70 + ['med'] * 20 + ['high'] * 10
    weight = random.choice(weighted_random)
    if weight == 'low':
        profit = random.randint(2,15)
    elif weight == 'med':
        profit = random.randint(16,35)
    elif weight == 'high':
        profit = random.randint(40,55)
    userData['tokens'] += profit
    userdb.save_database(user, userData);
    return profit

def token_circulation():
    data = userdb.load_database();
    token_total = 0
    for user in data:
        userData, current_tokens = userdb.load_parameter(user, 'tokens', int("0"))
        token_total += current_tokens
    return token_total

class IRCScript(template.IRCScript):
    print('loaded tokens')
    def privmsg(self, user, channel, msg):
        if re.match('^-mine', msg, re.I):
            profit = mine(user)
            self.sendMsg(channel, user + ' mined ' + str(profit) + ' tokens.')
            
        looting = re.match('^-loot\s(?P<target>[^\s]+)$', msg, re.I)
        if looting:
            if looting.group('target') == 'me' or looting.group('target') == user:
                self.sendNotice(user, "You can't loot yourself!")
            elif looting.group('target') == self.NICK:
                self.sendNotice(user, "Surely you aren't planning on looting from your own loli.")
            else:
                target = looting.group('target')
                userdb.load_database();
                userData, current_tokens = userdb.load_parameter(user, 'tokens', int("0"))
                targetData, target_tokens = userdb.load_parameter(target, 'tokens', int("0"))
                if target_tokens > 0:
                    weighted_random = ['bs'] * 5 + ['nil'] * 50 + ['low'] * 30 + ['med'] * 10 + ['high'] * 5
                    weight = random.choice(weighted_random)
                    ## Determine profit ##
                    if weight == 'bs':
                        profit = -(random.randint(600,1000))
                    elif weight == 'nil':
                        profit = int('0')
                    elif weight == 'low':
                        profit = random.randint(50,150)
                    elif weight == 'med':
                        profit = random.randint(200,300)
                    elif weight == 'high':
                        profit = random.randint(300,500)
                    ## Check if both users have enough ##
                    if profit > 0:
                        if target_tokens >= profit:
                            target_tokens -= profit
                            current_tokens += profit
                            self.sendNotice(user, "You were able to nab "+str(profit)+" tokens!")
                        elif target_tokens < profit:
                            self.sendNotice(user, "You were able to nab "+str(target_tokens)+" tokens!")
                            current_tokens += target_tokens
                            target_tokens = int('0')
                    elif profit < 0:
                        print('HAHA BITCH, you got rekt')
                        profit = -profit
                        if current_tokens >= profit:
                            current_tokens -= profit
                            target_tokens += profit
                            self.sendNotice(user, "The little wench noticed you! Lost "+str(profit)+" tokens!")
                        elif current_tokens < profit:
                            self.sendNotice(user, "The little wench noticed you! Lost "+str(current_tokens)+" tokens!")
                            target_tokens += current_tokens
                            current_tokens = int('0')
                    else:
                        self.sendNotice(user, "Try as you might, you were too distracted by a wandering loli to loot.")
                    userData['tokens'] = current_tokens
                    targetData['tokens'] = target_tokens
                    userdb.save_database(user, userData)
                    userdb.save_database(target, targetData)
                else:
                    self.sendNotice(user, target+" doesn't have any tokens.")
          
        ## Give ##
        giving = re.match('^-give\s(?P<target>[^\s]+)\s(?P<amount>\d+)$', msg, re.I)
        if giving:
            if giving.group('target') == 'me' or giving.group('target') == user:
                self.sendNotice(user, "You can't give yourself tokens!")
            elif giving.group('target') == self.NICK:
                self.sendNotice(user, "I'll really take it you know.")
            else:
                target = giving.group('target')
                amount = int(giving.group('amount'))
                userdb.load_database();
                userData, current_tokens = userdb.load_parameter(user, 'tokens', int("0"))
                targetData, target_tokens = userdb.load_parameter(target, 'tokens', int("0"))
                if 'last_seen' in targetData:
                    if current_tokens >= amount and amount != 0:
                        current_tokens -= amount
                        target_tokens += amount
                        userData['tokens'] = current_tokens
                        targetData['tokens'] = target_tokens
                        userdb.save_database(user, userData)
                        userdb.save_database(target, targetData)
                    elif current_tokens < amount and amount != 0:
                        self.sendNotice(user, "You don't have enough tokens!")
                    else:
                        self.sendNotice(user, "I'll give you nothing.")
                else:
                    self.sendNotice(user, "I've never seen them before.")
        ## Balance ##
        balanced = re.match('^-balance(\s(?P<target>[^\s]+)|)', msg, re.I)
        if balanced:
            if balanced.group('target') == 'me' or balanced.group('target') == None:
                target = user
            else:
                target = balanced.group('target')
            userdb.load_database();
            userData, current_tokens = userdb.load_parameter(target, 'tokens', int("0"))
            self.sendMsg(channel, target + ' has ' + str(current_tokens) + ' tokens.')
            
        ## Token Circulation ##
        if re.match('^-tokens', msg, re.I):
            tokens = token_circulation();
            self.sendNotice(user, 'The Financial District has a total of '+str(tokens)+' tokens currently in circulation.')
        
        ## Store ##
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
