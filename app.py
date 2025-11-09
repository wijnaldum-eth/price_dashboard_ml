import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import settings
from utils.pyth_client import pyth_client
from utils.exceptions import APIError

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

# Pyth Network API functions
@st.cache_data(ttl=settings.CACHE_TTL_PRICES)
def get_top_cryptos(limit=10):
    """Fetch top N cryptocurrencies from Pyth Network"""
    try:
        # Get tracked coins from settings
        coin_ids = settings.TRACKED_COINS[:limit]
        prices_data = pyth_client.get_current_prices(coin_ids)
        
        # Convert to list format expected by the UI
        result = []
        for coin_id, data in prices_data.items():
            result.append(data)
        
        return result
    except APIError as e:
        st.error(f"Pyth Network API Error: {str(e)}")
        return []
    except Exception as e:
        st.error(f"Error fetching data from Pyth Network: {str(e)}")
        return []

@st.cache_data(ttl=settings.CACHE_TTL_HISTORICAL)
def get_coin_data(coin_id, days=30):
    """Fetch historical data for a specific coin from Pyth Network"""
    try:
        df = pyth_client.get_historical_data(coin_id, days=days)
        
        # Convert DataFrame to the format expected by process_historical_data
        if not df.empty:
            # Convert to millisecond timestamps and create prices array
            prices = [[int(ts.timestamp() * 1000), price] 
                     for ts, price in zip(df['timestamp'], df['price'])]
            return {'prices': prices, 'market_caps': [], 'total_volumes': []}
        else:
            return {'prices': [], 'market_caps': [], 'total_volumes': []}
    except APIError as e:
        st.warning(f"Could not fetch historical data: {str(e)}")
        return {'prices': [], 'market_caps': [], 'total_volumes': []}
    except Exception as e:
        st.warning(f"Error processing historical data: {str(e)}")
        return {'prices': [], 'market_caps': [], 'total_volumes': []}

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
    
    # Get top cryptocurrencies from Pyth Network
    top_coins = get_top_cryptos(limit=10)
    
    if top_coins and len(top_coins) > 0:
        try:
            # Build coin selection lists
            coin_names = [f"{coin['name']} ({coin['symbol']})" for coin in top_coins]
            coin_ids = [coin['id'] for coin in top_coins]
            
            # Find current selection index
            current_index = 0
            if 'selected_coin' in st.session_state and st.session_state.selected_coin in coin_ids:
                current_index = coin_ids.index(st.session_state.selected_coin)
            
            # Coin selection dropdown
            selected_coin_name = st.sidebar.selectbox(
                "Select Cryptocurrency",
                coin_names,
                index=current_index,
                key="coin_selector"
            )
            
            # Update session state
            new_coin_id = coin_ids[coin_names.index(selected_coin_name)]
            if st.session_state.selected_coin != new_coin_id:
                st.session_state.selected_coin = new_coin_id
                st.rerun()
            
        except Exception as e:
            st.sidebar.error(f"Error processing coin data: {str(e)}")
            # Fallback to default
            if 'selected_coin' not in st.session_state:
                st.session_state.selected_coin = 'bitcoin'
    else:
        st.sidebar.warning("Unable to load cryptocurrency list from Pyth Network")
        # Fallback to default
        if 'selected_coin' not in st.session_state:
            st.session_state.selected_coin = 'bitcoin'
    
    st.sidebar.markdown("---")
    st.sidebar.info("ℹ️ Real-time data powered by Pyth Network 🔮")
    
    return time_period

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
    time_period = render_sidebar()
    
    # Main content
    st.title("📊 CryptoInsight Pro")
    st.markdown("Real-time cryptocurrency market intelligence powered by **Pyth Network** 🔮")
    
    # Get top coins data
    top_coins = get_top_cryptos(limit=10)
    
    if not top_coins or len(top_coins) == 0:
        st.error("Unable to load cryptocurrency data. Please try again later.")
        st.info("This may be due to API rate limits or network issues.")
        return
    
    try:
        # Get and display coin data
        coin_data = next((coin for coin in top_coins 
                         if coin['id'] == st.session_state.selected_coin), None)
        
        if coin_data:
            # Metrics row
            render_metrics(coin_data)
            
            # Chart section
            st.markdown("---")
            
            # Map time period to days
            days_map = {"24h": 1, "7d": 7, "30d": 30, "90d": 90, "1y": 365}
            days = days_map.get(time_period, 30)
            
            historical_data = get_coin_data(st.session_state.selected_coin, days=days)
            df_historical = process_historical_data(historical_data, days=days)
            
            if not df_historical.empty:
                render_price_chart(df_historical)
            else:
                st.warning(f"No historical data available for {coin_data['name']}")
            
            # AI Insights
            st.markdown("---")
            render_ai_insights(coin_data)
        else:
            st.error(f"Could not find data for selected coin: {st.session_state.selected_coin}")
            st.info("Please select a different cryptocurrency from the sidebar.")
            
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("Please try selecting a different cryptocurrency or refresh the page.")

if __name__ == "__main__":
    main()
