#!/usr/bin/env python

class IRCScript:
    def __init__(self, client):
        self.sendMsg = client.privmsg
        self.sendNotice = client.notice
        self.sendAction = client.action
        self.sendKick = client.kick
        self.sendIRC = client.sendIRC
        self.join = client.join
        self.part = client.part
        self.NICK = client.NICK
    def privmsg(self, user, channel, msg): pass
    def action(self, user, channel, msg): pass
    def notice(self, user, msg): pass
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
