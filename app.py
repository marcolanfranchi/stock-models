import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from ui.components import stock_header_with_info, stock_chart, stock_news_list
from data.load_data import main as refresh_database, connect_to_db
import time
import pytz

# Cache the function that retrieves stock metadata
# @st.cache_data(ttl=600)  # cache for 10 minutes
def load_stock_metadata(selected_stock):
    cursor = conn.cursor()
    stock_metadata = pd.read_sql(
        f"SELECT * FROM public.lu_stock WHERE ticker = '{selected_stock}';",
        conn)
    stock_metadata['first_trade_date'] = pd.to_datetime(stock_metadata['first_trade_date']).dt.date
    return stock_metadata

# Cache the function that retrieves stock data
# @st.cache_data(ttl=600)  # cache for 10 minutes
def load_stock_data(selected_stock):
    cursor = conn.cursor()
    stock_data = pd.read_sql(
        f"SELECT * FROM public.stocks WHERE ticker = '{selected_stock}' order by date desc;",
        conn)
    stock_data['date'] = pd.to_datetime(stock_data['date'], utc=True).dt.date
    return stock_data

# Cache the function that retrieves stock news
# @st.cache_data(ttl=600)  # cache for 10 minutes
def load_stock_news(selected_stock):
    cursor = conn.cursor()
    stock_news = pd.read_sql(
        f"SELECT * FROM public.stock_news WHERE ticker = '{selected_stock}' order by provider_publish_time desc;",
        conn)
    return stock_news

# page configurations
st.set_page_config(
    page_title="stock-models",
    page_icon="📈",
    layout="wide"
)

# remove streamlit's main menu and footer
hide_default_format = """
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)

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
    st.write("")
    st.write("a simple UI/database I built to display a collection of stocks of my interest. I am working on building models for different stocks to display here.")
    st.write("")
    st.write("🚧 models are currently under development 🚧") 
    st.write("---")

# display the list of stocks in the sidebar
with st.sidebar:
    col1, col2 = st.columns([1,2])
    with col1:
        selected_stock = st.selectbox('select a stock', stocks, index=0)
    with col2:
        pass

# Load the data for the selected stock
stock_metadata = load_stock_metadata(selected_stock)
stock_data = load_stock_data(selected_stock)
stock_news = load_stock_news(selected_stock)

with st.sidebar:
    with refreshCol:
            st.write("")
            if st.button('refresh data'):
                text_placeholder = st.empty() # placeholder for the text
                current_time = datetime.now(pytz.timezone('US/Pacific'))
                last_updated = pd.to_datetime(stock_metadata['last_updated'][0]).tz_localize('US/Pacific')
                if last_updated >= (current_time - timedelta(minutes=15)):
                # if False:
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
        st.markdown(f'<u>*relevant news:*</u>', unsafe_allow_html=True)
        st.write("")
        st.write("")
        st.write("")
        st.write("")

        stock_news_list(stock_news)


# display the stock header and chart
stock_header_with_info(stock_metadata, stock_data)
st.write("---")
stock_chart(stock_data, stock_metadata)


