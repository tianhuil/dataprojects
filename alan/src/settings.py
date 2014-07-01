### General Paths ####
from pypaths import *

### QUANDL Stock date range info
#start_date = '2004-01-01'
#end_date = '2005-12-31'
train_start_date = '2000-01-01'
train_end_date = '2006-12-31'

test_start_date = '2009-01-01'
test_end_date = '2012-12-31'




authtoken="ZwZp5EomA34QgSDRezss" #this is optional

host = 'localhost'
user = 'incubator'
db = 'Commodities'

to_use = ['oil','natural_gas', 'corn', 'wheat']#,'gold','silver']

#Quandl info
stockpath = 'quandl'

indicators = { 'oil':'CHRIS/CME_CL1',
               'natural_gas':'CHRIS/CME_NG1',
               'corn':'CHRIS/CME_C1',
               'wheat':'CHRIS/CME_W1',
               }

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




##### SQL INFO  ######

sql_info = {'usr':'incubator',
            'pwd':'',
            'dba':'Commodities'
            }

####  Learner Info #####
pred_list = ['time_remaining','CPI','GDP','stress_ind']
maxdays=31
comm_choice = 'oil'


