#!/usr/bin/env python

import template
import re, pickle, random, logging
from dbmanager import databaseManager as dbm



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
    userdb = dbm.load_database(user);
    userdb, current_tokens = dbm.load_parameter(userdb, 'tokens', 0);
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
        userdb['tokens'] = current_tokens
        dbm.save_database(user, userdb);
        state = [dice, end]
    else:
        state = None
    return state
def cointoss(user, bet, call):
    userdb = dbm.load_database(user);
    userdb, current_tokens = dbm.load_parameter(userdb, 'tokens', 0);
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
        userdb['tokens'] = current_tokens
        dbm.save_database(user, userdb);
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
        userdb = dbm.load_database(user);
        userdb, current_game = dbm.load_parameter(userdb, 'blackjack', None);
        userdb, current_tokens = dbm.load_parameter(userdb, 'tokens', 0);
        if current_game:
            game = 'ingame'
        elif current_tokens >= bet:
            userdb['tokens'] = current_tokens - bet
            userdb['blackjack'] = game
            dbm.save_database(user, userdb);
            game['player'], game['dealer'] = colorize(player_hand), colorize(dealer_hand)
        else:
            game = None
        return game
        
    def blackjack_hit(user):
        userdb = dbm.load_database(user);
        userdb, current_game = dbm.load_parameter(userdb, 'blackjack', None);
        if current_game:
            current_game['player'].append(current_game['deck'].pop())
            userdb['blackjack'] = current_game
            dbm.save_database(user, userdb);
            player_hand = current_game['player']
            dealer_hand = current_game['dealer']
            total = add_hand(player_hand)
            hands = [colorize(player_hand), colorize(dealer_hand)]
        else:
            hands = None
        return hands
        
    def blackjack_stand(user):
        userdb = dbm.load_database(user);
        userdb, current_game = dbm.load_parameter(userdb, 'blackjack', None);
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
            userdb, current_tokens = dbm.load_parameter(userdb, 'tokens', 0)
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
            del userdb['blackjack']
            userdb['tokens'] = int(current_tokens)
            dbm.save_database(user, userdb);
        else:
            result = None
        return result
        
    def blackjack_double(user):
        userdb = dbm.load_database(user);
        userdb, current_game = dbm.load_parameter(userdb, 'blackjack', None);
        userdb, current_tokens = dbm.load_parameter(userdb, 'tokens', 0)
        if current_game and current_tokens >= current_game['bet']:
            current_game['player'].append(current_game['deck'].pop())
            current_tokens -= current_game['bet']
            current_game['bet'] *= 2
            userdb['blackjack'] = current_game
            userdb['tokens'] = current_tokens
            dbm.save_database(user, userdb);
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
        userdb = dbm.load_database(user);
        userdb, current_game = dbm.load_parameter(userdb, 'blackjack', None);
        userdb, current_tokens = dbm.load_parameter(userdb, 'tokens', 0);
        if current_game:
            current_tokens += int(current_game['bet']/2)
            player_hand = current_game['player']
            dealer_hand = current_game['dealer']
            userdb['tokens'] = current_tokens
            del userdb['blackjack']
            dbm.save_database(user, userdb);
            losses = [int(current_game['bet']/2), colorize(player_hand), colorize(dealer_hand)]
        else:
            losses = None
        return losses
    
    def show_hand(user):
        userdb = dbm.load_database(user);
        userdb, current_game = dbm.load_parameter(userdb, 'blackjack', None);
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
        userdb = dbm.load_database(user);
        userdb, current_game = dbm.load_parameter(userdb, 'blackjack', None);
        total = add_hand(current_game['player'])
        if total > 21:
            state = current_game['player']
            del userdb['blackjack']
            dbm.save_database(user, userdb);
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
                    self.sendMsg(channel, 'D['+' '.join(hit[1])+'] U['+' '.join(hit[0])+'] '+user+' went bust!')
            else:
                self.sendNotice(user, "You currently aren't in a game.")
        ## Standing ## 
        if re.match('^-sta(nd|y)$', msg, re.I):
            stand = card_dealer.blackjack_stand(user);
            if stand[0] == 'win':
                self.sendMsg(channel, 'D['+' '.join(stand[2])+'] U['+' '.join(stand[1])+'] '+user+' won!')
            elif stand[0] == 'loss':
                self.sendMsg(channel, 'D['+' '.join(stand[2])+'] U['+' '.join(stand[1])+'] '+user+' lost.')
            elif stand[0] == 'tie':
                self.sendMsg(channel, 'D['+' '.join(stand[2])+'] U['+' '.join(stand[1])+'] '+user+' tied, the bet was pushed.')
            else:
                self.sendNotice(user, "You currently aren't in a game.")
        ## Doubling Down ##     
        if re.match('^-double$', msg, re.I):
            double = card_dealer.blackjack_double(user);
            if double and double != 'notoken':
                self.sendNotice(user, '['+' '.join(double[0])+']')
                if card_dealer.bust(user):
                    self.sendMsg(channel, 'D['+' '.join(double[1])+'] U['+' '.join(double[0])+'] '+user+' went bust!')
            elif double and double == 'notoken':
                self.sendNotice(user, "You don't have the tokens to back up your bet.")
            else:
                self.sendNotice(user, "You currently aren't in a game.")
        ## Surrendering ##
        if re.match('^-(surrender|ff)$', msg, re.I):
            surrender = card_dealer.blackjack_surrender(user);
            if surrender:
                self.sendMsg(channel, 'D['+' '.join(surrender[2])+'] U['+' '.join(surrender[1])+'] '+user+' surrendered, half the bet was refunded.')
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
                self.sendMsg(channel, ' '.join(str(result[0]))+' '+user+' won full bet!')
            elif result and result[1] == 'win':
                self.sendMsg(channel, ' '.join(str(result[0]))+' '+user+' won half bet.')
            elif result and result[1] == 'loss':
                self.sendMsg(channel, ' '.join(str(result[0]))+' '+user+' lost.')
            else:
                self.sendNotice(user, "You don't have the tokens to back up your bet.")
                
                
        #- Coin Flip -#
        ct = re.match('^-coinbet\s(?P<bet>\d+)\s(?P<call>(h|t|head(s|)|tail(s|)))$', msg, re.I)
        if ct:
            result = cointoss(user, int(ct.group('bet')), ct.group('call').lower());
            if result and result[1] == 'win':
                self.sendMsg(channel, '['+str(result[0])+'] '+user+' won!')
            elif result and result[1] == 'loss':
                self.sendMsg(channel, '['+str(result[0])+'] '+user+' lost.')
            else:
                self.sendNotice(user, "You don't have the tokens to back up your bet.")
