#!/usr/bin/env python

import template
import re, base64
import urllib.parse as up
import pycurl, io, json
import config

class bitlyManager:
    def __init__(self):
        self.auth = config.BITLY_CLIENTID + ':' + config.BITLY_CLIENT_SECRET
        post_data = {'grant_type': 'password',
                     'username': config.BITLY_USER,
                     'password': config.BITLY_PASS}
        self.postfields = up.urlencode(post_data)
        self.access_token = ''
        self.retrieve_auth();
        
    def retrieve_auth(self):
        c = pycurl.Curl()
        c.setopt(c.URL, 'https://api-ssl.bitly.com/oauth/access_token')
        c.setopt(c.USERPWD, self.auth)
        c.setopt(c.POSTFIELDS, self.postfields)
        b = io.BytesIO()
        c.setopt(pycurl.WRITEFUNCTION, b.write)
        c.perform()
        c.close()
        data = b.getvalue().decode('utf-8')
        token = json.loads(data)
        self.access_token = token['access_token']
     
    def shorten_url(self, url):
        params = {'access_token':self.access_token, 'longUrl': url, 'domain': 'j.mp'}
        c = pycurl.Curl()
        c.setopt(c.URL, 'https://api-ssl.bitly.com/v3/shorten' + '?' + up.urlencode(params))
        b = io.BytesIO()
        c.setopt(pycurl.WRITEFUNCTION, b.write)
        c.perform()
        c.close()
        data = b.getvalue().decode('utf-8')
        result = json.loads(data)
        try:
            shortened_url = result['data']['url']
        except Exception as e:
            print(e)
            shortened_url = None
        return shortened_url

class IRCScript(template.IRCScript):
    print('loaded bitly')
    def privmsg(self, user, channel, msg):
        shortening = re.match('^\.bitly\s(?P<url>[^\s]+)', msg, re.I)
        if shortening:
            b = bitlyManager();
            if 'http://' not in shortening.group('url'):
                url = 'http://' + shortening.group('url')
            else:
                url = shortening.group('url')
            shortened_url = b.shorten_url(url);
            if shortened_url:
                self.sendMsg(channel, shortened_url)
            else:
                self.sendNotice(user, 'It failed.')
