#!/usr/bin/python
# -*- coding: utf-8 -*-

# plot_performance.py

import os.path

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from mc_sim_fin.mc import mc_analysis
from performance import monte_carlo,buy_N_hold

if __name__ == "__main__":
    data = pd.io.parsers.read_csv(
        "equity.csv", header=0, 
        parse_dates=True, index_col=0
    ).sort_values(by='datetime')
    data=data[:-1]
    data.index=pd.to_datetime(data.index,unit='s')
    # Plot three charts: Equity curve, 
    # period returns, drawdowns
    fig = plt.figure()
    # Set the outer colour to white
    fig.patch.set_facecolor('white')     
    fig.set_size_inches(10.5, 10.5)
    # Plot the equity curve
    ax1 = fig.add_subplot(311, ylabel='Portfolio value, %')
    data['equity_curve'].plot(ax=ax1, color="blue", lw=2.)
    plt.grid(True)

    # Plot the returns
    ax2 = fig.add_subplot(312, ylabel='Period returns, %')
    data['returns'].plot(ax=ax2, color="black", lw=2.)
    plt.grid(True)

    # Plot the returns
    ax3 = fig.add_subplot(313, ylabel='Drawdowns, %')
    data['drawdown'].plot(ax=ax3, color="red", lw=2.)
    plt.grid(True)

    # Plot the figure
    plt.show()

    print("returns of buy and hold from date of first trade to last trade=",buy_N_hold()*100,"%")
    print(monte_carlo())