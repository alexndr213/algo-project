import krakenex
from pykrakenapi import KrakenAPI
import pandas as pd
from datetime import timedelta
import time
import numpy as np
import matplotlib as plt
#%% API
with open('/home/alex/Documents/skola/finproj/key.txt') as f:
    key = f.read()
with open('/home/alex/Documents/skola/finproj/secret.txt') as f:
    secret = f.read()
    
api = krakenex.API(key.rstrip(), secret.rstrip())
k = KrakenAPI(api)
#%% Function
def convert_to_ohlc(df, granularity):
    # Determine time frame of data
    since = df['time'].iloc[0] * 1000000000
    to =  df['time'].iloc[-1] * 1000000000

    # Create an initial data table with entries from start till end time, with steps of 5 seconds
    timestamps = pd.date_range(since, to, freq=str(granularity) + 's')

    # Initialise output dataframe
    output = pd.DataFrame(index=timestamps, columns=['open', 'high', 'low', 'close'])

    # Step through data in steps of 5 seconds
    df['dtime'] = df.index
    df = df.set_index('time')
    for i in range(0, len(output.index)):
        # Select the relevant datapoints for this step
        relevant_rows = df[
            (df['dtime'] >= output.index[i]) &
            (df['dtime'] < (output.index[i] +
                              timedelta(seconds=granularity)))
            ]

        # Convert data in time frame to OHLC data
        if len(relevant_rows) > 0 and not relevant_rows.empty:
            # open
            output.loc[output.index[i], 'open'] = relevant_rows['price'].iloc[0]
            # high
            output.loc[output.index[i], 'high'] = np.max(relevant_rows['price'])
            # low
            output.loc[output.index[i], 'low'] = np.min(relevant_rows['price'])
            # close
            output.loc[output.index[i], 'close'] = relevant_rows['price'].iloc[-1]
        else:
            for col in output.keys():
                output.loc[output.index[i], str(col)] = np.nan

    return output
#%%test

account_balance=k.get_account_balance()
print(account_balance)

# s=k.get_order_book(XBTUSD,10)
df=k.get_ohlc_data('XBTUSD',1440)
df, last = k.get_recent_trades("XBTUSD", ascending=True)


data = pd.read_csv('/home/alex/Documents/skola/finproj/XBTUSD.csv')
data.head()

# Infinite loop for additiona!l OHLC data
# while True:
#     # Wait 60 seconds for new trades to happen
#     time.sleep(2)

#     # Get new trades data
#     data, last = k.get_recent_trades("XBTUSD", since=last, ascending=True)
#     # print(k.api_counter)
#     # Convert data to OHLC data, steps of 5 seconds
#     if not data.empty:
#         data = convert_to_ohlc(data, 2)
#         df = pd.concat([df, data])
#         print(data)

