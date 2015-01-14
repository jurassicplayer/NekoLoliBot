#!/usr/bin/env python
import template
import pickle, re, logging

class databaseManager:
    def __init__(self, database):
        self.db = database
        self.data = ''
        
    def load_database(self):
        try:
            self.data = pickle.load(open('data/'+self.db+'.db', 'rb'))
        except FileNotFoundError:
            print('Database not found. Remember to save.')
            self.data = {}
        return self.data
        
        
    def load_parameter(self, dataid, parameter, default):
        try:
            unitData = self.data[dataid]
        except KeyError:
            print('ID not found. Adding new ID. Remember to save.')
            self.data.update({dataid: {}})
            unitData = self.data[dataid]
        try:
            unitParameter = unitData[parameter]
        except KeyError:
            if default != None:
                print('Parameter not found. Adding new parameter. Remember to save.')
                unitData.update({parameter: default})
                unitParameter = unitData[parameter]
            else:
                print('Parameter not found. Default is None.')
                unitParameter = None
        return unitData, unitParameter

        
    def save_database(self, dataid, new_unitData):
        try:
            self.data[dataid] = new_unitData
            pickle.dump(self.data, open('data/'+self.db+'.db', 'wb'))
            logging.info('**dbm** Synced to %s DB: <%s> %s' % (self.db, dataid, new_unitData))
        except:
            self.data.update({dataid: new_unitData})
            pickle.dump(self.data, open('data/'+self.db+'.db', 'wb'))
            logging.info('**dbm** Created new DB [%s]: <%s> %s' % (self.db, dataid, new_unitData))
            print('Added to database')

    def print_database(self):
        database = pickle.load(open('data/'+self.db+'.db', 'rb'))
        logging.info('**dbm** Printed database')
        print(database)
        

class IRCScript(template.IRCScript):
    print('loaded dbm')
    def privmsg(self, user, channel, msg):
        regex = re.match('^\.dbm\s(?P<target>([^\s]+))', msg, re.I)
        if re.match('^\.dbm$', msg, re.I):
            userdbm = databaseManager('user')
            userdbm.print_database()
