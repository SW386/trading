# -*- coding: utf-8 -*-
"""
Created on Sat Jan  2 15:36:55 2021

@author: Shufan Wen
"""

import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import json
import sys
from datetime import datetime
from collections import defaultdict
from tqdm import tqdm


with open("config.json") as f:
    data = json.loads(f.read())
f.close()

#Extract Config Data
tickers = data["tickers"]
capital = data["capital"]
start_date = data["start"]
end_date = data["end"]
simulations = data["simulations"]
intervals = data["intervals"]

#Convert Date Strings to Datetime Objects
start_datetime = datetime.strptime(start_date, '%m-%d-%Y')
end_datetime = datetime.strptime(end_date, '%m-%d-%Y')

#Download and use Adjusted Close Data
print("Gathering Stocks:")
stock_data = yf.download(tickers, start=start_datetime, end=end_datetime)
stock_data = stock_data.dropna()["Adj Close"]
print("\n")

#Calculate Returns
daily_returns = stock_data.pct_change()
annual_returns = daily_returns.mean()*250

#Calculate Variance
daily_covariance = daily_returns.cov()
annual_covariance = daily_covariance*250

#Simulate Weights
returns = []
volatility = []
weights = []
ratios = []
assets = len(tickers)


for simulation in tqdm(range(simulations), file=sys.stdout, desc='Simulating Portfolios'):
    #Calculate weights, returns, volatility, and sharpe ratio
    rand_weights = np.random.random(assets)
    rand_weights /= np.sum(rand_weights)
    sim_returns = np.dot(rand_weights, annual_returns)
    sim_volatility = np.sqrt(np.dot(rand_weights.T, np.dot(annual_covariance, rand_weights)))
    sharpe_ratio = sim_returns/sim_volatility
    #Add weights, returns, and volatility to list
    returns.append(sim_returns)
    volatility.append(sim_volatility)
    weights.append(rand_weights)
    ratios.append(sharpe_ratio)
print("\n")

portfolio = defaultdict(list)
portfolio["Returns"] = returns
portfolio["Volatility"] = volatility
portfolio["Sharpe Ratio"] = ratios
#Create sections for each ticker
for weight_set in weights:
    for index, weight in enumerate(weight_set):
        #Get corresponding ticker name and add weight
        ticker = tickers[index]
        portfolio[ticker].append(weight)
portfolio = pd.DataFrame(portfolio)

#Calculate the Frontier, Max Returns at Each Risk Level
min_volatility = portfolio["Volatility"].min()
max_volatility = portfolio["Volatility"].max()
step = (max_volatility - min_volatility)/intervals
bucket_index = [-1]*(intervals)
bucket_values = [-2**32]*(intervals)


for index, row in tqdm(portfolio.iterrows(), file=sys.stdout, desc='Calculating Optimal Portfolio'):
    
    returns = row["Returns"]
    volatility = row["Volatility"]
    
    pos = int((volatility-min_volatility) / step)
    if pos >= intervals:
        pos = intervals-1
    if returns > bucket_values[pos]:
        bucket_values[pos] = returns
        bucket_index[pos] = index

print("\n")
        
if -1 in bucket_index:
    bucket_index.remove(-1)
    
frontier = portfolio.iloc[bucket_index,:]
frontier.to_csv("Frontier Portfolios")

plt.scatter(portfolio["Volatility"], portfolio["Returns"], c=portfolio["Sharpe Ratio"], cmap='viridis')
plt.colorbar(label='Sharpe Ratio')
plt.xlabel('Volatility')
plt.ylabel('Return')
plt.title("Efficient Frontier")
plt.show()

print("The Following Portfolio Had The Maximum Sharpe Ratio: ")
print(portfolio[portfolio["Sharpe Ratio"] == portfolio["Sharpe Ratio"].max()])







    
    
