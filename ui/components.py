import streamlit as st
from streamlit_extras.row import row
import plotly.express as px
import pandas as pd
import numpy as np

def stock_header(stock_metadata):
    # Extract the stock symbol and long name from the metadata dataframe (for col2)
    symbol = stock_metadata['symbol'].values[0]        
    long_name = stock_metadata['long_name'].values[0]

    # Extract other metadata (for col1)
    exchange_name = stock_metadata['exchange_name'].values[0]
    currency = stock_metadata['currency'].values[0]
    instrument_type = stock_metadata['instrument_type'].values[0]
    first_trade_date = stock_metadata['first_trade_date'].values[0]

    col1, col2 = st.columns([1, 1])
    with col1:
        st.write("")
        st.write("")
        subcol1, subcol2, subcol3, subcol4 = st.columns([1, 1, 1, 1])
        with subcol1:
            st.markdown("**exchange**")
            st.markdown(f"`{exchange_name}`")
        with subcol2:  
            st.markdown("**currency**")
            st.markdown(f"`{currency}`")
        with subcol3:
            st.markdown("**stock type**")
            st.markdown(f"`{instrument_type}`")
        with subcol4:
            st.markdown("**first trade**")
            st.write(pd.to_datetime(first_trade_date).date())
    with col2:
        st.markdown(f"""
                    <h1 style='text-align: right; font-size: 60px;'>{symbol}</h1>
                    """, unsafe_allow_html=True)
        st.markdown(f"""
                <p style='text-align: right; font-size: 24px;'>{long_name}</p>
                """, unsafe_allow_html=True)


def stock_chart_section(stock_data):
    pass


def stock_chart(stock_data, time_period='365 days'):
    # Convert the time_period string into a proper Timedelta
    time_delta = pd.Timedelta(time_period)
    
    # Filter the data based on the time_period
    start_date = pd.Timestamp.now().date() - time_delta
    filtered_data = stock_data[stock_data['date'] >= start_date]
    
    # Ensure the data is sorted by date
    filtered_data = filtered_data.sort_values(by='date')
    
    # Plot the data
    fig = px.line(filtered_data, x="date", y="close_price", title="Stock Price Over Time")
    fig.update_traces(line=dict(width=4))  # Set desired width (e.g., 4)
    st.plotly_chart(fig)

