import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from datetime import datetime, timedelta
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import settings

# Validate configuration
try:
    settings.validate()
except ValueError as e:
    st.error(f"Configuration Error: {e}")
    st.info("Please check your .env file and ensure all required variables are set.")
    st.stop()

# Configure page
st.set_page_config(
    page_title=settings.PAGE_TITLE,
    page_icon=settings.PAGE_ICON,
    layout=settings.LAYOUT,
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    .stButton>button {
        background-color: #4F46E5;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background-color: #4338CA;
        color: white;
    }
    .metric-card {
        background-color: #1E293B;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'selected_coin' not in st.session_state:
    st.session_state.selected_coin = 'bitcoin'

# CoinGecko API functions
def get_top_cryptos(limit=10):
    """Fetch top N cryptocurrencies by market cap"""
    url = f"https://api.coingecko.com/api/v3/coins/markets"
    params = {
        'vs_currency': 'usd',
        'order': 'market_cap_desc',
        'per_page': limit,
        'page': 1,
        'sparkline': False,
        'price_change_percentage': '24h,7d'
    }
    response = requests.get(url, params=params)
    return response.json()

def get_coin_data(coin_id, days=30):
    """Fetch historical data for a specific coin"""
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        'vs_currency': 'usd',
        'days': days,
        'interval': 'daily'
    }
    response = requests.get(url, params=params)
    return response.json()

def get_coin_info(coin_id):
    """Fetch detailed information about a specific coin"""
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    response = requests.get(url)
    return response.json()

# Data processing functions
def process_market_data(data):
    """Process market data into a pandas DataFrame"""
    df = pd.DataFrame(data)
    if not df.empty:
        # Convert timestamp to datetime
        df['last_updated'] = pd.to_datetime(df['last_updated'])
        # Format market cap and volume
        df['market_cap'] = df['market_cap'].apply(lambda x: f"${x:,.0f}")
        df['total_volume'] = df['total_volume'].apply(lambda x: f"${x:,.0f}")
    return df

def process_historical_data(data, days=30):
    """Process historical price data"""
    prices = data.get('prices', [])
    if not prices:
        return pd.DataFrame()
    
    df = pd.DataFrame(prices, columns=['timestamp', 'price'])
    df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
    df = df.set_index('date')
    return df

# UI Components
def render_sidebar():
    """Render the sidebar with coin selection and filters"""
    st.sidebar.title("🔍 Navigation")
    
    # Time period selection
    time_period = st.sidebar.selectbox(
        "Time Period",
        ["24h", "7d", "30d", "90d", "1y"],
        index=2
    )
    
    # Get top 10 cryptocurrencies
    try:
        top_coins = get_top_cryptos(limit=10)
        coin_names = [f"{coin['name']} ({coin['symbol'].upper()})" for coin in top_coins]
        coin_ids = [coin['id'] for coin in top_coins]
        
        # Coin selection
        selected_coin_name = st.sidebar.selectbox(
            "Select Cryptocurrency",
            coin_names,
            index=0
        )
        st.session_state.selected_coin = coin_ids[coin_names.index(selected_coin_name)]
        
    except Exception as e:
        st.sidebar.error(f"Error fetching coin data: {str(e)}")
    
    st.sidebar.markdown("---")
    st.sidebar.info("ℹ️ Data provided by CoinGecko API")

def render_metrics(coin_data):
    """Render key metrics for the selected coin"""
    if not coin_data:
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Current Price", f"${coin_data['current_price']:,.2f}")
    with col2:
        price_change_24h = coin_data.get('price_change_percentage_24h', 0)
        st.metric("24h Change", f"{price_change_24h:.2f}%", 
                 delta_color="inverse" if price_change_24h < 0 else "normal")
    with col3:
        st.metric("Market Cap", f"${coin_data['market_cap']:,.0f}")
    with col4:
        st.metric("24h Volume", f"${coin_data['total_volume']:,.0f}")

def render_price_chart(historical_data):
    """Render the main price chart"""
    if historical_data.empty:
        st.warning("No historical data available")
        return
    
    fig = go.Figure()
    
    # Add price line
    fig.add_trace(go.Scatter(
        x=historical_data.index,
        y=historical_data['price'],
        mode='lines',
        name='Price (USD)',
        line=dict(color='#4F46E5', width=2),
        hovertemplate='%{y:$,.2f}<extra></extra>'
    ))
    
    # Update layout
    fig.update_layout(
        title=f"{st.session_state.selected_coin.upper()} Price History",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        template="plotly_dark",
        hovermode="x unified",
        margin=dict(l=50, r=50, t=50, b=50),
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_ai_insights(coin_data):
    """Render AI-powered insights section"""
    st.header("🤖 AI-Powered Insights")
    
    # Placeholder for AI insights
    with st.expander("View Market Analysis", expanded=True):
        st.write("""
        **Market Sentiment**: The current market shows positive momentum with increasing trading volume.
        
        **Technical Analysis**: 
        - RSI: 65 (Approaching overbought territory)
        - MACD: Bullish crossover detected
        - Support: $45,000
        - Resistance: $52,000
        
        **Recommendation**: Consider taking partial profits if the price approaches the resistance level.
        """)
    
    with st.expander("News & Social Sentiment", expanded=False):
        st.write("""
        - 🚀 Major exchange listing announcement expected soon
        - 📈 Social media sentiment: 78% positive
        - 📰 Recent news: Institutional adoption increasing
        """)

# Main app
def main():
    # Sidebar
    render_sidebar()
    
    # Main content
    st.title("📊 CryptoInsight Pro")
    st.markdown("Real-time cryptocurrency market intelligence and analytics")
    
    try:
        # Get and display coin data
        coin_data = next((coin for coin in get_top_cryptos(limit=10) 
                         if coin['id'] == st.session_state.selected_coin), None)
        
        if coin_data:
            # Metrics row
            render_metrics(coin_data)
            
            # Chart section
            st.markdown("---")
            historical_data = get_coin_data(st.session_state.selected_coin, days=30)
            df_historical = process_historical_data(historical_data)
            render_price_chart(df_historical)
            
            # AI Insights
            st.markdown("---")
            render_ai_insights(coin_data)
            
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("Please check your internet connection and try again.")

if __name__ == "__main__":
    main()
