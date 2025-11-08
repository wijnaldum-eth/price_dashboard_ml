"""
Data processing utilities for cryptocurrency data.
Includes technical indicators, data cleaning, and feature engineering.
"""

import pandas as pd
import numpy as np
import logging
from typing import Optional, List, Tuple

from config.settings import settings
from utils.exceptions import DataProcessingError

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)


def calculate_moving_averages(df: pd.DataFrame, periods: List[int] = [7, 30, 90]) -> pd.DataFrame:
    """
    Calculate moving averages for given periods.
    
    Args:
        df: DataFrame with 'price' column
        periods: List of periods for moving averages
        
    Returns:
        DataFrame with additional MA columns
    """
    try:
        df = df.copy()
        for period in periods:
            df[f'ma_{period}'] = df['price'].rolling(window=period).mean()
        return df
    except Exception as e:
        logger.error(f"Error calculating moving averages: {e}")
        raise DataProcessingError(f"Failed to calculate moving averages: {e}")


def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """
    Calculate Relative Strength Index (RSI).
    
    Args:
        df: DataFrame with 'price' column
        period: RSI period (default 14)
        
    Returns:
        DataFrame with 'rsi' column
    """
    try:
        df = df.copy()
        
        # Calculate price changes
        delta = df['price'].diff()
        
        # Separate gains and losses
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        # Calculate RS and RSI
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        return df
    except Exception as e:
        logger.error(f"Error calculating RSI: {e}")
        raise DataProcessingError(f"Failed to calculate RSI: {e}")


def calculate_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    """
    Calculate MACD (Moving Average Convergence Divergence).
    
    Args:
        df: DataFrame with 'price' column
        fast: Fast EMA period
        slow: Slow EMA period
        signal: Signal line period
        
    Returns:
        DataFrame with 'macd', 'macd_signal', and 'macd_histogram' columns
    """
    try:
        df = df.copy()
        
        # Calculate EMAs
        ema_fast = df['price'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['price'].ewm(span=slow, adjust=False).mean()
        
        # Calculate MACD line
        df['macd'] = ema_fast - ema_slow
        
        # Calculate signal line
        df['macd_signal'] = df['macd'].ewm(span=signal, adjust=False).mean()
        
        # Calculate histogram
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        return df
    except Exception as e:
        logger.error(f"Error calculating MACD: {e}")
        raise DataProcessingError(f"Failed to calculate MACD: {e}")


def calculate_bollinger_bands(df: pd.DataFrame, period: int = 20, std_dev: int = 2) -> pd.DataFrame:
    """
    Calculate Bollinger Bands.
    
    Args:
        df: DataFrame with 'price' column
        period: Moving average period
        std_dev: Number of standard deviations
        
    Returns:
        DataFrame with 'bb_upper', 'bb_middle', and 'bb_lower' columns
    """
    try:
        df = df.copy()
        
        # Calculate middle band (SMA)
        df['bb_middle'] = df['price'].rolling(window=period).mean()
        
        # Calculate standard deviation
        std = df['price'].rolling(window=period).std()
        
        # Calculate upper and lower bands
        df['bb_upper'] = df['bb_middle'] + (std * std_dev)
        df['bb_lower'] = df['bb_middle'] - (std * std_dev)
        
        return df
    except Exception as e:
        logger.error(f"Error calculating Bollinger Bands: {e}")
        raise DataProcessingError(f"Failed to calculate Bollinger Bands: {e}")


def normalize_prices(df: pd.DataFrame, start_value: float = 100.0) -> pd.DataFrame:
    """
    Normalize prices to start at a specific value (for comparison charts).
    
    Args:
        df: DataFrame with 'price' column
        start_value: Starting value for normalization
        
    Returns:
        DataFrame with 'normalized_price' column
    """
    try:
        df = df.copy()
        first_price = df['price'].iloc[0]
        df['normalized_price'] = (df['price'] / first_price) * start_value
        return df
    except Exception as e:
        logger.error(f"Error normalizing prices: {e}")
        raise DataProcessingError(f"Failed to normalize prices: {e}")


def calculate_returns(df: pd.DataFrame, periods: List[int] = [1, 7, 30]) -> pd.DataFrame:
    """
    Calculate returns for different periods.
    
    Args:
        df: DataFrame with 'price' column
        periods: List of periods for return calculation
        
    Returns:
        DataFrame with return columns
    """
    try:
        df = df.copy()
        for period in periods:
            df[f'return_{period}d'] = df['price'].pct_change(periods=period) * 100
        return df
    except Exception as e:
        logger.error(f"Error calculating returns: {e}")
        raise DataProcessingError(f"Failed to calculate returns: {e}")


def calculate_volatility(df: pd.DataFrame, window: int = 30) -> pd.DataFrame:
    """
    Calculate rolling volatility (standard deviation of returns).
    
    Args:
        df: DataFrame with 'price' column
        window: Rolling window size
        
    Returns:
        DataFrame with 'volatility' column
    """
    try:
        df = df.copy()
        returns = df['price'].pct_change()
        df['volatility'] = returns.rolling(window=window).std() * np.sqrt(365) * 100
        return df
    except Exception as e:
        logger.error(f"Error calculating volatility: {e}")
        raise DataProcessingError(f"Failed to calculate volatility: {e}")


def detect_support_resistance(df: pd.DataFrame, window: int = 20) -> Tuple[float, float]:
    """
    Detect support and resistance levels using local minima/maxima.
    
    Args:
        df: DataFrame with 'price' column
        window: Window size for local extrema detection
        
    Returns:
        Tuple of (support_level, resistance_level)
    """
    try:
        prices = df['price'].values
        
        # Find local minima (support)
        local_min = []
        for i in range(window, len(prices) - window):
            if prices[i] == min(prices[i-window:i+window+1]):
                local_min.append(prices[i])
        
        # Find local maxima (resistance)
        local_max = []
        for i in range(window, len(prices) - window):
            if prices[i] == max(prices[i-window:i+window+1]):
                local_max.append(prices[i])
        
        support = np.mean(local_min) if local_min else df['price'].min()
        resistance = np.mean(local_max) if local_max else df['price'].max()
        
        return support, resistance
    except Exception as e:
        logger.error(f"Error detecting support/resistance: {e}")
        raise DataProcessingError(f"Failed to detect support/resistance: {e}")


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and validate cryptocurrency data.
    
    Args:
        df: Raw DataFrame
        
    Returns:
        Cleaned DataFrame
    """
    try:
        df = df.copy()
        
        # Remove duplicates
        df = df[~df.index.duplicated(keep='first')]
        
        # Sort by index (date)
        df = df.sort_index()
        
        # Forward fill missing values
        df = df.fillna(method='ffill')
        
        # Remove any remaining NaN values
        df = df.dropna()
        
        # Ensure positive prices
        if 'price' in df.columns:
            df = df[df['price'] > 0]
        
        return df
    except Exception as e:
        logger.error(f"Error cleaning data: {e}")
        raise DataProcessingError(f"Failed to clean data: {e}")


def prepare_lstm_data(df: pd.DataFrame, sequence_length: int = 60, 
                      train_split: float = 0.8) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, object]:
    """
    Prepare data for LSTM model training.
    
    Args:
        df: DataFrame with 'price' column
        sequence_length: Number of time steps for LSTM input
        train_split: Proportion of data for training
        
    Returns:
        Tuple of (X_train, y_train, X_test, y_test, scaler)
    """
    try:
        from sklearn.preprocessing import MinMaxScaler
        
        # Extract prices
        prices = df['price'].values.reshape(-1, 1)
        
        # Scale data
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_prices = scaler.fit_transform(prices)
        
        # Create sequences
        X, y = [], []
        for i in range(sequence_length, len(scaled_prices)):
            X.append(scaled_prices[i-sequence_length:i, 0])
            y.append(scaled_prices[i, 0])
        
        X, y = np.array(X), np.array(y)
        
        # Reshape for LSTM [samples, time steps, features]
        X = np.reshape(X, (X.shape[0], X.shape[1], 1))
        
        # Split into train and test
        split_idx = int(len(X) * train_split)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        return X_train, y_train, X_test, y_test, scaler
        
    except Exception as e:
        logger.error(f"Error preparing LSTM data: {e}")
        raise DataProcessingError(f"Failed to prepare LSTM data: {e}")


def calculate_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate all technical indicators at once.
    
    Args:
        df: DataFrame with 'price' column
        
    Returns:
        DataFrame with all indicators
    """
    try:
        df = clean_data(df)
        df = calculate_moving_averages(df)
        df = calculate_rsi(df)
        df = calculate_macd(df)
        df = calculate_bollinger_bands(df)
        df = calculate_returns(df)
        df = calculate_volatility(df)
        
        return df
    except Exception as e:
        logger.error(f"Error calculating all indicators: {e}")
        raise DataProcessingError(f"Failed to calculate all indicators: {e}")


def interpret_rsi(rsi: float) -> str:
    """
    Interpret RSI value.
    
    Args:
        rsi: RSI value
        
    Returns:
        Interpretation string
    """
    if rsi >= 70:
        return "Overbought - Consider selling"
    elif rsi <= 30:
        return "Oversold - Consider buying"
    else:
        return "Neutral"


def interpret_macd(macd: float, signal: float) -> str:
    """
    Interpret MACD values.
    
    Args:
        macd: MACD line value
        signal: Signal line value
        
    Returns:
        Interpretation string
    """
    if macd > signal:
        return "Bullish - MACD above signal"
    elif macd < signal:
        return "Bearish - MACD below signal"
    else:
        return "Neutral"
