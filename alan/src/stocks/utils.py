import numpy as np
import pandas as pd
import datetime

def SQLdate_to_ord(dates):
    """converts a SQL date of form YYYYMMDD into an ordinal"""
    date = np.array([datetime.date(a/10000, (a%10000)/100, (a%100)).toordinal() for a in dates])
    return date

def SQLdate_to_date(dates):
    """converts a SQL date of form YYYYMMDD into a datetime object""" 
    date = [datetime.date(a/10000, (a%10000)/100, (a%100)) for a in dates]
    return date
