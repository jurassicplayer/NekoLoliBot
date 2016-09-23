#!/usr/bin/env python

class IRCScript:
    def __init__(self, server):
        self.server = server
        self.sendMsg = server.privmsg
        self.sendNotice = server.notice
        self.sendAction = server.action
        self.sendKick = server.kick
        self.sendIRC = server.sendIRC
        self.sendJoin = server.join
        self.sendPart = server.part
        self.NICK = server.NICK
    def servermsg(self, prefix, user, host, command, params, trailing): pass
    def action(self, origin, target, msg): pass
    def join(self, origin, target): pass
    def kick(self, kicker, params): pass
    def mode(self, mod, user, channel, mode): pass #FIXIT
    def nick(self, origin, target): pass
    def notice(self, origin, target, msg): pass
    def part(self, origin, target): pass
    def privmsg(self, origin, target, msg): pass
    def quit(self, user, quitMessage): pass #FIXIT
