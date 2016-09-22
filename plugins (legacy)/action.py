#!/usr/bin/env python

import template
import re


action_database = {
    'hug':  {'self':   ["pulls %s's head to her chest and gives a warm embrace.",                      'action',   'sub'], 
             'other':  ["brings %s closer to her heart with a loving hug.",                            'action',   'sub'],
             'bot':    ["I don't want to stoop to your level.",                                        'msg',    'nosub'],
             'action': ["Ehehehe~ *///////*",                                                          'msg',    'nosub']
            },
    'kiss': {'self':   ["gives %s a shy peck on the cheek and scampers away, crimson-faced.",          'action',   'sub'],
             'other':  ["goes up to %s, but can't bring herself to do it.",                            'action',   'sub'],
             'bot':    ["I'm not a one-girl yuri show!",                                               'msg',    'nosub'],
             'action': ["W-W-Wha-What do you think you are doing!",                                    'msg',    'nosub']
            },
    'love': {'self':   ["looks at you questioningly.",                                                 'action', 'nosub'],
             'other':  ["You can't tell me who to fall in love with~!",                                'msg',    'nosub'],
             'bot':    ["I don't-...are you feeling alright?",                                         'msg',    'nosub'],
             'action': ["I love you too, Onii-chan~! (♡´･ᴗ･`♡)",                                       'msg',    'nosub']
            },
    'praise': {'self': ["I'm so proud of you, %s nii-chan!",                                           'msg',      'sub'],
             'other':  ["puffs her chest and looks at %s proudly.",                                    'action',   'sub'],
             'bot':    ["I did well if I had to say so myself <3 ~!",                                  'msg',    'nosub'],
             'action': ["Thank you~! I tried really hard.",                                            'msg',    'nosub']
            },
    'pet':  {'self':   ["softly pets %s head with a warm smile.",                                      'action',   'sub'],
             'other':  ["reaches up as high as possible, standing on her tiptoes and pets %s's head.", 'action',   'sub'],
             'bot':    ["I don't really want to pet myself, but you can pet me~!",                     'msg',    'nosub'],
             'action': ["(๑´◡`๑) *funyaa~*",                                                           'msg',    'nosub']
            },
    'pat':  {'self':   ["softly pats %s head with a warm smile.",                                      'action',   'sub'],
             'other':  ["reaches up as high as possible, standing on her tiptoes and pats %s's head.", 'action',   'sub'],
             'bot':    ["I don't really want to pat myself, but you can pat me~!",                     'msg',    'nosub'],
             'action': ["(๑´◡`๑) *funyaa~*",                                                           'msg',    'nosub']
            }
    }

class IRCScript(template.IRCScript):
    print('loaded actions')
    def privmsg(self, user, channel, msg):
        regex = re.match("^-(?P<action>[^\s]+)(\s(?P<target>([^\s]+))|)$", msg, re.I)
        for action in action_database:
            try:
                if regex.group('action') == action:
                    ## Determine who is being targeted ##
                    if regex.group('target') == 'me' or regex.group('target') == None:
                        target = 'self'
                        target_nick = user
                    elif regex.group('target') == 'yourself' or regex.group('target') == self.NICK:
                        target = 'bot'
                        target_nick = self.NICK
                    else:
                        target = 'other'
                        target_nick = regex.group('target')
                    ## Figure out what to reply with based on database ##
                    if action_database[action][target][1] == 'msg' and action_database[action][target][2] == 'sub':
                        self.sendMsg(channel, action_database[action][target][0] % target_nick)
                    elif action_database[action][target][1] == 'msg' and action_database[action][target][2] == 'nosub':
                        self.sendMsg(channel, action_database[action][target][0])
                    elif action_database[action][target][1] == 'action' and action_database[action][target][2] == 'sub':
                        self.sendAction(channel, action_database[action][target][0] % target_nick)
                    elif action_database[action][target][1] == 'action' and action_database[action][target][2] == 'nosub':
                        self.sendAction(channel, action_database[action][target][0])
            except:
                pass
    def action(self, user, channel, msg):
        regex = re.match("^(?P<action>[^\s]+)s(\s(?P<target>([^\s]+))|)$", msg, re.I)
        for action in action_database:
            try:
                if regex.group('action') == action or regex.group('action') == action+'e':
                    ## Determine who is being targeted ##
                    if regex.group('target') == self.NICK:
                        target = 'action'
                    ## Figure out what to reply with based on database ##
                    if action_database[action][target][1] == 'msg' and action_database[action][target][2] == 'sub':
                        self.sendMsg(channel, action_database[action][target][0] % user)
                    elif action_database[action][target][1] == 'msg' and action_database[action][target][2] == 'nosub':
                        self.sendMsg(channel, action_database[action][target][0])
                    elif action_database[action][target][1] == 'action' and action_database[action][target][2] == 'sub':
                        self.sendAction(channel, action_database[action][target][0] % user)
                    elif action_database[action][target][1] == 'action' and action_database[action][target][2] == 'nosub':
                        self.sendAction(channel, action_database[action][target][0])
            except:
                pass
