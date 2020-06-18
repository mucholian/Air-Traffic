"""
This module will clean and shape the data from sql database for each airport, merges with other datasets and calculates the follwong:
    1) average number of daily flights since 2015 for the week ending Fridays (in line with EIA data calendar). data prior to 2017/2018 is basically terrible.
    2) average distance per flight out of each airport for the given time period.
    3) total_miles travelled out of the given airports (say 200 flights per day during the week, and avg distance to destinations on that day was).
    4) around 85%-90% of departures include destination airports. This could be improved by using ALL STATE VECTOR data from OpenSky and reconcile the two datasets. (more on this later)
EACH OF THIS VARIABLES WILL HAVE THEIR OWN DB_TABLE FOR EACH AIRPORT
OpenSky servers are slow and it will take a while to download the data. Unless they cannot access to their Impala Shell service.
NOTE: Data license for this project data only allows private/academic research. 
Your account has been granted access to our database for any non-commercial purposes.
"""
# %%
import pandas as pd
import numpy as np
import seaborn as sns
import math
import matplotlib
import matplotlib.pyplot as plt
import requests
import sqlite3
import datetime
import time
import os
import json
import ciso8601
from numpy import cos, sin, arcsin, sqrt
from math import radians
import http.client
from dateutil.parser import parse
from scipy import stats

# %% calculates distance without relying on external APIs
# even better than the HAVERSINE and GEOPY packages. 
# Those package relies on Google geo services etc.
# and I will hit the limit quite quickly
def haversine_np(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2
    c = 2 * np.arcsin(np.sqrt(a))
    km = 6367 * c
    ml = km * 0.621371
    return ml

# %% assumptions, constants, raw data
conn = sqlite3.connect('flights_data.db') # db name
c = conn.cursor()
# this section reads the airports details provided by OpenSky
# the file contains details such as geo coordinates etc for thousands of airports globally
f_directory = 'C:/Users/Moses/Python/flights_data/'
f_name_airports = 'airports_icao'           # list of airports and their geo locations
f_csv = '.csv'                              # extention
f_mode = '_departure'                       # or 'arrival'
airports_headers = ['ident','name','latitude_deg','longitude_deg',              # from a database of global airports   
'continent','iso_country','iso_region','gps_code','iata_code']
AA = pd.read_csv( ''.join([f_directory,f_name_airports,f_csv]),index_col=0)     # read airports file
AA = AA[airports_headers]                   # drop unused columns

pl = pd.read_csv('C:/Users/Moses/Python/flights_data/airports_list.csv')        # list of airports that we are looking at
pl_headers = ['iata','city','state','icao24','latitude_deg','longitude_deg']    # airports data headers
ARIP_LIST = pl['icao24'].tolist()           # list of airports we want to track
MODE = ['Departures']                       # Arrivals/Departures
subset = ['index','icao24','callsign','estDepartureAirport','estArrivalAirport','lastSeen']  # only secelt these ones for db

# new df for each of the final output
# data before 2017/2018 is really patchy
start_year = 2018                   # can adjust
start_date = datetime.date(year=start_year,month=1,day=1)  # start date for sending queries
time_range = 7                      # days - for max query range for airports
today = datetime.datetime.utcnow()  # database is based on UTC
today = today.date()
end_date = today                    # can be anything

####
global_index = pd.date_range(start=start_date,end=end_date, freq='W-FRI')       # create weekly datetime_index ending this/last week

# NUMBER OF WEEKLY FLIGHTS
total_weekly_flights = pd.DataFrame(index=global_index) # total weekly flight counts
total_weekly_flights['week_ending'] = global_index      # 'WEEK_ENDING' here is basically 'Date'. It is mostly used as key for merging dfs in this module.

# AVERAGE DAILY FLIGHTS
avg_daily_flights = pd.DataFrame(index=global_index)    # column for each airport
avg_daily_flights['week_ending'] = global_index

# AVG MILES PER FLIGHT FOR THE GIVEN WEEK (for the given airport)
avg_miles_per_flight = pd.DataFrame(index=global_index)            # column for each airport
avg_miles_per_flight['week_ending'] = global_index

# THIS IS DAILY AVG
tot_miles_per_day = pd.DataFrame(index=global_index) # total daily miles
tot_miles_per_day['week_ending'] = global_index

# % OF FLIGHT DEPARTURE(ARRIVAL) DATA POINTS THAT REPORT DESTINATION(ORIGIN)
ratio_reporting_dest = pd.DataFrame(index=global_index) # column for each airport
ratio_reporting_dest['week_ending'] = global_index

# %% read the data from db, and clean and reshape it
# read the data for each airport
# I will create a daily table too and add it to the DB
for AR in ARIP_LIST:            # for each AR in airports list 
    print(AR)                   # so i can track where in the process is it
    strg = 'SELECT * FROM DeparturesRaw WHERE estDepartureAirport=' + "'" +AR+"'" # select all the data for each airport 
    result = c.execute(strg).fetchall()      # fetch from curser
    LA = pd.DataFrame(result,columns=subset) # data for the AA airport
    LA.drop(columns=['index'],inplace=True)  # SQL added an index column
    LA = pd.merge(LA,AA,how = 'left',left_on = 'estArrivalAirport',right_on = 'ident')  # add geo data for the destinations. about 85% of flights have destinations
    # GET GEO COORDINATES OF CURRENT AIRPORT (DEPARTURE AIRPORT)
    AA_coords = AA.loc[AA[AA['ident'] == AR].index[0],['latitude_deg','longitude_deg']] # look up the coordinates of current airport
    AA_lat = AA_coords['latitude_deg']
    AA_lon = AA_coords['longitude_deg']
    
    # FOR CALCULATING DISTANCE, TEMPORARILY DROP ROWS THAT DON'T HAVE DESTINATION DETAILS.
    LA_2 = LA.dropna(subset=['estArrivalAirport'])  
     # this df is for Haversine function to iterate down and calculate distance based on geo coords
    ## calculate distance from origin to destination (AA in the loop) by passing on each row
    LA_2['distance'] = haversine_np(AA_lon,AA_lat,LA_2['longitude_deg'],LA_2['latitude_deg'])
    LA_F = pd.merge(LA, LA_2,  how='left') # this is the final df with the distants
    LA_F['lastSeen'] = LA_F['lastSeen'].astype('datetime64[ns]')
   
    # data before 2017-2018 looks very patchy and incomplete
    # but i am still keeping historicals in raw data tables
    s_date = datetime.datetime(year=start_year,month=1,day=1)
    LA_F=LA_F[LA_F['lastSeen'] >= s_date]

    # DOWNSAMPLING DISTANCE TO WEEKLY
    weekly_data = LA_F.groupby("estDepartureAirport").resample('W-Fri', label='right', closed = 'right', on='lastSeen').mean().reset_index().sort_values(by='lastSeen')
    weekly_data = weekly_data[['lastSeen','estDepartureAirport','distance']]
    weekly_data.rename(columns={'distance': 'miles_per_flight'}, inplace=True)

    # DOWNSAMPLING FLIGHT COUNT TO WEEKLY
    weekly_data_2 = LA_F.groupby("estDepartureAirport").resample('W-Fri', label='right', closed = 'right', on='lastSeen').count() # COUNT FLIGHTS in the period
    weekly_data_2['dest_available'] = (weekly_data_2['estArrivalAirport'] / weekly_data_2['estDepartureAirport']) # for what % of flights do we have distance/destination? 
    weekly_data_2 = weekly_data_2[['estDepartureAirport','dest_available']]
    weekly_data_2.rename(columns={ 'estDepartureAirport': 'flight_count'}, inplace=True)

    # total df with all the datapoints
    total_weekly = pd.merge(weekly_data, weekly_data_2,  how='left', on=['lastSeen']) # merge two tables. one is distance and one is flight count
    total_weekly.rename(columns={'lastSeen': 'week_ending','estDepartureAirport': "airport", 'dest_available': 'data_coverage'}, inplace=True)
    total_weekly.loc[total_weekly['flight_count'] < 100, 'flight_count'] = 0
    total_weekly.replace(0, np.nan, inplace=True) #replace 0 w nan
    ##### (NOT HAPPY WITH THIS LINE BELOW) FIX IT!!!
    # get mean arnd the missing point not the whole data
    # total_weekly['flight_count']=total_weekly['flight_count'].replace(np.nan,total_weekly['flight_count'].mean()) # replace missingg vals with mean
    #####

    ###### absolutely check out the daily flights are available for each day
    total_weekly['daily_flights'] = total_weekly.flight_count / 7 #this should be divided by NUMBER OF DAYS WITH DATA IN THAT WEEK
    total_weekly['total_miles'] = total_weekly.miles_per_flight * total_weekly.daily_flights

    ## from here down we take each of the columns for the given airport and insert into its aggrgt table
    # total_weekly_flights
    sub_df = total_weekly[['week_ending','flight_count']] #select sub_df
    sub_df.replace(0, np.nan, inplace=True) #replace 0 w Nan
    sub_df.rename(columns={ 'flight_count': AR}, inplace=True)  # rename the column to airport name code to be added to main table
    total_weekly_flights = total_weekly_flights.merge(sub_df,how = 'left', on = 'week_ending') # add this airport's weekly flight count to the main df
    total_weekly_flights.set_index(["week_ending"], inplace = True, drop = True) # reset the index to week end
    total_weekly_flights["total"] = total_weekly_flights.sum(axis=1)
    # avg_daily_flights
    sub_df = total_weekly[['week_ending','daily_flights']]
    sub_df.replace(0, np.nan, inplace=True)
    sub_df.rename(columns={ 'daily_flights': AR}, inplace=True)
    avg_daily_flights = avg_daily_flights.merge(sub_df,how = 'left', on = 'week_ending')
    avg_daily_flights.set_index(["week_ending"], inplace = True, drop = True)
    avg_daily_flights["total"] = avg_daily_flights.sum(axis=1)
    # avg_miles_per_flight
    sub_df = total_weekly[['week_ending','miles_per_flight']]
    sub_df.replace(0, np.nan, inplace=True)
    sub_df.rename(columns={'miles_per_flight': AR}, inplace=True)
    avg_miles_per_flight = avg_miles_per_flight.merge(sub_df,how = 'left', on = 'week_ending')
    avg_miles_per_flight.set_index(["week_ending"], inplace = True, drop = True)
    avg_miles_per_flight["total"] = avg_miles_per_flight.sum(axis=1)
    # tot_miles_per_day
    sub_df = total_weekly[['week_ending','total_miles']] #select sub_df
    sub_df.replace(0, np.nan, inplace=True) #replace 0 w nan
    sub_df.rename(columns={'total_miles': AR}, inplace=True) #rename the column to airports code for aggregate df
    tot_miles_per_day = tot_miles_per_day.merge(sub_df,how = 'left', on = 'week_ending') # add to aggrgt df
    tot_miles_per_day.set_index(["week_ending"], inplace = True, drop = True) # reset the index to week ending
    tot_miles_per_day["total"] = tot_miles_per_day.sum(axis=1)
    # ratio_reporting_dest
    sub_df = total_weekly[['week_ending','data_coverage']]
    sub_df.replace(0, np.nan, inplace=True)
    sub_df.rename(columns={ 'data_coverage': AR}, inplace=True)
    ratio_reporting_dest = ratio_reporting_dest.merge(sub_df,how = 'left', on = 'week_ending')
    ratio_reporting_dest.set_index(["week_ending"], inplace = True,append = True, drop = True)
    ratio_reporting_dest["total"] = ratio_reporting_dest.mean(axis=1) # this is mean of all the rows

## saving into csv and SQL
# CSV files will be very easy to upload to GitHub
# avg_daily_flights.fillna(method='ffill', inplace=True)
avg_daily_flights.to_csv('C:/Users/Moses/Python/results/avg_daily_flights.csv') #this is global df file
avg_daily_flights.to_sql('avg_daily_flights', con=conn, if_exists='replace') #insert into SQL table

# tot_miles_per_day.fillna(method='ffill', inplace=True)
tot_miles_per_day.to_csv('C:/Users/Moses/Python/results/tot_miles_per_day.csv') #this is global df file
tot_miles_per_day.to_sql('tot_miles_per_day', con=conn, if_exists='replace') #insert into SQL table

# avg_miles_per_flight.fillna(method='ffill', inplace=True)
avg_miles_per_flight.to_csv('C:/Users/Moses/Python/results/avg_miles_per_flight.csv') #this is global df file
avg_miles_per_flight.to_sql('avg_miles_per_flight', con=conn, if_exists='replace') #insert into SQL table

# total_weekly_flights.fillna(method='ffill', inplace=True)
total_weekly_flights.to_csv('C:/Users/Moses/Python/results/total_weekly_flights.csv') #this is global df file
total_weekly_flights.to_sql('total_weekly_flights', con=conn, if_exists='replace') #insert into SQL table

# ratio_reporting_dest.fillna(method='ffill', inplace=True)
avg_daily_flights.to_csv('C:/Users/Moses/Python/results/ratio_reporting_dest.csv') #this is global df file
ratio_reporting_dest.to_sql('ratio_reporting_dest', con=conn, if_exists='replace') #insert into SQL table

conn.close() # kill the db connection
