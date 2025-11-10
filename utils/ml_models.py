"""
Machine Learning Models for Cryptocurrency Price Forecasting.
Implements LSTM time-series prediction with confidence intervals and performance metrics.
"""

import os
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path

# ML imports
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, mean_absolute_percentage_error

from config.settings import settings
from utils.database import db_manager
from utils.exceptions import ModelError

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Set TensorFlow logging level
tf.get_logger().setLevel(logging.ERROR)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


class LSTMPredictor:
    """
    LSTM-based cryptocurrency price predictor.
    Handles data preprocessing, model training, prediction, and evaluation.
    """

    def __init__(self, coin_id: str, sequence_length: int = 30, forecast_days: int = 7):
        """
        Initialize LSTM predictor for a specific cryptocurrency.

        Args:
            coin_id: Cryptocurrency identifier (e.g., 'bitcoin')
            sequence_length: Number of days to use for prediction (default: 30)
            forecast_days: Number of days to forecast (default: 7)
        """
        self.coin_id = coin_id
        self.sequence_length = sequence_length
        self.forecast_days = forecast_days
        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.model_path = None
        self.metadata = {}

        # Model hyperparameters
        self.hyperparams = {
            'lstm_units': 50,
            'dropout_rate': 0.2,
            'dense_units': 25,
            'batch_size': 32,
            'epochs': 50,
            'validation_split': 0.1,
            'learning_rate': 0.001
        }

    def load_data(self, days: int = 90) -> pd.DataFrame:
        """
        Load historical price data from database.

        Args:
            days: Number of days of historical data to load

        Returns:
            DataFrame with timestamp and price columns
        """
        try:
            historical_data = db_manager.get_historical_prices(self.coin_id, days=days)

            if not historical_data:
                raise ModelError(f"No historical data found for {self.coin_id}")

            # Convert to DataFrame
            df = pd.DataFrame(historical_data)
            # Robust timestamp parsing with UTC timezone handling
            df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True, errors='coerce')
            df = df.sort_values('timestamp').set_index('timestamp')

            # Drop rows with invalid timestamps
            df = df[df.index.notna()]

            # Keep only price column for now
            df = df[['price']].dropna()

            if len(df) < self.sequence_length + self.forecast_days:
                raise ModelError(f"Insufficient data for {self.coin_id}: {len(df)} records, need at least {self.sequence_length + self.forecast_days}")

            logger.info(f"Loaded {len(df)} price records for {self.coin_id}")
            return df

        except Exception as e:
            logger.error(f"Failed to load data for {self.coin_id}: {e}")
            raise ModelError(f"Data loading failed: {str(e)}")

    def preprocess_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Preprocess data for LSTM training.

        Args:
            df: DataFrame with price data

        Returns:
            Tuple of (X_train, y_train, X_test, y_test)
        """
        try:
            # Normalize prices
            prices = df[['price']].values
            self.scaler = MinMaxScaler(feature_range=(0, 1))
            scaled_prices = self.scaler.fit_transform(prices)

            # Create sequences
            X, y = [], []
            for i in range(self.sequence_length, len(scaled_prices)):
                X.append(scaled_prices[i-self.sequence_length:i, 0])
                y.append(scaled_prices[i, 0])

            X, y = np.array(X), np.array(y)

            # Reshape X for LSTM input
            X = X.reshape((X.shape[0], X.shape[1], 1))

            # Split into train/test
            split_idx = int(len(X) * (1 - self.hyperparams['validation_split']))
            X_train, X_test = X[:split_idx], X[split_idx:]
            y_train, y_test = y[:split_idx], y[split_idx:]

            logger.info(f"Data preprocessed: {X_train.shape[0]} train, {X_test.shape[0]} test sequences")
            return X_train, y_train, X_test, y_test

        except Exception as e:
            logger.error(f"Data preprocessing failed: {e}")
            raise ModelError(f"Preprocessing failed: {str(e)}")

    def build_model(self, input_shape: Tuple[int, int]) -> Sequential:
        """
        Build LSTM model architecture.

        Args:
            input_shape: Shape of input data (sequence_length, features)

        Returns:
            Compiled LSTM model
        """
        try:
            model = Sequential([
                Input(shape=input_shape),
                LSTM(self.hyperparams['lstm_units'], return_sequences=True),
                Dropout(self.hyperparams['dropout_rate']),
                LSTM(self.hyperparams['lstm_units'], return_sequences=False),
                Dropout(self.hyperparams['dropout_rate']),
                Dense(self.hyperparams['dense_units']),
                Dense(1)
            ])

            # Compile model
            optimizer = tf.keras.optimizers.Adam(learning_rate=self.hyperparams['learning_rate'])
            model.compile(optimizer=optimizer, loss='mean_squared_error')

            logger.info(f"Model built with architecture: {model.summary()}")
            return model

        except Exception as e:
            logger.error(f"Model building failed: {e}")
            raise ModelError(f"Model building failed: {str(e)}")

    def train_model(self, X_train: np.ndarray, y_train: np.ndarray, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, Any]:
        """
        Train the LSTM model.

        Args:
            X_train: Training input sequences
            y_train: Training target values
            X_test: Test input sequences
            y_test: Test target values

        Returns:
            Training history and metrics
        """
        try:
            # Build model
            self.model = self.build_model((X_train.shape[1], X_train.shape[2]))

            # Callbacks
            early_stopping = EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True,
                verbose=0
            )

            # Create models directory if it doesn't exist
            models_dir = Path("models")
            models_dir.mkdir(exist_ok=True)

            # Model checkpoint
            checkpoint_path = models_dir / f"lstm_{self.coin_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.h5"
            model_checkpoint = ModelCheckpoint(
                str(checkpoint_path),
                monitor='val_loss',
                save_best_only=True,
                verbose=0
            )

            # Train model
            history = self.model.fit(
                X_train, y_train,
                epochs=self.hyperparams['epochs'],
                batch_size=self.hyperparams['batch_size'],
                validation_split=self.hyperparams['validation_split'],
                callbacks=[early_stopping, model_checkpoint],
                verbose=0
            )

            # Store model path
            self.model_path = str(checkpoint_path)

            # Calculate metrics on test set
            test_predictions = self.model.predict(X_test, verbose=0)
            test_metrics = self.calculate_metrics(y_test, test_predictions.flatten())

            training_info = {
                'epochs_trained': len(history.history['loss']),
                'final_loss': history.history['loss'][-1],
                'final_val_loss': history.history['val_loss'][-1],
                'best_val_loss': min(history.history['val_loss']),
                'metrics': test_metrics,
                'hyperparameters': self.hyperparams.copy(),
                'training_date': datetime.now().isoformat(),
                'model_path': self.model_path
            }

            # Store metadata
            self.metadata = training_info

            logger.info(f"Model trained for {self.coin_id}: {test_metrics}")
            return training_info

        except Exception as e:
            logger.error(f"Model training failed: {e}")
            raise ModelError(f"Training failed: {str(e)}")

    def predict_future(self, days_ahead: int = 7) -> Dict[str, Any]:
        """
        Generate future price predictions with confidence intervals.

        Args:
            days_ahead: Number of days to forecast

        Returns:
            Dictionary with predictions, confidence intervals, and metadata
        """
        try:
            if self.model is None:
                raise ModelError("Model not trained or loaded")

            # Load recent data for prediction
            df = self.load_data(days=60)  # Get last 60 days for context

            # Get the last sequence for prediction
            scaled_data = self.scaler.transform(df[['price']].values)
            last_sequence = scaled_data[-self.sequence_length:].reshape(1, self.sequence_length, 1)

            # Generate predictions
            predictions = []
            current_sequence = last_sequence.copy()

            for _ in range(days_ahead):
                # Predict next value
                next_pred = self.model.predict(current_sequence, verbose=0)[0][0]
                predictions.append(next_pred)

                # Update sequence for next prediction
                current_sequence = np.roll(current_sequence, -1, axis=1)
                current_sequence[0, -1, 0] = next_pred

            # Inverse transform predictions
            predictions_array = np.array(predictions).reshape(-1, 1)
            predictions_unscaled = self.scaler.inverse_transform(predictions_array).flatten()

            # Generate confidence intervals (simplified approach using prediction std)
            # In a real implementation, you'd use prediction intervals from model uncertainty
            pred_std = np.std(predictions_unscaled) * 0.1  # 10% of prediction std as uncertainty
            confidence_intervals = {
                'lower': predictions_unscaled - 1.96 * pred_std,  # 95% CI
                'upper': predictions_unscaled + 1.96 * pred_std
            }

            # Generate future dates
            last_date = df.index[-1]
            future_dates = [last_date + timedelta(days=i+1) for i in range(days_ahead)]
            # Ensure all dates have timezone info
            future_dates = [date.replace(tzinfo=timezone.utc) if date.tzinfo is None else date for date in future_dates]

            result = {
                'coin_id': self.coin_id,
                'predictions': predictions_unscaled.tolist(),
                'confidence_intervals': {
                    'lower': confidence_intervals['lower'].tolist(),
                    'upper': confidence_intervals['upper'].tolist()
                },
                'dates': [date.isoformat() for date in future_dates],
                'prediction_date': datetime.now(timezone.utc).isoformat(),
                'days_ahead': days_ahead
            }

            logger.info(f"Generated {days_ahead}-day predictions for {self.coin_id}")
            return result

        except Exception as e:
            logger.error(f"Future prediction failed: {e}")
            raise ModelError(f"Prediction failed: {str(e)}")

    def calculate_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """
        Calculate prediction accuracy metrics.

        Args:
            y_true: True values
            y_pred: Predicted values

        Returns:
            Dictionary with RMSE, MAE, MAPE metrics
        """
        try:
            rmse = np.sqrt(mean_squared_error(y_true, y_pred))
            mae = mean_absolute_error(y_true, y_pred)
            mape = mean_absolute_percentage_error(y_true, y_pred) * 100  # Convert to percentage

            return {
                'rmse': float(rmse),
                'mae': float(mae),
                'mape': float(mape)
            }

        except Exception as e:
            logger.error(f"Metrics calculation failed: {e}")
            return {'rmse': 0.0, 'mae': 0.0, 'mape': 0.0}

    def save_metadata(self, filepath: Optional[str] = None) -> str:
        """
        Save model metadata to JSON file.

        Args:
            filepath: Optional custom filepath

        Returns:
            Path to saved metadata file
        """
        try:
            if not filepath:
                models_dir = Path("models")
                models_dir.mkdir(exist_ok=True)
                filepath = models_dir / f"metadata_{self.coin_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            # Include scaler parameters in metadata
            metadata = self.metadata.copy()
            if self.scaler and hasattr(self.scaler, 'data_min_'):
                metadata['scaler'] = {
                    'data_min': self.scaler.data_min_.tolist(),
                    'data_max': self.scaler.data_max_.tolist(),
                    'data_range': self.scaler.data_range_.tolist(),
                    'scale': self.scaler.scale_.tolist(),
                    'min': self.scaler.min_.tolist(),
                    'fitted': True
                }

            with open(filepath, 'w') as f:
                json.dump(metadata, f, indent=2, default=str)

            logger.info(f"Metadata saved to {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"Metadata save failed: {e}")
            raise ModelError(f"Metadata save failed: {str(e)}")

    def load_model(self, model_path: str) -> bool:
        """
        Load a trained model from disk.

        Args:
            model_path: Path to the saved model file

        Returns:
            True if loaded successfully
        """
        try:
            self.model = load_model(model_path)
            self.model_path = model_path

            # Try to load metadata
            metadata_path = model_path.replace('.h5', '_metadata.json')
            if not os.path.exists(metadata_path):
                # Try alternative metadata filename pattern
                import glob
                metadata_files = glob.glob(f"models/metadata_{self.coin_id}_*.json")
                if metadata_files:
                    metadata_path = max(metadata_files, key=os.path.getmtime)

            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    self.metadata = json.load(f)

                # Restore scaler state if available
                if 'scaler' in self.metadata and self.metadata['scaler'].get('fitted', False):
                    scaler_data = self.metadata['scaler']
                    self.scaler = MinMaxScaler()
                    self.scaler.data_min_ = np.array(scaler_data['data_min'])
                    self.scaler.data_max_ = np.array(scaler_data['data_max'])
                    self.scaler.data_range_ = np.array(scaler_data['data_range'])
                    self.scaler.scale_ = np.array(scaler_data['scale'])
                    self.scaler.min_ = np.array(scaler_data['min'])
                    # Set fitted attribute
                    self.scaler._validate_params()

            logger.info(f"Model loaded from {model_path}")
            return True

        except Exception as e:
            logger.error(f"Model loading failed: {e}")
            return False

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get comprehensive model information.

        Returns:
            Dictionary with model details, metrics, and metadata
        """
        return {
            'coin_id': self.coin_id,
            'model_type': 'LSTM',
            'sequence_length': self.sequence_length,
            'forecast_days': self.forecast_days,
            'hyperparameters': self.hyperparams,
            'metadata': self.metadata,
            'model_path': self.model_path,
            'is_trained': self.model is not None
        }


def train_lstm_model(coin_id: str, force_retrain: bool = False) -> LSTMPredictor:
    """
    Train or load an LSTM model for a cryptocurrency.

    Args:
        coin_id: Cryptocurrency identifier
        force_retrain: Force retraining even if model exists

    Returns:
        Trained LSTMPredictor instance
    """
    predictor = LSTMPredictor(coin_id)

    # Check if model already exists
    models_dir = Path("models")
    if models_dir.exists() and not force_retrain:
        model_files = list(models_dir.glob(f"lstm_{coin_id}_*.h5"))
        if model_files:
            latest_model = max(model_files, key=lambda x: x.stat().st_mtime)
            if predictor.load_model(str(latest_model)):
                logger.info(f"Loaded existing model for {coin_id}")
                return predictor

    # Train new model
    logger.info(f"Training new LSTM model for {coin_id}")
    df = predictor.load_data()
    X_train, y_train, X_test, y_test = predictor.preprocess_data(df)
    training_info = predictor.train_model(X_train, y_train, X_test, y_test)

    # Save metadata with consistent naming
    metadata_path = predictor.model_path.replace('.h5', '_metadata.json')
    predictor.save_metadata(metadata_path)

    return predictor


# Global model cache for performance
_model_cache = {}

def get_lstm_predictor(coin_id: str) -> LSTMPredictor:
    """
    Get or create LSTM predictor for a coin (with caching).

    Args:
        coin_id: Cryptocurrency identifier

    Returns:
        LSTMPredictor instance
    """
    if coin_id not in _model_cache:
        _model_cache[coin_id] = train_lstm_model(coin_id)

    return _model_cache[coin_id]
