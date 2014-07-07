### General Paths ####
from pypaths import *

### GDelt ###
gdelt_downstatus = 'GDeltDownStatus.txt'
gdelt_sql = 'GDeltSQLStatus.txt'

### QUANDL Stock date range info
start_date = '2000-01-01'
end_date = '2012-12-31' 
stock_downstatus = 'StockDownStatus.txt'
stock_sql = 'StockSQLStatus.txt'

# there is potential to add more in commodities in the future
to_use = ['oil',]#'natural_gas', 'corn', 'wheat']

#Quandl info
authtoken="ZwZp5EomA34QgSDRezss" #this is optional
stockpath = 'quandl'

indicators = { 'oil':'CHRIS/CME_CL1',
               'natural_gas':'CHRIS/CME_NG1',
               'corn':'CHRIS/CME_C1',
               'wheat':'CHRIS/CME_W1',
               }

# Not currently implemented 
baskets = {'oil':'energy',
           'natural_gas':'energy',
           'corn':'food',
           'wheat':'food',
           }


end_months = {'wheat':[3,5,7,9,12],
              'corn': [3,5,7,9,12],
              'oil':  range(1,13),
              'natural_gas': range(1,13)
    }
end_day = {'wheat':15,
            'corn': 15,
            'oil':  25,
            'natural_gas': 28
    }

#St Louis Fed info
fed_api_key = '5a0f30658c0004e7a5d5a3e473101452'
fed_series = {'CPIAUCNS':'CPI','GDPCA':'GDP','RECPROUSM156N':'RecProb',
              'UMCSENT':'umSent','FEDFUNDS':'FedFundsRate','POP':'Population',
              'STLFSI':'stressInd'}
fed_downstatus = 'FedDownStatus.txt'
fed_sql = 'FedSQLStatus.txt'


##### SQL INFO  ######
host = 'localhost'
user = 'incubator'
pwd = ''
db = 'Commodities'

####  Learner Info #####
train_start_date = '2000-01-01'
train_end_date = '2006-12-31'

test_start_date = '2009-01-01'
test_end_date = '2012-12-31'

pred_list = ['time_remaining','CPI','GDP','stress_ind']
maxdays=31
comm_choice = 'oil'


