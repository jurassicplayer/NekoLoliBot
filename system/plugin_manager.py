 #!/usr/bin/env python

import os, sys, logging, threading
import importlib as i

#Plugins folder
plugin_folder = 'plugins'
sys.path.append(plugin_folder)

log = logging.getLogger(__name__)
class PluginManager:
    def __init__(self, recv_queue):
        self.plugin_list = set()
        self.process_thread = threading.Thread(target=self.process_data_thread, args=[recv_queue], daemon='true')
        self.process_thread.start()
        self.load_all_plugins()


    def load_plugin(self, plugin_name):
        if plugin_name == "template": return
        try:
            module = i.import_module(plugin_name)
            self.plugin_list.add(plugin_name)
            log.info('Loaded plugin: %s' % plugin_name)
        except:
            log.warning('Failed to load plugin: %s' % plugin_name)
    def unload_plugin(self, plugin_name):
        self.plugin_list.remove(plugin_name)
        del sys.modules[plugin_name]
        try:
            module = sys.modules[plugin_name]
            log.warning('Failed to unload plugin: %s' % plugin_name)
        except KeyError:
            log.info('Unloaded plugin: %s' % plugin_name)
    def reload_plugin(self, plugin_name):
        try:
            module = sys.modules[plugin_name]
            module = i.reload(module)
            log.info('Reloaded plugin: %s' % plugin_name)
        except KeyError:
            module = load_plugin(plugin_name)
    def load_all_plugins(self):
        for file_name in os.listdir(plugin_folder):
            if file_name.endswith(".py"):
                plugin_name = file_name[:-3]
                self.load_plugin(plugin_name)
    def unload_all_plugins(self):
        for plugin_name in plugin_list:
            self.unload_plugin(plugin_name)
    def reload_all_plugins(self):
        for plugin_name in plugin_list:
            self.reload_plugin(plugin_name)


    def process_data_thread(self, recv_queue):
        while 1:
            server, message = recv_queue.get()
            log.info(server.HOST + ' ' + message.raw_message)
            recv_queue.task_done()
