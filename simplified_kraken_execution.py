import krakenex
from pykrakenapi import KrakenAPI
import pandas as pd
from datetime import datetime
import pytz
import time
import numpy as np
import matplotlib.pyplot as plt

with open('/home/alex/Documents/skola/finproj/key_live.txt') as f:
                key = f.read()
with open('/home/alex/Documents/skola/finproj/secret_live.txt') as f:
    secret = f.read()
api = krakenex.API(key.rstrip(), secret.rstrip())
c = KrakenAPI(api)

longwindow_N=100
shortwindow_N=20
status='OUT'
val=True # True makes trades _NOT_ go through
pair='XXBTZEUR'


while True:
    
    longwindow=c.get_ohlc_data(pair, interval=1440, since=None, ascending=False)[0].iloc[:longwindow_N]['close']
    shortwindow=longwindow[:20]
    
    if (np.mean(shortwindow)>np.mean(longwindow)) and (status=='OUT'):
        orderinfo=c.add_standard_order(pair,type='buy',ordertype='market',volume=0.0002,validate=val)
        orderID=orderinfo['txid']
        
    elif (np.mean(shortwindow)<np.mean(longwindow)) and (status=='IN'):
        c.add_standard_order(pair,'sell', 'market', volume=0.0002,validate=val)
        status='OUT'
    print(status)
    time.sleep(10*60)
    