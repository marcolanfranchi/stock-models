import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import os
import psycopg2
import plotly.figure_factory as ff
from components import stock_header, stock_chart_section

# load environment variables from .env file
load_dotenv()

# get database connection details from environment variables
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')

st.set_page_config(
    page_title="stock-models",
    page_icon="📈",
    layout="wide"
)

st.title('stock-models')
st.write("a simple web app to display different models that i've built for predicting stock prices.") 


stocks = pd.read_csv('data/stocks.csv')['symbol'].tolist()
selected_stock = st.selectbox('Select a stock', stocks, index=0)
st.write("---")

# Connect to the PostgreSQL server
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
# conn.autocommit = True
cursor = conn.cursor()

# load the stock metadata from the database
stock_metadata = pd.read_sql(
    f"SELECT * FROM public.lu_stock WHERE symbol = '{selected_stock}'",
    conn)

# load the stock data from the database
stock_data = pd.read_sql(
    f"SELECT * FROM public.stocks WHERE ticker = '{selected_stock}'",
    conn)

# metadata_row(stock_metadata)
stock_header(stock_metadata)
stock_chart_section(stock_data)


