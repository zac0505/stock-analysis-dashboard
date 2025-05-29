import yfinance as yf
import pandas as pd
import streamlit as st

@st.cache_data(ttl=300)
def get_stock_data(ticker, period="1y"):
    """Fetch stock data"""
    try:
        stock = yf.Ticker(ticker)
        return stock.history(period=period)
    except:
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def get_stock_info(ticker):
    """Get company info"""
    try:
        return yf.Ticker(ticker).info
    except:
        return {}
