#!/usr/bin/python
# -*- coding: utf-8 -*-

# performance.py

from __future__ import print_function

import numpy as np
import pandas as pd
import random
from mc_sim_fin.mc import mc_analysis


def create_sharpe_ratio(returns, periods=252):
    """
    Create the Sharpe ratio for the strategy, based on a 
    benchmark of zero (i.e. no risk-free rate information).

    Parameters:
    returns - A pandas Series representing period percentage returns.
    periods - Daily (252), Hourly (252*6.5), Minutely(252*6.5*60) etc.
    """

    return np.sqrt(periods) * (np.mean(returns)) / np.std(returns)



def monte_carlo():
    data = pd.io.parsers.read_csv(
        '/home/alex/Documents/skola/finproj/algo-project/backtest_result.csv', header=0, 
        parse_dates=True, index_col=0
    )
    profit_results = data['returns_pct']
    profit_results=profit_results[profit_results!=0]
    profit_results=profit_results.iloc[1:]
    date_results=profit_results.index.tolist()
    profit_results=profit_results.to_numpy()
    results = pd.DataFrame({'date_results': date_results, 'profit_results': profit_results})
    mc_sims_results = mc_analysis(results, start_equity=10000, ruin_equity=4000)
    return mc_sims_results


    
    
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
