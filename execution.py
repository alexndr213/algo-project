#!/usr/bin/python
# -*- coding: utf-8 -*-

# execution.py

from __future__ import print_function

from abc import ABCMeta, abstractmethod
import datetime
try:
    import Queue as queue
except ImportError:
    import queue

from event import FillEvent, OrderEvent
import time
import krakenex
from pykrakenapi import KrakenAPI



class ExecutionHandler(object):
    """
    The ExecutionHandler abstract class handles the interaction
    between a set of order objects generated by a Portfolio and
    the ultimate set of Fill objects that actually occur in the
    market. 

    The handlers can be used to subclass simulated brokerages
    or live brokerages, with identical interfaces. This allows
    strategies to be backtested in a very similar manner to the
    live trading engine.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def execute_order(self, event):
        """
        Takes an Order event and executes it, producing
        a Fill event that gets placed onto the Events queue.

        Parameters:
        event - Contains an Event object with order information.
        """
        raise NotImplementedError("Should implement execute_order()")


class SimulatedExecutionHandler(ExecutionHandler):
    """
    The simulated execution handler simply converts all order
    objects into their equivalent fill objects automatically
    without latency, slippage or fill-ratio issues.

    This allows a straightforward "first go" test of any strategy,
    before implementation with a more sophisticated execution
    handler.
    """
    
    def __init__(self, events):
        """
        Initialises the handler, setting the event queues
        up internally.

        Parameters:
        events - The Queue of Event objects.
        """
        self.events = events

    def execute_order(self, event):
        """
        Simply converts Order objects into Fill objects naively,
        i.e. without any latency, slippage or fill ratio problems.

        Parameters:
        event - Contains an Event object with order information.
        """
        if event.type == 'ORDER':
            fill_event = FillEvent(
                datetime.datetime.utcnow(), event.symbol,
                'test', event.quantity, event.direction, None
            )
            self.events.put(fill_event)
            

class KrakenExecutionHandler(ExecutionHandler):
    """ NEED MODIFICATIONS FOR KRAKEN API
    Handles order execution via Kraken
    API, for use against accounts when trading live
    directly. 
    """
    def __init__(
        self, events,  currency="ZEUR"
        ):
        """
        Initialises the IBExecutionHandler instance.
        """
        self.events = events
        self.currency = currency
        self.create_kraken_connection()
    
        # c.add_standard_order(pair,'sell', 'market', volume=0.0002,validate=val)
    
    def create_kraken_connection(self):
        """
        Connect to the Trader Workstation (TWS) running on the
        usual port of 7496, with a clientId of 10.
        The clientId is chosen by us and we will need
        separate IDs for both the execution connection and
        market data connection, if the latter is used elsewhere.
        """
        with open('/home/alex/Documents/skola/finproj/key.txt') as f:
            key = f.read()
        with open('/home/alex/Documents/skola/finproj/secret.txt') as f:
            secret = f.read()
        
        api = krakenex.API(key.rstrip(), secret.rstrip())
        kraken_conn = KrakenAPI(api)
        return kraken_conn

    
    
    def create_fill(self, msg):
        """
        Handles the creation of the FillEvent that will be
        placed onto the events queue subsequent to an order
        being filled.
        """
        fd = self.fill_dict[msg.orderId]
        # Prepare the fill data
        symbol = fd["symbol"]
        exchange = fd["exchange"]
        filled = msg.filled
        direction = fd["direction"]
        fill_cost = msg.avgFillPrice
        # Create a fill event object
        fill_event = FillEvent(
        datetime.datetime.utcnow(), symbol,
        exchange, filled, direction, fill_cost
        )
        # Make sure that multiple messages don't create
        # additional fills. 
        self.fill_dict[msg.orderId]["filled"] = True
        # Place the fill event onto the event queue
        self.events.put(fill_event)
        
        
    def execute_order(self, event):
        """
        Creates the necessary InteractiveBrokers order object
        and submits it to IB via their API.
        The results are then queried in order to generate a
        corresponding Fill object, which is placed back on
        the event queue.
        Parameters:
        event - Contains an Event object with order information.
        """
        
        # OrderEvent(symbol, order_type, abs(cur_quantity), 'BUY')
        if event.type == 'ORDER':
            # Prepare the parameters for the asset order
            asset = event.symbol
            order_type = event.order_type
            quantity = event.quantity
            direction = event.direction
            
            orderinfo=self.connection.add_standard_order(asset,ordertype=order_type,type=direction,volume=quantity)
            # orderinfo=c.add_standard_order(pair,type='sell',ordertype='market',volume=0.0002,validate=val)
            orderdescription=orderinfo['descr']['order']
            try:
                orderID=orderinfo['txid']
                fill_event = FillEvent(
                datetime.datetime.utcnow(), asset,
                'kraken', orderID, direction, None
                )
                FillEvent()
            except ValueError:
                print('order did not go through, check order validate set to FALSE, creating placeholder FIll object')
            fill_event = FillEvent(
            datetime.datetime.utcnow(), asset,
            exchange='test', filled, direction, fill_cost
            )
            
            self, timeindex, symbol, exchange, quantity, 
                 direction, fill_cost, commission=None):
    
            self.events.put(fill_event)