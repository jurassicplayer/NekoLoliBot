#!/usr/bin/env python

import os, sys, re, logging
import importlib as i

sys.path.append('system')
from irc_client import IRCClient
from plugin_manager import PluginManager

log_file = 'system/log'
log_format = "%(asctime)s[%(name)14s][%(levelname)8s] %(message)s"
date_format = '[%m/%d/%y][%I:%M:%S]'
logging.basicConfig(level=logging.DEBUG, filename=log_file, format=log_format, datefmt=date_format)
log = logging.getLogger('NekoLoliBot')

import queue
recv_queue = queue.Queue()
if __name__ == '__main__':
    log.info('>> Starting bot...')
    #Instantiate a client
    client = IRCClient(recv_queue)
    plug_manager = PluginManager(recv_queue)
    input('Press Enter to exit.\n')
