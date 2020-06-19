import json
import numpy as np
import pandas as pd
from urllib.error import URLError, HTTPError
from urllib.request import urlopen

class EIAgov(object):
    def __init__(self, token, series):
        '''
        Purpose:
        Initialise the EIAgov class by requesting:
        - EIA token
        - id code(s) of the series to be downloaded

        Parameters:
        - token: string
        - series: string or list of strings
        '''
        self.token = token
        self.series = series

    '''
    def __repr__(self):
        return str(self.series)
    '''

    def Raw(self, ser):
        # Construct url
        url = 'http://api.eia.gov/series/?api_key=' + self.token + '&series_id=' + ser.upper()

        try:
            # URL request, URL opener, read content
            response = urlopen(url);
            raw_byte = response.read()
            raw_string = str(raw_byte, 'utf-8-sig')
            jso = json.loads(raw_string)
            return jso

        except HTTPError as e:
            print('HTTP error type.')
            print('Error code: ', e.code)

        except URLError as e:
            print('URL type error.')
            print('Reason: ', e.reason)

    def GetData(self):
        # Deal with the date series                       
        date_ = self.Raw(self.series[0])        
        date_series = date_['series'][0]['data']
        endi = len(date_series) # or len(date_['series'][0]['data'])
        date = []
        for i in range (endi):
            date.append(date_series[i][0])

        # Create dataframe
        df = pd.DataFrame(data=date)
        df.columns = ['Date']

        # Deal with data
        lenj = len(self.series)
        for j in range (lenj):
            data_ = self.Raw(self.series[j])
            data_series = data_['series'][0]['data']
            data = []
            endk = len(date_series)         
            for k in range (endk):
                data.append(data_series[k][1])
            df[self.series[j]] = data
        
        return df

## all the details are here https://www.eia.gov/opendata/qb.php?category=371

if __name__ == '__main__':
    tok = 'xxxxxxxxxxxxxxxxxxxxxxx' # register for ur key. its instant 
    ng = ['PET.WTXIM_R10-Z00_2.4']  # dataset id. This is East Coast (PADD 1) Imports of Total Petroleum Products, 4 Week Avg
    data = EIAgov(tok, ng)
    print(data.GetData())






