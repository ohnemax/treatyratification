 #!/usr/bin/python
 # -*- coding: utf-8 -*-
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from matplotlib import cm
import matplotlib as mpl
import cartopy.io.shapereader as shpreader
import datetime
from dateutil.relativedelta import relativedelta

from dateutil import parser as dateparser
import operator

import json

import numpy as np

import pandas as pd

# set comparison date
# today
# compdate = datetime.datetime.now()
# compdatestring = compdatedate.strftime("%Y-%m-%d")

# 1st anniversary
compdatestring = "2018-07-07"
compdate = dateparser.parse(compdatestring)

# dates when treaties opened for signature. from http://disarmament.un.org/treaties/
sigopen = {u'Anti-Personnel Mine Ban Convention': '3 December 1997',
           u'Treaty on Conventional Armed Forces in Europe (CFE)': '19 November 1990',
           u'Chemical Weapons Convention': '13 January 1993',
           u'Outer Space Treaty': '27 January 1967',
           u'Inter-American Convention on Transparency': '07 June 1999',
           u'Antarctic Treaty': '1 December 1959',
           u'International Convention for the Suppression of Acts of Nuclear Terrorism': '14 September 2005',
           u'Treaty on the Non-Proliferation of Nuclear Weapons (NPT)': '1 July 1968', 
           u'Convention on Certain Conventional Weapons': '10 April 1981',
           u'Partial Test Ban Treaty': '8 August 1963',
           u'1925 Geneva Protocol': '17 June 1925',
           u'Convention on Cluster Munitions': '3 December 2008',
           u'Convention on Environmental Modification Techniques (ENMOD)': '18 May 1977',
           u'Biological Weapons Convention': '10 April 1972',
           u'Treaty on Open Skies': '24 March 1992',
           u'Inter-American Convention on Firearms': '14 November 1997',
           u'Comprehensive Nuclear-Test-Ban Treaty': '24 September 1996',
           u'Sea-Bed Treaty': '11 February 1971',
           u'Kinshasa Convention': '19 November 2010',
           u'Pelindaba Treaty': '11 April 1996', 
           u'Treaty on the Prohibition of Nuclear Weapons': '20 September 2017',
           u'Arms Trade Treaty': '3 June 2013',
           u'Treaty on a Nuclear-Weapon-Free Zone in Central Asia (CANWFZ)': '8 September 2006',
           u'Bangkok Treaty': '15 December 1995',
           u'Treaty of Tlatelolco': '14 February 1967',
           u'Moon Treaty (Celestial Bodies)': '18 December 1979',
           u'South Pacific Nuclear Free Zone Treaty': '6 August 1985'}
# u'Treaty of Rarotonga': '6 August 1985'}

# load harvested file (from harvest.py)
f = open('treatydata.json', 'r')
allcountries = json.load(f)
f.close()


shapename = 'admin_0_countries'
countries_shp = shpreader.natural_earth(resolution='110m',
                                        category='cultural', name=shapename)
red = (1, 0, 0)
blue = (0, 0, 1)
color = red

# name translation between the natural earth dataset and the treaty dataset
ct = {'Bolivia': 'Bolivia (Plurinational State of)',
      "Côte d'Ivoire": "C&ocirc;te d'Ivoire",
      'Dem. Rep. Korea': "Democratic People's Republic of Korea",
      'Greenland': 'Denmark',
      'Iran': 'Iran (Islamic Republic of)',
      'Republic of the Congo': 'Democratic Republic of the Congo',
      'Lao PDR': "Lao People's Democratic Republic",
      'Macedonia': 'The former Yugoslav Republic of Macedonia',
      'Puerto Rico': 'United States of America',
      'Syria': 'Syrian Arab Republic',
      'The Gambia': 'Gambia',
      'United Kingdom': 'United Kingdom of Great Britain and Northern Ireland',
      'United States': 'United States of America',
      'Venezuela': 'Venezuela (Bolivarian Republic of)',
      'Vietnam': 'Viet Nam',
      'Western Sahara': 'Morocco',
      'Tanzania': 'United Republic of Tanzania'}

notreatylist = ['ratificationtime-min', 'ratificationtime-median', 'totaltreaties', 'ratificationtime-mean', 'signedandratified', 'signed', 'ratified', 'acceded', 'ratificationtime-max']

# prepare an easy to handle panda data frame for the country-wise data, count countries and treaties
treaties = []
clist = []
norat = []
tdata = {i: [] for i in notreatylist}
tdata['country'] = []

for c in allcountries:
    clist.append(c)
    if(allcountries[c]['signedandratified'] == 0 and allcountries[c]['acceded'] == 0):
        norat.append(c)
    ctlist = []
    tdata['country'].append(c)
    for t in allcountries[c]:
        if t in notreatylist:
            tdata[t].append(allcountries[c][t])
            ctlist.append(t)
        else:
            if not t in treaties:
                treaties.append(t)
    if len(ctlist) != len(notreatylist):
        print (c)

adf = pd.DataFrame(data=tdata)



# create dataframe for ratification times
ratdays = []
ratcountries = []
rattreaties = []
ratdates = []

for c in allcountries:
    cr = 0
    for t in allcountries[c]:
        if type(allcountries[c][t]) == dict:
            if 'ratificationtime' in allcountries[c][t]:
                cr += 1
                ratdays.append(allcountries[c][t]['ratificationtime'])
                ratcountries.append(c)
                rattreaties.append(t)
                ratdates.append(allcountries[c][t]['ratified'])
    # if(cr != allcountries[c]['ratified']):
    #     print("hm", c, cr, allcountries[c]['ratified'])
    #     print(allcountries[c])
d = {'ratificationdays': ratdays, 'ratificationcountries': ratcountries, 'ratificationtreaties': rattreaties, 'ratificationdates': ratdates}
tdf = pd.DataFrame(data=d)

# create dataframe for accession dates
acccountries = []
acctreaties = []
accdates = []

for c in allcountries:
    for t in allcountries[c]:
        if type(allcountries[c][t]) == dict:
            if 'acceded' in allcountries[c][t]:
                acccountries.append(c)
                acctreaties.append(t)
                accdates.append(allcountries[c][t]['acceded'])
d = {'accessioncountries': acccountries, 'accessiontreaties': acctreaties, 'accessiondates': accdates}
acdf = pd.DataFrame(data=d)

# Russian Federation
# Treaty ratified, but not signed:
# 1925 Geneva Protocol
# Saint Kitts and Nevis
# Treaty ratified, but not signed:
# Sea-Bed Treaty

# zero ratification time
totalratified = 0
countrieswithzerotime = 0
treatieswithzerotime = 0
countrieswithzerotimelist = []
for c in allcountries:
    zero = False
    for t in allcountries[c]:
        if type(allcountries[c][t]) == dict:
            if 'ratificationtime' in allcountries[c][t]:
                totalratified += 1
                if allcountries[c][t]['ratificationtime'] == 0:
                    zero = True
                    treatieswithzerotime += 1
    if zero:
        countrieswithzerotime += 1
        countrieswithzerotimelist.append(c)

countrieswithzerotimelist = list(set(countrieswithzerotimelist))



tpnwsignatures = []
tpnwdate = []
tpnwratificationmedian = []
tpnwfutureratificationdatemedian = []
tpnwfutureratificationdate = []
tpnwratificationtime = []

for c in allcountries:
    if 'Treaty on the Prohibition of Nuclear Weapons' in allcountries[c]:
        tpnwsignatures.append(c)
        sd = allcountries[c]['Treaty on the Prohibition of Nuclear Weapons']['signed']
        tpnwdate.append(sd)
        if 'ratificationtime-min' in allcountries[c]:
            mid = allcountries[c]['ratificationtime-min']
            tpnwratificationtime.append(allcountries[c]['ratificationtime-min'])
        else:
            tpnwratificationtime.append(-1)
        if 'ratificationtime-median' in allcountries[c]:
            md = allcountries[c]['ratificationtime-median']
            tpnwratificationmedian.append(allcountries[c]['ratificationtime-median'])
        else:
            tpnwratificationmedian.append(-1)
        if 'ratified' in allcountries[c]['Treaty on the Prohibition of Nuclear Weapons']:
            rd = allcountries[c]['Treaty on the Prohibition of Nuclear Weapons']['ratified']
            tpnwfutureratificationdate.append(rd)
            tpnwfutureratificationdatemedian.append(rd)
        else:
            signdate = dateparser.parse(sd)
            signdate = signdate + datetime.timedelta(days = md)
            tpnwfutureratificationdatemedian.append(signdate.strftime("%Y-%m-%d"))
            signdate = dateparser.parse(sd)
            signdate = signdate + datetime.timedelta(days = mid)
            tpnwfutureratificationdate.append(signdate.strftime("%Y-%m-%d"))

# ban treaty median ratification time for signature states
d = {'signatures': tpnwsignatures,
     'date': tpnwdate,
     'ratificationmin': tpnwratificationtime,
     'ratificationmedian': tpnwratificationmedian,
     'futureratificationdate': tpnwfutureratificationdate,
     'futureratificationdatemedian': tpnwfutureratificationdatemedian}
tpnwdf = pd.DataFrame(data=d)

#FIX add 90 days
wowdate = tpnwdf.sort_values(by=['futureratificationdate']).iloc[49].values[1]
wowdays = (dateparser.parse(wowdate) - dateparser.parse(sigopen['Treaty on the Prohibition of Nuclear Weapons'])).days
woweifdate = (dateparser.parse(wowdate) + datetime.timedelta(days = 90)).strftime("%Y-%m-%d")
wow2date = tpnwdf.sort_values(by=['futureratificationdatemedian']).iloc[49].values[2]
wow2days = (dateparser.parse(wow2date) - dateparser.parse(sigopen['Treaty on the Prohibition of Nuclear Weapons'])).days
wow2eifdate = (dateparser.parse(wow2date) + datetime.timedelta(days = 90)).strftime("%Y-%m-%d")

# ban analysis

banrcountries = tdf[tdf['ratificationtreaties'] == 'Treaty on the Prohibition of Nuclear Weapons']['ratificationcountries']
br = {'country': [], 'ban': [], 'all': [], 'median': []}
for c in banrcountries:
    br['country'].append(c)
    br['ban'].append(tdf[(tdf['ratificationtreaties'] == 'Treaty on the Prohibition of Nuclear Weapons') & (tdf['ratificationcountries'] == c)]['ratificationdays'].values)
    br['all'].append(sorted(tdf[tdf['ratificationcountries'] == c]['ratificationdays'].values.tolist()))
    br['all'][-1].remove(br['ban'][-1])
    if br['all'][-1] != []:
        br['median'].append(str(np.median(br['all'][-1])))
    else:
        br['median'].append('-')
bdf = pd.DataFrame(data = br)

# days since tpnw comparison date
dstso =  compdate - dateparser.parse(sigopen['Treaty on the Prohibition of Nuclear Weapons'])

#check similar ratificaitons (accessions count as ratifications here)
similarratlist = {}
for t in sigopen:
    opendate = dateparser.parse(sigopen[t])
    comparedate = opendate + datetime.timedelta(days = dstso.days)
    similarratlist[t] = len(tdf[(tdf['ratificationtreaties'] == t) & (tdf['ratificationdates'] <= comparedate.strftime('%Y-%m-%d'))])
    similaracc = len(acdf[(acdf['accessiontreaties'] == t) & (acdf['accessiondates'] <= comparedate.strftime("%Y-%m-%d"))])
    if similaracc > 0:
        similarratlist[t] += similaracc

# competition of treaties. count accesions as ratificaitons
comp = {'treaty': []}
for m in range(1, 25):
    comp[str(m)] = []
for t in sigopen:
    comp['treaty'].append(t)
    for m in range(1, 25):
        opendate = dateparser.parse(sigopen[t])
        #six_months = date.today() + relativedelta(months=+6)
        comparedate = opendate + relativedelta(months=m)
        res = len(tdf[(tdf['ratificationtreaties'] == t) & (tdf['ratificationdates'] <= comparedate.strftime("%Y-%m-%d"))])
        resa = len(acdf[(acdf['accessiontreaties'] == t) & (acdf['accessiondates'] <= comparedate.strftime("%Y-%m-%d"))])
        comp[str(m)].append(res + resa)

compdf = pd.DataFrame(comp)

# 50 countries for other treaties
club50 = {}
for t in sigopen:
    tmp = tdf[tdf['ratificationtreaties'] == t]
    if(len(tmp) >= 50):
        d50 = tmp.sort_values(by=['ratificationdates']).iloc[49]['ratificationdates']
        d50date = dateparser.parse(d50)
        opendate = dateparser.parse(sigopen[t])
        club50[t] = (d50date - opendate).days

missed = {'country': [], 'min': [], 'all': [], 'median': [], 'dayssincesignature': []}
for c in allcountries:
    if c not in banrcountries.values:
        if c in tpnwdf['signatures'].values:
            sigdate = dateparser.parse(tpnwdf[tpnwdf['signatures'] == c]['date'].values[0])
            delta = compdate - sigdate
            if tpnwdf[tpnwdf['signatures'] == c]['futureratificationdate'].values[0] <= compdatestring:
                missed['country'].append(c)
                l = sorted(tdf[tdf['ratificationcountries'] == c]['ratificationdays'].values.tolist())
                missed['median'].append(np.median(l))
                missed['dayssincesignature'].append(delta.days)
                missed['min'].append(min(l))
                missed['all'].append(l)
midf = pd.DataFrame(data = missed)
            

# output
print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
print("ON THE DATASET")
print("There are {:d} treaties in the dataset".format(len(treaties)))
print(sorted(treaties))
print("")
print("There are {:d} countries in the dataset".format(len(allcountries)))
print("--------------------------------------------------------------------------------")
print("{:d} have not ratified or acceded any treaty".format(len(norat)))
print("These countries are: {:s}".format(", ".join(norat)))
print("--------------------------------------------------------------------------------")
print("Overall, {:d} signature depositions, {:d} ratifications and {:d} accessions are included in the dataset".format(sum(adf['signed']), sum(adf['ratified']), sum(adf['acceded'])))

print("Countries have ")
print("... signed at least {:d}, but not more then {:d} treaties, and on average {:.1f}".format(min(adf['signed']), max(adf['signed']), np.mean(adf['signed'])))
print("... ratified at least {:d}, but not more then {:d} treaties, and on average {:.1f}".format(min(adf['ratified']), max(adf['ratified']), np.mean(adf['ratified'])))
print("... acceded at least {:d}, but not more then {:d} treaties, and on average {:.1f}".format(min(adf['acceded']), max(adf['acceded']), np.mean(adf['acceded'])))

print("For all ratification events, ")
print("...the mean ratification time is {:.1f} days".format(np.mean(tdf['ratificationdays'])))
print("...the median ratification time is {:.1f} days".format(np.median(tdf['ratificationdays'])))
print("...the minimal ratification time is {:.1f} days".format(min(tdf['ratificationdays'])))
print("...the maximal ratification time is {:.1f} days".format(max(tdf['ratificationdays'])))

print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
print("MINIMAL RATIFICATION TIME ZERO")
print("Total ratified treaties: {:d}".format(totalratified))
print("Total ratified treaties in 0 days: {:d}".format(treatieswithzerotime))
print("Number of countries that have ratified treaties in 0 days: {:d}".format(countrieswithzerotime))
print("Country list: {:s}".format(", ".join(countrieswithzerotimelist)))

print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
print("SHORTEST RATIFICATION (NPT)")
stdf = tdf.loc[tdf['ratificationtreaties'] == 'Treaty on the Non-Proliferation of Nuclear Weapons (NPT)']
stdf = stdf.sort_values(by=['ratificationdays'])
for i in range(10):
    print("{:d}, {:s}".format(stdf.iloc[[i]]['ratificationdays'].values[0],
                              stdf.iloc[[i]]['ratificationcountries'].values[0]))
    
# longest ratification general
print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
print("LONGEST RATIFICATION (GENERAL)")
stdf = tdf.sort_values(by=['ratificationdays'], ascending=False)
#stdf = tdf.sort_values(by=['ratificationdays'])
for i in range(20):
    print("{:f}, {:s}, {:s}".format(stdf.iloc[[i]]['ratificationdays'].values[0] / 365.0,
                                    stdf.iloc[[i]]['ratificationcountries'].values[0],
                                    stdf.iloc[[i]]['ratificationtreaties'].values[0]))

print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
print("LONGEST RATIFICATION (NPT)")
stdf = tdf.loc[tdf['ratificationtreaties'] == 'Treaty on the Non-Proliferation of Nuclear Weapons (NPT)']
stdf = stdf.sort_values(by=['ratificationdays'], ascending=False)
#stdf = tdf.sort_values(by=['ratificationdays'])
for i in range(10):
    print("{:f}, {:s}".format(stdf.iloc[[i]]['ratificationdays'].values[0] / 365.0,
                              stdf.iloc[[i]]['ratificationcountries'].values[0]))


print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
print("TPNW facts")
    
print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
print("TPNW ratification prediction")
print("Based on MINIMAL ratification times, 50 ratifications will probably be reached on: {:s}".format(wowdate))
print("  this is {:d} days after opening for signature".format(wowdays))
print("  Treaty would enter into force: {:s}".format(woweifdate))
print("  Last country to sign: {:s}".format(tpnwdf.sort_values(by=['futureratificationdate']).iloc[49].values[-1]))
print("Based on MEDIAN ratification times, 50 ratifications will probably be reached on: {:s}".format(wow2date))
print("  this is {:d} days after opening for signature".format(wow2days))
print("  Treaty would enter into force: {:s}".format(wow2eifdate))
print("  Last country to sign: {:s}".format(tpnwdf.sort_values(by=['futureratificationdatemedian']).iloc[49].values[-1]))

print("Countries that ratified TPNW")
for index, row in bdf.iterrows():
    print("{:s} ratified TPNW in {:s} days, and other treaties: {:s} (median: {:s})".format(row['country'], row['ban'], str(row['all']), str(row['median'])))

print('Among signatories, median ratification time for treaties varies between {:f} and {:f} days.'.format(min(tpnwdf['ratificationmedian']), max(tpnwdf['ratificationmedian'])))

print("{:d} Countries that have missed to ratify Ban Treaty faster than other treaties:".format(len(midf)))
for index, row in midf.iterrows():
    print("{:s}, days since signature {:d}, ratification time for other treaties: {:s} (median {:.2f})".format(row['country'], row['dayssincesignature'], str(row['all']), row['median']))

print("TPNW was opened for signature {:d} days before {:s}.".format(dstso.days, compdatestring))
print("after the same amount of time, ")

for t in sorted(similarratlist.items(), key=operator.itemgetter(1)):
    print("... {:s} had {:d} ratifications".format(t[0], similarratlist[t[0]]))

print("Other treaties achieved 50 ratifications:")
for t in sorted(club50.items(), key=operator.itemgetter(1)):
    print("... {:s} after {:d} days".format(t[0], club50[t[0]]))


# create two csv files. one holds all countries treaty data, the other one some averages / statistics
treatydata = "country,treaty,signature date,signature time,ratification date,ratification time,accession date,accession time"
for c in allcountries:
    for t in allcountries[c]:
        if t in notreatylist:
            continue
        signeddate = ""
        signeddays = ""
        if 'signed' in allcountries[c][t]:
            signeddate = allcountries[c][t]['signed']
            signeddays = str((dateparser.parse(allcountries[c][t]['signed']) - dateparser.parse(sigopen[t])).days)
#            signeddays = allcountries[c][t]['signed']
        ratifieddate = ""
        ratifieddays = ""
        if 'ratified' in allcountries[c][t]:
            ratifieddate = allcountries[c][t]['ratified']
            if 'signed' in allcountries[c][t]:
                ratifieddays = str(allcountries[c][t]['ratificationtime'])
        accessiondate = ""
        accessiondays = ""
        if 'acceded' in allcountries[c][t]:
            accessiondate = allcountries[c][t]['acceded']
            accessiondays = str((dateparser.parse(allcountries[c][t]['acceded']) - dateparser.parse(sigopen[t])).days)
        treatydata += "{:s},{:s},{:s},{:s},{:s},{:s},{:s},{:s}\n".format(c,t,signeddate, signeddays, ratifieddate, ratifieddays, accessiondate, accessiondays)
f = open('countrytreatydata.csv', 'w')        
f.write(treatydata)
f.close()

# adf holds what we want for second table
adf.to_csv('countrydata.csv', columns=['country', 'totaltreaties', 'signed', 'ratified', 'acceded', 'signedandratified', 'ratificationtime-min', 'ratificationtime-median', 'ratificationtime-mean', 'ratificationtime-max'], index=False)

# third: competition
compdf.to_csv('competition.csv', columns=['treaty'] + [str(i) for i in range(1, 25)], index=False)

print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
print("Now some plots")

# median
fig = plt.figure(figsize=(12,7))
ax = plt.axes(projection=ccrs.PlateCarree())

allmedian = []
for country in allcountries:
    allmedian.append(allcountries[country]['ratificationtime-median'])
maxmedian = max(allmedian)
maxcolor = 365 * 5


for country in shpreader.Reader(countries_shp).records():
    if country.attributes['NAME_LONG'] in ct:
        name = ct[country.attributes['NAME_LONG']]
    else:
        name = country.attributes['NAME_LONG']
    if name in allcountries and allcountries[name]['signedandratified'] > 0:
        if allcountries[name]['ratificationtime-median'] < maxcolor:
            coloridx = int(255 * allcountries[name]['ratificationtime-median'] / maxcolor)
        else:
            coloridx = 255
        color = cm.copper_r(coloridx)
    else:
        print(country.attributes['NAME_LONG'])
        color = (0.4, 0.4, 0.4)
    # print(country.attributes['NAME_LONG'], color)
    ax.add_geometries(country.geometry, ccrs.PlateCarree(),
                      facecolor=color,
                      edgecolor=(0, 0, 0))
                      # label=country.attributes['NAME_LONG'])

# https://stackoverflow.com/questions/35873209/matplotlib-add-colorbar-to-cartopy-image    
sm = plt.cm.ScalarMappable(cmap=plt.get_cmap('copper_r'))
sm._A = []
cb = plt.colorbar(sm, orientation='horizontal', fraction=0.046, pad=0.04)
cb.set_ticks([0, 0.2, 0.4, 0.6, 0.8, 1])
cb.set_ticklabels(['immediate', '1 year', '2 years', '3 years', '4 years', '>=5 years'])

plt.title('Median Time of Treaty Ratification')
plt.tight_layout()
plt.savefig('median.pdf')
plt.savefig('median.svg')
plt.show()

# mean
fig = plt.figure(figsize=(12,7))
ax = plt.axes(projection=ccrs.PlateCarree())

allmean = []
for country in allcountries:
    allmean.append(allcountries[country]['ratificationtime-mean'])
maxmean = max(allmean)
maxcolor = 365 * 10


for country in shpreader.Reader(countries_shp).records():
    if country.attributes['NAME_LONG'] in ct:
        name = ct[country.attributes['NAME_LONG']]
    else:
        name = country.attributes['NAME_LONG']
    if name in allcountries and allcountries[name]['signedandratified'] > 0:
        if allcountries[name]['ratificationtime-mean'] < maxcolor:
            coloridx = int(255.0 * allcountries[name]['ratificationtime-mean'] / maxcolor)
        else:
            coloridx = 255
        color = cm.copper_r(coloridx)
    else:
        print(country.attributes['NAME_LONG'])
        color = (0.4, 0.4, 0.4)
    # print(country.attributes['NAME_LONG'], color)
    ax.add_geometries(country.geometry, ccrs.PlateCarree(),
                      facecolor=color,
                      edgecolor=(0, 0, 0))
                      # label=country.attributes['NAME_LONG'])

# https://stackoverflow.com/questions/35873209/matplotlib-add-colorbar-to-cartopy-image    
sm = plt.cm.ScalarMappable(cmap=plt.get_cmap('copper_r'))
sm._A = []
cb = plt.colorbar(sm, orientation='horizontal', fraction=0.046, pad=0.04)
cb.set_ticks([0, 0.2, 0.4, 0.6, 0.8, 1])
cb.set_ticklabels(['immediate', '2 year', '4 years', '6 years', '8 years', '>=10 years'])

plt.title('Mean Time of Treaty Ratification')
plt.tight_layout()
plt.savefig('mean.svg')
plt.savefig('mean.pdf')
plt.show()

# min
fig = plt.figure(figsize=(12,7))
ax = plt.axes(projection=ccrs.PlateCarree())

allmin = []
for country in allcountries:
    allmin.append(allcountries[country]['ratificationtime-min'])
maxmin = max(allmin)
maxcolor = 365 * 1


for country in shpreader.Reader(countries_shp).records():
    if country.attributes['NAME_LONG'] in ct:
        name = ct[country.attributes['NAME_LONG']]
    else:
        name = country.attributes['NAME_LONG']
    if name in allcountries and allcountries[name]['signedandratified'] > 0:
        if allcountries[name]['ratificationtime-min'] < maxcolor:
            coloridx = int(255 * allcountries[name]['ratificationtime-min'] / maxcolor)
        else:
            coloridx = 255
        color = cm.copper_r(coloridx)
    else:
        print(country.attributes['NAME_LONG'])
        color = (0.4, 0.4, 0.4)
    # print(country.attributes['NAME_LONG'], color)
    ax.add_geometries(country.geometry, ccrs.PlateCarree(),
                      facecolor=color,
                      edgecolor=(0, 0, 0))
                      # label=country.attributes['NAME_LONG'])

# https://stackoverflow.com/questions/35873209/matplotlib-add-colorbar-to-cartopy-image    
sm = plt.cm.ScalarMappable(cmap=plt.get_cmap('copper_r'))
sm._A = []
cb = plt.colorbar(sm, orientation='horizontal', fraction=0.046, pad=0.04)
cb.set_ticks([0, 0.25, 0.5, 0.75,  1])
cb.set_ticklabels(['immediate', 'quarter', 'half', 'three quarters', '1 year'])

plt.title('Min Time of Treaty Ratification')
plt.tight_layout()
plt.savefig('min.svg')
plt.savefig('min.pdf')
plt.show()

# max
fig = plt.figure(figsize=(12,7))
ax = plt.axes(projection=ccrs.PlateCarree())

allmax = []
for country in allcountries:
    allmax.append(allcountries[country]['ratificationtime-max'])
maxmax = max(allmax)
maxcolor = 365 * 20


for country in shpreader.Reader(countries_shp).records():
    if country.attributes['NAME_LONG'] in ct:
        name = ct[country.attributes['NAME_LONG']]
    else:
        name = country.attributes['NAME_LONG']
    if name in allcountries and allcountries[name]['signedandratified'] > 0:
        if allcountries[name]['ratificationtime-max'] < maxcolor:
            coloridx = int(255 * allcountries[name]['ratificationtime-max'] / maxcolor)
        else:
            coloridx = 255
        color = cm.copper_r(coloridx)
    else:
        print(country.attributes['NAME_LONG'])
        color = (0.4, 0.4, 0.4)
    # print(country.attributes['NAME_LONG'], color)
    ax.add_geometries(country.geometry, ccrs.PlateCarree(),
                      facecolor=color,
                      edgecolor=(0, 0, 0))
                      # label=country.attributes['NAME_LONG'])

# https://stackoverflow.com/questions/35873209/matplotlib-add-colorbar-to-cartopy-image    
sm = plt.cm.ScalarMappable(cmap=plt.get_cmap('copper_r'))
sm._A = []
cb = plt.colorbar(sm, orientation='horizontal', fraction=0.046, pad=0.04)
cb.set_ticks([0, 0.2, 0.4, 0.6, 0.8, 1])
cb.set_ticklabels(['immediate', '4 years', '8 years', '12 years', '16 years', '>=20 years'])

plt.title('Maximal Time of Treaty Ratification')
plt.tight_layout()
plt.savefig('max.svg')
plt.savefig('max.pdf')
plt.show()

# ban
fig = plt.figure(figsize=(12,7))
ax = plt.axes(projection=ccrs.PlateCarree())

maxcolor = 365 

tpnw = 'Treaty on the Prohibition of Nuclear Weapons'

for country in shpreader.Reader(countries_shp).records():
    if country.attributes['NAME_LONG'] in ct:
        name = ct[country.attributes['NAME_LONG']]
    else:
        name = country.attributes['NAME_LONG']
    if name in allcountries:
        if tpnw in allcountries[name]:
            color = (0.4, 0.4, 0.4)
            rat = False
            for i in range(len(allcountries[name][tpnw]['actions'])):
                if 'signature' in allcountries[name][tpnw]['actions'][i].lower():
                    sd = allcountries[name][tpnw]['dates'][i]
                    sdate = dateparser.parse(sd)
                if 'ratification' in allcountries[name][tpnw]['actions'][i].lower():
                    rd = allcountries[name][tpnw]['dates'][i]
                    rdate = dateparser.parse(rd)
                    rat = True
            if rat:
                ratdays = (rdate - sdate).days
                coloridx = int(255.0 * ratdays / maxcolor)
                color = cm.copper_r(coloridx)
        else:
            color = (1, 1, 1)
    else:
        print(country.attributes['NAME_LONG'])
        color = (1, 1, 1)
    # print(country.attributes['NAME_LONG'], color)
    ax.add_geometries(country.geometry, ccrs.PlateCarree(),
                      facecolor=color,
                      edgecolor=(0, 0, 0))
                      # label=country.attributes['NAME_LONG'])

# https://stackoverflow.com/questions/35873209/matplotlib-add-colorbar-to-cartopy-image    
sm = plt.cm.ScalarMappable(cmap=plt.get_cmap('copper_r'))
sm._A = []
cb = plt.colorbar(sm, orientation='horizontal', fraction=0.046, pad=0.04)
cb.set_ticks([0, 0.25, 0.5, 0.75, 1])
cb.set_ticklabels(['immediate', 'quarter', 'half', '3 quarter', '1 years or more'])

plt.title('TPNW: Time of Treaty Ratification')
plt.tight_layout()
plt.savefig('tpnw-rat.svg')
plt.savefig('tpnw-rat.pdf')
plt.show()


# ban treaty possible ratification
fig = plt.figure(figsize=(12,7))
ax = plt.axes(projection=ccrs.PlateCarree())


# plot ratification
tpnw = 'Treaty on the Prohibition of Nuclear Weapons'

startdate = dateparser.parse('2017-09-20')
middate = dateparser.parse(wowdate)
fulldays = (middate - startdate).days * 2.0
enddate = startdate + datetime.timedelta(days = fulldays)
maxcolor = fulldays

for country in shpreader.Reader(countries_shp).records():
    if country.attributes['NAME_LONG'] in ct:
        name = ct[country.attributes['NAME_LONG']]
    else:
        name = country.attributes['NAME_LONG']
    if name in tpnwdf['signatures'].values:
        fmin = tpnwdf[tpnwdf['signatures'] == name]['futureratificationdate'].values[0]
        difference = (dateparser.parse(fmin) - startdate).days
        coloridx = int(255.0 * difference / maxcolor)
        color = cm.copper_r(coloridx)
    else:
        color = (1, 1, 1)
    # print(country.attributes['NAME_LONG'], color)
    ax.add_geometries(country.geometry, ccrs.PlateCarree(),
                      facecolor=color,
                      edgecolor=(0, 0, 0))
                      # label=country.attributes['NAME_LONG'])

sm = plt.cm.ScalarMappable(cmap=plt.get_cmap('copper_r'))
sm._A = []
cb = plt.colorbar(sm, orientation='horizontal', fraction=0.046, pad=0.04)
cb.set_ticks([0, 0.5, 1.0])
cb.set_ticklabels(['2017-09-20', wowdate, '>=' + enddate.strftime("%Y-%m-%d")])

plt.title('TPNW: When should they ratify?')
plt.tight_layout()
plt.savefig('tpnw-ratification-estimate-min.svg')
plt.savefig('tpnw-ratification-estimate-min.pdf')
plt.show()
                      
