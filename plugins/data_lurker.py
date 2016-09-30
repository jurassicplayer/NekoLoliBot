#!/usr/bin/env python

import template
import logging, sys, time

log = logging.getLogger(__name__)
class IRCScript(template.IRCScript):
    def servermsg(self, prefix, user, host, command, params, trailing):
        DM = sys.modules['database'].dM_object
        user = DM.add_user(prefix)
        if command == 'RPL_NAMREPLY':
            users = trailing.replace('~', '').replace('&', '').replace('@', '').replace('%', '').replace('+', '')
            user_list = users.split(' ')
            for user in user_list:
                self.sendMsg('NickServ', 'status %s' % user)
        elif command == 'JOIN':
            self.sendMsg('NickServ', 'status %s' % prefix)
        elif command == 'NOTICE':
            if prefix == 'NickServ':
                try:
                    nickserv_args = trailing.split(' ')
                    if nickserv_args[0] == 'STATUS':
                        prefix = nickserv_args[1]
                        user = DM.add_user(prefix)
                        user['irc_stats'].update({'auth': nickserv_args[2]})
                except: pass
        elif command == 'PRIVMSG':
            if prefix and user and host and trailing:
                user['irc_stats'].update({'last_message' : trailing,
                                          'last_seen' : time.ctime()})
        elif command in ('QUIT', 'PART'):
            user['irc_stats'].update({'auth' : 0})
        try:
            user.update({'last_updated': time.ctime()})
            DM.database[prefix] = user
        except: pass
"""
[Prefix: irc.gbatemp.net]   [User: ]            [Host: ]             [Cmd: RPL_NAMREPLY]    [Params: jplayer_bot = #gbatemp.net][Trailing: jplayer_bot VinsCool Shinobi Artemis-kun Forstride CheatFreak +jplayer &FAST6191 Surkow|laptop SES Cishet_Incel Taco_Mac balrog Phazon liomajor bug +|Shadow| &p1ngpong drf|Desktop capin Framework ~Costello +Lyn +Normmatt SmithsX Tempy &duck Venko Cyan smea itoikenza +signz Arif Kai DaChekka +Breith Spilly @FIX94 amrod +Jdbye Bandit shiftedabsurdity &BotServ]
[Prefix: irc.gbatemp.net]   [User: ]            [Host: ]             [Cmd: RPL_ENDOFNAMES]  [Params: jplayer_bot #gbatemp.net]  [Trailing: End of /NAMES list.]
[Prefix: irc.gbatemp.net]   [User: ]            [Host: ]             [Cmd: 307]             [Params: jplayer_bot jplayer]       [Trailing: is identified for this nick]
[Prefix: Katsuhiko]         [User: masa-sama]   [Host: gbatemp-2A802][Cmd: JOIN]            [Params: :#gbatemp.net]             [Trailing: ]
[Prefix: Smiths]            [User: bluesclues]  [Host: 575D56DA.7E]  [Cmd: JOIN]            [Params: :#gbatemp.net]             [Trailing: ]

[Prefix: Smiths][User: bluesclues][Host: 575D56DA.7E512AAB.668FAF7.IP][Cmd: QUIT][Params: :Quit: aye aye aye][Trailing: ]
[Prefix: NickServ]          [User: services]    [Host: services.host][Cmd: NOTICE]          [Params: jplayer_bot]               [Trailing: STATUS jplayer 3 jplayer]
"""
