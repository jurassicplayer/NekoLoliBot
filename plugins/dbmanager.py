#!/usr/bin/env python
import template
import pickle, re, logging

class databaseManager():
    def load_database(user):
        try:
            database = pickle.load(open('data/user.db', 'rb'))
            userdb = database[user]
        except KeyError:
            print('KeyError, user not found. Adding new user. Remember to save database.')
            database.update({user: {}})
            userdb = database[user]
        except FileNotFoundError:
            print('Database not found, reinitializing Remember to save database.')
            userdb = {}
        return userdb
        
        
    def load_parameter(userdb, parameter, default):
        try:
            userparameter = userdb[parameter]
        except KeyError:
            print('KeyError, parameter not found. Adding new parameter. Remember to save database.')
            userdb.update({parameter: default})
            userparameter = default
        return userdb, userparameter

        
    def save_database(user, new_userdb):
        try:
            database = pickle.load(open('data/user.db', 'rb'))
            database[user] = new_userdb
            pickle.dump(database, open('data/user.db', 'wb'))
            logging.info('**dbm** Synced to database: <%s> %s' % (user, new_userdb))
        except:
            database = {user: new_userdb}
            pickle.dump(database, open('data/user.db', 'wb'))
            logging.info('**dbm** Created new database: <%s> %s' % (user, new_userdb))
    def print_database():
        database = pickle.load(open('data/user.db', 'rb'))
        logging.info('**dbm** Printed database')
        print(database)

class IRCScript(template.IRCScript):
    print('loaded dbm')
    def privmsg(self, user, channel, msg):
        regex = re.match('^\.dbm\s(?P<target>([^\s]+))', msg, re.I)
        if re.match('^\.dbm$', msg, re.I):
            databaseManager.print_database();
        elif regex:
            userinfo = databaseManager.load_database(regex.group('target'))
            logging.info('**dbm** <%s> Printed user info of %s' %(user, regex.group('target')))
            print(userinfo)
