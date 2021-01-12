#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan  9 17:44:14 2021

@author: Shufan
"""

import yfinance as yf
from datetime import datetime, timedelta
from sklearn.cluster import KMeans

BUY = set(["buy", "overweight", "outperform", "overperform", "overperformer", "accumulate", "add", "positive"])
HOLD = set(["hold", "equal-weight", "perform", "neutral", "in-line", "sector", "market", "mixed", "average", "fair"])
SELL = set(["sell", "underweight", "underperform", "underperformer", "reduce", "negative", "below"])


def sentiment(recommendations):
    """Function for Analyzing Firm Sentiment
    
    Parameters
    ----------
    recommendations : List of Strings
        List of commonly used phrases for stock sentiment

    Returns
    -------
    data : Dictionary
        Maps sentiment (Buy, Hold, Sell, Unknown) to number of analysts suggesting

    """
    buy_rec = 0
    hold_rec = 0
    sell_rec = 0
    unknown = 0
    
    for recommendation in recommendations:
        
        data = recommendation.lower().split(" ")
        currbuy = 0
        currhold = 0
        currsell = 0
        
        if BUY.intersection(data):
            currbuy += 1
        if HOLD.intersection(data):
            currhold += 1
        if SELL.intersection(data):
            currsell += 1
            
        if currbuy + currsell + currhold < 1:
            #If the analyst sentiment is not in the 3 categories
            print(recommendation)
            unknown += 1
        elif currbuy + currsell + currhold > 1:
            #In the case of market underperform or sector overweight etc 
            #We wish to take only the positive or negative sentiment
            buy_rec += currbuy
            sell_rec += currsell
        else:
            buy_rec += currbuy
            hold_rec += currhold
            sell_rec += currsell
    
    data = {"Buy": buy_rec,
            "Hold": hold_rec, 
            "Sell": sell_rec,
            "Unknown": unknown}
    
    return data

def support_and_resistance(ticker, start, end, interval="1h"):
    """ Calculate Mean Resistance and Support as well as Max and Min Price
    
    Parameters
    ----------
    ticker : Ticker
        yfinance Ticker Object
    start : Datetime
        Start Date
    end : Datetime
        End Date
    interval : String, optional
        yfinance code for intervals. Defaults to 1 hour
        

    Returns
    -------
    data : Dictionary
        Fields are Maximum, Minimum, Support, and Resistance

    """
    
    print(ticker)
    
    data = ticker.history(interval = interval, start = start, end = end)
    supports = kmeans_clustering(data["Low"])
    resistances = kmeans_clustering(data["High"])
    
    
    maximum = max(data["High"])
    minimum = min(data["Low"])
    resistance = max(resistances)
    support = min(supports)
    
    data = {"Maximum": maximum, 
            "Minimum": minimum, 
            "Support": support, 
            "Resistance": resistance}
    
    return data

def kmeans_clustering(data, saturation=0.05):
    """Finds Optimal Cluster Centers for 1D Series
    

    Parameters
    ----------
    data : Series
        Either High or Low prices
        
    saturation : Integer, optional
        Value to accept change in inertia The default is 0.5.

    Returns
    -------
    list
        List of clusters centers indicative of support or resistance

    """
    
    data = data.to_numpy().reshape(-1, 1)
    inertias = []
    cluster_centers = []
    
    for i in range(1, 10):
        model = KMeans(n_clusters = i)
        model.fit(data)
        inertias.append(model.inertia_)
        cluster_centers.append(model.cluster_centers_)

    for i in range(8):
        if abs(inertias[i+1] - inertias[i])/inertias[0] < saturation:
            return cluster_centers[i]
    
    return cluster_centers[-1]
        



