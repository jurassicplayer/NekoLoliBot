#!/usr/bin/env python

class IRCScript:
    def __init__(self, server):
        self.sendMsg = server.privmsg
        self.sendNotice = server.notice
        self.sendAction = server.action
        self.sendKick = server.kick
        self.sendIRC = server.sendIRC
        self.join = server.join
        self.part = server.part
        self.NICK = server.NICK
    def privmsg(self, origin, target, msg): pass
    def action(self, origin, target, msg): pass
    def notice(self, origin, target, msg): pass
    def joined(self, user, channel): pass
    def userJoined(self, user, channel): pass
    def nick(self, user, newnick): pass
    def left(self, user, channel): pass
    def userLeft(self, user, channel): pass
    def userQuit(self, user, quitMessage): pass
    def kicked(self, channel, kicker, msg): pass
    def userKicked(self, kickee, channel, kicker, msg): pass
    def userMode(self, mod, user, channel, mode): pass
    def channelMode(self, mod, channel, mode): pass
