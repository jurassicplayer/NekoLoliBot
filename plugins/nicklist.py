#!/usr/bin/env python
import template
import pickle, re, logging

class nickTracker():
    def swap_nick():
        print('derp')
    def user_present():
        print('Checks if the user is present in the channel.')
        print('Grab list of nicks with /NAMES #channel')
        print('')
        
class IRCScript(template.IRCScript):
    print('loaded nicklist')
    def nickSwap(self, user, newnick, channel):
        print(user + ' changed nick to '+ newnick)