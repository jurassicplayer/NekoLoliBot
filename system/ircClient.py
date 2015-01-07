#!/usr/bin/env python

import socket, logging
logging.basicConfig(level=logging.DEBUG, filename="logfile", filemode="a+", format="%(asctime)-15s %(levelname)-8s %(message)s")

class IRCClient():
    def __init__(self, HOST, PORT, NICK, IDENT, REALNAME, CHAN):
        self.HOST=HOST
        self.PORT=PORT
        self.NICK=NICK
        self.IDENT=IDENT
        self.REALNAME=REALNAME
        self.CHAN=CHAN
        self.irc = socket.socket()
    def connect(self):
        self.irc.connect((self.HOST, self.PORT))
        logging.info('<<Connecting to %s:%s' % (self.HOST, self.PORT))
    def pollNick(self):
        self.irc.send(bytes('NAMES '+self.CHAN + '\r\n', 'utf-8'))
        logging.info('<<Requesting nick list')
    def nick(self, NICK):
        self.NICK=NICK
        self.irc.send(bytes('NICK '+NICK+'\r\n', 'utf-8'))
        logging.info('<<Requesting nick %s' % NICK)
    def identify(self):
        self.irc.send(bytes('USER %s %s bla :%s \r\n' % (self.IDENT, self.HOST, self.REALNAME), 'utf-8'))
        logging.info('<<Identiftying as %s' % self.IDENT)
    def join(self, CHAN):
        self.CHAN=CHAN
        self.irc.send(bytes('JOIN '+CHAN+'\r\n', 'utf-8'))
        logging.info('<<Joining %s channel' % CHAN)
    def part(self, CHAN):
        self.irc.send(bytes('PART '+CHAN+'\r\n', 'utf-8'))
        logging.info('<<Parting %s channel' % CHAN)
    def pong(self, line):
        logging.info('>>PING %s' % line.split()[1])
        self.irc.send(bytes('PONG %s\r\n' % line.split()[1], 'utf-8'))
        logging.info('<<PONG %s' % line.split()[1])
    def version(self):
        print('Version requested.')
    def sendMsg(self, channel, msg):
        self.irc.send(bytes('PRIVMSG '+channel+' :' + msg + '\r\n', 'utf-8'))
        logging.info('<<PRIVMSG %s :%s' % (channel, msg))
    def sendNotice(self, channel, msg):
        self.irc.send(bytes('NOTICE '+channel+' :' + msg + '\r\n', 'utf-8'))
        logging.info('<<NOTICE %s :%s' % (channel, msg))
    def sendAction(self, channel, msg):
        self.irc.send(bytes('PRIVMSG '+channel+' :\x01ACTION ' + msg + '\x01\r\n', 'utf-8'))
        logging.info('<<ACTION %s :%s' % (channel, msg))
    def sendKick(self, user, msg):
        self.irc.send(bytes('KICK '+self.CHAN+' '+ user +' :' + msg + '\r\n', 'utf-8'))
        logging.info('<<Kicking user %s' % user)
    def sendIRC(self, msg):
        self.irc.send(bytes(msg+'\r\n', 'utf-8'))
        logging.info('<<Sending cmd "%s"' % msg)
