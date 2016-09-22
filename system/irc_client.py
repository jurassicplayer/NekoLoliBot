#!/usr/bin/env python

import socket, logging, threading, queue, os, sys, re

log = logging.getLogger(__name__)
class IRCClient:
    def __init__(self, recv_queue):
        self.server = IRCServer('irc.rizon.net', 6667, 'NekoLoliBot', 'NLB', 'ToyBot', ['#RandStr'], recv_queue)
        self.server2 = IRCServer('irc.irchighway.net', 6667, 'NekoLoliBot', 'NLB', 'ToyBot', ['#RandStr'], recv_queue)
        self.server.connect()
        self.server2.connect()
        
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
                line = str.rstrip(line)
                line = str.strip(line)
                message_object = IRCMessage(line)
                self.recv_queue.put((self, message_object))
                #log.info(line)
                if message_object.cmd == 'RPL_ENDOFMOTD' and self.connection_status == 0:
                    self.join(self.CHAN);
                    self.connection_status = 1
                elif self.connection_status == 1:
                    pass
                if message_object.cmd == 'PING':
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
        self.prefix = ''
        self.user = ''
        self.host = ''
        self.cmd = ''
        self.params = ''
        self.trailing = ''
        self.process_message(message)
    def shady_param_hack(self):
        #################################################################
        # A certain few RPL_Codes don't follow the standard IRC message #
        # format and give back information as a parameter. This is just #
        # a hacky solution to slap all parameters except the first back #
        # into the trailing section.                                    #
        #################################################################
        try:
            old_params = self.params.split(' ', 1)
            self.params = old_params[0]
            self.trailing = '%s :%s' % (old_params[1], self.trailing)
        except: log.warning(self.params)
    def process_message(self, raw_message):
        message = re.match('^(:((?P<servername>\S+?)|(?P<nick>\S+?))(!(?P<user>\S+?)|)(@(?P<host>\S+?)|)\s|)(?P<command>\S+)(\s(?P<params>.*?)(?=\s:)|)(\s|)(:(?P<trailing>.*)|)', raw_message, re.I)
        if message:
            if message.group('servername'): self.prefix = message.group('servername')
            if message.group('user'): self.user = message.group('user')
            if message.group('host'): self.host = message.group('host')
            if message.group('command'): self.cmd = message.group('command')
            if message.group('params'): self.params = message.group('params')
            if message.group('trailing'): self.trailing = message.group('trailing')
            #RPL Command Conversion#
            ## Sauce: http://www.networksorcery.com/enp/protocol/irc.htm
            ## Supplement: https://www.alien.net.au/irc/irc2numerics.html
            if self.cmd == '001': self.cmd = 'RPL_WELCOME'
            elif self.cmd == '002': self.cmd = 'RPL_YOURHOST'
            elif self.cmd == '003': self.cmd = 'RPL_CREATED'
            elif self.cmd == '004': self.cmd = 'RPL_MYINFO'
            elif self.cmd == '005': 
                self.cmd = 'RPL_BOUNCE'
                self.shady_param_hack()
            elif self.cmd == '042': 
                self.cmd = 'RPL_YOURID'
                self.shady_param_hack()
            elif self.cmd == '200': self.cmd = 'RPL_TRACELINK'
            elif self.cmd == '201': self.cmd = 'RPL_TRACECONNECTING'
            elif self.cmd == '202': self.cmd = 'RPL_TRACEHANDSHAKE'
            elif self.cmd == '203': self.cmd = 'RPL_TRACEUNKNOWN'
            elif self.cmd == '204': self.cmd = 'RPL_TRACEOPERATOR'
            elif self.cmd == '205': self.cmd = 'RPL_TRACEUSER'
            elif self.cmd == '206': self.cmd = 'RPL_TRACESERVER'
            elif self.cmd == '207': self.cmd = 'RPL_TRACESERVICE'
            elif self.cmd == '208': self.cmd = 'RPL_TRACENEWTYPE'
            elif self.cmd == '209': self.cmd = 'RPL_TRACECLASS'
            elif self.cmd == '210': self.cmd = 'RPL_TRACERECONNECT'
            elif self.cmd == '211': self.cmd = 'RPL_STATSLINKINFO'
            elif self.cmd == '212': self.cmd = 'RPL_STATSCOMMANDS'
            elif self.cmd == '219': self.cmd = 'RPL_ENDOFSTATS'
            elif self.cmd == '221': self.cmd = 'RPL_UMODEIS'
            elif self.cmd == '234': self.cmd = 'RPL_SERVLIST'
            elif self.cmd == '235': self.cmd = 'RPL_SERVLISTEND'
            elif self.cmd == '242': self.cmd = 'RPL_STATSUPTIME'
            elif self.cmd == '243': self.cmd = 'RPL_STATSOLINE'
            elif self.cmd == '251': self.cmd = 'RPL_LUSERCLIENT'
            elif self.cmd == '252':
                self.cmd = 'RPL_LUSEROP'
                self.shady_param_hack()
            elif self.cmd == '253':
                self.cmd = 'RPL_LUSERUNKNOWN'
                self.shady_param_hack()
            elif self.cmd == '254':
                self.cmd = 'RPL_LUSERCHANNELS'
                self.shady_param_hack()
            elif self.cmd == '255': self.cmd = 'RPL_LUSERME'
            elif self.cmd == '256': self.cmd = 'RPL_ADMINME'
            elif self.cmd == '257': self.cmd = 'RPL_ADMINLOC1'
            elif self.cmd == '258': self.cmd = 'RPL_ADMINLOC2'
            elif self.cmd == '259': self.cmd = 'RPL_ADMINEMAIL'
            elif self.cmd == '261': self.cmd = 'RPL_TRACELOG'
            elif self.cmd == '262': self.cmd = 'RPL_TRACEEND'
            elif self.cmd == '263': self.cmd = 'RPL_TRYAGAIN'
            elif self.cmd == '265':
                self.cmd = 'RPL_LOCALUSERS'
                self.shady_param_hack()
            elif self.cmd == '266':
                self.cmd = 'RPL_GLOBALUSERS'
                self.shady_param_hack()
            elif self.cmd == '301': self.cmd = 'RPL_AWAY'
            elif self.cmd == '302': self.cmd = 'RPL_USERHOST'
            elif self.cmd == '303': self.cmd = 'RPL_ISON'
            elif self.cmd == '305': self.cmd = 'RPL_UNAWAY'
            elif self.cmd == '306': self.cmd = 'RPL_NOWAWAY'
            elif self.cmd == '311': self.cmd = 'RPL_WHOISUSER'
            elif self.cmd == '312': self.cmd = 'RPL_WHOISSERVER'
            elif self.cmd == '313': self.cmd = 'RPL_WHOISOPERATOR'
            elif self.cmd == '314': self.cmd = 'RPL_WHOWASUSER'
            elif self.cmd == '315': self.cmd = 'RPL_ENDOFWHO'
            elif self.cmd == '317': self.cmd = 'RPL_WHOISIDLE'
            elif self.cmd == '318': self.cmd = 'RPL_ENDOFWHOIS'
            elif self.cmd == '319': self.cmd = 'RPL_WHOISCHANNELS'
            elif self.cmd == '321': self.cmd = 'RPL_LISTSTART'
            elif self.cmd == '322': self.cmd = 'RPL_LIST'
            elif self.cmd == '323': self.cmd = 'RPL_LISTEND'
            elif self.cmd == '324': self.cmd = 'RPL_CHANNELMODEIS'
            elif self.cmd == '325': self.cmd = 'RPL_UNIQOPIS'
            elif self.cmd == '331': self.cmd = 'RPL_NOTOPIC'
            elif self.cmd == '332': self.cmd = 'RPL_TOPIC'
            elif self.cmd == '341': self.cmd = 'RPL_INVITING'
            elif self.cmd == '342': self.cmd = 'RPL_SUMMONING'
            elif self.cmd == '346': self.cmd = 'RPL_INVITELIST'
            elif self.cmd == '347': self.cmd = 'RPL_ENDOFINVITELIST'
            elif self.cmd == '348': self.cmd = 'RPL_EXCEPTLIST'
            elif self.cmd == '349': self.cmd = 'RPL_ENDOFEXCEPTLIST'
            elif self.cmd == '351': self.cmd = 'RPL_VERSION'
            elif self.cmd == '352': self.cmd = 'RPL_WHOREPLY'
            elif self.cmd == '353': self.cmd = 'RPL_NAMREPLY'
            elif self.cmd == '364': self.cmd = 'RPL_LINKS'
            elif self.cmd == '365': self.cmd = 'RPL_ENDOFLINKS'
            elif self.cmd == '366': self.cmd = 'RPL_ENDOFNAMES'
            elif self.cmd == '367': self.cmd = 'RPL_BANLIST'
            elif self.cmd == '368': self.cmd = 'RPL_ENDOFBANLIST'
            elif self.cmd == '369': self.cmd = 'RPL_ENDOFWHOWAS'
            elif self.cmd == '371': self.cmd = 'RPL_INFO'
            elif self.cmd == '372': self.cmd = 'RPL_MOTD'
            elif self.cmd == '374': self.cmd = 'RPL_ENDOFINFO'
            elif self.cmd == '375': self.cmd = 'RPL_MOTDSTART'
            elif self.cmd == '376': self.cmd = 'RPL_ENDOFMOTD'
            elif self.cmd == '381': self.cmd = 'RPL_YOUREOPER'
            elif self.cmd == '382': self.cmd = 'RPL_REHASHING'
            elif self.cmd == '383': self.cmd = 'RPL_YOURESERVICE'
            elif self.cmd == '391': self.cmd = 'RPL_TIME'
            elif self.cmd == '392': self.cmd = 'RPL_USERSSTART'
            elif self.cmd == '393': self.cmd = 'RPL_USERS'
            elif self.cmd == '394': self.cmd = 'RPL_ENDOFUSERS'
            elif self.cmd == '395': self.cmd = 'RPL_NOUSERS'
            elif self.cmd == '401': self.cmd = 'ERR_NOSUCHNICK'
            elif self.cmd == '402': self.cmd = 'ERR_NOSUCHSERVER'
            elif self.cmd == '403': self.cmd = 'ERR_NOSUCHCHANNEL'
            elif self.cmd == '404': self.cmd = 'ERR_CANNOTSENDTOCHAN'
            elif self.cmd == '405': self.cmd = 'ERR_TOOMANYCHANNELS'
            elif self.cmd == '406': self.cmd = 'ERR_WASNOSUCHNICK'
            elif self.cmd == '407': self.cmd = 'ERR_TOOMANYTARGETS'
            elif self.cmd == '408': self.cmd = 'ERR_NOSUCHSERVICE'
            elif self.cmd == '409': self.cmd = 'ERR_NOORIGIN'
            elif self.cmd == '411': self.cmd = 'ERR_NORECIPIENT'
            elif self.cmd == '412': self.cmd = 'ERR_NOTEXTTOSEND'
            elif self.cmd == '413': self.cmd = 'ERR_NOTOPLEVEL'
            elif self.cmd == '414': self.cmd = 'ERR_WILDTOPLEVEL'
            elif self.cmd == '415': self.cmd = 'ERR_BADMASK'
            elif self.cmd == '421': self.cmd = 'ERR_UNKNOWNCOMMAND'
            elif self.cmd == '422': self.cmd = 'ERR_NOMOTD'
            elif self.cmd == '423': self.cmd = 'ERR_NOADMININFO'
            elif self.cmd == '424': self.cmd = 'ERR_FILEERROR'
            elif self.cmd == '431': self.cmd = 'ERR_NONICKNAMEGIVEN'
            elif self.cmd == '432': self.cmd = 'ERR_ERRONEUSNICKNAME'
            elif self.cmd == '433': self.cmd = 'ERR_NICKNAMEINUSE'
            elif self.cmd == '436': self.cmd = 'ERR_NICKCOLLISION'
            elif self.cmd == '437': self.cmd = 'ERR_UNAVAILRESOURCE'
            elif self.cmd == '439': self.cmd = 'ERR_TARGETTOOFAST'
            elif self.cmd == '441': self.cmd = 'ERR_USERNOTINCHANNEL'
            elif self.cmd == '442': self.cmd = 'ERR_NOTONCHANNEL'
            elif self.cmd == '443': self.cmd = 'ERR_USERONCHANNEL'
            elif self.cmd == '444': self.cmd = 'ERR_NOLOGIN'
            elif self.cmd == '445': self.cmd = 'ERR_SUMMONDISABLED'
            elif self.cmd == '446': self.cmd = 'ERR_USERSDISABLED'
            elif self.cmd == '451': self.cmd = 'ERR_NOTREGISTERED'
            elif self.cmd == '461': self.cmd = 'ERR_NEEDMOREPARAMS'
            elif self.cmd == '462': self.cmd = 'ERR_ALREADYREGISTRED'
            elif self.cmd == '463': self.cmd = 'ERR_NOPERMFORHOST'
            elif self.cmd == '464': self.cmd = 'ERR_PASSWDMISMATCH'
            elif self.cmd == '465': self.cmd = 'ERR_YOUREBANNEDCREEP'
            elif self.cmd == '466': self.cmd = 'ERR_YOUWILLBEBANNED'
            elif self.cmd == '467': self.cmd = 'ERR_KEYSET'
            elif self.cmd == '471': self.cmd = 'ERR_CHANNELISFULL'
            elif self.cmd == '472': self.cmd = 'ERR_UNKNOWNMODE'
            elif self.cmd == '473': self.cmd = 'ERR_INVITEONLYCHAN'
            elif self.cmd == '474': self.cmd = 'ERR_BANNEDFROMCHAN'
            elif self.cmd == '475': self.cmd = 'ERR_BADCHANNELKEY'
            elif self.cmd == '476': self.cmd = 'ERR_BADCHANMASK'
            elif self.cmd == '477': self.cmd = 'ERR_NOCHANMODES'
            elif self.cmd == '478': self.cmd = 'ERR_BANLISTFULL'
            elif self.cmd == '481': self.cmd = 'ERR_NOPRIVILEGES'
            elif self.cmd == '482': self.cmd = 'ERR_CHANOPRIVSNEEDED'
            elif self.cmd == '483': self.cmd = 'ERR_CANTKILLSERVER'
            elif self.cmd == '484': self.cmd = 'ERR_RESTRICTED'
            elif self.cmd == '485': self.cmd = 'ERR_UNIQOPPRIVSNEEDED'
            elif self.cmd == '491': self.cmd = 'ERR_NOOPERHOST'
            elif self.cmd == '501': self.cmd = 'ERR_UMODEUNKNOWNFLAG'
            elif self.cmd == '502': self.cmd = 'ERR_USERSDONTMATCH'
            elif self.cmd == 'JOIN': pass
            elif self.cmd == 'KICK': pass
            elif self.cmd == 'MODE': pass
            elif self.cmd == 'NICK': pass
            elif self.cmd == 'NOTICE': pass
            elif self.cmd == 'PART': pass
            elif self.cmd == 'PING': pass
            elif self.cmd == 'PRIVMSG':
                if self.trailing.find('\x01ACTION') != -1:
                    self.cmd = 'ACTION'
                    self.trailing = self.trailing[8:-1]
                elif self.trailing.find('\x01VERSION') != -1:
                    self.cmd = 'VERSION'
                elif self.trailing.find('\x01DCC') != -1:
                    self.cmd = 'DCC'
                else: pass
            elif self.cmd == 'QUIT': pass
            else: 
                log.warning('Unknown IRC command: %s' % self.cmd)
                pass
