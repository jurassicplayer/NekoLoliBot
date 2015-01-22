#!/usr/bin/env python

import template
import re
import html as h
import urllib.request as ur
import urllib.parse as up

def isup(url):
    try:
        data = ur.urlopen('http://isup.me/'+up.quote_plus(url), None, 15)
    except Exception as e:
        print(e)
        return
    html = h.unescape(data.read().decode('utf-8'))
    match =  re.match('.*?"container">[^\w]+(?P<status>[^<]+)<[^>]+>(?P<url>[^<]+)<[^>]+>(<[^>]+>|)(?P<urlstatus>[^<]+)<.*?', html, re.I|re.DOTALL)
    status = match.group('status')[:-1]+match.group('url')+match.group('urlstatus')
    return status

class IRCScript(template.IRCScript):
    print('loaded isup')
    def privmsg(self, user, channel, msg):
        isitup = re.match('^\.isup\s(?P<url>[^\s]+)?', msg, re.I)
        if isitup:
            status = isup(isitup.group('url'))
            self.sendMsg(channel, status)
