import numpy as np
import pylab as pl
import datetime 
import pandas as pd
import scipy.signal as signal
from sklearn import linear_model

import sys
sys.path.append('../')
import settings

from stock_model import load_stock, date_contract, moving_average, momentum, update_avgs

maxdays = settings.maxdays
comm_choice = settings.comm_choice
start_date = [ 2000,1,1]
end_date = [2010,12,31]

contract_dates = [[a,b,15] for a in range(start_date[0]-2,end_date[0]+2) for b in settings.end_months[comm_choice] ] 

contract_dates = np.array([datetime.date(*a).toordinal() for a in contract_dates])
start_date = datetime.date(*start_date).toordinal()
end_date = datetime.date(*end_date).toordinal()

data_path = '/home/ameert/git_projects/dataprojects/alan/data/st_louis_fed/'


stock_data = load_stock(comm_choice, start_date, end_date)
#get the time to maturity in fraction of overall time
date_contract(contract_dates, stock_data)
momentum(stock_data)

pred_list = settings.pred_list
stock_data, pred_list=update_avgs(stock_data, pred_list, maxdays)


clf = linear_model.LinearRegression()

model_params = np.load('modeltmp.npz')
coef = model_params['coef']
intercept = model_params['intercept']
coef_names = model_params['predict_names']
clf.coef_ = coef
clf.intercept_ = intercept
clf.predict(stock_data[pred_list])

model = clf.predict(stock_data[pred_list])

train_start = [ int(a) for a in settings.start_date.split('-')]
train_end = [ int(a) for a in settings.end_date.split('-')]

train_start = datetime.date(*train_start).toordinal()
train_end = datetime.date(*train_end).toordinal()


pl.subplot(2,2,1)
pl.plot(stock_data.index, stock_data['settle'], c='k')
pl.plot(stock_data.index[maxdays:], model[maxdays:], c='r')
rect = pl.gca().add_patch(pl.Rectangle((train_start,pl.ylim()[0]),train_end-train_start,pl.ylim()[1]-pl.ylim()[0], zorder = -10, facecolor = 'k', alpha = 0.25))
ax = pl.gca()
pl.setp( ax.xaxis.get_majorticklabels(), rotation=70 )
pl.xlabel('date')
pl.ylabel('price')

pl.subplot(2,2,2)
pl.plot(stock_data.index[maxdays:], (stock_data['settle'][maxdays:]-model[maxdays:])/stock_data['settle'][maxdays:], c='r')
rect = pl.gca().add_patch(pl.Rectangle((train_start,pl.ylim()[0]),train_end-train_start,pl.ylim()[1]-pl.ylim()[0], zorder = -10, facecolor = 'k', alpha = 0.25))
ax = pl.gca()
pl.setp( ax.xaxis.get_majorticklabels(), rotation=70 )
pl.xlabel('date')
pl.ylabel('residual')


pl.subplot(2,2,3)
pl.plot(stock_data.index[maxdays:], (stock_data['settle'][maxdays:]-model[maxdays:])**2, c='r')
rect = pl.gca().add_patch(pl.Rectangle((train_start,pl.ylim()[0]),train_end-train_start,pl.ylim()[1]-pl.ylim()[0], zorder = -10, facecolor = 'k', alpha = 0.25))
ax = pl.gca()
pl.setp( ax.xaxis.get_majorticklabels(), rotation=70 )
pl.xlabel('date')
pl.ylabel('square residual')

if 1:
    pl.subplot(2,2,4)
    autocor = signal.correlate(stock_data['settle'], model, mode='same')
    offset = np.arange(-model.size/2, model.size/2)
    max_autocorr = np.extract(autocor >= np.max(autocor)-0.000001, offset)[0]
    pl.plot(offset,autocor)
    pl.text(0.1, 0.1, r'max\_autocorr$=$%0.1f'%max_autocorr, transform=pl.gca().transAxes)
    ax = pl.gca()
    pl.setp( ax.xaxis.get_majorticklabels(), rotation=70 )
    pl.xlabel('offset days')
    pl.ylabel('autocorrelation')

    pl.figtext(0.5, 0.95, comm_choice.replace('_',r'\_'))


print clf.coef_
print clf.intercept_
print coef_names

mom_memory = []
price_memory = []
cpi_mom_memory = []

for a,b in zip(coef_names,clf.coef_):
    if "mom_avg_" in a:
        val = int(a.split('mom_avg_')[1])
        mom_memory.append((val,b))
    elif "p_avg_" in a:
        val = int(a.split('p_avg_')[1])
        price_memory.append((val,b))
    elif "CPI_mom_" in a:
        val = int(a.split('CPI_mom_')[1])
        cpi_mom_memory.append((val,b))

mom_memory = np.array(mom_memory)
price_memory = np.array(price_memory)
cpi_mom_memory = np.array(cpi_mom_memory)

pm = np.cumsum(price_memory[::-1,1]/price_memory[::-1,0])[::-1]
print "price memory"
print pm
mm = np.cumsum(mom_memory[::-1,1]/mom_memory[::-1,0])[::-1]
print "momentum memory"
print mm
cm = np.cumsum(cpi_mom_memory[::-1,1]/cpi_mom_memory[::-1,0])[::-1]
print "CPI momentum memory"
print cm


if 0:
    pl.subplot(2,2,4)
    pl.plot(price_memory[:,0],pm, 'b')
    pl.plot(mom_memory[:,0],mm, 'r')
    
    pl.xlabel('days')
    pl.ylabel('memory')

    pl.figtext(0.5, 0.95, comm_choice)

pl.subplots_adjust(hspace = 0.6, wspace = 0.4, bottom=0.15)
pl.show()

