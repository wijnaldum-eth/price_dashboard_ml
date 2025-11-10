"""
Predictions Page - LSTM Time-Series Forecasting.
Displays 7-day cryptocurrency price predictions with confidence intervals.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from utils.ml_models import get_lstm_predictor
from utils.database import db_manager
from utils.exceptions import ModelError

# Page configuration
st.set_page_config(
    page_title="Price Predictions - CryptoInsight Pro",
    page_icon="📈",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .prediction-card {
        background-color: #1E293B;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #374151;
        margin: 1rem 0;
    }
    .metric-highlight {
        background-color: #0F172A;
        padding: 1rem;
        border-radius: 6px;
        border-left: 4px solid #3B82F6;
    }
    .forecast-positive { color: #10B981; font-weight: bold; }
    .forecast-negative { color: #EF4444; font-weight: bold; }
    .confidence-band {
        fill: rgba(59, 130, 246, 0.1);
        stroke: rgba(59, 130, 246, 0.3);
    }
    </style>
""", unsafe_allow_html=True)


def create_prediction_chart(historical_data, predictions_data, coin_name):
    """Create interactive prediction chart with historical + forecast data."""

    # Historical data
    hist_df = pd.DataFrame(historical_data)
    hist_df['timestamp'] = pd.to_datetime(hist_df['timestamp'], utc=True, errors='coerce')
    hist_df = hist_df.dropna(subset=['timestamp']).sort_values('timestamp')

    # Predictions data
    pred_dates = [pd.to_datetime(date, utc=True, errors='coerce') for date in predictions_data['dates']]
    pred_dates = [d for d in pred_dates if pd.notna(d)]  # Filter out NaT values
    pred_prices = predictions_data['predictions'][:len(pred_dates)]  # Trim to match dates
    pred_lower = predictions_data['confidence_intervals']['lower'][:len(pred_dates)]
    pred_upper = predictions_data['confidence_intervals']['upper'][:len(pred_dates)]

    # Create figure
    fig = go.Figure()

    # Historical prices
    fig.add_trace(go.Scatter(
        x=hist_df['timestamp'],
        y=hist_df['price'],
        mode='lines',
        name='Historical Price',
        line=dict(color='#3B82F6', width=2),
        hovertemplate='%{x}<br>$%{y:,.2f}<extra></extra>'
    ))

    # Prediction line
    fig.add_trace(go.Scatter(
        x=pred_dates,
        y=pred_prices,
        mode='lines+markers',
        name='7-Day Forecast',
        line=dict(color='#10B981', width=3, dash='dot'),
        marker=dict(size=8, symbol='diamond'),
        hovertemplate='%{x}<br>Forecast: $%{y:,.2f}<extra></extra>'
    ))

    # Confidence interval
    fig.add_trace(go.Scatter(
        x=pred_dates + pred_dates[::-1],
        y=pred_upper + pred_lower[::-1],
        fill='toself',
        fillcolor='rgba(16, 185, 129, 0.2)',
        line=dict(color='rgba(16, 185, 129, 0.3)'),
        name='95% Confidence Interval',
        hoverinfo='skip'
    ))

    # Update layout
    fig.update_layout(
        title=f"{coin_name} Price Prediction - Next 7 Days",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        hovermode="x unified",
        template="plotly_dark",
        height=500,
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )

    # Format y-axis as currency
    fig.update_yaxes(tickprefix="$", tickformat=",.0f")

    return fig


def display_model_metrics(predictor):
    """Display model performance metrics."""

    info = predictor.get_model_info()
    metrics = info.get('metadata', {}).get('metrics', {})

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Model Type",
            "LSTM Neural Network",
            help="Long Short-Term Memory recurrent neural network"
        )

    with col2:
        st.metric(
            "Training Data",
            f"{info.get('sequence_length', 30)} Days",
            help="Historical data window used for training"
        )

    with col3:
        if metrics:
            st.metric(
                "Model Accuracy",
                f"{100 - metrics.get('mape', 0):.1f}%",
                help=f"Mean Absolute Percentage Error: {metrics.get('mape', 0):.1f}%"
            )
        else:
            st.metric("Model Accuracy", "N/A")

    with col4:
        last_trained = info.get('metadata', {}).get('training_date', 'Unknown')
        if last_trained != 'Unknown':
            try:
                dt = pd.to_datetime(last_trained, utc=True, errors='coerce')
                if pd.notna(dt):
                    days_ago = (datetime.now(dt.tzinfo) - dt).days
                    st.metric(
                        "Last Trained",
                        f"{days_ago} days ago" if days_ago > 0 else "Today"
                    )
                else:
                    st.metric("Last Trained", "Recently")
            except:
                st.metric("Last Trained", "Recently")
        else:
            st.metric("Last Trained", "Unknown")


def main():
    """Main page function."""

    st.title("📈 Price Predictions")
    st.markdown("**LSTM Time-Series Forecasting** - 7-day cryptocurrency price predictions")

    # Sidebar controls
    st.sidebar.header("⚙️ Prediction Settings")

    # Coin selector
    available_coins = ['bitcoin', 'ethereum', 'solana', 'cardano', 'polkadot']
    coin_display_names = {
        'bitcoin': 'Bitcoin (BTC)',
        'ethereum': 'Ethereum (ETH)',
        'solana': 'Solana (SOL)',
        'cardano': 'Cardano (ADA)',
        'polkadot': 'Polkadot (DOT)'
    }

    selected_coin = st.sidebar.selectbox(
        "Select Cryptocurrency",
        options=available_coins,
        format_func=lambda x: coin_display_names[x],
        help="Choose a cryptocurrency to generate price predictions"
    )

    # Forecast button
    generate_forecast = st.sidebar.button(
        "🔮 Generate Forecast",
        type="primary",
        use_container_width=True
    )

    # Model info section
    with st.sidebar.expander("ℹ️ Model Information"):
        st.markdown("""
        **LSTM Neural Network**
        - **Architecture**: 50 LSTM units × 2 layers
        - **Training**: 30-day sequences, early stopping
        - **Forecast**: 7-day ahead predictions
        - **Confidence**: 95% prediction intervals

        **Data Source**: SQL database with 90 days history
        """)

    # Main content area
    if generate_forecast:
        with st.spinner("🔄 Training/loading LSTM model and generating predictions..."):
            try:
                # Get predictor (trains if needed)
                predictor = get_lstm_predictor(selected_coin)

                # Generate predictions
                predictions = predictor.predict_future(days_ahead=7)

                # Get historical data for chart
                historical = db_manager.get_historical_prices(selected_coin, days=30)

                if not historical:
                    st.error(f"No historical data available for {coin_display_names[selected_coin]}")
                    return

                # Display results
                st.success(f"✅ Forecast generated for {coin_display_names[selected_coin]}!")

                # Model metrics
                st.subheader("📊 Model Performance")
                display_model_metrics(predictor)

                # Prediction chart
                st.subheader("📈 Price Forecast Chart")
                coin_name = coin_display_names[selected_coin]
                fig = create_prediction_chart(historical, predictions, coin_name)
                st.plotly_chart(fig, use_container_width=True)

                # Prediction summary
                st.subheader("🎯 7-Day Forecast Summary")

                pred_df = pd.DataFrame({
                    'Date': [pd.to_datetime(date, utc=True, errors='coerce').strftime('%Y-%m-%d') 
                            if pd.notna(pd.to_datetime(date, utc=True, errors='coerce')) else 'Invalid Date'
                            for date in predictions['dates']],
                    'Predicted Price': predictions['predictions'],
                    'Lower Bound': predictions['confidence_intervals']['lower'],
                    'Upper Bound': predictions['confidence_intervals']['upper']
                })

                # Style the dataframe
                def style_price(val):
                    return f"${val:,.2f}"

                styled_df = pred_df.style.format({
                    'Predicted Price': style_price,
                    'Lower Bound': style_price,
                    'Upper Bound': style_price
                })

                st.dataframe(styled_df, use_container_width=True)

                # Key insights
                current_price = historical[-1]['price'] if historical else 0
                final_prediction = predictions['predictions'][-1]
                change_pct = ((final_prediction - current_price) / current_price) * 100

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Current Price",
                        f"${current_price:,.2f}",
                        help="Latest available price from database"
                    )

                with col2:
                    st.metric(
                        "7-Day Forecast",
                        f"${final_prediction:,.2f}",
                        f"{change_pct:+.1f}%" if current_price > 0 else "N/A",
                        help="Predicted price 7 days from now"
                    )

                with col3:
                    confidence_range = predictions['confidence_intervals']['upper'][-1] - predictions['confidence_intervals']['lower'][-1]
                    st.metric(
                        "Prediction Range",
                        f"${confidence_range:,.0f}",
                        help="95% confidence interval width"
                    )

                # Forecast trend
                if change_pct > 5:
                    trend = "📈 Bullish"
                    trend_class = "forecast-positive"
                elif change_pct < -5:
                    trend = "📉 Bearish"
                    trend_class = "forecast-negative"
                else:
                    trend = "➡️ Sideways"
                    trend_class = ""

                st.markdown(f"""
                <div class="prediction-card">
                    <h4>Market Outlook: <span class="{trend_class}">{trend}</span></h4>
                    <p>The LSTM model predicts a {change_pct:+.1f}% change over the next 7 days.</p>
                    <p><strong>Confidence Level:</strong> 95% prediction interval shown in light green.</p>
                    <p><em>Note: Cryptocurrency prices are highly volatile. This forecast is for informational purposes only.</em></p>
                </div>
                """, unsafe_allow_html=True)

            except ModelError as e:
                st.error(f"Model Error: {str(e)}")
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")
                st.error("Please try again or contact support if the issue persists.")

    else:
        # Default state - show instructions
        st.info("👆 Select a cryptocurrency from the sidebar and click 'Generate Forecast' to see LSTM predictions!")

        # Sample visualization placeholder
        st.subheader("🎯 How It Works")
        st.markdown("""
        **LSTM Time-Series Forecasting Process:**
        1. **Data Loading**: Fetch 90 days of historical price data from SQL database
        2. **Preprocessing**: Normalize prices and create 30-day sequences for training
        3. **Model Training**: LSTM neural network learns patterns in price movements
        4. **Prediction**: Generate 7-day ahead forecasts with confidence intervals
        5. **Visualization**: Interactive chart showing historical + predicted prices

        **Key Features:**
        - ✅ Real-time model training with early stopping
        - ✅ 95% confidence intervals for uncertainty quantification
        - ✅ Model performance metrics (RMSE, MAE, MAPE)
        - ✅ Interactive charts with historical context
        """)


if __name__ == "__main__":
    main()
