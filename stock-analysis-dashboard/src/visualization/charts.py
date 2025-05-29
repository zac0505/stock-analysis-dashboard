import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_price_chart(data, ticker):
    """Create price chart with volume"""
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                       vertical_spacing=0.03, row_heights=[0.7, 0.3])
    
    fig.add_trace(go.Candlestick(x=data.index, open=data['Open'],
                                high=data['High'], low=data['Low'],
                                close=data['Close'], name='Price'), row=1, col=1)
    
    fig.add_trace(go.Bar(x=data.index, y=data['Volume'], name='Volume'), row=2, col=1)
    
    fig.update_layout(title=f'{ticker} Stock Price', template='plotly_dark',
                     yaxis_title='Price ($)', height=600)
    return fig

def create_technical_chart(data, ticker):
    """Create technical analysis chart"""
    fig = go.Figure()
    
    # Price and moving averages
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name='Close', line=dict(width=2)))
    fig.add_trace(go.Scatter(x=data.index, y=data['SMA_20'], name='SMA 20', line=dict(width=1)))
    fig.add_trace(go.Scatter(x=data.index, y=data['SMA_50'], name='SMA 50', line=dict(width=1)))
    
    # Bollinger Bands
    fig.add_trace(go.Scatter(x=data.index, y=data['BB_Upper'], name='BB Upper',
                           line=dict(color='gray', width=1, dash='dash')))
    fig.add_trace(go.Scatter(x=data.index, y=data['BB_Lower'], name='BB Lower',
                           line=dict(color='gray', width=1, dash='dash'),
                           fill='tonexty', fillcolor='rgba(128,128,128,0.2)'))
    
    fig.update_layout(title=f'{ticker} Technical Analysis', template='plotly_dark',
                     yaxis_title='Price ($)', height=500)
    return fig
