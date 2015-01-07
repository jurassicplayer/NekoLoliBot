#!/usr/bin/env python

import template
import re


color_table = {
    'white': '00',
    'black': '01',
    'darkblue': '02',
    'darkgreen': '03',
    'red': '04',
    'darkred': '05',
    'darkviolet': '06',
    'orange': '07',
    'yellow': '08',
    'lightgreen': '09',
    'cyan': '10',
    'lightcyan': '11',
    'blue': '12',
    'violet': '13',
    'darkgray': '14',
    'lightgray': '15'
    }
caret_table = {
    'reset': '\x0f',
    'bold': '\x02',
    'color': '\x03',
    'italic': '\x1d',
    'strike': '\x13',
    'underline': '\x1f',
    'reverse': '\x16'
    }
class Colorize:
    def rainbow(msg):
        colors = ['05','04','07','08','03','09','10','11','02','12','06','13']
        color_count = len(colors)
        color_index = 0
        chars_ignore = [',', ' ']
        
        split = list(msg)
        cycles = len(split)
        for x in range(0, cycles):
            if split[x] in chars_ignore:
                pass
            else:
                split[x] = '\x03'+colors[color_index]+split[x]
                if color_index == color_count-1:
                    color_index = 0
                else:
                    color_index +=1
        msg = ''.join(split)
        msg = caret_table['color']+color_table['white']+','+color_table['black']+msg+caret_table['reset']
        return msg
    def color(msg, fg, bg):
        if fg and bg:
            msg = caret_table['color']+color_table[fg]+','+color_table[bg]+msg
        elif fg:
            msg = caret_table['color']+color_table[fg]+msg
        msg = msg+caret_table['reset']
        return msg
    def style(msg, style):
        if style in caret_table:
            msg = caret_table[style]+msg
        msg = msg+caret_table['reset']
        return msg
class IRCScript(template.IRCScript):
    print('loaded colorize')
    def privmsg(self, user, channel, msg):
        rainbow = re.match('^-rainbow\s(-(?P<option>[bius]+)\s|)(?P<message>.*)', msg, re.I)
        if rainbow:
            message = Colorize.rainbow(rainbow.group('message'))
            if rainbow.group('option'):
                if 'b' in rainbow.group('option'):
                    message = Colorize.style(message, 'bold')
                if 'i' in rainbow.group('option'):
                    message = Colorize.style(message, 'italic')
                if 's' in rainbow.group('option'):
                    message = Colorize.style(message, 'strike')
                if 'u' in rainbow.group('option'):
                    message = Colorize.style(message, 'underline')
            self.sendMsg(self.channel, message)
