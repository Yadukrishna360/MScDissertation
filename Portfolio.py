import streamlit as st
import yfinance as yf
import pandas as pd

def fetch_portfolio_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period="1mo", interval="1d")  # Fetching 1 month of daily data for simplicity
        return data
    except Exception as e:
        st.error(f"Failed to fetch data for {ticker}: {e}")
        return pd.DataFrame()

def portfolio_page():
    st.write("## Portfolio Page")

    if 'portfolio_tickers' not in st.session_state:
        st.session_state.portfolio_tickers = []

    # Ticker input
    ticker_input = st.text_input("Enter stock ticker (up to 3)", "")
    if st.button("Add Stock"):
        if ticker_input and len(st.session_state.portfolio_tickers) < 3:
            st.session_state.portfolio_tickers.append(ticker_input.upper())
            st.success("Stock added to portfolio!")
        elif len(st.session_state.portfolio_tickers) == 3:
            st.warning("You can only track up to 3 stocks.")
        ticker_input = ""

    # Allow removal of tickers
    if st.session_state.portfolio_tickers:
        ticker_to_remove = st.selectbox("Remove stock ticker", st.session_state.portfolio_tickers)
        if st.button("Remove Stock"):
            st.session_state.portfolio_tickers.remove(ticker_to_remove)
            st.success("Stock removed from portfolio!")

    # Display stock data for each ticker
    stocks_data = {}
    if st.session_state.portfolio_tickers:
        col1, col2, col3 = st.columns(3)
        for i, ticker in enumerate(st.session_state.portfolio_tickers):
            data = fetch_portfolio_stock_data(ticker)
            stocks_data[ticker] = data
            if i == 0:
                col = col1
            elif i == 1:
                col = col2
            else:
                col = col3

            if not data.empty:
                current_price = data['Close'].iloc[-1]
                high = data['High'].max()
                low = data['Low'].min()
                volume = data['Volume'].sum()
                col.write(f"**{ticker}**")
                col.metric("Current Price", f"${current_price:.2f}")
                col.metric("High", f"${high:.2f}")
                col.metric("Low", f"${low:.2f}")
                col.metric("Total Volume", f"{volume:,.0f}")

        # Line chart tracking all stocks
        combined_data = pd.concat(stocks_data.values(), axis=1)
        combined_data.columns = st.session_state.portfolio_tickers
        st.line_chart(combined_data)

