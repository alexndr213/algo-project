#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 26 11:25:03 2021

@author: alex
"""
import krakenex
from pykrakenapi import KrakenAPI

# krakenconnection
def return_kraken_connection():
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