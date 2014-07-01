import pandas as pd
import pandas.io.sql as psql
import MySQLdb as mysql
import warnings
warnings.filterwarnings('ignore', category=mysql.Warning)
import datetime 

import sys
sys.path.append('../')
import settings

from utils import *
from stock_returns import date_contract

Conn = mysql.connect(host = settings.host,
                     user = settings.user,
                     db = settings.db)
Conn.autocommit(True)
cursor = Conn.cursor()


for stock in settings.to_use:
    stock_frame = psql.frame_query('select SQLDATE, open, high, low, last, diff, settle, volume, open_interest from %s;' %stock, con=Conn)
    print 'loaded dataframe from MySQL. records:', len(stock_frame)

    stock_frame.index = SQLdate_to_date(stock_frame['SQLDATE'])
    stock_frame.index = pd.to_datetime(stock_frame.index)
    stock_frame['orddate'] = SQLdate_to_ord(stock_frame['SQLDATE'])

    contract_dates = pd.to_datetime(pd.Series(['%d-%d-%d' %(a,b,settings.end_day[stock]) for a in range(1995,2020) for b in range(1,12)]))

    contract_dates = pd.DatetimeIndex(contract_dates) - pd.tseries.offsets.BDay(3)

    # get the time to maturity in fraction of overall time
    date_contract(contract_dates, stock_frame)
    
    #remove any values that might cause log problems
    stock_frame['volume'] = np.where(stock_frame['volume'].values<1.01, 1.01,stock_frame['volume'].values)
    stock_frame['open_interest'] = np.where(stock_frame['open_interest'].values<1, 1,stock_frame['open_interest'].values)
    
    for data_name in ['CPI',  'GDP',  'Population',  'rec_prob',
                 'stress_ind',  'um_sent', 'FedFundsRate']:
        #Takes the most recent value of the metric as the current value
        cmd = 'select c.stockdate, d.value as {metric} from (select b.SQLDATE-min(abs(a.SQLDATE-b.SQLDATE)) as mdate, b.SQLDATE as stockdate from {metric} as a, {stock} as b where a.SQLDATE<=b.SQLDATE group by b.SQLDATE) as c, {metric} as d where c.mdate = d.SQLDATE;'.format(metric=data_name, stock=stock)
        metric_df = psql.frame_query(cmd, con=Conn)
        ord_metric = SQLdate_to_date(metric_df['stockdate'])
        metric_df.index = ord_metric
        metric_df.index = pd.to_datetime(metric_df.index)
    
        stock_frame = stock_frame.join(metric_df[data_name])
        print 'loaded dataframe from MySQL. records:', len(metric_df)



    # now add in the number of events per day from each country

    for country_name in ('US', 'IR', 'SA','NO','NI', 'RS', 'JA', 'KS','GM','FR'):
        #Takes the most recent value of the metric as the current value
        cmd = "select SQLDATE as stockdate, country, events as count%s  from country_totals  where country = '%s' ;" %(country_name,country_name)
        metric_df = psql.frame_query(cmd, con=Conn)
        ord_metric = SQLdate_to_date(metric_df['stockdate'])
        metric_df.index = ord_metric
        metric_df.index = pd.to_datetime(metric_df.index)
    
        stock_frame = stock_frame.join(metric_df['count%s' %country_name])
        print 'loaded dataframe from MySQL. records:', len(metric_df)
        
        cmd = "select SQLDATE as stockdate, numevents as count19%s  from EVENT19country  where Geo_CountryCode_1 = '%s' or Geo_CountryCode_2='%s' group by SQLDATE;" %(country_name,country_name,country_name)
        metric_df = psql.frame_query(cmd, con=Conn)
        ord_metric = SQLdate_to_date(metric_df['stockdate'])
        metric_df.index = ord_metric
        metric_df.index = pd.to_datetime(metric_df.index)
    
        stock_frame = stock_frame.join(metric_df['count19%s' %country_name])
        print 'loaded dataframe from MySQL. records:', len(metric_df)

        cmd = "select SQLDATE as stockdate, numevents as count18%s  from EVENT19country  where Geo_CountryCode_1 = '%s' or Geo_CountryCode_2='%s' group by SQLDATE;" %(country_name,country_name,country_name)
        metric_df = psql.frame_query(cmd, con=Conn)
        ord_metric = SQLdate_to_date(metric_df['stockdate'])
        metric_df.index = ord_metric
        metric_df.index = pd.to_datetime(metric_df.index)
    
        stock_frame = stock_frame.join(metric_df['count18%s' %country_name])
        print 'loaded dataframe from MySQL. records:', len(metric_df)
        
        

    print stock_frame    
    stock_frame.to_pickle(stock+'.pickle')

    

