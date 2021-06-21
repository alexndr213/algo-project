#!/usr/bin/python
# -*- coding: utf-8 -*-

# performance.py

from __future__ import print_function

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from data import HistoricCSVDataHandler


def monte_carlo(sims=100,ruin_pct=0.6):
    data = pd.io.parsers.read_csv(
       '~/Documents/skola/finproj/algo-project/optimizationcode/equity.csv', header=0, 
       parse_dates=True, index_col=0
    )
    profit_results = data['returns']
    profit_results=profit_results[profit_results!=0]
    profit_results=profit_results.iloc[1:]
    ruins=0
    pricewalk=[]
    temp=[]
    drawdown_list=[]
    max_dd_list=[]
    dd_duration_list=[]
    for i in range (0,sims):
        temp=[1]
        temp.extend(profit_results.sample(n=len(profit_results),axis=0,replace=False).tolist())
        temp=np.cumsum(temp)
        pricewalk.append(temp)
        pdtemp=pd.Series(
            temp[1:],index=profit_results.index,
            ).sort_index(ascending=True)
        dd, mdd, dd_d=create_drawdowns(pdtemp)
        drawdown_list.append(dd)
        if mdd>1-ruin_pct:
            ruins+=1
        max_dd_list.append(mdd)
        # dd_duration_list.append(dd_d)
    print('risk of ruin=',ruins/sims,
          '\nmedian of max drawdown=', np.median(max_dd_list),
          '\nmedian return=',np.median(profit_results),
          '\nmedian return/max drawdown=',np.median(profit_results)/np.median(max_dd_list))
    for i in range(0,sims):
        plt.plot(pricewalk[i],lw=.5,color='k')
    
    plt.plot(np.cumsum(profit_results.tolist())+1,lw=2,color='b')
    plt.xlabel('Trade #')
    plt.ylabel('Percentage return')
    plt.show()   

def buy_N_hold():
    data = pd.io.parsers.read_csv(
       '/home/alex/Documents/skola/finproj/algo-project/equity.csv', header=0, 
       parse_dates=True, index_col=0
    )
    name=data.columns[0]
    temp=data[name]
    temp=temp[temp!=0]
    percentage_return=temp.iloc[-1]/temp.iloc[0]
    
    return percentage_return

def create_sharpe_ratio(returns, periods=252):
    """
    Create the Sharpe ratio for the strategy, based on a 
    benchmark of zero (i.e. no risk-free rate information).

    Parameters:
    returns - A pandas Series representing period percentage returns.
    periods - Daily (252), Hourly (252*6.5), Minutely(252*6.5*60) etc.
    """
    return np.sqrt(periods) * (np.mean(returns)) / np.std(returns)


def create_drawdowns(pnl):
    """
    Calculate the largest peak-to-trough drawdown of the PnL curve
    as well as the duration of the drawdown. Requires that the 
    pnl_returns is a pandas Series.

    Parameters:
    pnl - A pandas Series representing period percentage returns.

    Returns:
    drawdown, duration - Highest peak-to-trough drawdown and duration.
    """

    # Calculate the cumulative returns curve 
    # and set up the High Water Mark
    hwm = [0]

    # Create the drawdown and duration series
    idx = pnl.index
    drawdown = pd.Series(index = idx)
    duration = pd.Series(index = idx)

    # Loop over the index range
    for t in range(1, len(idx)):
        hwm.append(max(hwm[t-1], pnl[t]))
        drawdown[t]= (hwm[t]-pnl[t])
        duration[t]= (0 if drawdown[t] == 0 else duration[t-1]+1)
    return drawdown, drawdown.max(), duration.max()
