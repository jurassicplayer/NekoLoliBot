#!/usr/bin/env python

import template
import logging

class IRCScript(template.IRCScript):
    print('loaded logger')
    logging.basicConfig(level=logging.DEBUG, filename="logfile", filemode="a+", format="%(asctime)-15s %(levelname)-8s %(message)s")
    
    def privmsg(self, user, channel, msg):
        logging.info(' [%s] <%s> %s' % (channel, user, msg))
    def action(self, user, channel, msg):
        logging.info(' [%s] * %s %s' % (channel, user, msg))
    def notice(self, user, msg):
        logging.info(' [NOTICE] * %s %s' % (user, msg))
    def joined(self, user, channel):
        logging.info('J[%s] * %s has joined the channel.' % (channel, user))
    def userJoined(self, user, channel):
        logging.info('J[%s] * %s has joined the channel.' % (channel, user))
    def nickSwap(self, user, newnick, channel):
        logging.info('N[%s] * %s is now known as %s.' % (channel, user, newnick))
    def userLeft(self, user, channel):
        logging.info('L[%s] * %s has left the channel.' % (channel, user))
    def userQuit(self, user, quitMessage):
        logging.info('Qs %s has quit (%s).' % (user, quitMessage))
    def userKicked(self, kickee, channel, kicker, message):
        logging.info('K[%s] * %s has kicked %s from the channel (%s).' % (channel, kicker, kickee, message))
    def userMode(self, mod, user, channel, mode):
        logging.info('M[%s] * %s has given %s (%s).' % (channel, mod, user, mode))
