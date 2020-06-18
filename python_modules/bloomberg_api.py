"""
Pulling data via bloomberg api. Average prices for week ending friday.
Monthly is also average price for the month.
"""
# %%
import pandas as pd
import math
import seaborn as snn
import numpy as np
import matplotlib
import requests
import sqlite3
import os
import datetime
import sqlalchemy as sql
import pdblp as bbg
from xbbg import blp

# %% assumption and settings
#create bloomberg connection
con = bbg.BCon(debug=False, port=8194, timeout=5000)
con.start()
today = datetime.datetime.now()
s_date = '2011-01-01'
e_date = today
#read ticker list
names = ['Tickers']
tix = pd.read_csv("tickers.csv",names=names).values.tolist()
# create a global df for all prices. index needs to be created for begining of the month
global_index = pd.date_range(start=s_date,end=e_date, freq='W-FRI')
global_df = pd.DataFrame(index=global_index)

# %% bloomberg data requests
#create loop here for tickers in tix
for tt in tix:
    test_temp = blp.bdh(tickers=tt,flds=['last_price'],start_date=s_date,
        end_date=e_date,Quote='G',Per='W', Fill='B', Days='W')
    #get the name for dataframe header
    tick_name = blp.bdp(tickers=tt,flds=['Security_Name'])
    header=str(tt).strip('[]')
    test_temp.columns=[header]
    #merge current df with global df
    global_df=global_df.join(test_temp, how='outer')

global_df.to_csv('prices.csv')
