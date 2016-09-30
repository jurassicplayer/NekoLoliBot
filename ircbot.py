#!/usr/bin/env python

import sys, logging
import importlib as i
try:
    import readline
except: pass

sys.path.append('system')
from irc_client import IRCClient
from plugin_manager import PluginManager

log_file = 'system/log'
log_format = "%(asctime)s[%(name)14s][%(levelname)8s] %(message)s"
date_format = '[%m/%d/%y][%I:%M:%S]'
logging.basicConfig(level=logging.DEBUG, filename=log_file, format=log_format, datefmt=date_format)
log = logging.getLogger('NekoLoliBot')


def process_command(irc_client, irc_cmd):
    irc_cmd = irc_cmd.split(' ', 1)
    try:
        server = irc_cmd[0]
        message = irc_cmd[1]
        irc_client.server_list[server].sendIRC(str(message))
    except:
        e = sys.exc_info()
        error_string = '>> Manual message error: (root) "%s: %s"' % (str(e[0]).split("'")[1], e[1])
        log.error(error_string)
        print(error_string)
def populate_serverlist():
    srv_list = []
    for i, server_name in enumerate(irc_client.server_list):
        print('[%s] %s' % (i, server_name))
        srv_list.append(server_name)
    return srv_list


import queue
recv_queue = queue.Queue()
if __name__ == '__main__':
    log.info('>> Starting bot...')
    #Instantiate a client
    client = IRCClient(recv_queue)
    plug_manager = PluginManager(recv_queue)
    while 1:
        irc_cmd = input()
        if irc_cmd == 'exit': break
        elif irc_cmd: process_command(client, irc_cmd)
        else: pass
