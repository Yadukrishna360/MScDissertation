import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
import time
from prophet import Prophet
import pandas as pd
from datetime import datetime
import numpy as np

# Ensure compatibility by setting float_ to float64
np.float_ = np.float64

def home_page():
    st.write("## Home Page: Stock Tracker")

    # Sidebar for selecting stock ticker and interval
    stock_ticker = st.sidebar.text_input("Enter Stock Ticker", "AAPL")
    update_interval = st.sidebar.slider("Update Interval (seconds)", min_value=10, max_value=300, value=60)
    interval_option = st.sidebar.selectbox(
        "Select Candlestick Chart Interval",
        ("2 Years (1d)", "1 Year (1d)", "1 Month (1h)", "1 Week (15m)", "5 Days (5m)", "1 Day (1m)")
    )

    # Function to fetch stock data
    def get_stock_data(ticker, period, interval):
        stock = yf.Ticker(ticker)
        stock_info = stock.history(period=period, interval=interval)
        return stock_info

    # Function to fetch live price and previous close
    def get_live_data(ticker):
        stock = yf.Ticker(ticker)
        live_data = stock.history(period="1d", interval="1m")
        history_data = stock.history(period="5d", interval="1d")  # Fetch 5 days to get the previous close
        
        if not live_data.empty and not history_data.empty:
            current_price = live_data['Close'].iloc[-1]
            
            # Ensure at least two days of data for previous close
            if len(history_data) > 1:
                previous_close = history_data['Close'].iloc[-2]
            else:
                previous_close = None  # Not enough data for previous close
            return current_price, previous_close
        else:
            return None, None

    # Plotting functions
    def plot_candlestick(data):
        fig = go.Figure(data=[go.Candlestick(
            x=data.index, 
            open=data['Open'], 
            high=data['High'], 
            low=data['Low'], 
            close=data['Close'], 
            name='Candlesticks'
        )])
        fig.update_layout(title=f'{stock_ticker} Stock Price', xaxis_title='Date', yaxis_title='Price (USD)', xaxis_rangeslider_visible=False)
        return fig

    def forecast_stock_price(ticker):
        forecast_data = get_stock_data(ticker, period='2y', interval='1d')
        df = forecast_data.reset_index()[['Date', 'Close']]
        df.columns = ['ds', 'y']
        df['ds'] = df['ds'].dt.tz_localize(None)

        # Ensure y is a float64 type to avoid compatibility issues
        df['y'] = df['y'].astype('float64')

        model = Prophet(daily_seasonality=True)
        model.fit(df)
        future = model.make_future_dataframe(periods=60)
        forecast = model.predict(future)
        return forecast_data, forecast

    price_placeholder = st.empty()
    chart_placeholder = st.empty()
    stock_info_placeholder = st.empty()  # Placeholder for stock info
    forecast_placeholder = st.empty()

    # Fetch live price and previous close (used for percentage change)
    current_price, previous_close = get_live_data(stock_ticker)
    if current_price is not None and previous_close is not None:
        price_change = current_price - previous_close
        price_change_percent = (price_change / previous_close) * 100
        # Color based on increase or decrease
        price_color = "green" if price_change > 0 else "red"
    else:
        price_change_percent = None  # Not enough data for previous close

    if stock_ticker:
        forecast_data, forecast = forecast_stock_price(stock_ticker)
        while True:
            period, interval = get_period_interval(interval_option)
            candlestick_data = get_stock_data(stock_ticker, period, interval)

            with chart_placeholder.container():
                if not candlestick_data.empty:
                    st.plotly_chart(plot_candlestick(candlestick_data), use_container_width=True)
                else:
                    st.warning("No data available for the selected ticker and interval")

            # Display stock information below the candlestick chart with customizable font sizes
            if not candlestick_data.empty:
                latest_data = candlestick_data.iloc[-1]
                with stock_info_placeholder.container():
                    st.write("### Stock Information")

                    # Define font size
                    font_size = "20px"
                    font_size1 = "32px"
                    # Display data in a row with each value in a separate column and apply CSS styling for font size
                    col1, col2, col3, col4, col5, col6 = st.columns(6)
                    
                    # Titles as table headers with font size
                    col1.markdown(f"<h4 style='font-size:{font_size};'>Ticker</h4>", unsafe_allow_html=True)
                    col2.markdown(f"<h4 style='font-size:{font_size};'>Opening Price</h4>", unsafe_allow_html=True)
                    col3.markdown(f"<h4 style='font-size:{font_size};'>Closing Price</h4>", unsafe_allow_html=True)
                    col4.markdown(f"<h4 style='font-size:{font_size};'>High Price</h4>", unsafe_allow_html=True)
                    col5.markdown(f"<h4 style='font-size:{font_size};'>Low Price</h4>", unsafe_allow_html=True)
                    col6.markdown(f"<h4 style='font-size:{font_size};'>Total Volume</h4>", unsafe_allow_html=True)
                    
                    # Values in corresponding columns with font size
                    col1.markdown(f"<p style='font-size:{font_size1};'>{stock_ticker}</p>", unsafe_allow_html=True)
                    col2.markdown(f"<p style='font-size:{font_size1};'>${latest_data['Open']:.2f}</p>", unsafe_allow_html=True)
                    col3.markdown(f"<p style='font-size:{font_size1};'>${latest_data['Close']:.2f}</p>", unsafe_allow_html=True)
                    col4.markdown(f"<p style='font-size:{font_size1};'>${latest_data['High']:.2f}</p>", unsafe_allow_html=True)
                    col5.markdown(f"<p style='font-size:{font_size1};'>${latest_data['Low']:.2f}</p>", unsafe_allow_html=True)
                    col6.markdown(f"<p style='font-size:{font_size1};'>{latest_data['Volume']:,}</p>", unsafe_allow_html=True)

            # Live price and percentage change display
            with price_placeholder.container():
                st.write(f"### Live Price for {stock_ticker}")
                if current_price is not None:
                    st.metric(label="Current Price", value=f"${current_price:.2f}", delta=f"{price_change_percent:.2f}%" if price_change_percent is not None else "N/A", delta_color="inverse" if price_change > 0 else "normal")
                else:
                    st.warning("No live data available")

            try:
                forecast_data, forecast = forecast_stock_price(stock_ticker)
                with forecast_placeholder.container():
                    st.plotly_chart(plot_forecast(forecast_data, forecast, stock_ticker), use_container_width=True)
            except Exception as e:
                st.error(f"Error in forecasting: {e}")
            time.sleep(update_interval)

def get_period_interval(option):
    if option == "2 Years (1d)":
        return "2y", "1d"
    elif option == "1 Year (1d)":
        return "1y", "1d"
    elif option == "1 Month (1h)":
        return "1mo", "1h"
    elif option == "1 Week (15m)":
        return "7d", "15m"
    elif option == "5 Days (5m)":
        return "5d", "5m"
    elif option == "1 Day (1m)":
        return "1d", "1m"

def plot_forecast(forecast_data, forecast, stock_ticker):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=forecast_data.index, y=forecast_data['Close'], name='Actual Price', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], name='Forecast', line=dict(color='green')))
    fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_lower'], name='Lower Confidence', line=dict(dash='dash', color='gray')))
    fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_upper'], name='Upper Confidence', line=dict(dash='dash', color='gray')))
    fig.update_layout(title=f'{stock_ticker} Stock Price Forecast (60 Days)', xaxis_title='Date', yaxis_title='Price (USD)', xaxis_rangeslider_visible=False)
    return fig
