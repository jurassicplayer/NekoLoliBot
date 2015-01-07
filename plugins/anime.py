#!/usr/bin/env python

import template
import re, random
import html as h
import urllib.request as u
from colorize import Colorize as c

def nyaa_search(search, category, filtering, sorting, ordering):
    search_term = search
    nyaa_categories = {
        'All':                                              '0_0',       #All categories
        'Anime':                                            '1_0',       #Anime
        'AMV':                                             '1_32',       #Anime - Anime Music Video
        'Anime - English-translated Anime':                '1_37',       #Anime - English-translated Anime
        'Anime - Non-English-translated Anime':            '1_38',       #Anime - Non-English-translated Anime
        'Anime - Raw Anime':                               '1_11',       #Anime - Raw Anime
        'Audio':                                            '3_0',       #Audio
        'Audio - Lossless Audio':                          '3_14',       #Audio - Lossless Audio
        'Audio - Lossy Audio':                             '3_15',       #Audio - Lossy Audio
        'Lit':                                              '2_0',       #Literature
        'Literature - English-translated Literature':      '2_12',       #Literature - English-translated Literature
        'Literature - Non-English-translated Literature':  '2_39',       #Literature - Non-English-translated Literature
        'Literature - Raw Literature':                     '2_13',       #Literature - Raw Literature
        'Live':                                             '5_0',       #Live Action
        'Live Action - English-translated Live Action':    '5_19',       #Live Action - English-translated Live Action
        'Live Action - Live Action Promotional Video':     '5_22',       #Live Action - Live Action Promotional Video
        'Live Action - Non-English-translated Live Action':'5_21',       #Live Action - Non-English-translated Live Action
        'Live Action - Raw Live Action':                   '5_20',       #Live Action - Raw Live Action
        'Pic':                                              '4_0',       #Pictures
        'Pictures - Graphics':                             '4_18',       #Pictures - Graphics
        'Pictures - Photos':                               '4_17',       #Pictures - Photos
        'Software':                                         '6_0',       #Software
        'Software - Applications':                         '6_23',       #Software - Applications
        'Software - Games':                                '6_24'        #Software - Games
        }
    if category:
        for cat in nyaa_categories:
            if cat == category:
                search_cat = nyaa_categories[category]
            else:
                search_cat = nyaa_categories['All']
    else:
        search_cat = nyaa_categories['All']
    if filtering:
        if filtering == 'All':
            search_filter = '0'
        elif filtering == 'Remake':
            search_filter = '1'
        elif filtering == 'Trusted':
            search_filter = '2'
        elif filtering == 'A+':
            search_filter = '3'
        else:
            search_filter = '0'
    else:
        search_filter = '0'
    if sorting:
        if sorting == 'Date':
            search_sort = '1'
        elif sorting == 'Seed':
            search_sort = '2'
        elif sorting == 'Leech':
            search_sort = '3'
        elif sorting == 'DLs':
            search_sort = '4'
        elif sorting == 'Size':
            search_sort = '5'
        elif sorting == 'Name':
            search_sort = '6'
        else:
            search_sort = '1'
    else:
        search_sort = '1'
    if ordering:
        if ordering == 'Ascend':
            search_order = '2'
        elif order == 'Descend':
            search_order = '1'
        else:
            search_order = '1'
    else:
        search_order = '1'
    try:
        data = u.urlopen('http://www.nyaa.se/?page=search&cats='+search_cat+'&filter='+search_filter+'&sort='+search_sort+'&order='+search_order+'&term='+h.escape(search_term)+'&offset=1', None,15)
    except urllib.error.URLError:
        return None
    html = h.unescape(data.read().decode('utf-8'))
    pattern = re.compile('.*?class="((?P<filter>[^\s]+)\s|)tlistrow.*?tlistname"><a href="(?P<infolink>[^"]+)">(?P<title>(?:(?!<\/a>).)*).*?tlistdownload"><a href="(?P<dl_link>[^"]+)".*?tlistsize">(?P<size>(?:(?!<\/td>).)*).*?tlistsn">(?P<seed>(?:(?!<\/td>).)*).*?tlistln">(?P<leech>(?:(?!<\/td>).)*).*?tlistdn">(?P<down>(?:(?!<\/td>).)*).*?tlistmn">(?P<comment>(?:(?!<\/td>).)*).*?', re.I)
    match_index = 0
    result = []
    for match in pattern.finditer(html):
        if match_index < 3:
            result.append([str(match.group('filter')), str(match.group('infolink')), str(match.group('title')), str(match.group('dl_link')), str(match.group('size')), str(match.group('seed')), str(match.group('leech')), str(match.group('down')), str(match.group('comment'))])
            match_index +=1
        else: break
    return result
        

class IRCScript(template.IRCScript):
    print('loaded anime')
    def privmsg(self, user, channel, msg):
        if re.match('Madoka', msg, re.I):
            self.sendMsg(channel, '／人◕ ‿‿ ◕人＼ ＷＯＮ’Ｔ　ＹＯＵ　ＢＥＣＯＭＥ　Ａ　ＭＡＧＩＣＡＬ　ＧＩＲＬ？')
        if re.match('HAIL BUNNY', msg, re.I):
            self.sendMsg(channel, 'http://i.imgur.com/O5ibQ6p.gif')
        if re.match('^-kokoro$', msg, re.I):
            self.sendMsg(channel, 'http://i.imgur.com/gGg4hvE.jpg')
        nyaa = re.match('^.nyaa\s(?P<message>.*)', msg, re.I)
        if nyaa:
            message = nyaa.group('message')
            flags = {}
            while message.find('-') !=-1:
                option = re.match('-(?P<flag>[^\s]+)\s(?P<argument>[^\s]+)\s(?P<message>.*)', message, re.I)
                flags.update({option.group('flag'): option.group('argument')})
                message = option.group('message')
            try:
                category = flags['cat']
            except KeyError:
                category = None
            try:
                filtering = flags['filter']
            except KeyError:
                filtering = None
            try:
                sorting = flags['sort']
            except KeyError:
                sorting = None
            try:
                ordering = flags['order']
            except KeyError:
                ordering = None
            result = nyaa_search(message, category, filtering, sorting, ordering)
            if result:
                for x in range(0, len(result)):
                    self.sendMsg(channel, c.color(result[x][2], 'white', 'black')+' | [S: '+c.color(result[x][5], 'lightgreen', None)+' L: '+c.color(result[x][6], 'red', None)+']['+result[x][4]+']')
                    self.sendMsg(channel, 'Info: '+result[x][1]+'       DL link: '+result[x][3])
            else:
                self.sendMsg(channel, 'The search gave no results or timed out.')
        if re.match('^-chart', msg, re.I):
            self.sendMsg(channel, 'http://anichart.net')

    def action(self, user, channel, msg):
        regex = re.match("^slaps\s"+self.nick+"$", msg, re.I)
        if regex:
            self.sendMsg(channel, 'http://i.imgur.com/EVAWS04.gif')
