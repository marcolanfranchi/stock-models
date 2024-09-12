import os
import psycopg2
import yfinance as yf
from dotenv import load_dotenv
import datetime as dt
import pandas as pd

def insert_stock_data(ticker_symbol, hist_data, cursor):
    """
    inserts stock data into the stocks table
    """
    for date, row in hist_data.iterrows():
        cursor.execute("""
            INSERT INTO stocks (ticker, date, open_price, close_price, high_price, low_price, volume)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (ticker, date) DO UPDATE SET 
                open_price = EXCLUDED.open_price,
                close_price = EXCLUDED.close_price,
                high_price = EXCLUDED.high_price,
                low_price = EXCLUDED.low_price,
                volume = EXCLUDED.volume
        """, (ticker_symbol, date, float(row['Open']), float(row['Close']), float(row['High']), float(row['Low']), float(row['Volume'])))

# Function to insert stock metadata into the lu_stock table
def insert_stock_metadata(ticker_symbol, metadata, cursor):
    cursor.execute("""
        INSERT INTO lu_stock (symbol, currency, exchange_name, full_exchange_name, instrument_type, 
                              first_trade_date, regular_market_price, fifty_two_week_high, fifty_two_week_low, 
                              regular_market_day_high, regular_market_day_low, regular_market_volume, 
                              long_name, short_name, chart_previous_close, timezone, exchange_timezone_name)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (symbol) DO UPDATE SET 
            currency = EXCLUDED.currency,
            exchange_name = EXCLUDED.exchange_name,
            full_exchange_name = EXCLUDED.full_exchange_name,
            instrument_type = EXCLUDED.instrument_type,
            first_trade_date = EXCLUDED.first_trade_date,
            regular_market_price = EXCLUDED.regular_market_price,
            fifty_two_week_high = EXCLUDED.fifty_two_week_high,
            fifty_two_week_low = EXCLUDED.fifty_two_week_low,
            regular_market_day_high = EXCLUDED.regular_market_day_high,
            regular_market_day_low = EXCLUDED.regular_market_day_low,
            regular_market_volume = EXCLUDED.regular_market_volume,
            long_name = EXCLUDED.long_name,
            short_name = EXCLUDED.short_name,
            chart_previous_close = EXCLUDED.chart_previous_close,
            timezone = EXCLUDED.timezone,
            exchange_timezone_name = EXCLUDED.exchange_timezone_name
    """, 
    (ticker_symbol, metadata.get('currency'), metadata.get('exchangeName'), metadata.get('fullExchangeName'),
          metadata.get('instrumentType'), 
          dt.datetime.fromtimestamp(metadata.get('firstTradeDate')),  # Convert from UNIX timestamp
          metadata.get('regularMarketPrice'), metadata.get('fiftyTwoWeekHigh'), metadata.get('fiftyTwoWeekLow'),
          metadata.get('regularMarketDayHigh'), metadata.get('regularMarketDayLow'), metadata.get('regularMarketVolume'),
          metadata.get('longName'), metadata.get('shortName'), metadata.get('chartPreviousClose'),
          metadata.get('timezone'), metadata.get('exchangeTimezoneName')))
    
def main():

    # load environment variables
    load_dotenv()

    # get database connection details from environment variables
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')

    # connect to PostgreSQL
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    conn.autocommit = True
    cursor = conn.cursor()

    stocks = pd.read_csv('data/stocks.csv')['symbol'].tolist()
    for ticker_symbol in stocks:
        print(f"Fetching data for {ticker_symbol}...")
        stock = yf.Ticker(ticker_symbol)
        # Fetch historical market data
        hist = stock.history(period="max")

        # Fetch stock metadata
        metadata = stock.history_metadata

        # Insert stock data
        insert_stock_data(ticker_symbol, hist, cursor)
        print("Stock Data inserted successfully.")

        # Insert stock metadata into lu_stock table
        if metadata:
            insert_stock_metadata(ticker_symbol, metadata, cursor)
        
        print(f"Metadata for {ticker_symbol} inserted successfully.")
     

    # Close the connection
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
