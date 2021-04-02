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
    # aapl=aapl[0]
    # aapl=pd.DataFrame.from_dict(aapl,orient='index')
    aapl.to_csv('GOOG.csv')
    
open()