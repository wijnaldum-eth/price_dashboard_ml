"""
Portfolio Simulator Page - Track and analyze cryptocurrency portfolio.
Calculate portfolio value, allocation, and performance.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from utils.api_client import coingecko_client
from utils.visualizations import create_portfolio_pie_chart

# Page configuration
st.set_page_config(
    page_title="Portfolio - CryptoInsight Pro",
    page_icon="💼",
    layout="wide"
)

# Initialize session state for portfolio
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}


@st.cache_data(ttl=settings.CACHE_TTL_PRICES)
def fetch_current_prices():
    """Fetch current prices for portfolio calculation."""
    try:
        return coingecko_client.get_current_prices(settings.TRACKED_COINS)
    except Exception as e:
        st.error(f"Error fetching prices: {e}")
        return None


def calculate_portfolio_value(holdings, prices):
    """Calculate total portfolio value and breakdown."""
    portfolio_data = []
    total_value = 0
    
    for coin_id, amount in holdings.items():
        if coin_id in prices and amount > 0:
            coin_data = prices[coin_id]
            value = amount * coin_data['current_price']
            total_value += value
            
            portfolio_data.append({
                'coin_id': coin_id,
                'name': coin_data['name'],
                'symbol': coin_data['symbol'],
                'amount': amount,
                'price': coin_data['current_price'],
                'value': value,
                'change_24h': coin_data.get('price_change_percentage_24h', 0)
            })
    
    # Calculate allocation percentages
    for item in portfolio_data:
        item['allocation'] = (item['value'] / total_value * 100) if total_value > 0 else 0
    
    return portfolio_data, total_value


def main():
    st.title("💼 Portfolio Simulator")
    st.markdown("Track and analyze your cryptocurrency portfolio")
    
    # Sidebar for portfolio inputs
    st.sidebar.header("Portfolio Holdings")
    st.sidebar.markdown("Enter your cryptocurrency holdings:")
    
    holdings = {}
    for coin_id in settings.TRACKED_COINS:
        coin_name = settings.COIN_DISPLAY_NAMES[coin_id]
        amount = st.sidebar.number_input(
            coin_name,
            min_value=0.0,
            value=st.session_state.portfolio.get(coin_id, 0.0),
            step=0.1,
            format="%.4f",
            key=f"holding_{coin_id}"
        )
        if amount > 0:
            holdings[coin_id] = amount
    
    # Save and Clear buttons
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("💾 Save Portfolio"):
            st.session_state.portfolio = holdings
            st.success("Portfolio saved!")
    with col2:
        if st.button("🗑️ Clear All"):
            st.session_state.portfolio = {}
            st.rerun()
    
    # Main content
    if not holdings:
        st.info("👆 Enter your cryptocurrency holdings in the sidebar to get started")
        st.markdown("""
        ### How to use:
        1. Enter the amount of each cryptocurrency you own in the sidebar
        2. Click "Save Portfolio" to save your holdings
        3. View your portfolio value, allocation, and performance
        4. Export your portfolio data as CSV
        """)
        return
    
    # Fetch current prices
    with st.spinner("Fetching current prices..."):
        prices = fetch_current_prices()
    
    if not prices:
        st.error("Unable to fetch price data. Please try again later.")
        return
    
    # Calculate portfolio
    portfolio_data, total_value = calculate_portfolio_value(holdings, prices)
    
    if not portfolio_data:
        st.warning("No valid holdings found in your portfolio")
        return
    
    # Display total value
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Total Portfolio Value",
            value=f"${total_value:,.2f}",
            delta=None
        )
    
    with col2:
        # Calculate weighted 24h change
        weighted_change = sum(
            item['change_24h'] * item['allocation'] / 100 
            for item in portfolio_data
        )
        st.metric(
            label="24h Portfolio Change",
            value=f"{weighted_change:.2f}%",
            delta=f"{weighted_change:.2f}%"
        )
    
    with col3:
        st.metric(
            label="Number of Assets",
            value=len(portfolio_data)
        )
    
    st.markdown("---")
    
    # Portfolio breakdown
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Portfolio Allocation")
        
        # Create pie chart
        allocation_data = {item['name']: item['value'] for item in portfolio_data}
        fig = create_portfolio_pie_chart(allocation_data)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Holdings Breakdown")
        
        # Create detailed table
        df = pd.DataFrame(portfolio_data)
        df_display = pd.DataFrame({
            'Asset': df['name'],
            'Amount': df['amount'].apply(lambda x: f"{x:.4f}"),
            'Price': df['price'].apply(lambda x: f"${x:,.2f}"),
            'Value': df['value'].apply(lambda x: f"${x:,.2f}"),
            'Allocation': df['allocation'].apply(lambda x: f"{x:.2f}%"),
            '24h Change': df['change_24h'].apply(lambda x: f"{x:+.2f}%")
        })
        
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True
        )
    
    st.markdown("---")
    
    # Performance metrics
    st.subheader("Performance Analysis")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        top_performer = max(portfolio_data, key=lambda x: x['change_24h'])
        st.metric(
            "Top Performer (24h)",
            top_performer['name'],
            f"{top_performer['change_24h']:+.2f}%"
        )
    
    with col2:
        worst_performer = min(portfolio_data, key=lambda x: x['change_24h'])
        st.metric(
            "Worst Performer (24h)",
            worst_performer['name'],
            f"{worst_performer['change_24h']:+.2f}%"
        )
    
    with col3:
        largest_holding = max(portfolio_data, key=lambda x: x['allocation'])
        st.metric(
            "Largest Holding",
            largest_holding['name'],
            f"{largest_holding['allocation']:.1f}%"
        )
    
    with col4:
        avg_change = sum(item['change_24h'] for item in portfolio_data) / len(portfolio_data)
        st.metric(
            "Average 24h Change",
            f"{avg_change:.2f}%"
        )
    
    # Export functionality
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### Export Portfolio Data")
    
    with col2:
        # Prepare export data
        export_df = pd.DataFrame(portfolio_data)
        export_df['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        export_df['total_portfolio_value'] = total_value
        
        csv = export_df.to_csv(index=False)
        st.download_button(
            label="📥 Export to CSV",
            data=csv,
            file_name=f"portfolio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )


if __name__ == "__main__":
    main()
