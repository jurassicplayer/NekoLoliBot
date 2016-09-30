 #!/usr/bin/env python

import importlib, logging, os, re, sys, threading

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
            module = importlib.import_module(plugin_name)
            self.plugin_list.add(plugin_name)
            log.info('>> Loaded plugin: %s' % plugin_name)
        except:
            e = sys.exc_info()
            error_string = '>> Plugin error: (%s) "%s: %s"' % (plugin_name, str(e[0]).split("'")[1], e[1])
            log.error(error_string)
            print(error_string)
    def unload_plugin(self, plugin_name):
        self.plugin_list.remove(plugin_name)
        del sys.modules[plugin_name]
        try:
            module = sys.modules[plugin_name]
            log.warning('>> Failed to unload plugin: %s' % plugin_name)
        except KeyError:
            log.info('>> Unloaded plugin: %s' % plugin_name)
    def reload_plugin(self, plugin_name):
        try:
            module = sys.modules[plugin_name]
            module = importlib.reload(module)
            log.info('>> Reloaded plugin: %s' % plugin_name)
        except KeyError:
            module = self.load_plugin(plugin_name)
    def load_all_plugins(self):
        for file_name in os.listdir(plugin_folder):
            if file_name.endswith(".py"):
                plugin_name = file_name[:-3]
                self.load_plugin(plugin_name)
    def unload_all_plugins(self):
        plugin_list = self.plugin_list.copy()
        for plugin_name in plugin_list:
            self.unload_plugin(plugin_name)
    def reload_all_plugins(self):
        for plugin_name in self.plugin_list:
            self.reload_plugin(plugin_name)

    def process_data_thread(self, recv_queue):
        while 1:
            server, message = recv_queue.get()
            plugin_msg = re.match('^.plugin.*', message.trailing, re.I)
            if plugin_msg:
                module = sys.modules['plugin']
                p = module.IRCScript(server)
                p.pluginmsg(self, message.prefix, message.user, message.host, message.cmd, message.params, message.trailing)
            else:
                for plugin_name in self.plugin_list:
                    module = sys.modules[plugin_name]
                    try:
                        p = module.IRCScript(server)
                        p.servermsg(message.prefix, message.user, message.host, message.cmd, message.params, message.trailing)
                        if message.cmd == 'ACTION': p.action(message.prefix, message.params, message.trailing)
                        elif message.cmd == 'JOIN': p.join(message.prefix, message.trailing)
                        elif message.cmd == 'KICK': p.kick(message.prefix, message.params)
                        elif message.cmd == 'MODE': pass #p.mode() #FIXIT
                        elif message.cmd == 'NICK': p.nick(message.prefix, message.params)
                        elif message.cmd == 'NOTICE': p.notice(message.prefix, message.params, message.trailing)
                        elif message.cmd == 'PART': p.part(message.prefix, message.params)
                        elif message.cmd == 'PRIVMSG': p.privmsg(message.prefix, message.params, message.trailing)
                        elif message.cmd == 'QUIT': pass #p.quit() #FIXIT
                    except:
                        e = sys.exc_info()
                        error_string = '>> Plugin error: (%s) "%s: %s"' % (plugin_name, str(e[0]).split("'")[1], e[1])
                        log.error(error_string)
                        print(error_string)
            recv_queue.task_done()
