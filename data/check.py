# libraries
import yfinance as yf
import pandas as pd
import sys
import os

def check_ticker(ticker):
    stock = yf.Ticker(ticker)
    # get stock METADATA
    stock_history = stock.history(period='1d')
    stock_metadata = stock.history_metadata
    # print metadata line by line
    for key, value in stock_metadata.items():
        print(key, ":", value)

def add_stock_to_csv(stock):
    file_path = 'data/stocks.csv'
    
    # check if the file exists
    if not os.path.exists(file_path):
        print(f"{file_path} does not exist.")
        # # create the file and add the header
        # with open(file_path, 'w') as f:
        #     f.write('ticker\n')
    
    # read the existing stocks into a list
    stocks = pd.read_csv(file_path)['ticker'].tolist()
    
    # check if the stock is already in the file
    if stock in stocks:
        print(f"{stock} is already in {file_path}.")
    else:
        # add the new stock
        df = pd.DataFrame({'ticker': stocks + [stock]})
        df.to_csv(file_path, index=False)
        print(f"{stock} has been added to {file_path}. Once you refresh the data, you will be able to view the stock data.")

def main(): 
        if sys.argv[1] == None:
            print("Please enter a stock ticker.")
            exit()
        stock = sys.argv[1]
        check_ticker(stock)

        # ask the user if they want to add the stock to the CSV
        user_input = input("Would you like to add this stock to data/stocks.csv? (Y/N): ").strip().upper()
        if user_input == 'Y':
            add_stock_to_csv(stock)
        elif user_input == 'N':
            exit()
        else:
            print("Invalid input. Stock not added.")


if __name__ == "__main__":
    main()
