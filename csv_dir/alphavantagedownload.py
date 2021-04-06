from datetime import datetime as dt
import os
import sys
sys.path.append(os.path.join('..', 'pricing'))
import pandas as pd
from alpha_vantage.timeseries import TimeSeries

from alpha_vantage.alphavantage import AlphaVantage

if __name__ == "__main__":
    # Create an AlphaVantage API instance
    ts = TimeSeries(key="EB4BZ9KSCP812DDW",output_format='pandas')
    # Download the Apple Group OHLCV data from 
    print("Obtaining Apple data from AlphaVantage and saving as CSV...")
    aapl ,meta= ts.get_daily('GOOG',outputsize='full')
    # ts.get_daily_adjusted()
    aapl.to_csv('GOOG.csv')
    
s=open('GOOG.csv')


import pandas as pd

dfalphavantage = pd.read_csv (r'~/Documents/skola/finproj/algo-project/csv_dir/GOOG.csv',index_col=0,header=0)
print (dfalphavantage)

dfkrakenOHLCV = pd.read_csv (r'~/Documents/skola/finproj/algo-project/csv_dir/XBTUSD_1440m_daily.csv', names=[
                    'unix', 'open', 'high', 
                    'low', 'close', 'volume','trades'
                ],header=0)

dfkrakenOHLCV = pd.read_csv (r'~/Documents/skola/finproj/algo-project/csv_dir/XBTUSD_1440m_daily.csv')

# for i in range(0,len(dfkrakenOHLCV))
dfkrakenOHLCV['unix']= pd.to_datetime(dfkrakenOHLCV['unix'],unit='s')

import datetime
datetime.datetime.fromtimestamp(1381017600).strftime('%Y-%m-%d')

s=(dfalphavantage.columns==['date', '1. open', '2. high', '3. low', '4. close', '5. volume']).any
    
while True:
    try:
        pd.to_datetime(dfkrakenOHLCV.columns[0],unit='s')
        print('x')
        break
    except ValueError:
        print('y')