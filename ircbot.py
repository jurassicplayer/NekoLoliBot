#!/usr/bin/env python

import os, sys, re
import importlib as i

sys.path.append('system')
sys.path.append('plugins')
import config
from ircClient import IRCClient as IRCClient


## Plugin stuffs ##
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
    for name in os.listdir('plugins'):
        if name.endswith(".py") and name != 'template.py':
            module = name[:-3]
            load_plugin(module)
    for plugin in loaded_plugins:
        reload_plugin(plugin)


## IRC stuffs ##
def connect_all(HOST, PORT, NICK, IDENT, REALNAME, CHANNELS):
    client = IRCClient(HOST, PORT, NICK, IDENT, REALNAME, CHANNELS);
    client.connect();
    client.nick(NICK);
    client.user();
    client.join(CHANNELS);
    if config.GREETER:
        for channel in CHANNELS:
            client.privmsg(channel, config.GREET_TXT)
    return client
    


if __name__ == '__main__':
    #Instantiate a client
    client = connect_all(config.HOST, config.PORT, config.NICK, config.IDENT, config.REALNAME, config.CHANNELS);
    reload_all_plugins();
    
    connected = 0
    while 1:
        message = client.irc.recv(1024)
        try:
            temp = message.decode('utf-8').split('\r\n')
        except UnicodeDecodeError:
            pass
        for line in temp:
            ## Hunt for first connect and make absolutely sure we connected to the channel
            if line.find('PING') !=-1 and connected == 0:
                client.join(config.CHANNELS);
            elif line.find('JOIN') !=-1 and line.find(client.NICK) !=-1:
                connected = 1
            elif connected == 1:
                pass
            
            print(line.encode('utf-8'))
            ## Search for all IRC commands ##
            if line.find('PING') !=-1:
                client.pong(line)
            if line.find('.reload') !=-1:
                reload_all_plugins()
            message = re.match('^:((?P<user>[^\!]+)\!(?P<ident>[^@]+)@(?P<userhost>[^\s]+)|(?P<domain>([^\s]+)))\s(?P<type>([^\s]+))\s((?P<target>([^\s]+))\s(?P<message>.*)|(?P<info>.*))', line, re.I)
            if message:
                if message.group('type') == '001':
                    print('server welcome')
                elif message.group('type') == '002':
                    print('server version')
                elif message.group('type') == '003':
                    print('server created')
                elif message.group('type') == '004':
                    print('something')
                elif message.group('type') == '005':
                    print('server cmds supported')
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
                    if message.group('message').find('\x01ACTION')  !=-1:
                        user = message.group('user')
                        channel = message.group('target')
                        msg = message.group('message')[9:-1]
                        for module in loaded_plugins:
                            loaded_objects[module].action(user, channel, msg)
                    elif message.group('message').find('\x01VERSION') !=-1:
                        user = message.group('user')
                        client.notice(user, '\x01VERSION NekoLoliBot [Python3] -alpha-\x01\r\n')
                    elif message.group('message').find('\x01DCC') !=-1:
                        print('privmsg: '+message.group('message'))
                    else:
                        user = message.group('user')
                        if message.group('target') == client.NICK:
                            channel = user
                        else:
                            channel = message.group('target')
                        msg = message.group('message')
                        for module in loaded_plugins:
                            loaded_objects[module].privmsg(user, channel, msg[1:])
                elif message.group('type') == 'NOTICE' and message.group('user') == 'Nickserv':
                    print('Nickserv reply: '+message.group('message'))
                elif message.group('type') == 'NOTICE' and message.group('user') != 'Nickserv':
                    user = message.group('user')
                    channel = message.group('target')
                    msg = message.group('message')
                    for module in loaded_plugins:
                        loaded_objects[module].notice(user, msg[1:])
                elif message.group('type') == 'JOIN':
                    user = message.group('user')
                    channel = message.group('info')[1:]
                    if line.find(client.NICK) !=-1:
                        for module in loaded_plugins:
                            loaded_objects[module].joined(user, channel)
                    else:
                        for module in loaded_plugins:
                            loaded_objects[module].userJoined(user, channel)
                elif message.group('type') == 'PART':
                    user = message.group('user')
                    if message.group('info'):
                        channel = message.group('info')[1:]
                    elif message.group('target'):
                        channel = message.group('target')
                    if line.find(client.NICK) !=-1:
                        for module in loaded_plugins:
                            loaded_objects[module].left(user, channel)
                    else:
                        for module in loaded_plugins:
                            loaded_objects[module].userLeft(user, channel)
                elif message.group('type') == 'KICK':
                    kicker = message.group('user')
                    channel = message.group('target')
                    msg = re.match('(?P<kickee>[^\s]+)\s:(?P<msg>.*)', message.group('message'), re.I)
                    kickee = msg.group('kickee')
                    if kickee == client.NICK:
                        for module in loaded_plugins:
                            loaded_objects[module].kicked(channel, kicker, msg.group('msg'))
                    else:
                        for module in loaded_plugins:
                            loaded_objects[module].userKicked(kickee, channel, kicker, msg.group('msg'))
                elif message.group('type') == 'NICK':
                    user = message.group('user')
                    newnick = message.group('info')[1:]
                    for module in loaded_plugins:
                        loaded_objects[module].nick(user, newnick)
                elif message.group('type') == 'QUIT':
                    user = message.group('user')
                    try:
                        quitMessage = message.group('message')
                    except Exception:
                        quitMessage = None
                        pass
                    for module in loaded_plugins:
                        loaded_objects[module].userQuit(user, quitMessage)    
                elif message.group('type') == 'MODE':
                    mod = message.group('user')
                    channel = message.group('target')
                    option = re.match('^(?P<options>[^\s]+)(\s|)((?P<user>[^\s]+)|)$', message.group('message'), re.I)
                    mode = option.group('options')
                    try: 
                        user = option.group('user')
                        for module in loaded_plugins:
                            loaded_objects[module].userMode(mod, user, channel, mode)
                    except Exception:
                        for module in loaded_plugins:
                            loaded_objects[module].channelMode(mod, channel, mode[:-1])
                else:
                    print(line.encode('utf-8'))
