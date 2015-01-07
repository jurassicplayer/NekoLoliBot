#!/usr/bin/env python

class IRCScript:
    def __init__(self, client):
        self.sendMsg = client.sendMsg
        self.sendNotice = client.sendNotice
        self.sendAction = client.sendAction
        self.sendKick = client.sendKick
        self.sendIRC = client.sendIRC
        self.join = client.join
        self.part = client.part
        self.nick = client.NICK
        self.pollNick = client.pollNick
        self.channel = client.CHAN
    def privmsg(self, user, channel, msg): pass
    def action(self, user, channel, msg): pass
    def notice(self, user, msg): pass
    def joined(self, user, channel): pass
    def userJoined(self, user, channel): pass
    def nickSwap(self, user, newnick, channel): pass
    def left(self, user, channel): pass
    def userLeft(self, user, channel): pass
    def userQuit(self, user, quitMessage): pass
    def userKicked(self, kickee, channel, kicker, msg): pass
    def userMode(self, mod, user, channel, mode): pass
