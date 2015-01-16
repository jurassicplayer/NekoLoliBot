#!/usr/bin/env python

import template
import re, json
import html as h
import urllib.parse as up


def url_generator(fromLang, toLang, search_string):
    ## Should be checking if fromLang and toLang are actual languages and match or convert them to match via dictionary or something ##
    url = 'http://translate.google.com/translate_a/t?client=t&text=%s&hl=en&sl=%s&tl=%s&ie=UTF-8&oe=UTF-8&multires=1&otf=1&pc=1&trs=1&ssel=3&tsel=6&sc=1' % (up.quote_plus(search_string), fromLang, toLang)
    return url

## Translate from English to Japanese ##
import pycurl, io
def request_data(url):
    
    ## Generate curl request ##
    c = pycurl.Curl()
    c.setopt(pycurl.URL, url)
    c.setopt(pycurl.COOKIEJAR, 'system/cookie.txt')
    ## Write curl output to io ##
    b = io.BytesIO()
    c.setopt(pycurl.WRITEFUNCTION, b.write)
    c.perform()
    c.close()
    data = b.getvalue().decode('utf-8')
    json_ready = re.sub(',+', ',', data)
    jsond = json.loads(json_ready)
    return jsond[0][0]

class IRCScript(template.IRCScript):
    print('loaded translate')
    def privmsg(self, user, channel, msg):
        translate = re.match('^\.tl\s(?P<from>[a-zA-Z][a-zA-Z])2(?P<to>[a-zA-Z][a-zA-Z])\s(?P<phrase>.*)', msg, re.I)
        if translate:
            tlfrom = translate.group('from')
            tlto = translate.group('to')
            url = url_generator(translate.group('from'), translate.group('to'), translate.group('phrase'));
            tled = request_data(url);
            if tled[2] and tlto == 'ja':
                self.sendMsg(channel, tlfrom+': '+tled[1]+' | '+tlto+': '+tled[0]+' | Romaji: '+tled[2])
            elif tled[2] and tlto == 'zh':
                self.sendMsg(channel, tlfrom+': '+tled[1]+' | '+tlto+': '+tled[0]+' | Pinyin: '+tled[2])
            else:
                self.sendMsg(channel, tlfrom+': '+tled[1]+' | '+tlto+': '+tled[0])
