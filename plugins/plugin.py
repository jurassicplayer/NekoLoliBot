 #!/usr/bin/env python
import re, sys
import template
class IRCScript(template.IRCScript):
    def pluginmsg(self, PM, prefix, user, host, command, params, msg):
        plugin_msg = re.match('^.plugin\s(?P<command>\S+)\s(?P<plugins>.*)', msg, re.I)
        if plugin_msg:
            plugins = plugin_msg.group('plugins')
            if plugins != 'all':
                plugins = plugins.replace('|', ' ').replace(',',' ')
                plugins = plugins.split(' ')
            if plugin_msg.group('command') == 'load':
                if plugins == 'all':
                    PM.load_all_plugins()
                else:
                    for plugin_name in plugins:
                        PM.load_plugin(plugin_name)
            elif plugin_msg.group('command') == 'unload':
                if plugins == 'all':
                    PM.unload_all_plugins()
                else:
                    for plugin_name in plugins:
                        PM.unload_plugin(plugin_name)
            elif plugin_msg.group('command') == 'reload':
                if plugins == 'all':
                    PM.reload_all_plugins()
                else:
                    for plugin_name in plugins:
                        PM.reload_plugin(plugin_name)
            elif plugin_msg.group('command') == 'list':
                if plugins == 'all':
                    self.sendMsg(params, PM.plugin_list)
