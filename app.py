import streamlit as st
import pandas as pd
import datetime as dt
import plotly.figure_factory as ff
from ui.components import stock_header_with_info, stock_chart, stock_news_list
from data.load_data import main as refresh_database
from data.create_db import connect_to_db
import time

# page configurations
st.set_page_config(
    page_title="stock-models",
    page_icon="📈",
    layout="wide"
)

# retreiving the stock data
conn = connect_to_db()
conn.autocommit = True
cursor = conn.cursor()

# load the list of stocks
stocks = pd.read_sql(f"SELECT DISTINCT ticker FROM public.lu_stock order by ticker", conn)

# sidebar
with st.sidebar:
    titleCol, refreshCol = st.columns([2, 1])
    with titleCol:
        st.title('stock-models')
    st.write("")
    st.write("a simple web app to display different models that i've built for a small collection of stocks of my interest.")
    st.write("")
    st.write("🚧 models are currently under development 🚧") 
    st.write("---")

# display the list of stocks in the sidebar
with st.sidebar:
    selected_stock = st.selectbox('select a stock', stocks, index=0)

# get the data for the selected stock
stock_metadata = pd.read_sql(
    f"SELECT * FROM public.lu_stock WHERE ticker = '{selected_stock}'",
    conn)
stock_metadata['first_trade_date'] = pd.to_datetime(stock_metadata['first_trade_date']).dt.date

# load the selected stocks data from the database
stock_data = pd.read_sql(
    f"SELECT * FROM public.stocks WHERE ticker = '{selected_stock}' order by date desc",
    conn)
stock_data['date'] = pd.to_datetime(stock_data['date'], utc=True).dt.date

# load the selected stocks news from the database
stock_news = pd.read_sql(
    f"SELECT * FROM public.stock_news WHERE ticker = '{selected_stock}' order by provider_publish_time desc",
    conn)

with st.sidebar:
    with refreshCol:
            st.write("")
            if st.button('refresh data'):
                text_placeholder = st.empty() # placeholder for the text
                if stock_metadata['last_updated'][0] >= (dt.datetime.now() - dt.timedelta(minutes=15)):
                    text_placeholder.write("data can only be refreshed once every 15 minutes.")
                else:
                    refresh_database()
                    text_placeholder.write("data refreshed successfully.")
                time.sleep(5) # wait for 5 seconds
                text_placeholder.empty() # clear the text

# display the news in the sidebar
with st.sidebar:
    if len(stock_news) > 0:
        st.write("---")
        st.write(f'*relevant news:*')
        st.write("---")
        stock_news_list(stock_news)


# display the stock header and chart
stock_header_with_info(stock_metadata, stock_data)
st.write("---")
stock_chart(stock_data, stock_metadata)


