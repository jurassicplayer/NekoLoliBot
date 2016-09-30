#!/usr/bin/env python

import template
import logging, pickle, pprint, re, sys, time

log = logging.getLogger(__name__)
class databaseManager:
    def __init__(self):
        self.database = self.open_database()
        self.sentinel = object()

    def add_user(self, user):
        if user not in ('Global', 'NickServ', ''):
            if user not in self.database:
                entry = {'irc_stats': {'alt_nicks': self.sentinel,
                                       'auth': self.sentinel,
                                       'current_mode': self.sentinel,
                                       'current_nick': self.sentinel,
                                       'last_message': self.sentinel,
                                       'last_seen': self.sentinel,},
                         'last_updated': time.ctime(),}
                self.database.update({user: entry}
                )
            else:
                entry = self.database[user]
            return entry
    def del_user(self, user):
        #FIXIT
        pass
    def set_parameter(self, user, param, new_value):
        #FIXIT
        self.database[user]['last_updated'] = time.ctime()
        pass
    def get_parameter(self, user, parameter):
        user_database = self.add_user(user)
        if user_database:
            value = self.recursive_search(parameter, user_database)
            return value
    def recursive_search(self, parameter, dictionary):
        if parameter in dictionary:
            if dictionary[parameter] is not self.sentinel:
                return dictionary[parameter]
        else:
            for k, v in dictionary.items():
                if isinstance(v, dict):
                    value = self.recursive_search(parameter, v)
                    if value is not self.sentinel:
                        return value
    def open_database(self):
        try:
            data = pickle.load(open('system/db', 'rb'))
        except FileNotFoundError:
            ERROR_DBNOTFOUND = '>> Database not found. Remember to save.'
            log.warning(ERROR_DBNOTFOUND)
            print(ERROR_DBNOTFOUND)
            data = {}
        return data
    def close_database(self):
        try:
            pickle.dump(self.database, open('system/db', 'wb'))
        except:
            e = sys.exc_info()
            error_string = '>> Database not saved: "%s: %s"' % (str(e[0]).split("'")[1], e[1])
            log.error(error_string)
            print(error_string)
    def export_database(self):
        data = self.database.copy()
        data = self.recursive_replace(data)
        pprint.pprint(data)
    def recursive_replace(self, dictionary):
        for k, v in dictionary.items():
            if isinstance(v, dict):
                dictionary[k] = self.recursive_replace(v)
            elif v == self.sentinel:
                dictionary[k] = ''
        return dictionary
dM_object = databaseManager()

class IRCScript(template.IRCScript):
    def privmsg(self, origin, target, msg):
        DM = sys.modules['database'].dM_object
        dm_msg = re.match('^\.db(?P<command>.*)', msg, re.I)
        if dm_msg:
            command = dm_msg.group('command')
            command = str.rstrip(command)
            command = str.strip(command)
            if command == '':
                DM.export_database()
            elif command == 'add':
                user = dm_msg.group('command').split(' ')[1]
                DM.add_user(origin)
            elif command == 'update': 
                DM.set_parameter(origin, '')
                DM.database[origin]['irc_stats']['last_message'] = msg
            elif command == 'search':
                print(DM.get_parameter(origin, 'last_message'))
