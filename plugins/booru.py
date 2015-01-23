#!/usr/bin/env python

import template
import re, random
import config
import html as h
import urllib.parse as up
import urllib.request as ur
import xml.etree.ElementTree as etree
from database import databaseManager as dbm
from colorize import Colorize as c
from bitly import bitlyManager


def argsplit(args):
    args = args.split(' ')
    opts = []
    tags = []
    for arg in args:
        if re.match('^-\w+$', arg, re.I):
            for opt in list(arg[1:]):
                opts.append(opt)
        elif re.match('^-\w:\w', arg, re.I):
            opts.append([arg[1:].split(':')[0], arg[1:].split(':')[1]])
        elif re.match('^--\w+$', arg, re.I):
            opts.append(arg[2:])
        elif re.match('^--\w+:\w+', arg, re.I):
            opts.append([arg[2:].split(':')[0], arg[2:].split(':')[1]])
        else:
            tags.append(arg)
    tags = ' '.join(tags)
    return opts, tags

class booruManager:
    def __init__(self):
        self.booru_dict={'danbooru': 'http://danbooru.donmai.us/post/index.xml?', 'konachan': 'http://konachan.com/post.xml?', 'yande.re': 'http://yande.re/post.xml?', 'safebooru': 'http://safebooru.org/index.php?page=dapi&s=post&q=index&'}
        ## Default Options ##
        self.source = 'konachan'
        self.width = 1920
        self.height =1080
        self.size_restriction = False
        self.rating = 's'
        self.landscape_only = False
        self.portrait_only = False
        self.boorudb = ''
    
    def set_config(self, opts):
        for opt in opts:
            try:
                if 'sauce' == opt[0] and opt[1] != 'booru':   
                    self.source = opt[1]
                else:
                    source = self.source
                if 'd' == opt or 'size' == opt:
                    width, height = opt.split('x', 1)
                    self.width = width
                    self.height = height
                    self.size_restriction = True
                else:
                    width = self.width
                    height = self.height
                    size_restriction = self.size_restriction
                if 'r' == opt[0] or 'rating' == opt[0]:
                    self.rating = opt[1]
                else:
                    rating = self.rating
                if ('l' == opt or 'landscape_only' == opt) and self.portrait_only != 1:
                    self.landscape_only = True
                else:
                    landscape_only = self.landscape_only
                if ('p' == opt or 'portrait_only' == opt) and self.landscape_only != 1:
                    self.portrait_only = True
                else:
                    portrait_only = self.portrait_only
            except Exception as e:
                print(e)
                print('Probably index error for my arrays.')
        self.boorudb = dbm(self.source)
    
    def generate_url(self, page, general_tags):
        if self.source == 'safebooru':
            page -= 1
            url = self.booru_dict[self.source] + 'limit=1000' + '&pid=' + str(page) + '&tags=' + general_tags
        else:
            url = self.booru_dict[self.source] + 'limit=100' + '&page=' + str(page) + '&tags=' + general_tags
        raw_data = ur.urlopen(url, None, 15)
        xml_data = raw_data.read()
        try:
            tree = etree.fromstring(xml_data)
            tree.find('post').get('file_url')
        except Exception as e:
            print(e)
            print('Failed to get from tree aka that page has no results.')
            tree = None
        return tree
        
    def per_page(self, page, tags):
        image_dictionary = {}
        split_tags = re.compile('(?P<tag>[^\s]+)', re.I)
        match_index = 0
        general_tags = []
        specific_tags = []
        for match in split_tags.finditer(tags):
            if match_index < 2:
                general_tags.append(match.group('tag'))
                match_index += 1
            else:
                specific_tags.append(match.group('tag'))
        general_tags = up.quote_plus(' '.join(general_tags))
        tree = self.generate_url(page, general_tags);
        if tree:
            image_dictionary = self.per_image(image_dictionary, specific_tags, tree);
        return image_dictionary

    def per_image(self, image_dictionary, specific_tags, tree):
        for elem in tree.findall('post'):
            params = 0
            if ('.jpg' in elem.get('file_url')) or ('.png' in elem.get('file_url')):
                #print('Static image')
                params += 1
            if (elem.get('rating') == self.rating) or (self.rating == 'q' and elem.get('rating') == 's'):
                #print('Allowed if the image rating is the same as the config rating, if the image rating is s while the config is q, and if the config is e allow everything.')
                params += 1
            if self.size_restriction is False or ((int(elem.get('width')) >= self.width) and self.size_restriction == True):
                #print('width greater OR no size restriction')
                params += 1
            if self.size_restriction is False or ((int(elem.get('height')) >= self.height) and self.size_restriction == True):
                #print('height greater OR no size restriction')
                params += 1
            if self.landscape_only is False or (self.landscape_only == True and int(elem.get('height')) < int(elem.get('width'))):
                #print('Allowed if landscape only off OR landscape only on and width greater than height')
                params += 1
            if self.portrait_only is False or (self.portrait_only == True and int(elem.get('width')) < int(elem.get('height'))):
                #print('Allowed if portrait only off OR portrait only on and height greater than width')
                params += 1
            if specific_tags:
                has_tag = []
                for tag in specific_tags:
                    if tag in elem.get('tags'):
                        has_tag.append('true')
                    else:
                        has_tag.append('false')
                if 'false' not in has_tag:
                    params += 1
            else:
                params += 1
            if self.source == 'danbooru':
                file_url = 'http://danbooru.donmai.us' + elem.get('file_url')
            else:
                file_url = elem.get('file_url')
            if params == 7:
                image_dictionary.update({elem.get('md5'):(file_url,elem.get('rating'),elem.get('width'),elem.get('height'),elem.get('tags'),elem.get('id'))})
        return image_dictionary
    
    def get_character(self, image_id):
        if self.source == 'danbooru':
            base_url = 'http://danbooru.donmai.us/posts/'
        elif self.source == 'safebooru':
            base_url = 'http://safebooru.org/index.php?page=post&s=view&id='
        elif self.source == 'yande.re':
            base_url = 'https://yande.re/post/show/'
        elif self.source == 'konachan':
            base_url = 'http://konachan.com/post/show/'
        result = ''
        try:
            data = ur.urlopen(base_url+image_id, None, 5)
            html = h.unescape(data.read().decode('utf-8'))
            if self.source == 'danbooru':
                pattern = re.compile('.*?class="category-4"><[^<]+<[^<]+<[^>]+>(?P<character>[^<]+).*?', re.I)
            elif self.source == 'safebooru':
                pattern = re.compile('.*?class="tag-type-character"><[^>]+>(?P<character>[^<]+).*?', re.I)
            elif self.source == 'yande.re':
                pattern = re.compile('.*?class="tag-link\stag-type-character"[^<]+<[^<]+<[^<]+<[^>]+>(?P<character>[^<]+).*?', re.I)
            elif self.source == 'konachan':
                pattern = re.compile('.*?class="tag-link\stag-type-character"[^<]+<[^<]+<[^<]+<[^>]+>(?P<character>[^<]+).*?', re.I)
            for match in pattern.finditer(html):
                result += ' '+match.group('character')+','
        except Exception as e:
            print(e)
        return result[:-1]

class IRCScript(template.IRCScript):
    print('loaded booru')
    def privmsg(self, user, channel, msg):
        boorud = re.match('^!(?P<booru>(booru|safebooru|konachan|danbooru|yandere))(\s|)(?P<tags>.*)', msg, re.I)
        if boorud:
            opts, tags = argsplit(boorud.group('tags'))
            bm = booruManager()
            bm.set_config([['sauce', boorud.group('booru')]])
            bm.set_config(opts)
            image_dict = {}
            for x in range(1, 11):
                img_dict = bm.per_page(x, tags)
                image_dict.update(img_dict)
            if image_dict:
                b = bitlyManager();
                selected_image = random.choice(list(image_dict.values()))
                characters = bm.get_character(selected_image[5]);
                selected_image = b.shorten_url(selected_image[0]);
                self.sendMsg(channel, selected_image + ' |' + characters)
            else:
                self.sendNotice(user, 'The search failed, maybe recheck your tags.')
