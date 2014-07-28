import numpy as np
import pandas as pd
import os.path as path
import Quandl

class fund_index_pair:    
    def __init__(self, fund_code, index_code, direction=1, start_date="2005-01-01"):
        self.fund_code = fund_code
        self.index_code = index_code
        self.start_date = start_date
        self.direction = direction
        
    def load(self):
        # If this is the first time of getting the data, send queries to Quandl website and download data there.
        #    Then, store the date in local directories as csv files
        # If the data has already been downloaded, load the local csv.
        fund_code = self.fund_code
        index_code = self.index_code
        start_date = self.start_date
        fund_file_name = "../data/" + fund_code.replace("/", "_") + ".csv"
        index_file_name = "../data/" + index_code.replace("/", "_") + ".csv"

        if path.isfile(fund_file_name): # file exists at local
            fund_data = pd.io.parsers.read_csv(fund_file_name, index_col=0) # the csv file has to be parsed to have date as index
        else: # download from Quandl and save it to local as csv file
            fund_data = Quandl.get(fund_code, trim_start=start_date, authtoken="XANwfFd9CmdoE3PdFzRg")
            fund_data.to_csv(fund_file_name)
        if path.isfile(index_file_name):
            index_data = pd.io.parsers.read_csv(index_file_name, index_col=0) # the csv file has to be parsed to have date as index
        else:
            index_data = Quandl.get(index_code, trim_start=start_date, authtoken="XANwfFd9CmdoE3PdFzRg")
            index_data.to_csv(index_file_name)

        # rename columns so that the two dataframes don't share any common names
        index_data.columns = map(''.join, zip([index_code+'_']*index_data.shape[1], list(index_data.columns))) # rename the columns with index_code as prefix
        fund_data.columns = map(''.join, zip([fund_code+'_']*fund_data.shape[1], list(fund_data.columns))) # rename the columns with fund_code as prefix    
        # join the two data frames by date
        self.data = fund_data.join(index_data, how='inner')
        if index_code+'_Adjusted Close' not in self.data.columns: # if no adjusted close, copy close to make name uniform across differnet data
            self.data[index_code+'_Adjusted Close'] = self.data[index_code+'_Close']

    # Remove Outliers
    def remove_outliers_by_moving_average(self, window_size=3, threshold=0.3):
        # This function returns the indexes of samples that moves far away (greater than a threshold)
        # from the moving average of samples before it
        # ser: series containing the data
        # window_size: window size for moving average
        # threshold: threshold to be considered large
        # Note: the first window_size samples are simply considered normal
        
        target_series = self.data[self.index_code+'_Adjusted Close']

        moving_avg = pd.rolling_mean(target_series, window=window_size)
        outlier_index = target_series[np.abs(target_series/moving_avg - 1) > threshold].index

        self.data = self.data.drop(outlier_index)
        
    def extend_data(self): 
        # expand the data with several differential values
        # the difference of movement between index and fund is the target variable
        # it could be further binarized depending on the application scenario
        # these new columns are probably useful for predictions

        # nan's are filled by interpolation.
        self.data = self.data.interpolate()

        # daily changes of fund close price and index adjusted close price
        self.data['fund_daily_change'] = (self.data[self.fund_code+'_Close'] - self.data[self.fund_code+'_Close'].shift(1))/self.data[self.fund_code+'_Close'].shift(1).astype(float)   # daily change of fund close price
        self.data['index_daily_change'] = (self.data[self.index_code+'_Adjusted Close'] - self.data[self.index_code+'_Adjusted Close'].shift(1))/self.data[self.index_code+'_Adjusted Close'].shift(1).astype(float)  # daily change of index adjusted close price
        self.data['fund_innerDay_change'] = (self.data[self.fund_code+'_Close'] - self.data[self.fund_code+'_Open'])/self.data[self.fund_code+'_Open'].astype(float)   # daily change of fund close price
        self.data['index_innerDay_change'] = (self.data[self.index_code+'_Adjusted Close'] - self.data[self.index_code+'_Open'])/self.data[self.index_code+'_Open'].astype(float)  # daily change of index adjusted close price
                
        # difference between fund's target from the its performance
        self.data['diff_changes'] = self.data['fund_daily_change'] - self.data['index_daily_change']*self.direction;
        
        # measuring volatility by the difference between high and low over open price
        self.data['fund_daily_volatility'] = (self.data[self.fund_code+'_High']-self.data[self.fund_code+'_Low'])/self.data[self.fund_code+'_Open'].astype(float)
        self.data['index_daily_volatility'] = (self.data[self.index_code+'_High']-self.data[self.index_code+'_Low'])/self.data[self.index_code+'_Open'].astype(float)

        # open price, since we try to predict the change of close price we could include the open price of that day as a signal
        self.data['onDay_fund_openMove'] = (self.data[self.fund_code+'_Open'].shift(-1)-self.data[self.fund_code+'_Close'])/self.data[self.fund_code+'_Close'].astype(float)
        self.data['onDay_index_openMove'] = (self.data[self.index_code+'_Open'].shift(-1)-self.data[self.index_code+'_Adjusted Close'])/self.data[self.index_code+'_Adjusted Close'].astype(float)

        # absolute changes, maybe more useful
        self.data['fund_abs_daily_change'] = self.data['fund_daily_change'].abs()
        self.data['index_abs_daily_change'] = self.data['index_daily_change'].abs()
        self.data['fund_abs_innerDay_change'] = self.data['fund_innerDay_change'].abs()
        self.data['index_abs_innerDay_change'] = self.data['index_innerDay_change'].abs()
        self.data['abs_diff_changes'] = self.data['diff_changes'].abs()
        self.data['onDay_fund_abs_openMove'] = self.data['onDay_fund_openMove'].abs()
        self.data['onDay_index_abs_openMove'] = self.data['onDay_index_openMove'].abs()
    
        # potential targets
        self.data['next_day_diff'] = self.data['diff_changes'].shift(-1)
        self.data['next_day_abs_diff'] = self.data['abs_diff_changes'].shift(-1)