#!/usr/bin/python
# -*- coding: utf-8 -*-

# data.py

from __future__ import print_function

from abc import ABCMeta, abstractmethod
import datetime
import os, os.path
import time
import numpy as np
import pandas as pd
try:
    import Queue as queue
except ImportError:
    import queue

from event import MarketEvent
import krakenex
from pykrakenapi import KrakenAPI

class DataHandler(object):
    """
    DataHandler is an abstract base class providing an interface for
    all subsequent (inherited) data handlers (both live and historic).

    The goal of a (derived) DataHandler object is to output a generated
    set of bars (OHLCVI) for each symbol requested. 

    This will replicate how a live strategy would function as current
    market data would be sent "down the pipe". Thus a historic and live
    system will be treated identically by the rest of the backtesting suite.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_latest_bar(self, symbol):
        """
        Returns the last bar updated.
        """
        raise NotImplementedError("Should implement get_latest_bar()")

    @abstractmethod
    def get_latest_bars(self, symbol, N=1):
        """
        Returns the last N bars updated.
        """
        raise NotImplementedError("Should implement get_latest_bars()")

    @abstractmethod
    def get_latest_bar_datetime(self, symbol):
        """
        Returns a Python datetime object for the last bar.
        """
        raise NotImplementedError("Should implement get_latest_bar_datetime()")

    @abstractmethod
    def get_latest_bar_value(self, symbol, val_type):
        """
        Returns one of the Open, High, Low, Close, Volume or OI
        from the last bar.
        """
        raise NotImplementedError("Should implement get_latest_bar_value()")

    @abstractmethod
    def get_latest_bars_values(self, symbol, val_type, N=1):
        """
        Returns the last N bar values from the 
        latest_symbol list, or N-k if less available.
        """
        raise NotImplementedError("Should implement get_latest_bars_values()")

    @abstractmethod
    def update_bars(self):
        """
        Pushes the latest bars to the bars_queue for each symbol
        in a tuple OHLCVI format: (datetime, open, high, low, 
        close, volume, open interest).
        """
        raise NotImplementedError("Should implement update_bars()")


class HistoricCSVDataHandler(DataHandler):
    """
    HistoricCSVDataHandler is designed to read CSV files for
    each requested symbol from disk and provide an interface
    to obtain the "latest" bar in a manner identical to a live
    trading interface. 
    """

    def __init__(self, events, csv_dir, symbol_list):
        """
        Initialises the historic data handler by requesting
        the location of the CSV files and a list of symbols.

        It will be assumed that all files are of the form
        'symbol.csv', where symbol is a string in the list.

        Parameters:
        events - The Event Queue.
        csv_dir - Absolute directory path to the CSV files.
        symbol_list - A list of symbol strings.
        """
        self.events = events
        self.csv_dir = csv_dir
        self.symbol_list = symbol_list

        self.symbol_data = {}
        self.latest_symbol_data = {}
        self.continue_backtest = True       
        self.bar_index = 0

        self._open_convert_csv_files()

    def _open_convert_csv_files(self):
        """
        Opens the CSV files from the data directory, converting
        them into pandas DataFrames within a symbol dictionary.

        For this handler it will be assumed that the data is
        taken from AlphaVantage. Thus its format will be respected.
        """
        comb_index = None
        for s in self.symbol_list:
            #loads data into temp to check format
           temp=pd.io.parsers.read_csv(
                    os.path.join(self.csv_dir, '%s.csv' % s))
           
           #checks if content is alphavantage format
           try:
               columncheck=temp.columns==['date', '1. open', '2. high', '3. low', '4. close', '5. volume']
               if columncheck.all():
                   # Load the CSV file with no header information, indexed on date for alphavantage
                   self.symbol_data[s] = pd.io.parsers.read_csv(
                   os.path.join(self.csv_dir, '%s.csv' % s),
                   header=0, index_col=0, parse_dates=True,
                   names=[
                   'datetime', 'open', 'high', 
                   'low', 'close', 'volume'
                   ]
                   ).sort_values(by='datetime', ascending = True)
           except:
               print('not AV format')
          
             #checks if content is yhoo format
           try:
               columncheck=temp.columns==['Date', 'Open', 'High', 'Low', 'Close','Adj Close', 'Volume']
               if columncheck.all():
                   # Load the CSV file with no header information, indexed on date for alphavantage
                   self.symbol_data[s] = pd.io.parsers.read_csv(
                   os.path.join(self.csv_dir, '%s.csv' % s),
                   header=0, index_col=0, parse_dates=True,
                   names=[
                   'datetime', 'open', 'high', 
                   'low', 'close','adj close', 'volume'
                   ]
                   ).sort_values(by='datetime', ascending = True)
           except:
               print('not yahoo format')  
          
            # kraken format
           try:
                #tries to convert first from unix to datetime if error, is not kraken format
                pd.to_datetime(temp.columns[0],unit='s')
                #imports data
                self.symbol_data[s] = pd.io.parsers.read_csv(
                os.path.join(self.csv_dir, '%s.csv' % s), parse_dates=True,
                names=[
                'datetime', 'open', 'high', 
                'low', 'close', 'volume','trades'
                ],header=0,index_col=0)
                self.symbol_data[s].index=pd.to_datetime(self.symbol_data[s].index,unit='s')
                print(self.symbol_data[s])
           except ValueError:
                print('not kraken format')
               
                
                    
            # Combine the index to pad forward values
           if comb_index is None:
                comb_index = self.symbol_data[s].index
           else:
                comb_index.union(self.symbol_data[s].index)
                # Set the latest symbol_data to None
           self.latest_symbol_data[s] = []
    
        for s in self.symbol_list:
             self.symbol_data[s] = self.symbol_data[s].reindex(
                 index=comb_index, method='pad'
             )
             self.symbol_data[s]["returns"] = self.symbol_data[s]["close"].pct_change()
             print(self.symbol_data[s])
             self.symbol_data[s] = self.symbol_data[s].iterrows()
        # print(self.symbol_data[s])



    def _get_new_bar(self, symbol):
        """
        Returns the latest bar from the data feed.
        """
        for b in self.symbol_data[symbol]:
            # print(b)
            yield b

    def get_latest_bar(self, symbol):
        """
        Returns the last bar from the latest_symbol list. används inte?
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return bars_list[-1]

    def get_latest_bars(self, symbol, N=1):
        """
        Returns the last N bars from the latest_symbol list,
        or N-k if less available.
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return bars_list[-N:]

    def get_latest_bar_datetime(self, symbol):
        """
        Returns a Python datetime object for the last bar.
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            
            # print(bars_list[-1][0],type(bars_list[-1][0]))
            return bars_list[-1][0]

    def get_latest_bar_value(self, symbol, val_type):
        """
        Returns one of the Open, High, Low, Close, Volume or OI
        values from the pandas Bar series object.
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            # s=getattr(bars_list[-1][1], val_type)
            # print(s)
            return getattr(bars_list[-1][1], val_type)

    def get_latest_bars_values(self, symbol, val_type, N=1):
        """
        Returns the last N bar values from the 
        latest_symbol list, or N-k if less available.
        """
        try:
            bars_list = self.get_latest_bars(symbol, N)
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            
            return np.array([getattr(b[1], val_type) for b in bars_list])

    def update_bars(self):
        """
        Pushes the latest bar to the latest_symbol_data structure
        for all symbols in the symbol list.
        """
        for s in self.symbol_list:
            try:
                bar = next(self._get_new_bar(s))
            except StopIteration:
                self.continue_backtest = False
            else:
                if bar is not None:
                    # print(self.latest_symbol_data[s])
                    self.latest_symbol_data[s].append(bar)
        self.events.put(MarketEvent())

class LiveKrakenDataHandler(DataHandler):
    
   
    
    def __init__(self, events, symbol_list,ohlc_time):
            """    
            Parameters:
            events - The Event Queue.
            
            symbol_list - A list of symbol strings.
            
            
            """
            with open('/home/alex/Documents/skola/finproj/key.txt') as f:
               key = f.read()
            with open('/home/alex/Documents/skola/finproj/secret.txt') as f:
                secret = f.read()
            
            api = krakenex.API(key.rstrip(), secret.rstrip())
            self.connection = KrakenAPI(api)
            
            self.events = events
            self.symbol_list = symbol_list
            self.symbol_data = {}
            self.latest_symbol_data = {}     
            self.bar_index = 0
            self.ohlc_time=ohlc_time
            self.last=0 #unixtime of last data pull
            
            
       
    def load_symbol_data_from_kraken(self,symbol_list):
        
        comb_index=None
        for s in self.symbol_list:
            self.symbol_data[s],self.last=self.connection.get_ohlc_data(s, interval=self.ohlc_time, since=None, ascending=True)
            if len(self.symbol_list)>0:
                time.sleep(2)
        
        if comb_index is None:
                comb_index = self.symbol_data[s].index
        else:
                comb_index.union(self.symbol_data[s].index)
                # Set the latest symbol_data to None
                self.latest_symbol_data[s] = []
    
        for s in self.symbol_list:
             self.symbol_data[s] = self.symbol_data[s].reindex(
                 index=comb_index, method='pad'
             )
        
       
    def get_latest_bars(self, symbol, N=1):
        """
        Returns the last N bars from the latest_symbol list,
        or N-k if less available.
        """
        # print(symbol)
        try:
            bars_list = self.symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return bars_list[-N:]

    def get_latest_bar_datetime(self, symbol):
        """
        Returns a Python datetime object for the last bar.
        """
        try:
            bars_list = self.symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return max(bars_list.index)


    def get_latest_bars_values(self, symbol, val_type, N=1):
        """
        Returns the last N bar values from the 
        latest_symbol list, or N-k if less available.
        """

        try:
            bars_list = self.get_latest_bars(symbol, N)
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            bars_val_type=np.array(bars_list[val_type])
            return bars_val_type 

    def update_bars(self):
        """
        Pushes the latest bar to the latest_symbol_data structure
        for all symbols in the symbol list.
        """
        for s in self.symbol_list:
            bar,last=self.connection.get_ohlc_data(s, interval=self.ohlc_time, since=self.last, ascending=True)
            # print(s)
            
            if (bar.iloc[0]['time']>self.symbol_data[s].iloc[0]['time']):
                self.symbol_data[s].append(bar)
                self.symbol_data[s]=self.symbol_data[s][:-1]
                self.last=last
                self.events.put(MarketEvent())
            
# %%% test
if __name__ == '__main__':
    events = queue.Queue()
    symbol_list = ['XXBTZEUR']
    ohlc_time=1
    s=LiveKrakenDataHandler.load_symbol_data_from_kraken

