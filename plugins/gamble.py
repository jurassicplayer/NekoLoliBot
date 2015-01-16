#!/usr/bin/env python

import template
import re, pickle, random, logging
from database import databaseManager as dbm
from colorize import Colorize as c

userdb = dbm('user');
def colorize(hand):
    new_hand = []
    for card in hand:
        if card[-1] == '♠' or card[-1] == '♣':
            card = '\x0301,00'+card+'\x0f'
        elif card[-1] == '♥' or card[-1] == '♦':
            card = '\x0304,00'+card+'\x0f'
        new_hand.append(card)
    return new_hand

def add_hand(hand):
        total = 0
        for card in hand:
            card_value = card[:-1]
            if card_value == 'J' or card_value == 'Q' or card_value == 'K': 
                card_value = '10'
            elif card_value == 'A': 
                card_value = '11'
            total += int(card_value)
        if total > 21:
            total = 0
            for card in hand:
                card_value = card[:-1]
                if card_value == 'J' or card_value == 'Q' or card_value == 'K': 
                    card_value = '10'
                elif card_value == 'A': 
                    card_value = '1'
                total += int(card_value)
        return total
    
def diceroll(user, bet, call):
    userdb.load_database();
    userData, current_tokens = userdb.load_parameter(user, 'tokens', 0);
    if current_tokens >= bet:
        current_tokens -= bet
        dice = [random.randrange(1,7), random.randrange(1,7)]
        total = dice[0]+dice[1]
        if call == total:
            current_tokens += int(bet*2)
            end = 'winall'
        elif call == (total+1) or call == (total-1):
            current_tokens += int(bet+(bet/2))
            end = 'win'
        else:
            end = 'loss'
        userData['tokens'] = current_tokens
        userdb.save_database(user, userData);
        state = [dice, end]
    else:
        state = None
    return state
def cointoss(user, bet, call):
    userdb.load_database();
    userData, current_tokens = userdb.load_parameter(user, 'tokens', 0);
    if current_tokens >= bet:
        current_tokens -= bet
        coin = random.randrange(1,3)
        if coin == 1:
            coin = 'heads'
        elif coin == 2:
            coin = 'tails'
        if call == 'h' or call == 'heads' or call == 'head':
            call = 'heads'
        elif call == 't' or call == 'tails' or call == 'tail':
            call = 'tails'
        if call == coin:
            current_tokens += int(bet*2)
            end = 'win'
        else:
            end = 'loss'
        userData['tokens'] = current_tokens
        userdb.save_database(user, userData);
        state = [coin, end]
    else:
        state = None
    return state

class card_dealer():
    def deal_blackjack(user, bet):
        card_deck = [
        '2♠', '3♠', '4♠', '5♠', '6♠', '7♠', '8♠', '9♠', '10♠', 'J♠', 'Q♠', 'K♠', 'A♠',
        '2♥', '3♥', '4♥', '5♥', '6♥', '7♥', '8♥', '9♥', '10♥', 'J♥', 'Q♥', 'K♥', 'A♥',
        '2♣', '3♣', '4♣', '5♣', '6♣', '7♣', '8♣', '9♣', '10♣', 'J♣', 'Q♣', 'K♣', 'A♣',
        '2♦', '3♦', '4♦', '5♦', '6♦', '7♦', '8♦', '9♦', '10♦', 'J♦', 'Q♦', 'K♦', 'A♦'
        ]
        bet = int(bet)
        deck = card_deck
        random.shuffle(deck)
        player_hand = []
        dealer_hand = []
        player_hand.append(deck.pop())
        dealer_hand.append(deck.pop())
        player_hand.append(deck.pop())
        dealer_hand.append(deck.pop())
        game = {
            'player': player_hand,
            'dealer': dealer_hand,
            'deck': deck,
            'bet': bet
            }
        userdb.load_database();
        userData, current_game = userdb.load_parameter(user, 'blackjack', None);
        userData, current_tokens = userdb.load_parameter(user, 'tokens', 0);
        if current_game:
            game = 'ingame'
        elif current_tokens >= bet:
            userData['tokens'] = current_tokens - bet
            userData['blackjack'] = game
            userdb.save_database(user, userData);
            game['player'], game['dealer'] = colorize(player_hand), colorize(dealer_hand)
        else:
            game = None
        return game
        
    def blackjack_hit(user):
        userdb.load_database();
        userData, current_game = userdb.load_parameter(user, 'blackjack', None);
        if current_game:
            current_game['player'].append(current_game['deck'].pop())
            userData['blackjack'] = current_game
            userdb.save_database(user, userData);
            player_hand = current_game['player']
            dealer_hand = current_game['dealer']
            total = add_hand(player_hand)
            hands = [colorize(player_hand), colorize(dealer_hand)]
        else:
            hands = None
        return hands
        
    def blackjack_stand(user):
        userdb.load_database();
        userData, current_game = userdb.load_parameter(user, 'blackjack', None);
        if current_game:
            player_hand = current_game['player']
            dealer_hand = current_game['dealer']
            player_total = add_hand(player_hand)
            dealer_total = add_hand(dealer_hand)
            if dealer_total >= 17 and len(dealer_hand) >= 2:
                pass
            else:
                while dealer_total < 17:
                    dealer_hand.append(current_game['deck'].pop())
                    dealer_total = add_hand(dealer_hand)
            userData, current_tokens = userdb.load_parameter(user, 'tokens', 0)
            if dealer_total > 21:
                current_tokens += current_game['bet']*2
                result = ['win', colorize(player_hand), colorize(dealer_hand)]
            elif player_total > dealer_total:
                current_tokens += current_game['bet']*2
                result = ['win', colorize(player_hand), colorize(dealer_hand)]
            elif player_total < dealer_total:
                result = ['loss', colorize(player_hand), colorize(dealer_hand)]
            elif player_total == dealer_total:
                current_tokens += current_game['bet']
                result = ['tie', colorize(player_hand), colorize(dealer_hand)]
            del userData['blackjack']
            userData['tokens'] = int(current_tokens)
            userdb.save_database(user, userData);
        else:
            result = None
        return result
        
    def blackjack_double(user):
        userdb.load_database();
        userData, current_game = userdb.load_parameter(user, 'blackjack', None);
        userData, current_tokens = userdb.load_parameter(user, 'tokens', 0)
        if current_game and current_tokens >= current_game['bet']:
            current_game['player'].append(current_game['deck'].pop())
            current_tokens -= current_game['bet']
            current_game['bet'] *= 2
            userData['blackjack'] = current_game
            userData['tokens'] = current_tokens
            userdb.save_database(user, userData);
            player_hand = current_game['player']
            dealer_hand = current_game['dealer']
            total = add_hand(player_hand)
            hands = [colorize(player_hand), colorize(dealer_hand)]
        elif current_game and current_tokens < current_game['bet']:
            hands = 'notoken'
        else:
            hands = None
        return hands
                
    def blackjack_surrender(user):
        userdb.load_database();
        userData, current_game = userdb.load_parameter(user, 'blackjack', None);
        userData, current_tokens = userdb.load_parameter(user, 'tokens', 0)
        if current_game:
            current_tokens += int(current_game['bet']/2)
            player_hand = current_game['player']
            dealer_hand = current_game['dealer']
            userData['tokens'] = current_tokens
            del userData['blackjack']
            userdb.save_database(user, userData);
            losses = [int(current_game['bet']/2), colorize(player_hand), colorize(dealer_hand)]
        else:
            losses = None
        return losses
    
    def show_hand(user):
        userdb.load_database();
        userData, current_game = userdb.load_parameter(user, 'blackjack', None);
        print(current_game)
        if current_game:
            player_hand = current_game['player']
            print(player_hand)
            #state = colorize(player_hand)
            state = player_hand
        else:
            state = None
        return state
    
    def bust(user):
        userdb.load_database();
        userData, current_game = userdb.load_parameter(user, 'blackjack', None);
        total = add_hand(current_game['player'])
        if total > 21:
            state = current_game['player']
            del userData['blackjack']
            userdb.save_database(user, userData);
        else:
            state = None
        return state
        

class IRCScript(template.IRCScript):
    print('loaded gamble')
    def privmsg(self, user, channel, msg):
        
        ## Start Match ##
        bet_match = re.match('^-blackjack\s(?P<bet>\d+)$', msg, re.I)
        if bet_match:
            game = card_dealer.deal_blackjack(user, bet_match.group('bet'));
            if game and game != 'ingame':
                self.sendNotice(user, '['+' '.join(game['player'])+']')
            elif game and game == 'ingame':
                self.sendNotice(user, "You are currently in a game!")
            else:
                self.sendNotice(user, "You don't have the tokens to back up your bet.")
        ## Hitting ##
        if re.match('^-hit$', msg, re.I):
            hit = card_dealer.blackjack_hit(user);
            if hit:
                self.sendNotice(user, '['+' '.join(hit[0])+']')
                if card_dealer.bust(user):
                    self.sendMsg(channel, user+': '+c.style('You busted', 'bold')+' | D['+' '.join(hit[1])+'] U['+' '.join(hit[0])+']')
            else:
                self.sendNotice(user, "You currently aren't in a game.")
        ## Standing ## 
        if re.match('^-sta(nd|y)$', msg, re.I):
            stand = card_dealer.blackjack_stand(user);
            if stand[0] == 'win':
                self.sendMsg(channel, user+': '+c.style('You win', 'bold')+' | D['+' '.join(stand[2])+'] U['+' '.join(stand[1])+']')
            elif stand[0] == 'loss':
                self.sendMsg(channel, user+': '+c.style('You lose', 'bold')+' | D['+' '.join(stand[2])+'] U['+' '.join(stand[1])+']')
            elif stand[0] == 'tie':
                self.sendMsg(channel, user+': '+c.style('You tied, your bet was returned', 'bold')+' | D['+' '.join(stand[2])+'] U['+' '.join(stand[1])+']')
            else:
                self.sendNotice(user, "You currently aren't in a game.")
        ## Doubling Down ##     
        if re.match('^-double$', msg, re.I):
            double = card_dealer.blackjack_double(user);
            if double and double != 'notoken':
                self.sendNotice(user, '['+' '.join(double[0])+']')
                if card_dealer.bust(user):
                    self.sendMsg(channel, user+': '+c.style('You busted', 'bold')+' | D['+' '.join(double[1])+'] U['+' '.join(double[0])+']')
            elif double and double == 'notoken':
                self.sendNotice(user, "You don't have the tokens to back up your bet.")
            else:
                self.sendNotice(user, "You currently aren't in a game.")
        ## Surrendering ##
        if re.match('^-(surrender|ff)$', msg, re.I):
            surrender = card_dealer.blackjack_surrender(user);
            if surrender:
                self.sendMsg(channel, user+': '+c.style('You surrendered, half your bet was returned', 'bold')+' | D['+' '.join(surrender[2])+'] U['+' '.join(surrender[1])+']')
            else:
                self.sendNotice(user, "You currently aren't in a game.")
        ## Show hand ##
        if re.match('^-show$', msg, re.I):
            show = card_dealer.show_hand(user);
            if show:
                self.sendNotice(channel, 'U['+' '.join(show)+']')
            else:
                self.sendNotice(user, "You currently aren't in a game.")
        
        
        ## Probability Games ##
        #- Dice -#
        dice = re.match('^-dicebet\s(?P<bet>\d+)\s(?P<call>0?[1-9]|1[0-2])$', msg, re.I)
        if dice:
            result = diceroll(user, int(dice.group('bet')), int(dice.group('call')));
            if result and result[1] == 'winall':
                self.sendMsg(channel, user+': '+c.style('You win full bet!', 'bold')+' | '+' '.join(str(result[0])))
            elif result and result[1] == 'win':
                self.sendMsg(channel, user+': '+c.style('You win half bet', 'bold')+' | '+' '.join(str(result[0])))
            elif result and result[1] == 'loss':
                self.sendMsg(channel, user+': '+c.style('You lose', 'bold')+' | '+' '.join(str(result[0])))
            else:
                self.sendNotice(user, "You don't have the tokens to back up your bet.")
                
                
        #- Coin Flip -#
        ct = re.match('^-coinbet\s(?P<bet>\d+)\s(?P<call>(h|t|head(s|)|tail(s|)))$', msg, re.I)
        if ct:
            result = cointoss(user, int(ct.group('bet')), ct.group('call').lower());
            if result and result[1] == 'win':
                self.sendMsg(channel, user+': '+c.style('You win', 'bold')+' | ['+str(result[0])+']')
            elif result and result[1] == 'loss':
                self.sendMsg(channel, user+': '+c.style('You lose', 'bold')+' | ['+str(result[0])+']')
            else:
                self.sendNotice(user, "You don't have the tokens to back up your bet.")
