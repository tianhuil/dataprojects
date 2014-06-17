import numpy as np
import pandas as pd
import MySQLdb as mysql
import pylab as pl
import sys

sys.path.append('../')
import settings

start = '20100000'
stop = '20100401'

Conn = mysql.connect(host = settings.host,
                     user = settings.user,
                     db = settings.db)
Conn.autocommit(True)
cursor = Conn.cursor()

numplots = len(settings.to_use)
yplots = 2
xplots = np.ceil(numplots/float(yplots))


fig1 = pl.figure()
fig1.subplots_adjust(hspace = 0.5, wspace = 0.7)
fig2 = pl.figure()
fig2.subplots_adjust(hspace = 0.5, wspace = 0.7)

fig4 = pl.figure()
fig4.subplots_adjust(hspace = 0.5, wspace = 0.7)
fig5 = pl.figure()
fig5.subplots_adjust(hspace = 0.5, wspace = 0.7)

mjd = 0

for count, stock in enumerate(settings.to_use):
    print stock
    cmd = 'select to_days(SQLDATE), high, low, settle, volume, open_interest from %s where SQLDATE between %s and %s order by SQLDATE;' %(stock, start, stop)
    print cmd
    cursor.execute(cmd)
    
    data = dict(zip(['juliandate', 'high', 'low', 'settle', 'volume',  'open_interest'], np.array(cursor.fetchall()).T))

    data =  pd.DataFrame(data)
    #normalize everything
    mjd = np.min(data['juliandate'])
    data['juliandate'] = data['juliandate']-mjd
    normval = data['settle'].copy()
    normval[1:] = normval[0:-1]

    for col in data.columns:
        print col
        print data[col].describe()
        #raw_input()
    
    
    pl.figure(fig1.number)
    fig1.add_subplot(xplots, yplots, count+1)
    pl.title(stock.replace('_', ' '))
    pl.grid('on')
    
    pl.plot(data['juliandate'],data['volume'], 'r', zorder =-999)
    pl.ylabel('Volume')
    pl.xlabel('Modified Julian Date')
    pl.xlim((0,pl.xlim()[1]))
    
    pl.twinx()
    pl.fill_between(data['juliandate'],(data['low']-normval)/normval,(data['high']-normval)/normval, facecolor='k', alpha=0.5)
    pl.plot(data['juliandate'],(data['settle']-normval)/normval)
    pl.ylabel('Price')
    pl.xlim((0,pl.xlim()[1]))

    pl.figure(fig5.number)
    fig5.add_subplot(xplots, yplots, count+1)
    pl.title(stock.replace('_', ' '))
    pl.grid('on')
    
    pl.fill_between(data['juliandate'],data['low'],data['high'], 
                    facecolor='k', alpha=0.5)
    pl.plot(data['juliandate'],data['settle'])
    pl.ylabel('Price')
    pl.xlim((0,pl.xlim()[1]))


    pl.figure(fig2.number)
    fig2.add_subplot(xplots, yplots, count+1)
    pl.title(stock.replace('_', ' '))
    pl.grid('on')
    
    pl.plot(data['juliandate'],data['open_interest'], 'r', zorder =-999)
    pl.ylabel('Open Interest')
    pl.xlabel('Modified Julian Date')
    pl.xlim((0,pl.xlim()[1]))
    #pl.twinx()
    #pl.fill_between(data['juliandate'],data['low']/data['settle'][0],data['high']/data['settle'][0], facecolor='k', alpha=0.5)
    #pl.plot(data['juliandate'],data['settle']/data['settle'][0])
    #pl.ylabel('Price')
    
    pl.figure(fig4.number)
    fig4.add_subplot(xplots, yplots, count+1)
    pl.title(stock.replace('_', ' '))
    pl.grid('on')
    
    pl.plot(data['juliandate'],data['open_interest'], 'r', zorder =-999)
    pl.ylabel('Open Interest')
    pl.xlabel('Modified Julian Date')
    pl.xlim((0,pl.xlim()[1]))
    
cmd = 'select SQLDATE, to_days(SQLDATE), count(*), avg(AvgTone), avg(GoldsteinScale) from EVENTS2010 where IsRootEvent = 1 and SQLDATE between %s and %s group by SQLDATE;'  %(start, stop)
print cmd
cursor.execute(cmd)

fig3 = pl.figure()


data = dict(zip(['SQLDATE','juliandate', 'eventcount', 'avgtone', 
                 'goldstein'], np.array(cursor.fetchall()).T))

pl.figure(fig3.number)
pl.subplots_adjust(hspace = 0.5, wspace = 0.3)
fig3.add_subplot(xplots, yplots,1)
pl.title('GDELT Events Per Day')
pl.grid('on')
pl.plot(data['juliandate']-mjd,data['eventcount'], 'r', zorder =-999)
pl.ylabel('Number of Events')
pl.xlabel('Modified Julian Date')
pl.xlim((0,pl.xlim()[1]))

fig3.add_subplot(xplots, yplots,2)
pl.title('GDELT AvgTone')
pl.grid('on')
pl.plot(data['juliandate']-mjd,data['avgtone'], 'r', zorder =-999)
pl.ylabel('Average Event Type')
pl.xlabel('Modified Julian Date')
pl.xlim((0,pl.xlim()[1]))

fig3.add_subplot(xplots, yplots,3)
pl.title('GDELT Goldstein')
pl.grid('on')
pl.plot(data['juliandate']-mjd,data['goldstein'], 'r', zorder =-999)
pl.ylabel('Goldstein')
pl.xlabel('Modified Julian Date')
pl.xlim((0,pl.xlim()[1]))



pl.show()

