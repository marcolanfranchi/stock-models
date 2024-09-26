# libraries
import yfinance as yf
import pandas as pd
import sys

def check_ticker(ticker):
    stock = yf.Ticker(ticker)
    # get stock METADATA
    stock_history = stock.history(period='1d')
    stock_metadata = stock.history_metadata
    # print metadata line by line
    for key, value in stock_metadata.items():
        print(key, ":", value)
    
if __name__ == "__main__":
    if sys.argv[1] == None:
        print("Please enter a stock ticker symbol.")
        exit()
    stock = sys.argv[1]
    check_ticker(stock)
