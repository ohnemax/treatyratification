import requests
from BeautifulSoup import BeautifulSoup, SoupStrainer
import datetime

from dateutil import parser as dateparser
import numpy as np
import json

def getcountry(hlink):
    signed = 0
    ratified = 0
    acceded = 0
    a = requests.get(hlink)
    parsed_html = BeautifulSoup(a.text, convertEntities=BeautifulSoup.HTML_ENTITIES)
    country = parsed_html.body.find('h1').text
    rattimes = []
    treaties = 0
    ret = {}
    print(country)
    for t in parsed_html.body.findAll('table', attrs={'class':'treaty'}):
        treaties += 1
        treaty = t.td.a.text
        ret[treaty] = {}
        actions = []
        dates = []
        places = []
        if treaty == 'Convention on Certain Conventional Weapons':
            ret[treaty]['protocolnames'] = []
            ret[treaty]['protocolactions'] = []
            ret[treaty]['protocoldates'] = []
            ac = t.findAll('td', attrs={'class':'action'})
            da = t.findAll('td', attrs={'class':'actionDate'})
            if len(ac) != len(da):
                print("Length difference action/actionDate!")
            else:
                for i in range(len(ac)):
                    b = ac[i].findAll('a')
                    if(b == []):
                        actions.append(ac[i].text.split('\n')[0])
                        places.append(ac[i].text.split('\n')[-1].strip(' ()'))
                        date = dateparser.parse(da[i].text.strip(' *')).strftime("%Y-%m-%d")
                        dates.append(date)
                    else:
                        ret[treaty]['protocolnames'].append(b[0].text)
                        ret[treaty]['protocolactions'].append(ac[i].text.split('\n')[0])
                        date = dateparser.parse(da[i].text.strip(' *')).strftime("%Y-%m-%d")
                        ret[treaty]['protocoldates'].append(date)
                
        else:
            ac = t.findAll('td', attrs={'class':'action'})
            da = t.findAll('td', attrs={'class':'actionDate'})
            if len(ac) != len(da):
                print("Length difference action/actionDate!")
            else:
                for i in range(len(ac)):
                    b = ac[i].findAll('a')
                    if(b == []):
                        actions.append(ac[i].text.split('\n')[0])
                        places.append(ac[i].text.split('\n')[-1].strip(' ()'))
                        date = dateparser.parse(da[i].text.strip(' *')).strftime("%Y-%m-%d")
                        dates.append(date)
                    # else: deal with protocols to treaties
        ret[treaty]['actions'] = actions
        ret[treaty]['places'] = places
        ret[treaty]['dates'] = dates
        for i in range(len(actions)):
            if "signature" in actions[i].lower():
                if 'signed' not in ret[treaty]:
                    signed += 1
                if 'signed' not in ret[treaty] or ret[treaty]['signed'] > dates[i]:
                    ret[treaty]['signed'] = dates[i]
            elif "ratification" in actions[i].lower() or "acceptance" in actions[i].lower() or "approval" in actions[i].lower():
                if 'ratified' not in ret[treaty]:
                    ratified += 1
                if 'ratified' not in ret[treaty] or ret[treaty]['ratified'] > dates[i]:
                    ret[treaty]['ratified'] = dates[i]
            elif "accession" in actions[i].lower() or "succession" in actions[i].lower() or "acceptance" in actions[i].lower():
                if 'acceded' not in ret[treaty]:
                    acceded += 1
                if 'acceded' not in ret[treaty] or ret[treaty]['acceded'] > dates[i]:
                    ret[treaty]['acceded'] = dates[i]
            else:
                print("Unknown action: {:s}".format(actions[i]))
        if 'ratified' in ret[treaty] and 'signed' not in ret[treaty]:
            print("Treaty ratified, but not signed:")
            print(treaty)
        if 'signed' in ret[treaty] and 'ratified' in ret[treaty]:
            try:
                diff = dateparser.parse(ret[treaty]['ratified']) - dateparser.parse(ret[treaty]['signed'])
                days = diff.days
            except:
                print(ret[treaty]['ratified'])
                print(ret[treaty]['signed'])
                days = 0
            ret[treaty]['ratificationtime'] = days
            rattimes.append(diff.days)

    ret['signed'] = signed
    ret['ratified'] = ratified
    ret['signedandratified'] = len(rattimes)
    ret['totaltreaties'] = treaties
    if(len(rattimes) > 0): 
        ret['ratificationtime-mean'] = np.mean(rattimes)
        ret['ratificationtime-max'] = max(rattimes)
        ret['ratificationtime-min'] = min(rattimes)
        ret['ratificationtime-median'] = np.median(rattimes)
    else:
        ret['ratificationtime-mean'] = -1
        ret['ratificationtime-max'] = -1
        ret['ratificationtime-min'] = -1
        ret['ratificationtime-median'] = -1
    ret['acceded'] = acceded
    print("Actions for {:d} treaties".format(treaties))
    print("{:d} treaties were ratified, ratification time mean/median/min/max: {:.1f}/{:.1f}/{:d}/{:d} days".format(len(rattimes), ret['ratificationtime-mean'], ret['ratificationtime-median'], ret['ratificationtime-min'], ret['ratificationtime-max']))
    
    return ret
    
#hlink = "http://disarmament.un.org/treaties/s/afghanistan"

mainlink = "http://disarmament.un.org/treaties/"
a = requests.get(mainlink)
mainhtml = BeautifulSoup(a.text)
allcountries = {}
for link in mainhtml.body.findAll('a'):
    if '/s/' in link.get('href'):
       allcountries[link.text] = getcountry("http://disarmament.un.org" + link.get('href'))
    
f = open('treatydata.json', 'w')
json.dump(allcountries, f)
f.close()
