"""
This program will obtain historical data from OpenSky API. I have chosen to evaluate 'departures' and 'arrivals' for major airport to evaluate traffic and calculate demand for jet fuel.
OpenSky servers are slow and it will take a while to download the data. Unless they grant access to their Impala Shell service.
NOTE: Data license for this project data only allows private/academic research. 
     "Your account has been granted access to our database for any non-commercial purposes."
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
import json
import ciso8601
import http.client
from dateutil.parser import parse

# %% Assumptions
USERNAME = "mucholian"           # opensky details
PASSWORD = "Centenus18!"        
# doing a new round on airports that didnt have good data airports_icao
airp = pd.read_csv('C:/Users/Moses/Python/flights_data/airports2.csv') # airports db from data provider
airp_headers = ['iata','city','state','icao24','latitude_deg','longitude_deg'] # airports data headers
ARIP_LIST = airp['icao24'].tolist()   # list of airports that want to track
MODE = 'departure'  #In case we want to do loops for both MODE = ['departure','arrival']                 
# all the fields in the response string:
names = ['icao24','firstSeen','estDepartureAirport','lastSeen', 'estArrivalAirport','callsign',
'estDepartureAirportHorizDistance','estDepartureAirportVertDistance','estArrivalAirportHorizDistance',
'estArrivalAirportVertDistance','departureAirportCandidatesCount','arrivalAirportCandidatesCount'] 
subset = ['icao24','callsign','estDepartureAirport','estArrivalAirport','lastSeen'] # only select these ones for db

# %% Set time paramaters here
start_year = 2015       # Data before 2017/2018 is a mess...
start_date = datetime.date(year=start_year,month=1,day=1)   # start date for sending queries
time_range = 7          # days - for max query range for airports
today = datetime.datetime.utcnow()  # database is based on UTC
today = today.date()    # can adjust
end_date = today        # Time is UCT. Only at 8pm ETS we will get today's full list for today (In OpenSky's system)
global_index = pd.date_range(start=start_date,end=end_date, freq='W-FRI')   # create weekly datetime_index ending the most recent week
global_df = pd.DataFrame(index=global_index,columns=ARIP_LIST)  # used to map data availability
global_df['date'] = global_index            # if -1 means request failed (line 55-57)
conn = sqlite3.connect('flights_data.db')   # db name
c = conn.cursor()

# %% API QUERIES FOR DEPARTURES
# The outer loop is the list of 50 busiest airports in the US.
# the inner loop is for each week from begining date to now. to get Arrivals data too just run the loop twice with MODE[1]
# It adds the response data to SQL table at the end.
for AA in ARIP_LIST:                         # Outer loop is for each airport
    print("-----",AA,"-----")                # to track which airport is up now
    total_data = pd.DataFrame()              # temp df for airport level data
    for d in global_index:                   # d is the date that is the end of the given period (1 week here)
        e_date_ = str(int(d.timestamp()))    # timestamp for start-date for query url
        d_ = d + datetime.timedelta(days=-7) # MAX window for arrivals and departures queries is ONE WEEK
        s_date_ = str(int(d_.timestamp()))   # get timestamp for end date for url
        ## create query url
        url_1 = 'https://' + USERNAME + ':' + PASSWORD + '@opensky-network.org/api/flights/' + MODE + '?airport=' + AA + '&begin=' + s_date_ + '&end=' + e_date_
        ## OpenSky server frequently fails. try 10 times 
        count = 0                           # for number of attempts
        while count < 10:                   # i give it 10 times
            r_1 = requests.get(url_1)       # GET RESTFUL REQUEST
            count += 1                      # keep track of number of attempts
            if r_1.status_code != 200:      # if request not successful after 10 times move to next query.
                if count == 9: print(AA,"  ",d,"  fail")    # print if this week's query failed after 10 attempts
                # I will replace these prints with an error log
                # this is good to understand the performance, accuracy etc.
                print(AA,"  error Code  ",r_1.status_code,"  on attempt #",count) # what is the status of the response?
                time.sleep(1)             # wait one second before trying again
                continue                    # restart the loop 
            print(AA,"  ",d,"  good  #", count)     # print if the query was successful at which attempt
            break
        if r_1.status_code != 200: continue
        r_1_dict = r_1.json()               # read json response
        data_1 = pd.DataFrame(data=r_1_dict,columns=names)  #insert the raw data into df
        data_1 = data_1[subset]             # select relevant fields
        data_1['lastSeen'] = pd.to_datetime(data_1['lastSeen'], unit='s') # convert timestamp to date
        data_1 = data_1.drop_duplicates()   # some airports like SFO have dupes. receivers double count probably
        flight_num = len(data_1)            # number of flights in/out of the airport (based on departure/arrivals) for the given period
        global_df.loc[d,AA] = flight_num    # if request failed puts -1
        ### INSERT INTO SQL TABLE BELOW ####
        ### NOTE: careful if running ARRIVALS inquiry, table name should be 'ArrivalsRaw'
        data_1.to_sql('DeparturesRaw', con=conn, if_exists='append')   # Insert this period's data into 'DeparturesRaw'/'ArrivalsRaw'
        time.sleep(0.3) # dont want to send more than 5 quesries per second. They have bandwidth issues
conn.close()
filename = 'C:/Users/Moses/Python/flights_data_new/' + 'all' + '_' + MODE + '.csv' #
global_df.to_csv(filename)                   #this is the global df file. basically maps out which period for which airport did not return anything.


