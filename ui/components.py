import streamlit as st
import plotly.express as px
import pandas as pd

def stock_news_list(stock_news):
    """
    display a list of stock news articles
    """
    for i in range(min(25, len(stock_news))):
        col1, col2 = st.columns([2, 1])
        with col1:
            article = stock_news.iloc[i]
            publish_time = pd.to_datetime(article['provider_publish_time'])
            formatted_time = publish_time.strftime('%b %d, %Y')
            st.markdown(f"### [{article['title']}]({article['link']})")
            st.markdown(f"{formatted_time}")
            st.markdown(f"{article['type'].lower()} by *{article['publisher']}*")
        with col2:
            if article['thumbnail_url']:
                st.markdown(f'<img src="{article["thumbnail_url"]}" alt="{article["title"]}" style="width:300px;">', unsafe_allow_html=True)
        st.write("---")

def stock_header_with_info(stock_metadata, stock_data):
    """
    UI component to display basic stock information (name and current price)
    """
    ticker = stock_metadata['ticker'].values[0]
    long_name = stock_metadata['long_name'].values[0]

    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown(f"<h1 style='font-size: 48px;'>{ticker}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size: 18px;'>{long_name}</p>", unsafe_allow_html=True)
    with col2:
        st.write("")
        display_info_tabs(stock_metadata, stock_data)

        
def display_info_tabs(stock_metadata, stock_data):
    """
    tabs to display general stock information, daily stats, and 52-week stats
    """
    tabs = st.tabs(['General', 'Daily Stats', '52-week Stats'])
    with tabs[0]:
        display_general_info(stock_metadata)
    with tabs[1]:
        display_daily_stats(stock_metadata)
    with tabs[2]:
        display_52_week_stats(stock_data)


def display_general_info(stock_metadata):
    """
    display exchange, currency, stock type, and volume
    """
    exchange_name = stock_metadata['exchange_name'].values[0]
    currency = stock_metadata['currency'].values[0]
    instrument_type = stock_metadata['instrument_type'].values[0]
    # first_trade_date = stock_metadata['first_trade_date'].values[0]
    volume = stock_metadata['regular_market_volume'].values[0]
    subcol1, subcol2, subcol3, subcol4, subcol5 = st.columns([1, 1, 1, 1, 3])
    with subcol1:
        if exchange_name:
            st.markdown("*exchange:*")
            st.markdown(f'<span style="font-size:18px;">`{exchange_name}`</span>', unsafe_allow_html=True)
    with subcol2: 
        if currency: 
            st.markdown("*currency:*")
            st.markdown(f'<span style="font-size:18px;">`{currency}`</span>', unsafe_allow_html=True)
    with subcol3:
        if instrument_type:
            st.markdown("*stock type:*")
            st.markdown(f'<span style="font-size:18px;">`{instrument_type}`</span>', unsafe_allow_html=True)
    with subcol4:
        if volume:
            st.markdown("*volume:*")
            st.markdown(f'<span style="font-size:18px;">`{volume:,.0f}`</span>', unsafe_allow_html=True)
    with subcol5:
        pass

def display_daily_stats(stock_metadata):
    """
    display current price, daily low, and daily high
    """
    current_price = stock_metadata['regular_market_price'][0]
    last_open = stock_metadata['chart_previous_close'][0]
    daily_low = stock_metadata['regular_market_day_low'][0]
    daily_high = stock_metadata['regular_market_day_high'][0]
    subcol1, subcol2, subcol3, subcol4, subcol5 = st.columns([1, 1, 1, 1, 3])
    with subcol1:
        if current_price:
            st.markdown("*current price:*")
            st.markdown(f'<span style="font-size:18px;">`${current_price:,.2f}`</span>', unsafe_allow_html=True)
    
    with subcol2:
        if last_open:
            st.markdown("*last open:*")
            st.markdown(f'<span style="font-size:18px;">`${last_open:,.2f}`</span>', unsafe_allow_html=True)

    with subcol3:
        if daily_high:
            st.markdown("*daily high:*")
            st.markdown(f'<span style="font-size:18px;">`${daily_high:,.2f}`</span>', unsafe_allow_html=True)
        
    with subcol4:
        if daily_low:   
            st.markdown("*daily low:*")
            st.markdown(f'<span style="font-size:18px;">`${daily_low:,.2f}`</span>', unsafe_allow_html=True)
    
    with subcol5:
        pass

def display_52_week_stats(stock_data):
    """
    display 52-week high and 52-week low
    """
    year_data = filter_stock_data(stock_data, '365 days')
    high_52_week = year_data['close_price'].max()
    low_52_week = year_data['close_price'].min()
    subcol1, subcol2, subcol3 = st.columns([1, 1, 4])
    with subcol1:
        if high_52_week:
            st.markdown("*52-week high:*")
            st.markdown(f'<span style="font-size:18px;">`${high_52_week:,.2f}`</span>', unsafe_allow_html=True)
    with subcol2:
        if low_52_week:
            st.markdown("*52-week low:*")
            st.markdown(f'<span style="font-size:18px;">`${low_52_week:,.2f}`</span>', unsafe_allow_html=True)


def stock_chart(stock_data, stock_metadata):
    """
    display stock chart and price difference information
    """
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        time_frame = select_time_frame()
        filtered_data = filter_stock_data(stock_data, time_frame)

    with col2:
        display_price_info(filtered_data, stock_metadata)
    
    plot_stock_chart(filtered_data)


def select_time_frame():
    """
    UI component for selecting the time frame of the stock chart
    """
    time_frame = st.radio('Time frame:', ['1w', '1m', '6m', '1y', '5y', 'max'], index=1, horizontal=True)
    return to_time_period(time_frame)


def filter_stock_data(stock_data, time_frame):
    """
    filter the stock data based on the selected time period
    """
    time_delta = pd.Timedelta(time_frame)
    start_date = pd.Timestamp.now().date() - time_delta
    return stock_data[stock_data['date'] >= start_date].sort_values('date', ascending=False)


def display_price_info(filtered_data, stock_metadata):
    """
    display the current price, price difference, and percentage change
    """
    start_price = filtered_data['open_price'].iloc[-1]
    current_price = stock_metadata['regular_market_price'][0]
    price_diff = current_price - start_price
    price_diff_percent = (price_diff / start_price) * 100

    st.markdown(f"<h1 style='font-size: 48px;'>${current_price:,.2f}</h1>", unsafe_allow_html=True)

    sign = "+" if price_diff > 0 else "-"
    price_diff_text = f"{sign}${abs(price_diff):,.2f} ({sign}{abs(price_diff_percent):,.2f}%)"
    color = "green" if price_diff > 0 else "red"
    
    st.markdown(f"<p style='font-size: 18px; color: {color};'>{price_diff_text}</p>", unsafe_allow_html=True)

    last_updated = pd.to_datetime(stock_metadata['last_updated'][0])
    st.markdown(f"as of {last_updated.strftime('%b %d, %Y %I:%M%p')}")


def plot_stock_chart(filtered_data):
    """
    plot the stock chart using Plotly
    """
    fig = px.line(filtered_data, x="date", y="close_price")
    fig.update_traces(line=dict(width=6))
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Close Price",
        xaxis_tickformat='%b %d, %Y',
        xaxis_showgrid=False,
        hoverlabel=dict(font_size=18, bordercolor="white"),
    )
    st.plotly_chart(fig)


def to_time_period(time_frame):
    """
    converts time_frame string into a pandas Timedelta compatible string
    """
    periods = {
        '1w': '7 days',
        '1m': '30 days',
        '6m': '183 days',
        '1y': '365 days',
        '5y': '1825 days',
        'max': '45545 days'
    }
    return periods.get(time_frame, '365 days')

