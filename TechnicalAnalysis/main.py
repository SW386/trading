#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan  9 17:44:14 2021

@author: Shufan
"""

import pandas as pd
import yfinance as yf
import time
from datetime import datetime, timedelta
from technical import sentiment, support_and_resistance

def analyze_nasdaq(start, end, sentiment_days=365, difference=0.05, threshold=0.01):
    
    filepath = "../Utilities/nasdaqlisted.txt"
    nasdaq = pd.read_csv(filepath, sep="|")
    symbols = nasdaq["Symbol"]
    
    analyzed_symbols = []
    supports = []
    resistances = []
    prices = []
    positive_sentiments = []
    neutral_sentiments = []
    negative_sentiments = []
    percent_profits = []
    
    for index, symbol in enumerate(symbols):
        
        #Sleep so we dont timeout yfinance API
        if index+1 % 1600 == 0:
            time.sleep(3600)
            
        ticker = yf.Ticker(symbol)
        prev = datetime.today()-timedelta(sentiment_days)
        #Analyze an ticker if analysts have an opinion
        if ticker.recommendations and ticker.recommendations[prev:]:
            
            recommendations = ticker.recommendations["To Grade"]
            analyst_sentiment = sentiment(recommendations)
            
            if analyst_sentiment["Buy"] > analyst_sentiment["Sell"]:
                
                technicals = support_and_resistance(ticker, start, end)
                resistance = technicals["Resistance"]
                support = technicals["Support"]
                price = ticker.history().tail(1)["Close"].iloc[0]
                percent_profit = abs(resistance-price)/price
                
                sufficient_diff = abs(resistance-support)/price > difference
                within_threshold = abs(price-support)/price < threshold
                            
                if sufficient_diff and within_threshold:
                    
                    analyzed_symbols.append(symbol)
                    supports.append(support)
                    resistances.append(resistance)
                    prices.append(price)
                    percent_profits.append(percent_profit)
                    positive_sentiments.append(analyst_sentiment["Buy"])
                    neutral_sentiments.append(analyst_sentiment["Hold"])
                    negative_sentiments.append(analyst_sentiment["Sell"])
        
    data = {"Ticker" : analyzed_symbols,
            "Price" : prices,
            "Support" : supports,
            "Resistance" : resistances,
            "Profit" : percent_profits,
            "Buy" : positive_sentiments,
            "Hold" : neutral_sentiments,
            "Sell" : negative_sentiments}
    
    dataframe = pd.DataFrame(data)
    return dataframe    
    

if __name__ == "__main__":
    dataframe = analyze_nasdaq()
    dataframe.to_csv("Momentum.csv")
    

