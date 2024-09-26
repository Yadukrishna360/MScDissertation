import streamlit as st
import pandas as pd
import time
from datetime import datetime
import plotly.express as px
import yfinance as yf

def fetch_current_price(stock_name):
    """Fetch the current price of the stock using Yahoo Finance."""
    try:
        stock = yf.Ticker(stock_name)
        return stock.history(period="1d")['Close'].iloc[-1]  # Get the latest closing price
    except Exception as e:
        st.error(f"Error fetching price for {stock_name}: {e}")
        return None

def profile_page():
    st.write("## Profile Page")

    if 'profile_stocks' not in st.session_state:
        st.session_state.profile_stocks = []

    stock_name = st.text_input("Stock Name")
    purchase_price = st.number_input("Purchase Price", min_value=0.0, format="%.2f")
    quantity = st.number_input("Quantity", min_value=1)
    purchase_date = st.date_input("Purchase Date", datetime.today())

    if st.button("Add Stock"):
        if stock_name and purchase_price and quantity:
            st.session_state.profile_stocks.append({
                'name': stock_name,
                'purchase_price': purchase_price,
                'quantity': quantity,
                'purchase_date': purchase_date
            })
            st.success("Stock added to profile!")

    if st.session_state.profile_stocks:
        st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)
        st.write(f"<h1 style='font-size: 40px;'>Stocks in Profile:</h1>", unsafe_allow_html=True)

        # Initialize an empty container for displaying the updated stock data
        stock_data_container = st.empty()

        while True:
            # Fetch current prices
            profile_df = pd.DataFrame(st.session_state.profile_stocks)
            profile_df['current_price'] = profile_df['name'].apply(fetch_current_price)
            profile_df['total_investment'] = profile_df['purchase_price'] * profile_df['quantity']
            profile_df['total_profit'] = (profile_df['current_price'] - profile_df['purchase_price']) * profile_df['quantity']
            
            # Update the container with the new stock data
            with stock_data_container.container():
                # Add space of 100 px on top of the metrics
                st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

                # Display metrics in row and column format
                if not profile_df.empty:
                    total_invested = profile_df['total_investment'].sum()
                    total_profit = profile_df['total_profit'].sum()
                    total_amount = total_invested + total_profit

                    # Create columns for metrics
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        Total_amount_col = "yellow"
                        st.markdown(f"<h2 style='font-size: 24px;'>Total Amount:</h2>", unsafe_allow_html=True)
                        st.markdown(f"<h3 style='font-size: 50px;color: {Total_amount_col};'>${total_amount:.2f}</h3>", unsafe_allow_html=True)
                    
                    with col2:
                        Total_invested_col = "blue"
                        st.markdown(f"<h2 style='font-size: 24px;'>Total Invested:</h2>", unsafe_allow_html=True)
                        st.markdown(f"<h3 style='font-size: 50px; color: {Total_invested_col};'>${total_invested:.2f}</h3>", unsafe_allow_html=True)

                    with col3:
                        profit_color = "green" if total_profit >= 0 else "red"
                        st.markdown(f"<h2 style='font-size: 24px;'>Total Profit:</h2>", unsafe_allow_html=True)
                        st.markdown(f"<h3 style='font-size: 50px; color: {profit_color};'>${total_profit:.2f}</h3>", unsafe_allow_html=True)

                    # Add space of 150 px below the metrics
                    st.markdown("<div style='height: 150px;'></div>", unsafe_allow_html=True)

                    # Display each stock in row and column format
                    for index, row in profile_df.iterrows():
                        stock_col1, stock_col2, stock_col3, stock_col4, stock_col5, stock_col6, stock_col7 = st.columns(7)

                        border_style = "border: 1px solid grey; background-color: transparent; padding: 10px;"

                        with stock_col1:
                            st.markdown(f"<div style='{border_style}'><h4 style='font-size: 18px;'>Stock Name:</h4><h4 style='font-size: 25px;'>{row['name']}</h4></div>", unsafe_allow_html=True)

                        with stock_col2:
                            st.markdown(f"<div style='{border_style}'><h4 style='font-size: 18px;'>Purchase Price:</h4><h4 style='font-size: 25px;'>${row['purchase_price']:.2f}</h4></div>", unsafe_allow_html=True)

                        with stock_col3:
                            st.markdown(f"<div style='{border_style}'><h4 style='font-size: 18px;'>Quantity:</h4><h4 style='font-size: 25px;'>{row['quantity']}</h4></div>", unsafe_allow_html=True)

                        with stock_col4:
                            st.markdown(f"<div style='{border_style}'><h4 style='font-size: 18px;'>Current Price:</h4><h4 style='font-size: 25px;'>${row['current_price']:.2f}</h4></div>", unsafe_allow_html=True)

                        with stock_col5:
                            st.markdown(f"<div style='{border_style}'><h4 style='font-size: 18px;'>Total Investment:</h4><h4 style='font-size: 25px;'>${row['total_investment']:.2f}</h4></div>", unsafe_allow_html=True)

                        with stock_col6:
                            profit_color = 'green' if row['total_profit'] >= 0 else 'red'
                            st.markdown(f"<div style='{border_style}'><h4 style='font-size: 18px;'>Total Profit:</h4><h4 style='font-size: 25px; color: {profit_color};'>${row['total_profit']:.2f}</h4></div>", unsafe_allow_html=True)

                        with stock_col7:
                            st.markdown(f"<div style='{border_style}'><h4 style='font-size: 18px;'>Purchase Date:</h4><h4 style='font-size: 25px;'>{row['purchase_date']}</h4></div>", unsafe_allow_html=True)

                    # Display pie chart of stock quantities
                    st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)
                    st.write(f"<h1 style='font-size: 40px;'>Stock distribution chart:</h1>", unsafe_allow_html=True)
                    pie_data = profile_df.groupby('name')['quantity'].sum().reset_index()
                    fig = px.pie(pie_data, names='name', values='quantity', title='Stock Distribution')
                    st.plotly_chart(fig)

            # Wait for 10 seconds before updating
            time.sleep(10)

# To run the app, call the function in the main section
if __name__ == "__main__":
    profile_page()
