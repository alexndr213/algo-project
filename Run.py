#!/usr/bin/python
# -*- coding: utf-8 -*-

# backtest.py

from __future__ import print_function

from datetime import datetime
import pprint
try:
    import Queue as queue
except ImportError:
    import queue
import time
import signal

from kraken_connection import return_kraken_connection


from strategy import Strategy
from Event import SignalEvent
from data import LiveKrakenDataHandler
from execution import KrakenExecutionHandler
from portfolio import Portfolio
from mac import MovingAverageCrossStrategy

class Run(object):
    """
    Enscapsulates the settings and components for carrying out
    an event-driven backtest.
    """

    def __init__(
        self, symbol_list, initial_capital,ohlc_time,val,
        heartbeat, start_date, data_handler, 
        execution_handler, portfolio, strategy,connection
    ):
        """
        Initialises the backtest.

        Parameters:
        symbol_list - The list of symbol strings.
        intial_capital - The starting capital for the portfolio.
        heartbeat - Backtest "heartbeat" in seconds
        start_date - The start datetime of the strategy.
        data_handler - (Class) Handles the market data feed.
        execution_handler - (Class) Handles the orders/fills for trades.
        portfolio - (Class) Keeps track of portfolio current and prior positions.
        strategy - (Class) Generates signals based on market data.
        """
        self.connection=connection
        self.val=val
        self.ohlc_time= ohlc_time
        self.symbol_list = symbol_list
        self.initial_capital = initial_capital
        self.heartbeat = heartbeat
        self.start_date = start_date

        self.data_handler_cls = data_handler
        self.execution_handler_cls = execution_handler
        self.portfolio_cls = portfolio
        self.strategy_cls = strategy

        self.events = queue.Queue()
        
        self.signals = 0
        self.orders = 0
        self.fills = 0
        self.num_strats = 1
       
        self._generate_trading_instances()

    def _generate_trading_instances(self):
        """
        Generates the trading instance objects from 
        their class types.
        """
        print(
            "Creating DataHandler, Strategy, Portfolio and ExecutionHandler"
        )
        self.data_handler = self.data_handler_cls(self.events,self.symbol_list,self.ohlc_time)
        self.strategy = self.strategy_cls(self.data_handler, self.events)
        self.portfolio = self.portfolio_cls(self.data_handler, self.events, self.start_date, 
                                            self.initial_capital)
        self.execution_handler = self.execution_handler_cls(self.events,self.connection)

    def _run_(self):
        """
        Executes the backtest.
        """
        self.data_handler.load_symbol_data_from_kraken(self.symbol_list)
        # print(self.symbol_list)
        i = 0
        while True:
            i += 1
            print('loop index',i)
            # Update the market bars
       
            self.data_handler.update_bars()
         

            # Handle the events
            while True:
                try:
                    event = self.events.get(False)
                except queue.Empty:
                    break
                else: 
                    if event is not None:
                        if event.type == 'MARKET':
                            self.strategy.calculate_signals(event)
                            self.portfolio.update_timeindex(event)
                          
                        elif event.type == 'SIGNAL':
                            self.signals += 1                            
                            self.portfolio.update_signal(event)
                            
                        elif event.type == 'ORDER':
                            self.orders += 1
                            self.execution_handler.execute_order(event,val)
                            
                        elif event.type == 'FILL':
                            self.fills += 1
                            self.portfolio.update_fill(event)
                            
            time.sleep(self.heartbeat)

    def _output_performance(self):
        """
        Outputs the strategy performance from the trading.
        """
        self.portfolio.create_equity_curve_dataframe()
        
        print("Creating summary stats...")
        stats = self.portfolio.output_summary_stats()
        
        print("Creating equity curve...")
        print(self.portfolio.equity_curve.tail(10))
        pprint.pprint(stats)

        print("Signals: %s" % self.signals)
        print("Orders: %s" % self.orders)
        print("Fills: %s" % self.fills)

    def trade(self):
        """
        Simulates the backtest and outputs portfolio performance.
        """
        try:
            self._run_()
        except KeyboardInterrupt:
            self._output_performance()


#%% run 
if __name__ == "__main__":
    symbol_list = ['XXBTZEUR']
    initial_capital = 2000.0
    heartbeat = 60
    start_date = datetime.now()
    val=True #Setting this to FALSE will enable live trading
    ohlc_time=1 #ohlc bar time, 1minute bars etc, can only be 1,5,15,30,60,240,1440,10080,21600
    connection=return_kraken_connection()
    run = Run(
        symbol_list, initial_capital,ohlc_time,val,heartbeat,
        start_date, LiveKrakenDataHandler, KrakenExecutionHandler, 
        Portfolio, MovingAverageCrossStrategy,connection
    )
    run.trade()