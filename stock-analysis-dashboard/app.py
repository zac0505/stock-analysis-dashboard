import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Stock Analysis Dashboard", page_icon="📊", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .main-header {text-align: center; color: #FF6B6B; font-size: 3rem; margin-bottom: 2rem;}
    div[data-testid="metric-container"] {background-color: #262730; border: 1px solid #444; padding: 15px; border-radius: 10px;}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">📊 Stock Analysis Dashboard</h1>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    ticker = st.text_input("Stock Symbol", value="AAPL").upper()
    period = st.selectbox("Time Period", ["1mo", "3mo", "6mo", "1y", "2y"], index=3)
    
    st.markdown("---")
    st.markdown("**Built with:**")
    st.markdown("Python • Streamlit • yfinance")
    st.markdown("**Developer:** [Your Name](https://github.com/zac0505)")

# Tabs
tab1, tab2, tab3 = st.tabs(["📈 Overview", "📊 Technical Analysis", "📰 News & Info"])

# Import modules
try:
    from src.data.fetcher import get_stock_data, get_stock_info
    from src.analysis.technical import calculate_indicators
    from src.visualization.charts import create_price_chart, create_technical_chart
except:
    st.error("Loading modules...")

# Fetch data
@st.cache_data(ttl=300)
def load_data(ticker, period):
    stock = yf.Ticker(ticker)
    data = stock.history(period=period)
    info = stock.info
    news = stock.news[:5] if hasattr(stock, 'news') else []
    return data, info, news

try:
    data, info, news = load_data(ticker, period)
    
    if not data.empty:
        with tab1:
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            current_price = data['Close'].iloc[-1]
            prev_close = data['Close'].iloc[-2] if len(data) > 1 else current_price
            change = current_price - prev_close
            change_pct = (change / prev_close) * 100
            
            col1.metric("Price", f"${current_price:.2f}", f"{change_pct:+.2f}%")
            col2.metric("Volume", f"{data['Volume'].iloc[-1]:,.0f}")
            col3.metric("Market Cap", f"${info.get('marketCap', 0)/1e9:.2f}B" if info.get('marketCap') else "N/A")
            col4.metric("P/E Ratio", f"{info.get('trailingPE', 0):.2f}" if info.get('trailingPE') else "N/A")
            
            # Price Chart
            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=data.index, open=data['Open'], high=data['High'],
                low=data['Low'], close=data['Close'], name='OHLC'
            ))
            fig.update_layout(title=f"{ticker} Price Chart", template="plotly_dark", height=500)
            st.plotly_chart(fig, use_container_width=True)
            
            # Volume Chart
            fig_vol = go.Figure()
            fig_vol.add_trace(go.Bar(x=data.index, y=data['Volume'], name='Volume'))
            fig_vol.update_layout(title="Volume", template="plotly_dark", height=300)
            st.plotly_chart(fig_vol, use_container_width=True)
        
        with tab2:
            # Technical Indicators
            from src.analysis.technical import calculate_indicators
            data_with_indicators = calculate_indicators(data)
            
            # Indicator Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            rsi = data_with_indicators['RSI'].iloc[-1]
            sma20 = data_with_indicators['SMA_20'].iloc[-1]
            
            col1.metric("RSI", f"{rsi:.2f}", "Overbought" if rsi > 70 else "Oversold" if rsi < 30 else "Neutral")
            col2.metric("SMA 20", f"${sma20:.2f}")
            col3.metric("MACD", f"{data_with_indicators['MACD'].iloc[-1]:.4f}")
            col4.metric("Signal", "BUY" if rsi < 30 else "SELL" if rsi > 70 else "HOLD")
            
            # Technical Chart
            from src.visualization.charts import create_technical_chart
            tech_fig = create_technical_chart(data_with_indicators, ticker)
            st.plotly_chart(tech_fig, use_container_width=True)
            
            # RSI Chart
            fig_rsi = go.Figure()
            fig_rsi.add_trace(go.Scatter(x=data_with_indicators.index, y=data_with_indicators['RSI'], name='RSI'))
            fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
            fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
            fig_rsi.update_layout(title="RSI", template="plotly_dark", height=300)
            st.plotly_chart(fig_rsi, use_container_width=True)
        
        with tab3:
            # Company Info
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("Company Overview")
                st.write(info.get('longBusinessSummary', 'No description available.')[:500] + '...')
                
                st.subheader("Recent News")
                for article in news:
                    st.write(f"📰 **{article.get('title')}**")
                    st.caption(f"{article.get('publisher')} • [Read more]({article.get('link')})")
                    st.divider()
            
            with col2:
                st.subheader("Key Stats")
                stats = {
                    "Sector": info.get('sector', 'N/A'),
                    "Industry": info.get('industry', 'N/A'),
                    "Employees": f"{info.get('fullTimeEmployees', 'N/A'):,}",
                    "Beta": f"{info.get('beta', 'N/A'):.2f}" if info.get('beta') else 'N/A',
                    "Dividend Yield": f"{info.get('dividendYield', 0)*100:.2f}%" if info.get('dividendYield') else 'N/A',
                    "52W High": f"${info.get('fiftyTwoWeekHigh', 'N/A'):.2f}" if info.get('fiftyTwoWeekHigh') else 'N/A',
                    "52W Low": f"${info.get('fiftyTwoWeekLow', 'N/A'):.2f}" if info.get('fiftyTwoWeekLow') else 'N/A'
                }
                for key, value in stats.items():
                    st.write(f"**{key}:** {value}")
    else:
        st.error("No data available for this ticker.")
        
except Exception as e:
    st.error(f"Error: {str(e)}")
    st.info("Please check the ticker symbol and try again.")

# Footer
st.markdown("---")
st.markdown("Made withby [YZachary J. Campbell(http://linkedin.com/in/zachary-campbell-9650a72b6) | Data from Yahoo Finance")
