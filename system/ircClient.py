#!/usr/bin/env python

import socket, logging
logging.basicConfig(level=logging.DEBUG, filename="system/logfile", filemode="a+", format="%(asctime)-15s %(levelname)-8s %(message)s")

class IRCClient():
    def __init__(self, HOST, PORT, NICK, IDENT, REALNAME, CHAN):
        self.HOST=HOST
        self.PORT=PORT
        self.NICK=NICK
        self.IDENT=IDENT
        self.REALNAME=REALNAME
        self.CHAN=CHAN
        self.irc=socket.socket()
        
    def connect(self):
        self.irc.connect((self.HOST, self.PORT))
        logging.info('<<Connecting to %s:%s' % (self.HOST, self.PORT))
    def action(self, target, message):
        self.irc.send(bytes('PRIVMSG %s :\x01ACTION %s\x01\r\n' % (target, message), 'utf-8'))
        logging.info('<<ACTION %s :%s' % (target, message))
    def admin(self, server):
        self.irc.send(bytes('ADMIN %s\r\n' % server, 'utf-8'))
        logging.info('<<Requesting admin info' % server)
    def away(self, message):
        if message:
            self.irc.send(bytes('AWAY %s\r\n' % message, 'utf-8'))
            logging.info('<<Setting away status with message: %s' % message)
        else:
            self.irc.send(bytes('AWAY\r\n', 'utf-8'))
            logging.info('<<Removing away status')
    def info(self):
        self.irc.send(bytes('INFO\r\n', 'utf-8'))
        logging.info('<<Requesting information')
    def invite(self, nickname, channel):
        self.irc.send(bytes('INVITE %s %s\r\n' % (nickname, channel), 'utf-8'))
        logging.info('<<Inviting %s to %s' % (nickname, channel))
    def ison(self, nicknames):
        ## Nicknames must be in an array. 
        nickname = ' '.join(nicknames)
        self.irc.send(bytes('ISON %s\r\n' % nickname, 'utf-8'))
        logging.info('<<Requesting if users are online: %s' % nickname)
    def join(self, channels):
        for channel in channels:
            if channel not in self.CHAN:
                self.CHAN.append(channel)
            self.irc.send(bytes('JOIN %s\r\n' % channel, 'utf-8'))
            logging.info('<<Joining %s' % channel)
    def kick(self, channel, client, message):
        if message:
            self.irc.send(bytes('KICK %s %s %s\r\n' % (channel, client, message), 'utf-8'))
            logging.info('<<Kicking user %s from %s: %s' % (client, channel, message))
        else:
            self.irc.send(bytes('KICK %s %s\r\n' % (channel, client), 'utf-8'))
            logging.info('<<Kicking user %s from %s' % (client, channel))
    def mode(self, target, flags, args):
        if args:
            self.irc.send(bytes('MODE %s %s %s\r\n' % (target, flags, args), 'utf-8'))
            logging.info('<<Setting %s on %s with args: %s' % (flags, target, args))
        else:
            self.irc.send(bytes('MODE %s %s\r\n' % (target, flags), 'utf-8'))
            logging.info('<<Setting %s on %s with args: %s' % (flags, target))
    def names(self, channels):
        self.irc.send(bytes('NAMES %s\r\n' % channels, 'utf-8'))
        logging.info('<<Requesting users on %s' % channels)
    def nick(self, NICK):
        self.irc.send(bytes('NICK %s\r\n' % NICK, 'utf-8'))
        logging.info('<<Requesting nick %s' % NICK)
    def notice(self, target, message):
        self.irc.send(bytes('NOTICE %s :%s\r\n' % (target, message), 'utf-8'))
        logging.info('<<NOTICE %s :%s' % (target, message))
    def part(self, channels):
        self.irc.send(bytes('PART %s\r\n' % channels, 'utf-8'))
        logging.info('<<Parting from %s' % channels)
    def ping(self, line):
        logging.info('<<PING %s' % line)
        self.irc.send(bytes('PONG %s\r\n' % line, 'utf-8'))
        logging.info('>>PONG %s' % line.split()[1])
    def pong(self, line):
        logging.info('>>PING %s' % line.split()[1])
        self.irc.send(bytes('PONG %s\r\n' % line.split()[1], 'utf-8'))
        logging.info('<<PONG %s' % line.split()[1])
    def privmsg(self, target, message):
        self.irc.send(bytes('PRIVMSG %s :%s\r\n' % (target, message), 'utf-8'))
        logging.info('<<PRIVMSG %s :%s' % (target, message))
    def topic(self, channel, topic):
        self.irc.send(bytes('TOPIC %s %s\r\n' % (channel, topic), 'utf-8'))
        logging.info('<<Setting topic in %s :%s' % (channel, topic))
    def user(self):
        self.irc.send(bytes('USER %s %s bla :%s \r\n' % (self.IDENT, self.HOST, self.REALNAME), 'utf-8'))
        logging.info('<<Identiftying as %s' % self.IDENT)
    def userhost(self, nicknames):
        ## Nicknames must be in an array. 
        nickname = ' '.join(nicknames)
        self.irc.send(bytes('USERHOST %s\r\n' % nickname, 'utf-8'))
        logging.info('<<Requesting information of user: %s' % nickname)
    def who(self, search):
        self.irc.send(bytes('WHO %s\r\n' % search, 'utf-8'))
        logging.info('<<Requesting users matching %s' % search)
    def whois(self, nicknames):
        self.irc.send(bytes('WHOIS %s\r\n' % nicknames, 'utf-8'))
        logging.info('<<Requesting whois user info for %s' % nicknames)
    def whowas(self, nickname):
        self.irc.send(bytes('WHOWAS %s\r\n' % nickname, 'utf-8'))
        logging.info('<<Requesting whowas user info for %s' % nickname)
    def sendIRC(self, msg):
        self.irc.send(bytes('%s\r\n' % msg, 'utf-8'))
        logging.info('<<Sending %s' % msg)
