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
            st.markdown(f"*{exchange_name}*")
        with subcol2:  
            st.markdown("**currency**")
            st.markdown(f"*{currency}*")
        with subcol3:
            st.markdown("**stock type**")
            st.markdown(f"*{instrument_type}*")
        with subcol4:
            st.markdown("**first trade**")
            st.markdown(f"*{pd.to_datetime(first_trade_date).date()}*")
    with col2:
        st.markdown(f"""
                    <h1 style='text-align: right; font-size: 60px;'>{symbol}</h1>
                    """, unsafe_allow_html=True)
        st.markdown(f"""
                <p style='text-align: right; font-size: 18px;'>{long_name}</p>
                """, unsafe_allow_html=True)


def stock_chart_section(stock_data):
    st.write("---")
    # st.write("")
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("**current price (last close)**")
        st.markdown(f"""
                    <h1 style='font-size: 60px;'>${stock_data['close_price'].values[-1]:,.2f}</h1>
                    """, unsafe_allow_html=True) 
        st.markdown(f"""
                    <p style='font-size: 18px;'>{stock_data['date'].values[-1]}</p>
                    """, unsafe_allow_html=True)       
    with col2:
        yearly_high = stock_data[stock_data['date'] >= (pd.Timestamp.now().date() - pd.Timedelta('365 days'))]['close_price'].max()
        yearly_low = stock_data[stock_data['date'] >= (pd.Timestamp.now().date() - pd.Timedelta('365 days'))]['close_price'].min()
        volume = stock_data['volume'].values[-1]
        subcol1, subcol2, subcol3 = st.columns([1, 1, 1])
        with subcol1:
            # 52-week high
            st.markdown("<p style='text-align: right;'><strong>52-week high</strong></p>", unsafe_allow_html=True)
            st.markdown(f"""
                <p style='text-align: right;'>${yearly_high:,.2f}</p>
                """, unsafe_allow_html=True)
        with subcol2:
            # 52-week low
            st.markdown("<p style='text-align: right;'><strong>52-week low</strong></p>", unsafe_allow_html=True)
            st.markdown(f"""
                <p style='text-align: right;'>${yearly_low:,.2f}</p>
                """, unsafe_allow_html=True)
        with subcol3:
            # volume
            st.markdown("<p style='text-align: right;'><strong>volume</strong></p>", unsafe_allow_html=True)
            st.markdown(f"""
                <p style='text-align: right;'>{volume:,.0f}</p>
                """, unsafe_allow_html=True)

    # plot the chart        
    stock_chart(stock_data)



def stock_chart(stock_data, time_period='365 days'):
    # Convert the time_period string into a proper Timedelta
    time_delta = pd.Timedelta(time_period)
    
    # Filter the data based on the time_period
    start_date = pd.Timestamp.now().date() - time_delta
    filtered_data = stock_data[stock_data['date'] >= start_date]
    
    # Ensure the data is sorted by date
    filtered_data = filtered_data.sort_values(by='date')
    
    # Plot the data
    fig = px.line(filtered_data, x="date", y="close_price")
    fig.update_traces(line=dict(width=4))  # Set desired width (e.g., 4)
    st.plotly_chart(fig)

