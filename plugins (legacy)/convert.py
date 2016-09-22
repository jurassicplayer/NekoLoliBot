#!/usr/bin/env python
import template
import re, json
import urllib.request as ur

import quantities as pq
## Country Ids ##
try:
    data = ur.urlopen('http://www.freecurrencyconverterapi.com/api/v2/countries', None,15)
    result = json.loads(data.read().decode('utf-8'))
    country_dict = result['results']
except Exception as e:
    print(e)
## Stuff that quantities can't handle (Temperature and Digital storage) ## 
unit_table = {
    'Temperature': [{'to': 'F', 'rate': '%s*(9/5)+32', 'from': 'C'}, {'to': 'F', 'rate': '%s*(9/5)-459.67', 'from': 'K'}, {'to': 'C', 'rate': '%s*(5/9)-17.78', 'from': 'F'}, {'to': 'C', 'rate': '%s-273.15', 'from': 'K'}, {'to': 'K', 'rate': '%s+273.15', 'from': 'C'}, {'to': 'K', 'rate': '%s*(5/9)+255.37', 'from': 'F'}],
    'Digital Storage': []
    }


class unitConverter:
    def currency(Units, fromUnit, toUnit):
        final_unit = None
        try:
            data = ur.urlopen('http://rate-exchange.appspot.com/currency?from='+fromUnit+'&to='+toUnit, None,15)
            result = json.loads(data.read().decode('utf-8'))
            conversion_factor = result['rate']
            final_unit = round(float(conversion_factor)*float(Units), 2)
        except Exception as e:
            print(e)
        return final_unit
    
    def quantity(Units, fromUnit, toUnit):
        try:
            q = pq.Quantity(Units, fromUnit)
            q.units = toUnit
            remove_unit = len(toUnit)+1
            final_unit = str(q)[:-remove_unit]
        except Exception as e:
            print(e)
            final_unit = e
        return final_unit

## Splits currency/unit/temperature/digital storage conversions apart ##
def convert(Units, fromUnit, toUnit):
    final_unit = None
    unit_temp = re.match('(?P<temp>(degC|celcius|°C|C|degK|kelvin|°K|K|degF|fahrenheit|°F|F))', fromUnit, re.I)
    unit_digit = re.match('(?P<digital>(bit|b|byte|B|kilobit|kbit|kilobyte|kB|megabit|Mbit|megabyte|MB|gigabit|Gbit|gigabyte|GB|terabit|Tbit|terabyte|TB|petabit|Pbit|petabyte|PB|exabit|Ebit|exabyte|EB|zettabit|Zbit|zettabyte|ZB))', fromUnit, re.I)
    fromCurrency = None
    toCurrency = None
    for country in country_dict:
        if fromUnit.lower() == country_dict[country]['currencyId'].lower():
            fromCurrency = country_dict[country]['currencyId']
        elif toUnit.lower() == country_dict[country]['currencyId'].lower():
            toCurrency = country_dict[country]['currencyId']
        else: pass
    ## Split between currency and unit conversion ##
    if fromCurrency and toCurrency:
        final_unit = unitConverter.currency(Units, fromCurrency, toCurrency);
    elif unit_temp:
        for x in unit_table['Temperature']:
            if fromUnit.lower() == x['from'].lower() and toUnit.lower() == x['to'].lower():
                final_unit = round(eval(x['rate'] % Units), 2)
    elif unit_digit:
        print('digital storage conversion')
#       for x in unit_table[category]:
#           if fromUnit[0] == x['from'] and toUnit[0] == x['to']:
#               conversion_factor = x['rate']
#                final_unit = round(conversion_factor*float(Units), 2)
#            elif fromUnit[0] == x['to'] and toUnit[0] == x['from']:
#               ## Reverse conversion ====> 1/conversion_factor
#                conversion_factor = '1/('+x['rate']+')'
#                final_unit = round(conversion_factor*float(Units), 2)
    else:
        final_unit = unitConverter.quantity(Units, fromUnit, toUnit);
    return final_unit

class IRCScript(template.IRCScript):
    print('loaded convert')
    def privmsg(self, user, channel, msg):
        regex = re.match('^\.convert\s(?P<from>[^2]+)(\s|)2(\s|)(?P<to>[^\s]+)(\s(?P<units>[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?)|)', msg, re.I)
        if regex:
            if regex.group('units'):
                units = float(regex.group('units'))
            else:
                units = 1
            final_unit = convert(units, regex.group('from'), regex.group('to'));
            if final_unit:
                self.sendMsg(channel, str(units)+' '+regex.group('from')+' is '+str(final_unit)+' '+regex.group('to')+'.')
            else:
                self.sendMsg(channel, "I don't know how to convert "+regex.group('from')+' to '+regex.group('to')+'.')
