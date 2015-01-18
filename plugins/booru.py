#!/usr/bin/env python

import template
import re, random
import config
import urllib.parse as up
import urllib.request as ur
import xml.etree.ElementTree as etree
from colorize import Colorize as c

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
    
    def set_config(self, source, width, height, size_restriction, rating, landscape_only, portrait_only):
        if source:
            self.source = source
        else:
            source = self.source
        if width:
            self.width = width
        else:
            width = self.width
        if height:
            self.height = height
        else:
            height = self.height
        if size_restriction:
            self.size_restriction = size_restriction
        else:
            size_restriction = self.size_restriction
        if rating:
            self.rating = rating
        else:
            rating = self.rating
        if landscape_only:
            self.landscape_only = landscape_only
        else:
            landscape_only = self.landscape_only
        if portrait_only:
            self.portrait_only = portrait_only
        else:
            portrait_only = self.portrait_only
    
    def generate_url(self, page, general_tags):
        if self.source == 'safebooru':
            page -= 1
            url = self.booru_dict[self.source] + 'limit=1000' + '&pid=' + str(page) + '&tags=' + general_tags
        else:
            url = self.booru_dict[self.source] + 'limit=100' + '&page=' + str(page) + '&tags=' + general_tags
        try:
            raw_data = ur.urlopen(url, None, 15)
            xml_data = raw_data.read()
            tree = etree.fromstring(xml_data)
        except Exception as e:
            url = tree = None
        return url, tree
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
        try:
            url, tree = self.generate_url(page, general_tags);
            tree.find('post').get('file_url')
        except AttributeError:
            pass
            print('No more pages.')
        except Exception as e:
            print(e)
            return
        image_dictionary = self.per_image(image_dictionary, specific_tags, tree);
        return image_dictionary


    def per_image(self, image_dictionary, specific_tags, tree):
        for elem in tree.findall('post'):
            params = 0
            if ('.jpg' in elem.get('file_url')) or ('.png' in elem.get('file_url')):
                #print('Static image')
                params += 1
            if (elem.get('rating') == self.rating) or (self.rating == 'q' and elem.get('rating') == 's') or (self.rating == 'e'):
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
                image_dictionary.update({elem.get('md5'):(file_url,elem.get('rating'),elem.get('width'),elem.get('height'),elem.get('tags'))})
        return image_dictionary


class IRCScript(template.IRCScript):
    print('loaded booru')
    def privmsg(self, user, channel, msg):
        boorud = re.match('^!booru\s((?P<booru>(safebooru|konachan|danbooru|yande\.re))\s|)((?P<width>\d+)x(?P<height>\d+)\s|)(?P<tags>.*)', msg, re.I)
        if boorud:
            sauce = width = height = size_restriction = rating = landscape_only = portrait_only = None
            if boorud.group('booru'):
                sauce = boorud.group('booru')
            if boorud.group('width'):
                width = int(boorud.group('width'))
            if boorud.group('height'):
                height = int(boorud.group('height'))
            if boorud.group('width') and boorud.group('height'):
                size_restriction = True
            b = booruManager();
            b.set_config(sauce, width, height, size_restriction, rating, landscape_only, portrait_only);
            image_dict = {}
            for x in range(1, 6):
                img_dict = b.per_page(x, boorud.group('tags'))
                image_dict.update(img_dict)
            if image_dict:
                selected_image = next (iter (image_dict.values()))[0]
                self.sendMsg(channel, selected_image)
            else:
                self.sendNotice(user, 'The search failed, maybe recheck your tags.')
        randomd = re.match('^!booru random', msg, re.I)
        if randomd:
            sauce = width = height = size_restriction = rating = landscape_only = portrait_only = None
            sauce = random.choice(['danbooru', 'konachan', 'yande.re', 'safebooru'])
            b = booruManager();
            b.set_config(sauce, width, height, size_restriction, rating, landscape_only, portrait_only);
            image_dict = {}
            for x in range(1, 6):
                img_dict = b.per_page(x, boorud.group('tags'))
                image_dict.update(img_dict)
            if image_dict:
                selected_image = random.choice(image_dict.keys())[0]
                self.sendMsg(channel, selected_image)
