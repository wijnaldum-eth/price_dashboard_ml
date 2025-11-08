"""
Market Overview Page - Real-time cryptocurrency price tracker.
Displays top cryptocurrencies with live prices, changes, and sparklines.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from utils.pyth_client import pyth_client
from utils.cache_manager import cache_manager
from utils.data_processing import normalize_prices
from utils.visualizations import create_price_chart, create_comparison_chart
from utils.exceptions import CoinGeckoAPIError

# Page configuration
st.set_page_config(
    page_title="Market Overview - CryptoInsight Pro",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .metric-card {
        background-color: #1E293B;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #374151;
    }
    .positive { color: #10B981; }
    .negative { color: #EF4444; }
    </style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=settings.CACHE_TTL_PRICES)
def fetch_market_data(force_refresh=False):
    """Fetch current market data for tracked coins."""
    try:
        data = pyth_client.get_current_prices(settings.TRACKED_COINS)
        return data
    except Exception as e:
        st.error(f"Error fetching market data: {e}")
        return None


def render_metric_card(coin_data, col):
    """Render a metric card for a cryptocurrency."""
    with col:
        # Price change color
        change_24h = coin_data.get('price_change_percentage_24h', 0)
        color_class = 'positive' if change_24h >= 0 else 'negative'
        arrow = '▲' if change_24h >= 0 else '▼'
        
        st.markdown(f"""
            <div class="metric-card">
                <h3>{coin_data['name']} ({coin_data['symbol']})</h3>
                <h2>${coin_data['current_price']:,.2f}</h2>
                <p class="{color_class}">
                    {arrow} {abs(change_24h):.2f}% (24h)
                </p>
                <p style="font-size: 0.9em; color: #9CA3AF;">
                    Market Cap: ${coin_data['market_cap']:,.0f}<br>
                    Volume: ${coin_data['total_volume']:,.0f}
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Sparkline
        if coin_data.get('sparkline_7d'):
            sparkline_data = coin_data['sparkline_7d']
            if sparkline_data:
                st.line_chart(sparkline_data, height=60)


def main():
    st.title("📊 Market Overview")
    st.markdown("Real-time cryptocurrency prices and market data")
    
    # Header with refresh button
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    with col2:
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()
    with col3:
        cache_stats = cache_manager.get_stats()
        st.markdown(f"**Cache Hit Rate:** {cache_stats['hit_rate']}")
    
    st.markdown("---")
    
    # Fetch market data
    with st.spinner("Fetching market data..."):
        market_data = fetch_market_data()
    
    if not market_data:
        st.error("Unable to fetch market data. Please try again later.")
        return
    
    # Display metric cards in grid
    st.subheader("Top Cryptocurrencies")
    
    # Create 5 columns for top 5 coins
    cols = st.columns(5)
    for idx, (coin_id, coin_data) in enumerate(list(market_data.items())[:5]):
        render_metric_card(coin_data, cols[idx])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Second row for next 5 coins
    cols = st.columns(5)
    for idx, (coin_id, coin_data) in enumerate(list(market_data.items())[5:10]):
        render_metric_card(coin_data, cols[idx])
    
    st.markdown("---")
    
    # Price Comparison Section
    st.subheader("📈 Price Comparison")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # Coin selection
        coin_options = {settings.COIN_DISPLAY_NAMES[coin_id]: coin_id 
                       for coin_id in settings.TRACKED_COINS}
        
        selected_coins = st.multiselect(
            "Select coins to compare (2-5)",
            options=list(coin_options.keys()),
            default=list(coin_options.keys())[:3],
            max_selections=5
        )
        
        time_period = st.selectbox(
            "Time Period",
            options=["7 days", "30 days", "90 days"],
            index=1
        )
        
        normalize = st.checkbox("Normalize prices", value=True)
    
    with col2:
        if len(selected_coins) >= 2:
            # Map display names back to coin IDs
            selected_coin_ids = [coin_options[name] for name in selected_coins]
            
            # Determine days based on selection
            days_map = {"7 days": 7, "30 days": 30, "90 days": 90}
            days = days_map[time_period]
            
            try:
                with st.spinner("Loading price data..."):
                    # Fetch historical data for selected coins
                    comparison_data = {}
                    for coin_id in selected_coin_ids:
                        df = pyth_client.get_historical_data(coin_id, days=days)
                        if normalize:
                            df = normalize_prices(df)
                        comparison_data[coin_id] = df
                    
                    # Create comparison chart
                    if normalize:
                        fig = create_comparison_chart(comparison_data, selected_coins)
                    else:
                        # Create regular price chart
                        fig = create_price_chart(
                            list(comparison_data.values())[0],
                            f"{selected_coins[0]} Price History"
                        )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Comparison table
                    st.subheader("Comparison Metrics")
                    comparison_table = []
                    for coin_id in selected_coin_ids:
                        coin_data = market_data[coin_id]
                        comparison_table.append({
                            'Coin': coin_data['name'],
                            'Price': f"${coin_data['current_price']:,.2f}",
                            '24h Change': f"{coin_data['price_change_percentage_24h']:.2f}%",
                            '7d Change': f"{coin_data.get('price_change_percentage_7d', 0):.2f}%",
                            'Market Cap': f"${coin_data['market_cap']:,.0f}",
                            'Volume': f"${coin_data['total_volume']:,.0f}"
                        })
                    
                    st.dataframe(
                        pd.DataFrame(comparison_table),
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Export button
                    csv = pd.DataFrame(comparison_table).to_csv(index=False)
                    st.download_button(
                        label="📥 Export to CSV",
                        data=csv,
                        file_name=f"crypto_comparison_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                    
            except Exception as e:
                st.error(f"Error loading comparison data: {e}")
        else:
            st.info("Please select at least 2 coins to compare")
    
    # Auto-refresh every 60 seconds
    if st.session_state.get('auto_refresh', False):
        import time
        time.sleep(60)
        st.rerun()


if __name__ == "__main__":
    main()
