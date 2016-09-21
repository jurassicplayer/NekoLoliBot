#!/usr/bin/env python

import socket, logging, threading, queue, os, sys, re

log = logging.getLogger(__name__)
class IRCClient:
    def __init__(self, recv_queue):
        self.server = IRCServer('irc.rizon.net', 6667, 'NekoLoliBot', 'NLB', 'ToyBot', ['#RandStr'], recv_queue)
        self.server.connect()
        
class IRCServer:
    def __init__(self, HOST, PORT, NICK, IDENT, REALNAME, CHAN, recv_queue):
        self.HOST=HOST
        self.PORT=PORT
        self.NICK=NICK
        self.IDENT=IDENT
        self.REALNAME=REALNAME
        self.CHAN=CHAN
        self.irc=socket.socket()
        self.connection_status = 0
        self.recv_queue = recv_queue
        self.recv_thread = threading.Thread(target=self.recieve_data_thread, daemon='true')
    def recieve_data_thread(self):
        message_buffer = ''
        while 1:
            message = self.irc.recv(1024)
            try:
                message_buffer = message_buffer + message.decode('utf-8')
            except UnicodeDecodeError:
                pass
            temp = str.split(message_buffer, '\n')
            message_buffer=temp.pop()
            for line in temp:
                message_object = IRCMessage(line)
                self.recv_queue.put((self, message_object))
                #log.info(line)
                if line.find('376') !=-1 and self.connection_status == 0:
                    self.join(self.CHAN);
                    self.connection_status = 1
                elif self.connection_status == 1:
                    pass
                if line.find('PING') !=-1:
                    self.pong(line)
    def connect(self):
        self.irc.connect((self.HOST, self.PORT))
        log.info('<<Connecting to %s:%s' % (self.HOST, self.PORT))
        self.recv_thread.start()
        self.nick(self.NICK)
        self.user()
    def action(self, target, message):
        self.irc.send(bytes('PRIVMSG %s :\x01ACTION %s\x01\r\n' % (target, message), 'utf-8'))
        log.info('<<ACTION %s :%s' % (target, message))
    def admin(self, server):
        self.irc.send(bytes('ADMIN %s\r\n' % server, 'utf-8'))
        log.info('<<Requesting admin info' % server)
    def away(self, message):
        if message:
            self.irc.send(bytes('AWAY %s\r\n' % message, 'utf-8'))
            log.info('<<Setting away status with message: %s' % message)
        else:
            self.irc.send(bytes('AWAY\r\n', 'utf-8'))
            log.info('<<Removing away status')
    def info(self):
        self.irc.send(bytes('INFO\r\n', 'utf-8'))
        log.info('<<Requesting information')
    def invite(self, nickname, channel):
        self.irc.send(bytes('INVITE %s %s\r\n' % (nickname, channel), 'utf-8'))
        log.info('<<Inviting %s to %s' % (nickname, channel))
    def ison(self, nicknames):
        ## Nicknames must be in an array. 
        nickname = ' '.join(nicknames)
        self.irc.send(bytes('ISON %s\r\n' % nickname, 'utf-8'))
        log.info('<<Requesting if users are online: %s' % nickname)
    def join(self, channels):
        for channel in channels:
            if channel not in self.CHAN:
                self.CHAN.append(channel)
            self.irc.send(bytes('JOIN %s\r\n' % channel, 'utf-8'))
            log.info('<<Joining %s' % channel)
    def kick(self, channel, client, message):
        if message:
            self.irc.send(bytes('KICK %s %s %s\r\n' % (channel, client, message), 'utf-8'))
            log.info('<<Kicking user %s from %s: %s' % (client, channel, message))
        else:
            self.irc.send(bytes('KICK %s %s\r\n' % (channel, client), 'utf-8'))
            log.info('<<Kicking user %s from %s' % (client, channel))
    def mode(self, target, flags, args):
        if args:
            self.irc.send(bytes('MODE %s %s %s\r\n' % (target, flags, args), 'utf-8'))
            log.info('<<Setting %s on %s with args: %s' % (flags, target, args))
        else:
            self.irc.send(bytes('MODE %s %s\r\n' % (target, flags), 'utf-8'))
            log.info('<<Setting %s on %s with args: %s' % (flags, target))
    def names(self, channels):
        self.irc.send(bytes('NAMES %s\r\n' % channels, 'utf-8'))
        log.info('<<Requesting users on %s' % channels)
    def nick(self, NICK):
        self.irc.send(bytes('NICK %s\r\n' % NICK, 'utf-8'))
        log.info('<<Requesting nick %s' % NICK)
    def notice(self, target, message):
        self.irc.send(bytes('NOTICE %s :%s\r\n' % (target, message), 'utf-8'))
        log.info('<<NOTICE %s :%s' % (target, message))
    def part(self, channels):
        self.irc.send(bytes('PART %s\r\n' % channels, 'utf-8'))
        log.info('<<Parting from %s' % channels)
    def ping(self, line):
        self.irc.send(bytes('PING %s\r\n' % line, 'utf-8'))
        log.info('<<PING %s' % line.split()[1])
    def pong(self, line):
        self.irc.send(bytes('PONG %s\r\n' % line.split()[1], 'utf-8'))
        log.info('<<PONG %s' % line.split()[1])
    def privmsg(self, target, message):
        self.irc.send(bytes('PRIVMSG %s :%s\r\n' % (target, message), 'utf-8'))
        log.info('<<PRIVMSG %s :%s' % (target, message))
    def topic(self, channel, topic):
        self.irc.send(bytes('TOPIC %s %s\r\n' % (channel, topic), 'utf-8'))
        log.info('<<Setting topic in %s :%s' % (channel, topic))
    def user(self):
        self.irc.send(bytes('USER %s %s bla :%s \r\n' % (self.IDENT, self.HOST, self.REALNAME), 'utf-8'))
        log.info('<<Identiftying as %s' % self.IDENT)
    def userhost(self, nicknames):
        ## Nicknames must be in an array. 
        nickname = ' '.join(nicknames)
        self.irc.send(bytes('USERHOST %s\r\n' % nickname, 'utf-8'))
        log.info('<<Requesting information of user: %s' % nickname)
    def who(self, search):
        self.irc.send(bytes('WHO %s\r\n' % search, 'utf-8'))
        log.info('<<Requesting users matching %s' % search)
    def whois(self, nicknames):
        self.irc.send(bytes('WHOIS %s\r\n' % nicknames, 'utf-8'))
        log.info('<<Requesting whois user info for %s' % nicknames)
    def whowas(self, nickname):
        self.irc.send(bytes('WHOWAS %s\r\n' % nickname, 'utf-8'))
        log.info('<<Requesting whowas user info for %s' % nickname)
    def sendIRC(self, msg):
        self.irc.send(bytes('%s\r\n' % msg, 'utf-8'))
        log.info('<<Sending %s' % msg)
class IRCChannel:
    def __init__(self, server):
        self.connection_status = 0
        print('')
class IRCMessage:
    def __init__(self, message):
        self.raw_message = message
        self.user = ''
        self.ident = ''
        self.userhost = ''
        self.domain = ''
        self.rpl_code = ''
        self.target = ''
        self.message = ''
        self.info = ''
        self.process_message(message)
    def process_message(self, raw_message):
        message = re.match('^:((?P<user>[^\!]+)\!(?P<ident>[^@]+)@(?P<userhost>[^\s]+)|(?P<domain>([^\s]+)))\s(?P<type>([^\s]+))\s((?P<target>([^\s]+))\s(?P<message>.*)|(?P<info>.*))', raw_message, re.I)
        if message:
            if message.group('type') == '001':
                print('server welcome')
            elif message.group('type') == '002':
                print('server name and version')
            elif message.group('type') == '003':
                print('server created')
            elif message.group('type') == '004':
                print('server cmds supported')
            elif message.group('type') == '005':
                print('server bounced')
            elif message.group('type') == '042':
                print('unique ID')
            elif message.group('type') == '251':
                print('users on servers')
            elif message.group('type') == '252':
                print('IRCOps Online')
            elif message.group('type') == '253':
                print('unknown connections')
            elif message.group('type') == '254':
                print('number of channels')
            elif message.group('type') == '255':
                print('# of clients and servers')
            elif message.group('type') == '265':
                print('current local users')
            elif message.group('type') == '266':
                print('current global users')
            elif message.group('type') == '332':
                print('topic')
            elif message.group('type') == '333':
                print('channel admin and ip')
            elif message.group('type') == '375':
                print('motd welcome')
            elif message.group('type') == '372':
                print('motd')
            elif message.group('type') == '376':
                print('end of motd')
            elif message.group('type') == '353':
                print('names')
            elif message.group('type') == '366':
                print('end of names')
            elif message.group('type') == '404':
                print('cannot send to channel')
            elif message.group('type') == '439':
                print('processing connection')
            elif message.group('type') == '451':
                print('nick not registered')
            elif message.group('type') == '473':
                print('cannot join channel')
            elif message.group('type') == '479':
                print('illegal channel name')
            elif message.group('type') == 'PRIVMSG':
                try:
                    if message.group('message').find('\x01ACTION')  !=-1:
                        user = message.group('user')
                        channel = message.group('target')
                        msg = message.group('message')[9:-1]
                    elif message.group('message').find('\x01VERSION') !=-1:
                        user = message.group('user')
                        #client.notice(user, '\x01VERSION NekoLoliBot [Python3] -alpha-\x01\r\n')
                    elif message.group('message').find('\x01DCC') !=-1:
                        print('privmsg: '+message.group('message'))
                    else:
                        user = message.group('user')
                        #if message.group('target') == client.NICK:
                        #    channel = user
                        #else:
                        #    channel = message.group('target')
                        msg = message.group('message')[1:]
                except AttributeError:
                    print('Notice contained no message.')
            elif message.group('type') == 'NOTICE' and message.group('user') == 'Nickserv':
                print('Nickserv reply: '+message.group('message'))
            elif message.group('type') == 'NOTICE' and message.group('user') != 'Nickserv':
                user = message.group('user')
                channel = message.group('target')
                msg = message.group('message')[1:]
            elif message.group('type') == 'JOIN':
                user = message.group('user')
                try:
                    channel = message.group('info')[1:]
                except:
                    channel = ''
            elif message.group('type') == 'PART':
                user = message.group('user')
                if message.group('info'):
                    channel = message.group('info')[1:]
                elif message.group('target'):
                    channel = message.group('target')
            elif message.group('type') == 'KICK':
                kicker = message.group('user')
                channel = message.group('target')
                msg = re.match('(?P<kickee>[^\s]+)\s:(?P<msg>.*)', message.group('message'), re.I)
                kickee = msg.group('kickee')
            elif message.group('type') == 'NICK':
                user = message.group('user')
                newnick = message.group('info')[1:]
            elif message.group('type') == 'QUIT':
                user = message.group('user')
                try:
                    quitMessage = message.group('message')
                except Exception:
                    quitMessage = None
                    pass
            elif message.group('type') == 'MODE':
                mod = message.group('user')
                channel = message.group('target')
                option = re.match('^(?P<options>[^\s]+)(\s|)((?P<user>[^\s]+)|)$', message.group('message'), re.I)
                mode = option.group('options')
                user = option.group('user')
            else:
                print(raw_message.encode('utf-8'))
