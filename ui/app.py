import streamlit as st
import pandas as pd

st.title('stock-models')
st.write("A simple web app to display different models that I've built for predicting stock prices.") 

stocks = pd.read_csv('data/stocks.csv').columns.tolist()
st.write("stocks: ", [stock.strip() for stock in stocks])



