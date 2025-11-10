"""
MLOps Dashboard Page - Model lifecycle management and performance monitoring.
Displays model registry, performance metrics, and monitoring dashboards.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.model_registry import ModelRegistry
from utils.model_monitor import ModelMonitor

# Page configuration
st.set_page_config(
    page_title="MLOps Dashboard - CryptoInsight Pro",
    page_icon="📈",
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
        margin-bottom: 1rem;
    }
    .health-good { color: #10B981; }
    .health-warning { color: #F59E0B; }
    .health-critical { color: #EF4444; }
    .model-version {
        background-color: #374151;
        padding: 0.5rem;
        border-radius: 4px;
        margin: 0.25rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize components
registry = ModelRegistry()
monitor = ModelMonitor()

def get_health_color(score):
    """Get color class based on health score"""
    if score >= 80:
        return "health-good"
    elif score >= 60:
        return "health-warning"
    else:
        return "health-critical"

def render_model_registry_table():
    """Render the model registry table"""
    st.subheader("📋 Model Registry")

    models = registry.get_model_versions()

    if not models:
        st.info("No models registered yet. Train some models first!")
        return

    # Convert to DataFrame for display
    df = pd.DataFrame(models)
    df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')

    # Format metrics
    df['rmse'] = df['rmse'].round(4)
    df['mae'] = df['mae'].round(4)
    df['mape'] = df['mape'].round(2)

    # Reorder columns
    columns = ['version', 'coin_id', 'created_at', 'rmse', 'mae', 'mape', 'model_path']
    df_display = df[columns]

    # Rename columns for display
    df_display.columns = ['Version', 'Coin', 'Created', 'RMSE', 'MAE', 'MAPE (%)', 'Model Path']

    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True
    )

    # Export button
    csv = df_display.to_csv(index=False)
    st.download_button(
        label="📥 Export Registry to CSV",
        data=csv,
        file_name=f"model_registry_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

def render_performance_over_time():
    """Render performance trends over time"""
    st.subheader("📈 Performance Over Time")

    # Coin selector
    models = registry.get_model_versions()
    if not models:
        st.info("No performance data available")
        return

    coins = list(set([m['coin_id'] for m in models]))
    selected_coin = st.selectbox("Select Coin", coins, key="perf_coin")

    # Get performance history
    latest_version = registry.get_latest_version(selected_coin)
    if not latest_version:
        st.warning(f"No models found for {selected_coin}")
        return

    perf_history = monitor.get_performance_history(latest_version['version'], selected_coin)

    if not perf_history:
        st.info("No performance history available yet")
        return

    # Convert to DataFrame
    df = pd.DataFrame(perf_history)
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')

    # Create line chart
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['mape'],
        mode='lines+markers',
        name='MAPE (%)',
        line=dict(color='#3B82F6')
    ))

    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['rmse'],
        mode='lines+markers',
        name='RMSE',
        line=dict(color='#10B981'),
        yaxis='y2'
    ))

    fig.update_layout(
        title=f"Model Performance Trends - {selected_coin}",
        xaxis_title="Date",
        yaxis_title="MAPE (%)",
        yaxis2=dict(
            title="RMSE",
            overlaying="y",
            side="right"
        ),
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

def render_model_comparison():
    """Render model comparison side-by-side"""
    st.subheader("🔄 Model Comparison")

    models = registry.get_model_versions()
    if len(models) < 2:
        st.info("Need at least 2 models for comparison")
        return

    # Get unique coins
    coins = list(set([m['coin_id'] for m in models]))
    selected_coin = st.selectbox("Select Coin for Comparison", coins, key="comp_coin")

    # Get models for this coin
    coin_models = [m for m in models if m['coin_id'] == selected_coin]
    if len(coin_models) < 2:
        st.warning(f"Need at least 2 models for {selected_coin} to compare")
        return

    # Select two models to compare
    model_options = {f"{m['version']} (MAPE: {m['mape']:.2f}%)": m['version']
                    for m in coin_models}

    col1, col2 = st.columns(2)

    with col1:
        model1_version = st.selectbox("Model 1", list(model_options.keys()),
                                    index=0, key="model1")
        model1 = next(m for m in coin_models if m['version'] == model_options[model1_version])

    with col2:
        remaining_models = [k for k in model_options.keys() if k != model1_version]
        model2_version = st.selectbox("Model 2", remaining_models,
                                    index=0 if remaining_models else None, key="model2")
        if model2_version:
            model2 = next(m for m in coin_models if m['version'] == model_options[model2_version])
        else:
            st.warning("No second model available")
            return

    # Comparison table
    comparison_data = {
        'Metric': ['RMSE', 'MAE', 'MAPE (%)', 'Created'],
        'Model 1': [
            f"{model1['rmse']:.4f}",
            f"{model1['mae']:.4f}",
            f"{model1['mape']:.2f}",
            pd.to_datetime(model1['created_at']).strftime('%Y-%m-%d %H:%M')
        ],
        'Model 2': [
            f"{model2['rmse']:.4f}",
            f"{model2['mae']:.4f}",
            f"{model2['mape']:.2f}",
            pd.to_datetime(model2['created_at']).strftime('%Y-%m-%d %H:%M')
        ]
    }

    df_comp = pd.DataFrame(comparison_data)
    st.table(df_comp)

def render_prediction_accuracy():
    """Render prediction vs actual scatter plot"""
    st.subheader("🎯 Prediction Accuracy")

    models = registry.get_model_versions()
    if not models:
        st.info("No prediction data available")
        return

    coins = list(set([m['coin_id'] for m in models]))
    selected_coin = st.selectbox("Select Coin", coins, key="pred_coin")

    # Get latest model for this coin
    latest_model = registry.get_latest_version(selected_coin)
    if not latest_model:
        st.warning(f"No models found for {selected_coin}")
        return

    # Get predictions from database
    import sqlite3
    with sqlite3.connect("models/models.db") as conn:
        predictions = conn.execute('''
            SELECT predicted_price, actual_price
            FROM predictions
            WHERE model_version = ? AND coin_id = ? AND actual_price IS NOT NULL
            ORDER BY prediction_timestamp DESC
            LIMIT 100
        ''', (latest_model['version'], selected_coin)).fetchall()

    if not predictions:
        st.info("No prediction data available yet")
        return

    # Create scatter plot
    predicted = [p['predicted_price'] for p in predictions]
    actual = [p['actual_price'] for p in predictions]

    # Perfect prediction line
    max_val = max(max(predicted), max(actual))
    min_val = min(min(predicted), min(actual))
    perfect_line = [min_val, max_val]

    fig = go.Figure()

    # Scatter plot
    fig.add_trace(go.Scatter(
        x=actual,
        y=predicted,
        mode='markers',
        name='Predictions',
        marker=dict(color='#3B82F6', size=8)
    ))

    # Perfect prediction line
    fig.add_trace(go.Scatter(
        x=perfect_line,
        y=perfect_line,
        mode='lines',
        name='Perfect Prediction',
        line=dict(color='#EF4444', dash='dash')
    ))

    fig.update_layout(
        title=f"Predicted vs Actual Prices - {selected_coin}",
        xaxis_title="Actual Price ($)",
        yaxis_title="Predicted Price ($)",
        showlegend=True
    )

    st.plotly_chart(fig, use_container_width=True)

    # Accuracy metrics
    errors = [abs(p - a) / a * 100 for p, a in zip(predicted, actual)]
    avg_mape = sum(errors) / len(errors)

    st.metric("Average MAPE", f"{avg_mape:.2f}%")

def render_model_health_score():
    """Render overall model health indicators"""
    st.subheader("❤️ Model Health Dashboard")

    models = registry.get_model_versions()
    if not models:
        st.info("No models to monitor")
        return

    # Update actual prices first
    monitor.update_actual_prices()

    health_scores = []
    retraining_alerts = []

    for model in models:
        score = monitor.get_model_health_score(model['version'], model['coin_id'])
        degradation = monitor.detect_performance_degradation(model['version'], model['coin_id'])
        retrain_check = monitor.should_retrain_model(model['version'], model['coin_id'])

        health_scores.append({
            'model': model,
            'score': score,
            'degradation': degradation
        })

        if retrain_check.get('should_retrain', False):
            retraining_alerts.append({
                'model': model,
                'reason': retrain_check['reason']
            })

    # Show retraining alerts first
    if retraining_alerts:
        st.error("🚨 Retraining Required")
        for alert in retraining_alerts:
            model = alert['model']
            st.markdown(f"""
                **{model['coin_id']} - {model['version']}**: {alert['reason']}
            """)

            # Rollback options
            candidates = registry.get_rollback_candidates(model['coin_id'], model['version'])
            if candidates:
                st.markdown("**Rollback Options:**")
                for candidate in candidates[:3]:  # Show top 3 candidates
                    if st.button(f"Rollback to {candidate['version']} (MAPE: {candidate['mape']:.2f}%)",
                               key=f"rollback_{model['version']}_{candidate['version']}"):
                        result = registry.rollback_to_version(candidate['version'])
                        if result['success']:
                            st.success(result['message'])
                            st.rerun()
                        else:
                            st.error(result['error'])
            else:
                st.warning("No rollback candidates available")
        st.markdown("---")

    # Sort by health score
    health_scores.sort(key=lambda x: x['score'], reverse=True)

    # Display health scores
    cols = st.columns(min(3, len(health_scores)))

    for idx, health in enumerate(health_scores[:3]):
        with cols[idx]:
            model = health['model']
            score = health['score']
            degradation = health['degradation']

            color_class = get_health_color(score)

            st.markdown(f"""
                <div class="metric-card">
                    <h4>{model['coin_id']} - {model['version']}</h4>
                    <h2 class="{color_class}">{score:.1f}/100</h2>
                    <p>Health Score</p>
                    <p style="font-size: 0.8em;">
                        MAPE: {model['mape']:.2f}%<br>
                        {'⚠️ Degraded' if degradation.get('degraded') else '✅ Healthy'}
                    </p>
                </div>
            """, unsafe_allow_html=True)

def main():
    st.title("📈 MLOps Dashboard")
    st.markdown("Model lifecycle management and performance monitoring")

    # Header with refresh
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    with col2:
        if st.button("🔄 Refresh Data"):
            st.rerun()

    st.markdown("---")

    # Render all dashboard sections
    render_model_health_score()
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        render_model_registry_table()

    with col2:
        render_model_comparison()

    st.markdown("---")
    render_performance_over_time()
    st.markdown("---")
    render_prediction_accuracy()

if __name__ == "__main__":
    main()
