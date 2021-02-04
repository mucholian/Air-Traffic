# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %% [markdown]
# # weekly balances

# %%
import pandas as pd
import numpy as np
import seaborn as sns
import statsmodels.api as sm
import matplotlib
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
import math
import requests
import sqlite3
import datetime
import time
import os
import json
import io
import xlrd
import ciso8601
import urllib3
import http.client
from numpy import cos, sin, arcsin, sqrt
from math import radians
from dateutil.parser import parse
from scipy import stats
from datetime import date
import earthpy as et
from scipy.stats import norm
from sklearn.preprocessing import StandardScaler
from scipy import stats


# %%
# older data is bad
start_year = 2015  # have prices going back
s_date = datetime.datetime(year=start_year,month=1,day=1)
####
conn = sqlite3.connect('flights_data.db') # 3GB file. data from 2015
c = conn.cursor()
#### LIST AND DETAILS OFF THE 50 AIRPORTS I AM TRACKING
airports_headers = ['ident','name','latitude_deg','longitude_deg',              # from a database of global airports   
'continent','iso_country','iso_region','gps_code','iata_code','PADD']
ARIP_DATA = pd.read_csv('C:/Users/Moses/Python/flights_data/airports_list.csv') # file uploaded       
ARIP_H = ['iata','city','state','icao24','latitude_deg','longitude_deg']        # airports data headers
ARIP_LIST = ARIP_DATA['icao24'].tolist()                                        # list of airports we want to track
MODE = ['Departures']                                                           # Arrivals/Departures
arip_subset = ['index','icao24','callsign','estDepartureAirport','estArrivalAirport','lastSeen','latitude_deg','longitude_deg']
### DATABASE OF ALL AIRPORTS GLOBALY
SUB_HEADERS = ['ident','name','latitude_deg','longitude_deg','continent','iso_country','iso_region','gps_code','iata_code','PADD','state_province']
ARIP_MASTER =  pd.read_csv('C:/Users/Moses/Python/flights_data/airports_icao.csv')
ARIP_MASTER = ARIP_MASTER[SUB_HEADERS]       # read airports file

# %% [markdown]
# ### WEEKLY EIA DATA

# %%
## refinery output for each product
EIA_OUTPUT = pd.read_excel('weekly_doe_all.xls',sheet_name='tot_refo', index_col=0)
EIA_OUTPUT = EIA_OUTPUT.rename_axis("period")
EIA_OUTPUT.rename(columns={'date.1':'date'}, inplace=True)
s_date = datetime.datetime(year=start_year,month=1,day=1)
EIA_OUTPUT=EIA_OUTPUT[EIA_OUTPUT['date'] >= s_date]
EIA_OUTPUT['date']=EIA_OUTPUT[EIA_OUTPUT['date'] >= s_date]
EIA_OUTPUT = EIA_OUTPUT.filter(regex="Refiner and Blender Net Production of Kerosene-Type Jet Fuel")
headers=['US_prod','PADD1_prod','PADD2_prod','PADD3_prod','PADD4_prod','PADD5_prod']
names = EIA_OUTPUT.columns.to_list()
### fixing the names here...
test_keys = names
test_values = headers
res = {}
for key in test_keys: 
    for value in test_values: 
        res[key] = value 
        test_values.remove(value)
        break
EIA_OUTPUT.rename(columns=res, inplace=True)
EIA_OUTPUT.plot()


# %%
### fixing the names here...
test_keys = names
test_values = headers
res = {}
for key in test_keys: 
    for value in test_values: 
        res[key] = value 
        test_values.remove(value)
        break
EIA_OUTPUT.rename(columns=res, inplace=True)
# del res


# %%
EIA_STOCKS = pd.read_excel('weekly_doe_all.xls',sheet_name='stocks', index_col=0)
EIA_STOCKS = EIA_STOCKS.rename_axis("period")
EIA_STOCKS.rename(columns={'date.1':'date'}, inplace=True)
s_date = datetime.datetime(year=start_year,month=1,day=1)
EIA_STOCKS=EIA_STOCKS[EIA_STOCKS['date'] >= s_date]
EIA_STOCKS['date']=EIA_STOCKS[EIA_STOCKS['date'] >= s_date]
EIA_STOCKS = EIA_STOCKS.filter(regex="Kerosene-Type Jet Fuel")
headers=['US_stocks','PADD1_stocks','PADD2_stocks','PADD3_stocks','PADD4_stocks','PADD5_stocks']
names = EIA_STOCKS.columns.to_list()
### fixing the names here...
test_keys = names
test_values = headers
res = {}
for key in test_keys: 
    for value in test_values: 
        res[key] = value 
        test_values.remove(value)
        break
EIA_STOCKS.rename(columns=res, inplace=True)
# EIA_STOCKS.head()


# %%
EIA_RUNS = pd.read_excel('weekly_doe_all.xls',sheet_name='ref_in', index_col=0)
EIA_RUNS = EIA_RUNS.rename_axis("period")
EIA_RUNS.rename(columns={'date.1':'date'}, inplace=True)
s_date = datetime.datetime(year=start_year,month=1,day=1)
EIA_RUNS=EIA_RUNS[EIA_RUNS['date'] >= s_date]
EIA_RUNS['date']=EIA_RUNS[EIA_RUNS['date'] >= s_date]
EIA_RUNS = EIA_RUNS.filter(regex="Gross Inputs into Refineries") # look for relevant headers
headers=['US_runs','PADD1_runs','PADD2_runs','PADD3_runs','PADD4_runs','PADD5_runs']
names = EIA_RUNS.columns.to_list()
### fixing the names here...
test_keys = names
test_values = headers
res = {}
for key in test_keys: 
    for value in test_values: 
        res[key] = value 
        test_values.remove(value)
        break
EIA_RUNS.rename(columns=res, inplace=True)
# EIA_RUNS.head()


# %%
EIA_IMP = pd.read_excel('weekly_doe_all.xls',sheet_name='imports', index_col=0)
EIA_IMP = EIA_IMP.rename_axis("period")
EIA_IMP.rename(columns={'date.1':'date'}, inplace=True)
s_date = datetime.datetime(year=start_year,month=1,day=1)
EIA_IMP=EIA_IMP[EIA_IMP['date'] >= s_date]
EIA_IMP['date']=EIA_IMP[EIA_IMP['date'] >= s_date]
EIA_IMP = EIA_IMP.filter(regex="Kerosene-Type Jet Fuel") # look for relevant headers
headers=['US_imp','PADD1_imp','PADD2_imp','PADD3_imp','PADD4_imp','PADD5_imp']
names = EIA_IMP.columns.to_list()
### fixing the names here...
test_keys = names
test_values = headers
res = {}
for key in test_keys: 
    for value in test_values: 
        res[key] = value 
        test_values.remove(value)
        break
EIA_IMP.rename(columns=res, inplace=True)
# EIA_IMP.head()


# %%
EIA_EXP = pd.read_excel('weekly_doe_all.xls',sheet_name='exp', index_col=0)
EIA_EXP = EIA_EXP.rename_axis("period")
EIA_EXP.rename(columns={'date.1':'date'}, inplace=True)
s_date = datetime.datetime(year=start_year,month=1,day=1)
EIA_EXP=EIA_EXP[EIA_EXP['date'] >= s_date]
EIA_EXP['date']=EIA_EXP[EIA_EXP['date'] >= s_date]
EIA_EXP = EIA_EXP.filter(regex="Kerosene-Type Jet Fuel") # look for relevant headers
headers=['US_exp','PADD1_exp','PADD2_exp','PADD3_exp','PADD4_exp','PADD5_exp']
names = EIA_EXP.columns.to_list()
### fixing the names here...
test_keys = names
test_values = headers
res = {}
for key in test_keys: 
    for value in test_values: 
        res[key] = value 
        test_values.remove(value)
        break
EIA_EXP.rename(columns=res, inplace=True)
# EIA_EXP.head()


# %%
IMPLIED_DEMAND = pd.read_excel('weekly_doe_all.xls',sheet_name='demand', index_col=0)
IMPLIED_DEMAND = IMPLIED_DEMAND.rename_axis("period")
IMPLIED_DEMAND.rename(columns={'date.1':'date'}, inplace=True)
s_date = datetime.datetime(year=start_year,month=1,day=1)
IMPLIED_DEMAND=IMPLIED_DEMAND[IMPLIED_DEMAND['date'] >= s_date]
IMPLIED_DEMAND['date']=IMPLIED_DEMAND[IMPLIED_DEMAND['date'] >= s_date]
IMPLIED_DEMAND = IMPLIED_DEMAND.filter(regex="Kerosene-Type Jet Fuel") # look for relevant headers
headers=['US_demand','PADD1_demand','PADD2_demand','PADD3_demand','PADD4_demand','PADD5_demand']
names = IMPLIED_DEMAND.columns.to_list()
### fixing the names here...
test_keys = names
test_values = headers
res = {}
for key in test_keys: 
    for value in test_values: 
        res[key] = value 
        test_values.remove(value)
        break
IMPLIED_DEMAND.rename(columns=res, inplace=True)
# IMPLIED_DEMAND.head()


# %%
WEEKLY_BALANCES = pd.merge(EIA_STOCKS,EIA_RUNS,left_index=True, right_index=True)
WEEKLY_BALANCES = pd.merge(WEEKLY_BALANCES,EIA_OUTPUT,left_index=True, right_index=True)
WEEKLY_BALANCES = pd.merge(WEEKLY_BALANCES,EIA_EXP,left_index=True, right_index=True)
WEEKLY_BALANCES = pd.merge(WEEKLY_BALANCES,EIA_IMP,left_index=True, right_index=True)
WEEKLY_BALANCES = pd.merge(WEEKLY_BALANCES,IMPLIED_DEMAND,left_index=True, right_index=True)


# %%
WEEKLY_BALANCES_ = WEEKLY_BALANCES.pct_change()
WEEKLY_BALANCES_ = WEEKLY_BALANCES_.add_prefix('chg_')
WEEKLY_BALANCES = pd.merge(WEEKLY_BALANCES,WEEKLY_BALANCES_,left_index=True, right_index=True)
WEEKLY_BALANCES.to_csv('WEEKLY_EIA_BALANCES.csv')


# %%
PADD1 = WEEKLY_BALANCES.filter(regex="PADD1")
PADD1['PADD1_JET_YIELD'] =  PADD1.PADD1_prod/PADD1.PADD1_runs
PADD2 = WEEKLY_BALANCES.filter(regex="PADD2")
PADD2['PADD2_JET_YIELD'] =  PADD2.PADD2_prod/PADD2.PADD2_runs
PADD3 = WEEKLY_BALANCES.filter(regex="PADD3")
PADD3['PADD3_JET_YIELD'] =  PADD3.PADD3_prod/PADD3.PADD3_runs
PADD4 = WEEKLY_BALANCES.filter(regex="PADD4")
PADD4['PADD4_JET_YIELD'] =  PADD4.PADD4_prod/PADD4.PADD4_runs
PADD5 = WEEKLY_BALANCES.filter(regex="PADD5")
PADD5['PADD5_JET_YIELD'] =  PADD5.PADD5_prod/PADD5.PADD5_runs


# %%
PADD1.to_csv('PADD1_Balances.csv')
PADD2.to_csv('PADD2_Balances.csv')
PADD3.to_csv('PADD3_Balances.csv')
PADD4.to_csv('PADD4_Balances.csv')
PADD5.to_csv('PADD5_Balances.csv')

