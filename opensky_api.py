# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
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
import json
import ciso8601
import http.client
from dateutil.parser import parse

# %%
USERNAME = "username" # your username
PASSWORD = "password" # your password
pl = pd.read_csv('C:/Users/Moses/Python/flights_data/airports_list.csv') # airports db from data provider
pl_headers = ['iata','city','state','icao24','latitude_deg','longitude_deg'] # airports data headers
ARIP_LIST = pl['icao24'].tolist() # list of airports that want to track
MODE = ['departure','arrival'] # not used 'departure'/'arrival'
# response data fields:
names = ['icao24','firstSeen','estDepartureAirport','lastSeen','estArrivalAirport','callsign',
'estDepartureAirportHorizDistance','estDepartureAirportVertDistance','estArrivalAirportHorizDistance',
'estArrivalAirportVertDistance','departureAirportCandidatesCount','arrivalAirportCandidatesCount'] # all the fields in the response string
select_names = ['icao24','callsign','estDepartureAirport','estArrivalAirport','lastSeen'] # only secelt these ones for db

# %% Dates and other variables
start_year = 2015 # can adjust
start_date = datetime.date(year=start_year,month=1,day=1) #start date for sending queries
time_range = 7 #days - for max query range for airports
today = datetime.datetime.utcnow() #database is based on UTC
today = today.date()
end_date = today # can be anything
global_index = pd.date_range(start=start_date,end=end_date, freq='W-FRI') #create weekly datetime_index ending this/last week
global_df = pd.DataFrame(index=global_index,columns=ARIP_LIST) # used to map data availability
global_df['date'] = global_index # if -1 means request failed (line 55-57)
conn = sqlite3.connect('flights_data.db') # db name
c = conn.cursor()

# %%
# API QUERIES FOR DEPARTURES
for AA in ARIP_LIST: #this loop is for airports. 60 airports 
    total_data = pd.DataFrame() #temp df for airport level data
    for d in global_index:
        e_date_ = str(int(d.timestamp())) #get timestamp for start date for url
        d_ = d + datetime.timedelta(days=-7) # find the e_date
        s_date_ = str(int(d_.timestamp())) #get timestamp for end date for url
        ## create query url
        url_1 = 'https://' + USERNAME + ':' + PASSWORD + '@opensky-network.org/api/flights/' + MODE[0] + '?airport=' + AA + '&begin=' + s_date_ + '&end=' + e_date_
        r_1 = requests.get(url_1) #GET
        if(r_1.status_code != 200): #if request not successful move to next query. Could be set up to retry a few times before moving on
            global_df.loc[d,AA] = -1 # if not available put -1 for that week
            continue
        r_1_dict = r_1.json() #read json response
        data_1 = pd.DataFrame(data=r_1_dict,columns=names) #insert the raw data into df
        data_1 = data_1[select_names] #select relevant fields
        data_1['lastSeen'] = pd.to_datetime(data_1['lastSeen'], unit='s') #convert timestamp to date
        data_1 = data_1.drop_duplicates() # some airports like SFO have dupes. receivers double count probably
        flight_num = len(data_1) # number of flights in/out of the airport (based on departure/arrivals) for the given period
        global_df.loc[d,AA] = flight_num # if request failed puts -1
        data_1.to_sql('ArrivalsRaw', con=conn, if_exists='append') #insert into SQL table
# this is the csv map
conn.close()
filename_2 = 'C:/Users/Moses/Python/flights_data/' + 'all' + '_' + MODE[0] + '.csv'
global_df.to_csv(filename_2) #this is global df file


# %%
# API QUERIES FOR ARRIVALS - CAN INSTEAD ADD ANOTHER LOOP ON MODE[0] or MODE[1]
for AA in ARIP_LIST: #this loop is for airports. 60 airports 
    total_data = pd.DataFrame() #temp df for airport level data
    for d in global_index:
        e_date_ = str(int(d.timestamp())) #get timestamp for start date for url
        d_ = d + datetime.timedelta(days=-7) # find the e_date
        s_date_ = str(int(d_.timestamp())) #get timestamp for end date for url
        ## create query url
        url_1 = 'https://' + USERNAME + ':' + PASSWORD + '@opensky-network.org/api/flights/' + MODE[1] + '?airport=' + AA + '&begin=' + s_date_ + '&end=' + e_date_
        r_1 = requests.get(url_1) #GET
        if(r_1.status_code != 200): #if request not successful move to next query. Could be set up to retry a few times before moving on
            global_df.loc[d,AA] = -1 # if not available put -1 for that week
            continue
        r_1_dict = r_1.json() #read json response
        data_1 = pd.DataFrame(data=r_1_dict,columns=names) #insert the raw data into df
        data_1 = data_1[select_names] #select relevant fields
        data_1['lastSeen'] = pd.to_datetime(data_1['lastSeen'], unit='s') #convert timestamp to date
        data_1 = data_1.drop_duplicates() # some airports like SFO have dupes. receivers double count probably
        ## match d with the date column to get index number
        flight_num = len(data_1) # number of flights in/out of the airport (based on departure/arrivals) for the given period
        global_df.loc[d,AA] = flight_num # if request failed puts -1
        data_1.to_sql('ArrivalsRaw', con=conn, if_exists='append') #insert into SQL table)
# this is the csv map
conn.close()
filename_2 = 'C:/Users/Moses/Python/flights_data/' + 'all' + '_' + MODE[1] + '.csv'
global_df.to_csv(filename_2) #this is global df file
