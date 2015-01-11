#!/usr/bin/env python

import template
import re, pickle, time, logging
from dbmanager import databaseManager as dbm

class noteManager():
    def new_note(user, target, msg):
        userdb = dbm.load_database(target);
        userdb, notes = dbm.load_parameter(userdb, 'note', {user: []});
        try:
            notes[user].append(msg)
        except KeyError:
            notes.update({user: [msg]})
        userdb['note'].update(notes)
        dbm.save_database(target, userdb);
        logging.info('<<NM>> '+user+' made a new note for '+target)
    def del_note(user, target, cycles):
        cycles = int(cycles)
        userdb = dbm.load_database(target);
        userdb, notes = dbm.load_parameter(userdb, 'note', {user: []});
        if len(userdb['note'][user]) >= cycles:
            for x in range(0, cycles):
                userdb['note'][user].pop()
            state = 'success'
            dbm.save_database(target, userdb);
            logging.info('<<NM>> '+user+' deleted a note for '+target)
        else:
            state = 'failure'
        return state
    def show_note(user):
        userdb = dbm.load_database(user);
        userdb, notes = dbm.load_parameter(userdb, 'note', {user: []});
        for note_leaver in notes:
            all_notes = []
            for available_note in notes[note_leaver]:
                all_notes.append('['+note_leaver+'] '+available_note)
        userdb['note'] = {user: []}
        dbm.save_database(user, userdb);
        return all_notes
        
class IRCScript(template.IRCScript):
    print('loaded note')
    def privmsg(self, user, channel, msg):
        ## Creating note ##
        create_note = re.match('^.note\s(?P<target>[^\s]+)\s(?P<note>.*)', msg, re.I)
        if create_note:
            noteManager.new_note(user, create_note.group('target'), create_note.group('note'));
        ## Deleting notes ##
        delete_note = re.match('^.del(\s|)note\s(?P<target>[^\s]+)(\s(?P<cycles>0?[1-9]|[1-9][0-9])|)', msg, re.I)
        if delete_note:
            if delete_note.group('cycles') == None:
                cycles = 1
            elif int(delete_note.group('cycles')) <= 0:
                self.sendMsg(channel, 'No notes were deleted.')
                cycles = 0
            else:
                cycles = delete_note.group('cycles')
            state = noteManager.del_note(user, delete_note.group('target'), cycles)
            if state == 'failure':
                self.sendMsg(channel, 'Failed to remove note(s).')
            elif state == 'success':
                self.sendMsg(channel, 'Removed '+str(cycles)+' note(s) from queue.')
        ## Checking notes ##
        try:
            if user.find('.') !=-1 or user.find('py-ctcp') !=-1:
                pass
            else:
                all_notes = noteManager.show_note(user);
                for notes in all_notes:
                    self.sendNotice(user, notes)
        except AttributeError:
            pass
