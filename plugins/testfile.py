#!/usr/bin/env python

import template
import re

class IRCScript(template.IRCScript):
    print('loaded test')
#    def privmsg(self, user, channel, msg):
#        print(' [%s] <%s> %s' % (channel, user, msg))
#    def action(self, user, channel, data):
#        print(' [%s] * %s %s' % (channel, user, data))
#    def joined(self, user, channel):
#        print('J[%s] * %s has joined the channel.' % (channel, self.NICK))
#    def userJoined(self, user, channel):
#        print('J[%s] * %s has joined the channel.' % (channel, user))
#    def nickSwap(self, user, newnick, channel):
#        print('N[%s] * %s is now known as %s.' % (channel, user, newnick))
#    def userLeft(self, user, channel):
#        print('L[%s] * %s has left the channel.' % (channel, user))
#    def userQuit(self, user, quitMessage):
#        print('Q * %s has quit (%s).' % (user, quitMessage))
#    def userKicked(self, kickee, channel, kicker, message):
#        print('K[%s] * %s has kicked %s from the channel (%s).' % (channel, kicker, kickee, message))
#    def userMode(self, mod, user, channel, mode):
#        print('M[%s] * %s has given %s (%s).' % (channel, mod, user, mode))
