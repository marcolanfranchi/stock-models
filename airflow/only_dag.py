# from datetime import datetime, timedelta
# import yfinance as yf
# import pandas as pd
# from create_db import connect_to_db
# from airflow import DAG
# from airflow.operators.python_operator import PythonOperator


# def insert_stock_data(ticker_symbol, hist_data, cursor):
#     """
#     Inserts stock data into the stocks table
#     """
#     for date, row in hist_data.iterrows():
#         cursor.execute("""
#             INSERT INTO stocks (ticker, date, open_price, close_price, high_price, low_price, volume)
#             VALUES (%s, %s, %s, %s, %s, %s, %s)
#             ON CONFLICT (ticker, date) DO UPDATE SET 
#                 open_price = EXCLUDED.open_price,
#                 close_price = EXCLUDED.close_price,
#                 high_price = EXCLUDED.high_price,
#                 low_price = EXCLUDED.low_price,
#                 volume = EXCLUDED.volume
#         """, (ticker_symbol, date.date(),  
#             float(row['Open']), float(row['Close']), float(row['High']),
#             float(row['Low']), float(row['Volume'])))


# def insert_stock_metadata(ticker_symbol, metadata, cursor):
#     """
#     Inserts stock metadata into the lu_stock table
#     """
#     cursor.execute("""
#         INSERT INTO lu_stock (ticker, currency, exchange_name, full_exchange_name, instrument_type, 
#                               first_trade_date, regular_market_price, fifty_two_week_high, fifty_two_week_low, 
#                               regular_market_day_high, regular_market_day_low, regular_market_volume, 
#                               long_name, short_name, chart_previous_close, timezone, exchange_timezone_name, last_updated)
#         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#         ON CONFLICT (ticker) DO UPDATE SET 
#             currency = EXCLUDED.currency,
#             exchange_name = EXCLUDED.exchange_name,
#             full_exchange_name = EXCLUDED.full_exchange_name,
#             instrument_type = EXCLUDED.instrument_type,
#             first_trade_date = EXCLUDED.first_trade_date,
#             regular_market_price = EXCLUDED.regular_market_price,
#             fifty_two_week_high = EXCLUDED.fifty_two_week_high,
#             fifty_two_week_low = EXCLUDED.fifty_two_week_low,
#             regular_market_day_high = EXCLUDED.regular_market_day_high,
#             regular_market_day_low = EXCLUDED.regular_market_day_low,
#             regular_market_volume = EXCLUDED.regular_market_volume,
#             long_name = EXCLUDED.long_name,
#             short_name = EXCLUDED.short_name,
#             chart_previous_close = EXCLUDED.chart_previous_close,
#             timezone = EXCLUDED.timezone,
#             exchange_timezone_name = EXCLUDED.exchange_timezone_name,
#             last_updated = EXCLUDED.last_updated
#     """, 
#     (ticker_symbol, metadata.get('currency'), metadata.get('exchangeName'), metadata.get('fullExchangeName'),
#           metadata.get('instrumentType'), 
#           datetime.fromtimestamp(metadata.get('firstTradeDate')),  # Convert from UNIX timestamp
#           metadata.get('regularMarketPrice'), metadata.get('fiftyTwoWeekHigh'), metadata.get('fiftyTwoWeekLow'),
#           metadata.get('regularMarketDayHigh'), metadata.get('regularMarketDayLow'), metadata.get('regularMarketVolume'),
#           metadata.get('longName'), metadata.get('shortName'), metadata.get('chartPreviousClose'),
#           metadata.get('timezone'), metadata.get('exchangeTimezoneName'), datetime.now()))


# def insert_stock_news(ticker_symbol, news_data, cursor):
#     """
#     Inserts stock news into the stock_news table
#     """
#     # Filter news data to only those that have ticker_symbol in relatedTickers
#     news_data = [article for article in news_data if ticker_symbol in article.get('relatedTickers', [])]

#     for article in news_data:
#         # Extract the first thumbnail, if available
#         thumbnail_info = article.get('thumbnail', {}).get('resolutions', [{}])[0]
#         thumbnail_url = thumbnail_info.get('url', None)
#         thumbnail_width = thumbnail_info.get('width', None)
#         thumbnail_height = thumbnail_info.get('height', None)

#         # Convert providerPublishTime UNIX timestamp to timestamp
#         provider_publish_time = datetime.utcfromtimestamp(article['providerPublishTime']).strftime('%Y-%m-%d %H:%M:%S')

#         cursor.execute("""
#             INSERT INTO stock_news (ticker, date, uuid, title, publisher, link, provider_publish_time, type, thumbnail_url, thumbnail_width, thumbnail_height)
#             VALUES (%s, CURRENT_TIMESTAMP, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#             ON CONFLICT (uuid) DO NOTHING
#         """, (
#             ticker_symbol, article['uuid'], article['title'], article['publisher'], article['link'],
#             provider_publish_time, article['type'], thumbnail_url, thumbnail_width, thumbnail_height
#         ))

# def fetch_data(**kwargs):
#     # Connect to the database
#     conn = connect_to_db()
#     conn.autocommit = True
#     cursor = conn.cursor()

#     # Access the list of stocks
#     stocks = pd.read_csv('data/stocks.csv')['ticker'].tolist()

#     # Fetch data for each stock
#     for ticker_symbol in stocks:
#         print(f"----- fetching data for {ticker_symbol} ... -----")
#         stock = yf.Ticker(ticker_symbol)
        
#         # Fetch historical market data
#         hist = stock.history(period="max")
#         hist.index = hist.index.tz_convert('UTC')

#         # Fetch stock metadata
#         metadata = stock.history_metadata

#         # Fetch stock news data
#         news = stock.news  # This returns a list of news articles

#         # Insert stock data
#         insert_stock_data(ticker_symbol, hist, cursor)
#         print("📈 Stock data inserted successfully.")

#         # Insert stock metadata into lu_stock table
#         if metadata:
#             insert_stock_metadata(ticker_symbol, metadata, cursor)
#             print("ℹ️ Metadata inserted successfully.")

#         # Insert stock news data into stock_news table
#         if news:
#             insert_stock_news(ticker_symbol, news, cursor)
#             print("📰 News data inserted successfully.")
        
#         print(f"✅ All data for {ticker_symbol} fetched successfully.")
     
#     # Close the connection
#     cursor.close()
#     conn.close()

# # Define the DAG
# default_args = {
#     'owner': 'airflow',
#     'start_date': datetime(2024, 10, 1),
#     'retries': 1,
#     'retry_delay': timedelta(minutes=5),
# }

# dag = DAG(
#     'stock_data_pipeline',
#     default_args=default_args,
#     description='A simple stock data pipeline',
#     schedule_interval='*/3 * * * *',  # Runs every 3 minutes
# )

# # Define the task
# load_stock_data = PythonOperator(
#     task_id='fetch_data_task',
#     python_callable=fetch_data,
#     dag=dag,
# )

# # Set task dependencies (if needed)
