import streamlit as st
from streamlit_extras.row import row
import pandas as pd

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



def stock_chart(stock_data):
    st.write(stock_data)
    st.line_chart(stock_data['chart_previous_close'])
