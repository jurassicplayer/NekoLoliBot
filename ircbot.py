#!/usr/bin/env python

import os, sys, re

import importlib as i
plugin_dir = 'plugins'
sys.path.append(plugin_dir)
loaded_objects = {}
loaded_plugins = {}
def load_plugin(plugin):
    module = __import__(plugin, fromlist=[''])
    loaded_objects[plugin] = module.IRCScript(client)
    loaded_plugins[plugin] = module
def reload_plugin(plugin):
    module = i.reload(loaded_plugins[plugin])
    loaded_objects[plugin] = module.IRCScript(client)
def reload_all_plugins():
    for name in os.listdir(plugin_dir):
        if name.endswith(".py") and name != 'template.py':
            module = name[:-3]
            load_plugin(module)
    for plugin in loaded_plugins:
        reload_plugin(plugin)

HOST="irc.rizon.net"
PORT=6667
#HOST='irc.gbatemp.net'
#PORT=4500
NICK="NekoLoliBot"
IDENT="NekoBot"
REALNAME="NekoLoliBot"
CHAN="#gbatemp.net"
#CHAN='#CTSS'
CHAN="#RandStr"
#CHAN='#NekoLoliBot'

sys.path.append('system')
from ircClient import IRCClient as IRCClient
if __name__ == '__main__':
    #Instantiate a client
    client = IRCClient(HOST, PORT, NICK, IDENT, REALNAME, CHAN);
    reload_all_plugins();
    #Connect client to server
    client.connect();
    client.nick(NICK);
    client.identify();
    client.join(CHAN);
    client.sendMsg(CHAN, 'Hai everyone~!');
    
    connected = 0
    while 1:
        message = client.irc.recv(1024)
        try:
            temp = message.decode('utf-8').split('\r\n')
        except UnicodeDecodeError:
            pass
        for line in temp:
            ## Deconstruct line here into tokens to pass to plugins ##
            message = re.match("^:(?P<domain>([^\s]+))\s(?P<type>([^\s]+))\s(?P<channel>([^\s]+))\s:(?P<message>.*)", line, re.I)
            if message:
                user = message.group('domain').split('!',1)[0]
                msg = message.group('message')
                channel = message.group('channel')
                msgtype = message.group('type')
            print(line.encode('utf-8'))
            
            ## Hunt for first connect and make absolutely sure we connected to the channel
            if line.find('PING') !=-1 and connected == 0:
                client.join(CHAN);
            elif line.find('JOIN') !=-1 and line.find(client.NICK) !=-1:
                connected = 1
            elif connected == 1:
                pass
                
            ## PING Response ##
            if line.find('PING') !=-1:
                client.pong(line)
            if line.find('\x01VERSION\x01') !=-1:
                client.sendNotice(user, '\x01VERSION NekoLoliBot [Python3] -alpha-\x01\r\n')
            
            if line.find('!reload') !=-1:
                reload_all_plugins()
            
            
            ## Search for all IRC commands ##
            if line.find('PRIVMSG') !=-1:
                if line.find('ACTION') !=-1:
                    for module in loaded_plugins:
                        loaded_objects[module].action(user, channel, msg[8:-1])
                else:
                    for module in loaded_plugins:
                        loaded_objects[module].privmsg(user, channel, msg)
            if line.find('NOTICE') !=-1:
                for module in loaded_plugins:
                    loaded_objects[module].notice(user, msg)
            if line.find('JOIN') !=-1:
                if line.find(client.NICK) !=-1:
                    for module in loaded_plugins:
                        loaded_objects[module].joined(client.NICK, channel)
                else:
                    ## Deconstruct message to obtain joiner
                    joinee = re.match("^:(?P<user>.*?)\!(?P<ident>.*?)@(?P<maskedhost>.*?)\s(?P<type>(\w+))\s(?P<target>.*?)(?P<message>.*?)", line, re.I)
                    if joinee:
                        joiner = joinee.group('user')
                        for module in loaded_plugins:
                            loaded_objects[module].userJoined(joiner, channel)
            if line.find('NICK ') !=-1:
                nickuser = re.match("^:(?P<user>.*?)\!(?P<ident>.*?)@(?P<maskedhost>.*?)\s(?P<type>(\w+))\s:(?P<target>.*)", line, re.I)
                user = nickuser.group('user')
                target = nickuser.group('target')
                for module in loaded_plugins:
                    loaded_objects[module].nickSwap(user, target, channel)
            if line.find('PART') !=-1:
                if line.find(client.NICK) !=-1:
                    for module in loaded_plugins:
                        loaded_objects[module].left(user, channel)
                else:
                    for module in loaded_plugins:
                        loaded_objects[module].userLeft(user, channel)
            if line.find('QUIT') !=-1:
                for module in loaded_plugins:
                    loaded_objects[module].userQuit(user, msg)
            if msgtype == 'KICK':
                ## Deconstruct message to obtain kicker, kickee, and message
                kicked = re.match("^:(?P<kicker>.*?)\!(?P<ident>.*?)@(?P<maskedhost>.*?)\s(?P<type>(\w+))\s(?P<target>.*?)\s(?P<kickee>.*?)\s:(?P<message>.*)", line, re.I)
                if kicked and kicked.group('kickee') != client.NICK:
                    for module in loaded_plugins:
                        loaded_objects[module].userKicked(kicked.group('kickee'), channel, kicked.group('kicker'), kicked.group('message'))
                else:
                    connected = 0
            if line.find('MODE') !=-1:
                modeMsg = re.match("^:(?P<mod>.*?)\!(?P<ident>.*?)@(?P<maskedhost>.*?)\s(?P<type>(\w+))\s(?P<channel>.*?)\s(?P<mode>.*?)\s(?P<user>.*)", line, re.I)
                if modeMsg:
                    mod = modeMsg.group('mod')
                    user = modeMsg.group('user')
                    channel = modeMsg.group('channel')
                    mode = modeMsg.group('mode')
                    for module in loaded_plugins:
                        loaded_objects[module].userMode(mod, user, channel, mode)
