 #!/usr/bin/env python
import re
import template
class IRCScript(template.IRCScript):
    print('<< Py_Exec loaded, should not be loaded normally. This is for lazy asshats only.')
    def privmsg(self, origin, target, msg):
        regex = re.match('^\.py\s(?P<user_cmd>.*)', msg, re.I)
        if regex:
            exec(regex.group('user_cmd'))
