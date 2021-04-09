#!/usr/bin/python
# -*- coding: utf-8 -*-

# plot_performance.py

import os.path
import random
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pandas import DataFrame
from mc_sim_fin.mc import mc_analysis
from performance import monte_carlo


if __name__ == "__main__":
    data = pd.io.parsers.read_csv(
        '/home/alex/Documents/skola/finproj/algo-project/backtest_result.csv', header=0, 
        parse_dates=True, index_col=0
    )
    
    data['equity_curve_pct'].plot(ylabel='portfolio value %',color="blue", lw=1.)
    plt.grid(True)
    plt.show()
    
    data['returns_pct'].plot(ylabel='period returns %', color="black", lw=1.)
    plt.grid(True)
    plt.show()
    
    data['drawdown_pct'].plot(ylabel='drawdown %', color="green", lw=1.)
    plt.grid(True)
    plt.show()

    print(monte_carlo())