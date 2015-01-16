#!/usr/bin/env python

import template
import re, pickle, random, operator
from database import databaseManager as dbm
from loli import loliManager as lm
from colorize import Colorize as c

userdb = dbm('user');
class tokenManager:
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

    def take_tokens(user, amount):
        userdb.load_database();
        userData, current_tokens = userdb.load_parameter(user, 'tokens', int("0"))
        if current_tokens >= amount:
            current_tokens -= amount
            userData['tokens'] = current_tokens
            userdb.save_database(user, userData)
            state = 'success'
        elif current_tokens < amount:
            state = 'failure'
        return state, current_tokens, amount
        
    def give_tokens(user, amount):
        userdb.load_database();
        userData, current_tokens = userdb.load_parameter(user, 'tokens', int("0"))
        if 'last_seen' in userData:
            current_tokens += amount
            userData['tokens'] = current_tokens
            userdb.save_database(user, userData)
            state = 'success'
        else:
            state = 'failure'
        return state, current_tokens, amount

    def token_circulation():
        data = userdb.load_database();
        token_total = 0
        for user in data:
            userData, current_tokens = userdb.load_parameter(user, 'tokens', int("0"))
            token_total += current_tokens
        return token_total
    
    def top_ten():
        data = userdb.load_database();
        token_array = {}
        for user in data:
            userData, current_tokens = userdb.load_parameter(user, 'tokens', int("0"))
            token_array.update({user:current_tokens})
        token_array = sorted(token_array.items(), key=operator.itemgetter(1), reverse=True)
        new_array=[]
        for x in range(0,10):
            try:
                new_array.append(token_array[x])
            except Exception as e:
                pass
        return new_array

class IRCScript(template.IRCScript):
    print('loaded tokens')
    def privmsg(self, user, channel, msg):
        if re.match('^-mine', msg, re.I):
            profit = tokenManager.mine(user)
            self.sendMsg(channel, user + ' mined ' + str(profit) + ' tokens.')
            
        looting = re.match('^-loot\s(?P<target>[^\s]+)$', msg, re.I)
        if looting:
            if looting.group('target') == 'me' or looting.group('target') == user:
                self.sendNotice(user, "You can't loot yourself!")
            else:
                target = looting.group('target')
                weighted_random = ['bs'] * 500 + ['nil'] * 50 + ['low'] * 30 + ['med'] * 10 + ['high'] * 5
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
                    state, target_tokens, amount = tokenManager.take_tokens(target, profit);
                    if state == 'failure' and target_tokens == 0:
                        self.sendNotice(user, target+" doesn't have any tokens.")
                    elif state == 'failure' and target_tokens > 0:
                        tokenManager.take_tokens(target, target_tokens);
                        tokenManager.give_tokens(user, target_tokens);
                        self.sendNotice(user, "You were able to nab "+str(target_tokens)+" tokens!")
                    elif state == 'success':
                        tokenManager.give_tokens(user, amount);
                        self.sendNotice(user, "You were able to nab "+str(amount)+" tokens!")
                elif profit < 0:
                    print('HAHA BITCH, you got rekt')
                    profit = -profit
                    state, user_tokens, amount = tokenManager.take_tokens(user, profit);
                    if state == 'failure' and user_tokens == 0:
                        tokenManager.give_tokens(user, 50);
                        self.sendNotice(user, "TT^TT Onii-chan, you are so poor that you have to resort to stealing. Here, I'll give you 50 tokens, so please return to being the onii-chan I know and love~!")
                    elif state == 'failure' and user_tokens > 0:
                        tokenManager.take_tokens(user, user_tokens);
                        tokenManager.give_tokens(target, user_tokens);
                        self.sendNotice(user, "The little wench noticed you! Lost "+str(user_tokens)+" tokens!")
                    elif state == 'success':
                        tokenManager.give_tokens(target, amount);
                        self.sendNotice(user, "The little wench noticed you! Lost "+str(amount)+" tokens!")
                else:
                    self.sendNotice(user, "Try as you might, you were too distracted by a wandering loli to loot.")
          
        ## Give ##
        giving = re.match('^-give\s(?P<target>[^\s]+)\s(?P<amount>\d+)$', msg, re.I)
        if giving:
            if giving.group('target') == 'me' or giving.group('target') == user:
                self.sendNotice(user, "You can't give yourself tokens!")
            else:
                target = giving.group('target')
                amount = int(giving.group('amount'))
                state, user_tokens, gift = tokenManager.take_tokens(user, amount);
                if state == 'failure' and user_tokens == 0:
                    self.sendNotice(user, "You don't have any tokens.")
                elif state == 'failure' and user_tokens > 0:
                    self.sendNotice(user, "You don't have that much.")
                elif state == 'success':
                    state, target_tokens, gift = tokenManager.give_tokens(target, amount);
                    if state == 'failure':
                        tokenManager.give_tokens(user, amount);
                        self.sendNotice(user, "I've never seen them before.")
                    else:
                        self.sendNotice(user, "You gave "+target+" "+str(amount)+" tokens. How nice of you~!")

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
            tokens = tokenManager.token_circulation();
            self.sendNotice(user, 'The Financial District has a total of '+str(tokens)+' tokens currently in circulation.')
        
        ## Top 10 ##
        if re.match('^-top10', msg, re.I):
            token_array = tokenManager.top_ten();
            msgstring=''
            toptenindex = 1
            for name in token_array:
                if toptenindex != 1:
                    msgstring += str(toptenindex)+') '+c.style(name[0], 'bold')+' ['+str(name[1])+'] | '
                else:
                    msgstring += str(toptenindex)+') '+c.style(c.rainbow(name[0]), 'bold')+' ['+str(name[1])+'] | '
                toptenindex += 1
            self.sendNotice(user, msgstring[:-3])

        ## Temporary Give/Take Tokens (Admin) ##
        powers = re.match('^\.(?P<action>(give|take))\s(?P<target>[^\s]+)\s(?P<amount>\d+)$', msg, re.I)
        if powers:
            target = powers.group('target')
            amount = int(powers.group('amount'))
            if powers.group('action') == 'give':
                tokenManager.give_tokens(target, amount);
            elif powers.group('action') == 'take':
                tokenManager.take_tokens(target, amount);
