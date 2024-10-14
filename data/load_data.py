import yfinance as yf
import datetime as dt
import pandas as pd
import os
import psycopg2
from dotenv import load_dotenv


def connect_to_db(env="prod"):
    """
    Connect to the PostgreSQL database.
    Use 'env="dev"' for local db and 'env="prod"' for hosted db.
    """
    # load env variables
    load_dotenv()

    # decide which environment to use
    if env == "dev":
        # Local DB credentials
        DB_NAME = os.getenv('DB_NAME')
        DB_USER = os.getenv('DB_USER')
        DB_PASSWORD = os.getenv('DB_PASSWORD')
        DB_HOST = os.getenv('DB_HOST', 'localhost')
        DB_PORT = os.getenv('DB_PORT', '5432')
        # connect to local PostgreSQL
        return psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT)
    
    elif env == "prod":
        # Hosted DB credentials
        DB_URL = os.getenv('POSTGRES_URL')  # Full connection URL for hosted DB
        # connect to hosted PostgreSQL
        return psycopg2.connect(DB_URL)
    
    else:
        raise ValueError(f"Invalid environment '{env}' specified. Use 'dev' or 'prod'.")


def get_last_ingested_date(ticker_symbol, cursor):
    """
    Get the latest date for which stock data has already been inserted for the given ticker.
    """
    cursor.execute("""
        SELECT MAX(date) FROM stocks WHERE ticker = %s;
    """, (ticker_symbol,))
    
    result = cursor.fetchone()
    return result[0] if result[0] else dt.datetime(1970, 1, 1)


def insert_stock_data(ticker_symbol, hist_data, cursor):
    """
    inserts stock data into the stocks table for new dates only
    """
    for date, row in hist_data.iterrows():
        cursor.execute(
            """
            INSERT INTO stocks (ticker, date, open_price, close_price, high_price, low_price, volume)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (ticker, date) DO NOTHING
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
                              long_name, short_name, chart_previous_close, timezone, exchange_timezone_name, last_updated)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
            exchange_timezone_name = EXCLUDED.exchange_timezone_name,
            last_updated = EXCLUDED.last_updated
    """, 
    (ticker_symbol, metadata.get('currency'), metadata.get('exchangeName'), metadata.get('fullExchangeName'),
          metadata.get('instrumentType'), 
          dt.datetime.fromtimestamp(metadata.get('firstTradeDate')), # Convert from UNIX timestamp
          metadata.get('regularMarketPrice'), metadata.get('fiftyTwoWeekHigh'), metadata.get('fiftyTwoWeekLow'),
          metadata.get('regularMarketDayHigh'), metadata.get('regularMarketDayLow'), metadata.get('regularMarketVolume'),
          metadata.get('longName'), metadata.get('shortName'), metadata.get('chartPreviousClose'),
          metadata.get('timezone'), metadata.get('exchangeTimezoneName'), dt.datetime.now()))


def insert_stock_news(ticker_symbol, news_data, cursor):
    """
    inserts stock news into the stock_news table
    """
    # filter news data to only those that have ticker_symbol in relatedTickers
    news_data = [article for article in news_data if ticker_symbol in article.get('relatedTickers', [])]
    for article in news_data:
        # extract the first thumbnail, if available
        thumbnail_info = article.get('thumbnail', {}).get('resolutions', [{}])[0]
        thumbnail_url = thumbnail_info.get('url', None)
        thumbnail_width = thumbnail_info.get('width', None)
        thumbnail_height = thumbnail_info.get('height', None)

        # convert providerPublishTime UNIX timestamp to timestamp
        provider_publish_time = dt.datetime.utcfromtimestamp(article['providerPublishTime']).strftime('%Y-%m-%d %H:%M:%S')

        cursor.execute("""
            INSERT INTO stock_news (ticker, date, uuid, title, publisher, link, provider_publish_time, type, thumbnail_url, thumbnail_width, thumbnail_height)
            VALUES (%s, CURRENT_TIMESTAMP, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (uuid) DO NOTHING
        """, (
            ticker_symbol, article['uuid'], article['title'], article['publisher'], article['link'],
            provider_publish_time, article['type'], thumbnail_url, thumbnail_width, thumbnail_height
        ))


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
        
        # get the most recent date for which data is available in the database
        last_date = get_last_ingested_date(ticker_symbol, cursor)
        print(f"Last ingested date for {ticker_symbol}: {last_date}")

        # fetch historical market data
        hist = stock.history(period='max')
        # filter data to only include new dates
        hist = hist[hist.index >= last_date]
        # hist.index = hist.index.tz_convert('UTC')

        if not hist.empty:
            # insert stock data
            insert_stock_data(ticker_symbol, hist, cursor)
            print("📈 stock data inserted successfully.")
        else:
            print("⚠️ no new data to insert.")

        # fetch stock metadata
        metadata = stock.history_metadata # requires history() to be called first

        # insert stock metadata into lu_stock table
        if metadata:
            insert_stock_metadata(ticker_symbol, metadata, cursor)
            print("ℹ️ metadata inserted successfully.")
        
        # fetch stock news data
        news = stock.news

        # insert stock news data into stock_news table
        if news:
            insert_stock_news(ticker_symbol, news, cursor)
            print("📰 news data inserted successfully.")
        
        print(f"✅ all data for {ticker_symbol} fetched successfully.")
     
    # close the connection
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()