import os
import psycopg2
import yfinance as yf
from dotenv import load_dotenv
import datetime as dt
import pandas as pd


def connect_to_db():
    """
    Connect to the PostgreSQL database
    """
    # get database connection details from environment variables
    load_dotenv()
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')

    # return the connection to PostgreSQL
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )


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
        """, (ticker_symbol, date.date(),  
            float(row['Open']), float(row['Close']), float(row['High']),
            float(row['Low']), float(row['Volume'])))


def insert_stock_metadata(ticker_symbol, metadata, cursor):
    """
    inserts stock metadata into the lu_stock table
    """
    cursor.execute("""
        INSERT INTO lu_stock (ticker, currency, exchange_name, full_exchange_name, instrument_type, 
                              first_trade_date, regular_market_price, fifty_two_week_high, fifty_two_week_low, 
                              regular_market_day_high, regular_market_day_low, regular_market_volume, 
                              long_name, short_name, chart_previous_close, timezone, exchange_timezone_name)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (ticker) DO UPDATE SET 
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


def insert_stock_news(ticker_symbol, news, cursor): # implement this function
    """
    inserts stock news into the stock_news table
    """
    for article in news:
        cursor.execute("""
            INSERT INTO stock_news (ticker, title, summary, url, source, date)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (ticker, title) DO NOTHING
        """, (ticker_symbol, article['title'], article['summary'], article['url'], article['source'], article['date']))


def main():
    # connect to the database
    conn = connect_to_db()
    conn.autocommit = True
    cursor = conn.cursor()

    # access the list of stocks
    stocks = pd.read_csv('data/stocks.csv')['ticker'].tolist()

    # fetch data for each stock
    for ticker_symbol in stocks:
        print(f"----- fetching data for {ticker_symbol} ... -----")
        stock = yf.Ticker(ticker_symbol)
        # fetch historical market data
        hist = stock.history(period="max")
        hist.index = hist.index.tz_convert('UTC')

        # fetch stock metadata
        metadata = stock.history_metadata

        # insert stock data
        insert_stock_data(ticker_symbol, hist, cursor)
        print("📈 stock Data inserted successfully.")

        # insert stock metadata into lu_stock table
        if metadata:
            insert_stock_metadata(ticker_symbol, metadata, cursor)
        
        print(f"ℹ️ metadata inserted successfully.")
        print(f"✅ all data for {ticker_symbol} fetched successfully.")
     
    # Close the connection
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()