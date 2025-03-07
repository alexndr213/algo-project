#!/usr/bin/python
# -*- coding: utf-8 -*-

# mac.py

from __future__ import print_function
import scipy.optimize

import datetime
from scipy.optimize import brute
import scipy.optimize as opt
import itertools
import numpy as np
import pandas as pd
# import statsmodels.api as sm

from strategy import Strategy
from event import SignalEvent
from backtest import Backtest
from data import HistoricCSVDataHandler
from execution import SimulatedExecutionHandler
from portfolio import Portfolio


class MovingAverageCrossStrategy(Strategy):
    """
    Carries out a basic Moving Average Crossover strategy with a
    short/long simple weighted moving average. Default short/long
    windows are 100/400 periods respectively.
    """

    def __init__(
        self, bars, events, short_window, long_window
    ):
        """
        Initialises the Moving Average Cross Strategy.

        Parameters:
        bars - The DataHandler object that provides bar information
        events - The Event Queue object.
        short_window - The short moving average lookback.
        long_window - The long moving average lookback.
        """
        self.bars = bars
        self.symbol_list = self.bars.symbol_list
        self.events = events
        self.short_window = short_window
        self.long_window = long_window

        # Set to True if a symbol is in the market
        self.bought = self._calculate_initial_bought()

    def _calculate_initial_bought(self):
        """
        Adds keys to the bought dictionary for all symbols
        and sets them to 'OUT'.
        """
        bought = {}
        for s in self.symbol_list:
            bought[s] = 'OUT'
        return bought

    def calculate_signals(self, event):
        """
        Generates a new set of signals based on the MAC
        SMA with the short window crossing the long window
        meaning a long entry and vice versa for a short entry.    

        Parameters
        event - A MarketEvent object. 
        """
        if event.type == 'MARKET':
            for s in self.symbol_list:
                bars = self.bars.get_latest_bars_values(
                    s, "close", N=self.long_window
                )
                bar_date = self.bars.get_latest_bar_datetime(s)
                if bars is not None:
                    # and bars != []:
                    short_sma = np.mean(bars[-self.short_window:])
                    long_sma = np.mean(bars[-self.long_window:])

                    symbol = s
                    dt = datetime.datetime.utcnow()
                    sig_dir = ""

                    if short_sma > long_sma and self.bought[s] == "OUT":
                        # print("LONG: %s" % bar_date)
                        sig_dir = 'LONG'
                        signal = SignalEvent(1, symbol, dt, sig_dir, 1.0)
                        self.events.put(signal)
                        self.bought[s] = 'LONG'
                    elif short_sma < long_sma and self.bought[s] == "LONG":
                        # print("SHORT: %s" % bar_date)
                        sig_dir = 'EXIT'
                        signal = SignalEvent(1, symbol, dt, sig_dir, 1.0)
                        self.events.put(signal)
                        self.bought[s] = 'OUT'


if __name__ == "__main__":
    def f(x):
       
        shortwindow=round(x[0])
        longwindow=round(x[1])
        if shortwindow>=longwindow:
            return 1
        csv_dir = '~/Documents/skola/finproj/algo-project/optimizationcode/'  # CHANGE THIS!
        symbol_list = ['GOOG']
        initial_capital = 100000.0
        heartbeat = 0.0
        start_date = datetime.datetime(1990, 1, 1, 0, 0, 0)
    
        backtest = Backtest(
            csv_dir, symbol_list, initial_capital, heartbeat, 
            start_date, HistoricCSVDataHandler, SimulatedExecutionHandler, 
            Portfolio, MovingAverageCrossStrategy,shortwindow,longwindow
        )
        backtest.simulate_trading() 
        return -backtest._output_performance()
        
    res=opt.fmin(f,[310,385],maxiter=10,full_output=True)
    # ranges = (slice(10, 400, 1),)*2  
    # 380,395 maxima for google
    # 310,385 max för btc usd
    
    # result = brute(f, ranges, disp=True, finish=None)
    # print(result)