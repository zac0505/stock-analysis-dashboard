import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np  # Added missing import
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import random

# Page config
st.set_page_config(
    page_title="Stock Intelligence Dashboard", 
    page_icon="📈", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
    }
    
    .main-header {
        font-size: 3.5rem;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    
    .sub-header {
        text-align: center;
        color: #888;
        font-size: 1.2rem;
        margin-bottom: 3rem;
    }
    
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 15px;
        backdrop-filter: blur(10px);
    }
    
    .info-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
    }
    
    .price-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border: 1px solid rgba(102, 126, 234, 0.3);
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .demo-mode {
        background: rgba(255, 193, 7, 0.1);
        border: 1px solid rgba(255, 193, 7, 0.3);
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 20px;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.05);
        padding: 10px;
        border-radius: 15px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 24px;
        background: transparent;
        border-radius: 10px;
        color: #fff;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">Stock Intelligence Hub</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Professional Market Analysis & Insights</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🎯 Control Panel")
    
    ticker = st.text_input(
        "Stock Symbol",
        value="AAPL",
        help="Enter stock ticker (e.g., AAPL, GOOGL, TSLA)"
    ).upper()
    
    period = st.selectbox(
        "Analysis Period",
        options=["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y"],
        index=5,
        help="Select time period for analysis"
    )
    
    st.markdown("---")
    
    # Mode selector with default to Demo Mode
    mode = st.radio(
        "Data Mode",
        ["Demo Mode", "Live Data"],
        index=0,  # Default to Demo Mode
        help="Demo Mode recommended due to API limits"
    )
    
    if mode == "Live Data":
        st.warning("⚠️ Live data may be rate limited. Switch to Demo Mode if you experience issues.")
    
    st.markdown("---")
    
    # Developer info
    st.markdown("### 👨‍💻 Developer")
    st.markdown("**Zachary J. Campbell**")
    st.markdown("[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue)](https://linkedin.com/in/zachary-campbell-9650a72b6)")
    st.markdown("[![GitHub](https://img.shields.io/badge/GitHub-Follow-black)](https://github.com/zac0505)")

# Generate demo data
def generate_demo_data(ticker, days=252):
    """Generate realistic demo data"""
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    
    # Base prices for popular stocks
    base_prices = {
        "AAPL": 175.50,
        "GOOGL": 142.30,
        "TSLA": 238.45,
        "MSFT": 378.90,
        "AMZN": 155.20,
        "META": 345.60,
        "NVDA": 495.30
    }
    
    base_price = base_prices.get(ticker, 100 + random.uniform(50, 200))
    
    # Generate realistic price movement
    returns = np.random.normal(0.0005, 0.015, days)
    price = base_price * (1 + returns).cumprod()
    
    # Add some trend
    trend = np.linspace(0, 0.2, days) * (1 if random.random() > 0.5 else -1)
    price = price * (1 + trend * 0.5)
    
    # Create OHLC data
    data = pd.DataFrame(index=dates)
    data['Close'] = price
    data['Open'] = price * (1 + np.random.normal(0, 0.003, days))
    data['High'] = np.maximum(data['Open'], data['Close']) * (1 + np.abs(np.random.normal(0, 0.005, days)))
    data['Low'] = np.minimum(data['Open'], data['Close']) * (1 - np.abs(np.random.normal(0, 0.005, days)))
    data['Volume'] = np.random.randint(10_000_000, 100_000_000, days)
    
    return data

# Simplified data fetching for live mode
@st.cache_data(ttl=300)
def get_stock_data_simple(symbol, period):
    """Simple data fetch with minimal API calls"""
    try:
        # Download data without fetching info to reduce API calls
        data = yf.download(symbol, period=period, progress=False, show_errors=False)
        
        if data.empty:
            return None, "No data available for this symbol"
        
        # Clean column names if multi-level
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        
        return data, None
        
    except Exception as e:
        return None, f"Error: {str(e)}"

# Main app logic
if mode == "Demo Mode":
    st.markdown("""
    <div class="demo-mode">
        🎭 <b>Demo Mode Active</b> - Using simulated data for demonstration
    </div>
    """, unsafe_allow_html=True)
    
    # Generate demo data
    data = generate_demo_data(ticker)
    error = None
    
else:
    # Live data mode
    with st.spinner(f"🔄 Fetching live data for {ticker}..."):
        data, error = get_stock_data_simple(ticker, period)

# Display data
if error and mode == "Live Data":
    st.error(f"⚠️ {error}")
    st.info("💡 Switch to **Demo Mode** to explore the dashboard with simulated data")
    
    # Add button to switch to demo mode
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🎭 Switch to Demo Mode", type="primary", use_container_width=True):
            st.rerun()
            
elif data is not None and not data.empty:
    # Calculate metrics
    current_price = data['Close'].iloc[-1]
    prev_close = data['Close'].iloc[-2] if len(data) > 1 else current_price
    price_change = current_price - prev_close
    price_change_pct = (price_change / prev_close) * 100 if prev_close != 0 else 0
    
    # Price Card
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div class="price-card">
            <div style="font-size: 2rem; font-weight: 700; color: #fff;">{ticker}</div>
            <div style="font-size: 3.5rem; font-weight: 700; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                ${current_price:.2f}
            </div>
            <div style="font-size: 1.2rem; color: {'#4ade80' if price_change >= 0 else '#f87171'};">
                {'+' if price_change >= 0 else ''}{price_change:.2f} ({price_change_pct:+.2f}%)
            </div>
            {f'<div style="font-size: 0.9rem; color: #666; margin-top: 10px;">Demo Data</div>' if mode == "Demo Mode" else ''}
        </div>
        """, unsafe_allow_html=True)
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        volume = data['Volume'].iloc[-1]
        st.metric("Volume", f"{volume:,.0f}")
    
    with col2:
        day_high = data['High'].iloc[-1]
        day_low = data['Low'].iloc[-1]
        st.metric("Day Range", f"${day_low:.2f} - ${day_high:.2f}")
    
    with col3:
        high_52w = data['High'].max()
        st.metric("52W High", f"${high_52w:.2f}")
    
    with col4:
        low_52w = data['Low'].min()
        st.metric("52W Low", f"${low_52w:.2f}")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📈 Price Chart", "📊 Technical Analysis", "📰 Market Overview"])
    
    with tab1:
        # Candlestick chart
        fig = go.Figure()
        
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name='OHLC',
            increasing_line_color='#4ade80',
            decreasing_line_color='#f87171'
        ))
        
        # Add moving averages if enough data
        if len(data) >= 20:
            sma20 = data['Close'].rolling(20).mean()
            fig.add_trace(go.Scatter(
                x=data.index,
                y=sma20,
                name='SMA 20',
                line=dict(color='#fbbf24', width=2)
            ))
        
        if len(data) >= 50:
            sma50 = data['Close'].rolling(50).mean()
            fig.add_trace(go.Scatter(
                x=data.index,
                y=sma50,
                name='SMA 50',
                line=dict(color='#60a5fa', width=2)
            ))
        
        fig.update_layout(
            title=f"{ticker} Price Movement {'(Demo)' if mode == 'Demo Mode' else ''}",
            yaxis_title="Price ($)",
            template="plotly_dark",
            height=600,
            xaxis_rangeslider_visible=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#fff')
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Volume chart
        colors = ['#f87171' if data['Close'].iloc[i] < data['Open'].iloc[i] else '#4ade80' 
                  for i in range(len(data))]
        
        fig_vol = go.Figure()
        fig_vol.add_trace(go.Bar(
            x=data.index,
            y=data['Volume'],
            marker_color=colors,
            name='Volume'
        ))
        
        fig_vol.update_layout(
            title="Trading Volume",
            yaxis_title="Volume",
            template="plotly_dark",
            height=300,
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig_vol, use_container_width=True)
    
    with tab2:
        st.markdown("### 📊 Technical Indicators")
        
        # Calculate basic indicators
        col1, col2, col3 = st.columns(3)
        
        # RSI Calculation
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]
        
        with col1:
            st.markdown(f"""
            <div class="info-card" style="text-align: center;">
                <h3 style="color: #888;">RSI (14)</h3>
                <h2 style="color: {'#f87171' if current_rsi > 70 else '#4ade80' if current_rsi < 30 else '#fbbf24'}">
                    {current_rsi:.2f}
                </h2>
                <p style="color: #666;">{'Overbought' if current_rsi > 70 else 'Oversold' if current_rsi < 30 else 'Neutral'}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Simple MACD
            ema12 = data['Close'].ewm(span=12).mean()
            ema26 = data['Close'].ewm(span=26).mean()
            macd = ema12 - ema26
            signal = macd.ewm(span=9).mean()
            macd_current = macd.iloc[-1]
            signal_current = signal.iloc[-1]
            
            st.markdown(f"""
            <div class="info-card" style="text-align: center;">
                <h3 style="color: #888;">MACD</h3>
                <h2 style="color: {'#4ade80' if macd_current > signal_current else '#f87171'}">
                    {macd_current:.4f}
                </h2>
                <p style="color: #666;">{'Bullish' if macd_current > signal_current else 'Bearish'}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            # Price vs SMA
            if len(data) >= 20:
                sma20_current = data['Close'].rolling(20).mean().iloc[-1]
                above_sma = current_price > sma20_current
                
                st.markdown(f"""
                <div class="info-card" style="text-align: center;">
                    <h3 style="color: #888;">SMA 20</h3>
                    <h2 style="color: {'#4ade80' if above_sma else '#f87171'}">
                        ${sma20_current:.2f}
                    </h2>
                    <p style="color: #666;">Price {'Above' if above_sma else 'Below'}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # RSI Chart
        st.markdown("### RSI Trend")
        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(
            x=data.index,
            y=rsi,
            name='RSI',
            line=dict(color='#fbbf24', width=2)
        ))
        
        fig_rsi.add_hline(y=70, line_dash="dash", line_color="#f87171", annotation_text="Overbought")
        fig_rsi.add_hline(y=30, line_dash="dash", line_color="#4ade80", annotation_text="Oversold")
        
        fig_rsi.update_layout(
            yaxis_title="RSI",
            template="plotly_dark",
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig_rsi, use_container_width=True)
    
    with tab3:
        st.markdown("### 📊 Market Overview")
        
        # Performance metrics
        col1, col2 = st.columns(2)
        
        with col1:
            # Calculate performance
            week_ago = data['Close'].iloc[-5] if len(data) >= 5 else current_price
            month_ago = data['Close'].iloc[-22] if len(data) >= 22 else current_price
            year_start = data['Close'].iloc[0]
            
            week_perf = ((current_price - week_ago) / week_ago * 100) if week_ago != 0 else 0
            month_perf = ((current_price - month_ago) / month_ago * 100) if month_ago != 0 else 0
            ytd_perf = ((current_price - year_start) / year_start * 100) if year_start != 0 else 0
            
            st.markdown(f"""
            <div class="info-card">
                <h3>Performance Summary</h3>
                <p><b>1 Week:</b> <span style="color: {'#4ade80' if week_perf > 0 else '#f87171'}">{week_perf:+.2f}%</span></p>
                <p><b>1 Month:</b> <span style="color: {'#4ade80' if month_perf > 0 else '#f87171'}">{month_perf:+.2f}%</span></p>
                <p><b>YTD:</b> <span style="color: {'#4ade80' if ytd_perf > 0 else '#f87171'}">{ytd_perf:+.2f}%</span></p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Trading stats
            avg_volume = data['Volume'].mean()
            volume_today = data['Volume'].iloc[-1]
            volume_ratio = (volume_today / avg_volume) if avg_volume != 0 else 1
            
            # Simple volatility
            returns = data['Close'].pct_change().dropna()
            volatility = returns.std() * np.sqrt(252) * 100  # Annualized
            
            st.markdown(f"""
            <div class="info-card">
                <h3>Trading Statistics</h3>
                <p><b>Avg Volume:</b> {avg_volume/1e6:.1f}M</p>
                <p><b>Volume Ratio:</b> {volume_ratio:.2f}x</p>
                <p><b>Volatility:</b> {volatility:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Info section
        st.markdown("### 📰 Additional Information")
        
        if mode == "Demo Mode":
            st.info("📊 This is demo data for demonstration purposes. Switch to Live Data mode for real market data.")
        else:
            st.success("✅ Showing live market data")
        
        st.markdown("""
        <div class="info-card">
            <h4>About This Dashboard</h4>
            <p>This professional stock analysis dashboard provides real-time market data, technical indicators, 
            and comprehensive analysis tools. Built with modern web technologies and designed for optimal user experience.</p>
            <br>
            <p><b>Features:</b></p>
            <ul>
                <li>Real-time price data and charts</li>
                <li>Technical indicators (RSI, MACD, SMA)</li>
                <li>Volume analysis</li>
                <li>Performance metrics</li>
                <li>Responsive design</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

else:
    st.error("Unable to load data. Please try again or switch to Demo Mode.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px 0;">
    <p>Built with ❤️ by <a href="https://linkedin.com/in/zachary-campbell-9650a72b6" style="color: #667eea;">Zachary J. Campbell</a></p>
    <p style="font-size: 0.9rem;">Data provided by Yahoo Finance • Professional Stock Analysis Dashboard</p>
</div>
""", unsafe_allow_html=True)
