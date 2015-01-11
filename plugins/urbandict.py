#!/usr/bin/env python

import template
import re
import html as h
import urllib.request as u
import json

def ud_search(search_term):
    try:
        data = u.urlopen('http://api.urbandictionary.com/v0/define?term='+h.escape(search_term), None,15)
    except urllib.error.URLError:
        return None
    html = h.unescape(data.read().decode('utf-8'))
    jsond = json.loads(html)['list']
    try:
        item = jsond.pop(0)
        if len(item['definition']) < 150:
            definition = item['definition'].split("\r\n")
            result = ' '.join(definition)
        else:
            definition = item['definition'].split("\r\n")
            result = ' '.join(definition)
            result = result[0:150]+'...'
    except IndexError:
        result = None
    return result

def rm_html(html_data):
    cleanr =re.compile('<.*?>', re.I|re.DOTALL)
    cleantext = re.sub(cleanr,'', html_data)
    return cleantext

class IRCScript(template.IRCScript):
    print('loaded urban dictionary')
    def privmsg(self, user, channel, msg): 
        regex = re.match('^!ud\s(?P<search>.*)', msg, re.I)
        if regex:
            result = ud_search(regex.group('search'));
            if result:
                self.sendMsg(channel, str(result))
            else:
                self.sendMsg(channel, "What you are looking for isn't even modern slang.")
