#!/usr/bin/env python

class Client:
    def connect_server(self, *args, **kwargs): pass
    def disconnect_server(self, *args, **kwargs): pass
    def connect_channel(self, *args, **kwargs): pass
    def disconnect_channel(self, *args, **kwargs): pass
    def read_config(self): pass
class Server:
    def __init__(self):
        self.commands = []
    def setup(self, *args, **kwargs): pass
    def recv_data(self): pass
    def send_data(self, cmd, args):
        if cmd in self.commands:
            getaddr(self, cmd)(args)
class Channel:
    def setup(self, *args, **kwargs): pass
