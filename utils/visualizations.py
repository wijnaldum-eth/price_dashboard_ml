"""
Reusable visualization components using Plotly.
All charts follow consistent dark theme styling.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import List, Dict, Optional

# Dark theme configuration
DARK_THEME = {
    'template': 'plotly_dark',
    'paper_bgcolor': '#0E1117',
    'plot_bgcolor': '#1E293B',
    'font_color': '#FAFAFA',
    'grid_color': '#374151'
}

PRIMARY_COLOR = '#4F46E5'
SUCCESS_COLOR = '#10B981'
DANGER_COLOR = '#EF4444'


def create_price_chart(df: pd.DataFrame, title: str) -> go.Figure:
    """Create interactive price chart."""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['price'],
        mode='lines',
        name='Price',
        line=dict(color=PRIMARY_COLOR, width=2),
        hovertemplate='%{y:$,.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        template='plotly_dark',
        hovermode='x unified',
        height=500
    )
    
    return fig


def create_comparison_chart(dfs: Dict[str, pd.DataFrame], coin_names: List[str]) -> go.Figure:
    """Create normalized comparison chart for multiple coins."""
    fig = go.Figure()
    
    colors = [PRIMARY_COLOR, SUCCESS_COLOR, DANGER_COLOR, '#F59E0B', '#8B5CF6']
    
    for idx, (coin_id, df) in enumerate(dfs.items()):
        name = coin_names[idx] if idx < len(coin_names) else coin_id
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['normalized_price'],
            mode='lines',
            name=name,
            line=dict(color=colors[idx % len(colors)], width=2)
        ))
    
    fig.update_layout(
        title="Price Comparison (Normalized to 100)",
        xaxis_title="Date",
        yaxis_title="Normalized Price",
        template='plotly_dark',
        hovermode='x unified',
        height=500
    )
    
    return fig


def create_portfolio_pie_chart(holdings: Dict[str, float]) -> go.Figure:
    """Create portfolio allocation pie chart."""
    fig = go.Figure(data=[go.Pie(
        labels=list(holdings.keys()),
        values=list(holdings.values()),
        hole=0.4,
        marker=dict(colors=px.colors.sequential.Viridis)
    )])
    
    fig.update_layout(
        title="Portfolio Allocation",
        template='plotly_dark',
        height=400
    )
    
    return fig


def create_sentiment_gauge(score: float) -> go.Figure:
    """Create sentiment gauge chart."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Sentiment Score"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': PRIMARY_COLOR},
            'steps': [
                {'range': [0, 33], 'color': DANGER_COLOR},
                {'range': [33, 66], 'color': '#F59E0B'},
                {'range': [66, 100], 'color': SUCCESS_COLOR}
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': score
            }
        }
    ))
    
    fig.update_layout(
        template='plotly_dark',
        height=300
    )
    
    return fig


def create_prediction_chart(historical: pd.DataFrame, predicted: pd.DataFrame) -> go.Figure:
    """Create chart with historical and predicted prices."""
    fig = go.Figure()
    
    # Historical prices
    fig.add_trace(go.Scatter(
        x=historical.index,
        y=historical['price'],
        mode='lines',
        name='Historical',
        line=dict(color=PRIMARY_COLOR, width=2)
    ))
    
    # Predicted prices
    fig.add_trace(go.Scatter(
        x=predicted.index,
        y=predicted['predicted'],
        mode='lines',
        name='Predicted',
        line=dict(color=SUCCESS_COLOR, width=2, dash='dash')
    ))
    
    # Confidence interval
    if 'upper' in predicted.columns and 'lower' in predicted.columns:
        fig.add_trace(go.Scatter(
            x=predicted.index,
            y=predicted['upper'],
            mode='lines',
            line=dict(width=0),
            showlegend=False
        ))
        
        fig.add_trace(go.Scatter(
            x=predicted.index,
            y=predicted['lower'],
            mode='lines',
            fill='tonexty',
            fillcolor='rgba(16, 185, 129, 0.2)',
            line=dict(width=0),
            name='Confidence Interval'
        ))
    
    fig.update_layout(
        title="Price Prediction with Confidence Interval",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        template='plotly_dark',
        hovermode='x unified',
        height=500
    )
    
    return fig
