import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
import logging
import os

from utils.database import db_manager

logger = logging.getLogger(__name__)

class ModelMonitor:
    def __init__(self, db_path="models/models.db"):
        """Initialize model monitor with SQLite database"""
        self.db_path = db_path
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        """Create database and tables if they don't exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            # Predictions table to store model predictions
            conn.execute('''
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY,
                    model_version TEXT NOT NULL,
                    coin_id TEXT NOT NULL,
                    prediction_date DATETIME NOT NULL,
                    predicted_price REAL NOT NULL,
                    actual_price REAL,
                    prediction_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (model_version) REFERENCES model_registry(version)
                )
            ''')

            # Performance metrics table for rolling accuracy
            conn.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY,
                    model_version TEXT NOT NULL,
                    coin_id TEXT NOT NULL,
                    metric_date DATE NOT NULL,
                    period_days INTEGER NOT NULL,
                    rmse REAL,
                    mae REAL,
                    mape REAL,
                    sample_size INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (model_version) REFERENCES model_registry(version),
                    UNIQUE(model_version, coin_id, metric_date, period_days)
                )
            ''')

            conn.commit()

    def store_prediction(self, model_version: str, coin_id: str,
                        prediction_date: datetime, predicted_price: float):
        """Store a model prediction for later evaluation"""
        # Ensure prediction_date has timezone info
        if prediction_date.tzinfo is None:
            prediction_date = prediction_date.replace(tzinfo=timezone.utc)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO predictions
                (model_version, coin_id, prediction_date, predicted_price)
                VALUES (?, ?, ?, ?)
            ''', (model_version, coin_id, prediction_date.isoformat(), predicted_price))
            conn.commit()

    def update_actual_prices(self):
        """Update predictions with actual prices once they become available"""
        try:
            # Get predictions that don't have actual prices yet
            with sqlite3.connect(self.db_path) as conn:
                predictions = conn.execute('''
                    SELECT id, coin_id, prediction_date
                    FROM predictions
                    WHERE actual_price IS NULL
                    ORDER BY prediction_date ASC
                ''').fetchall()

                for pred in predictions:
                    pred_id = pred['id']
                    coin_id = pred['coin_id']
                    # Handle timestamps that may not have timezone info
                    pred_date_str = pred['prediction_date']
                    try:
                        # Try parsing with timezone first
                        pred_date = datetime.fromisoformat(pred_date_str)
                    except ValueError:
                        # If no timezone, assume UTC
                        pred_date = datetime.fromisoformat(pred_date_str + '+00:00')

                    # Get actual price from main database (within ±1 hour of prediction date)
                    actual_data = db_manager.get_price_range(
                        coin_id,
                        (pred_date - timedelta(hours=1)).isoformat(),
                        (pred_date + timedelta(hours=1)).isoformat()
                    )

                    if actual_data:
                        # Find the closest actual price to the prediction date
                        closest_price = None
                        min_diff = float('inf')

                        for data_point in actual_data:
                            # Handle timestamps that may not have timezone info
                            timestamp_str = data_point['timestamp']
                            try:
                                # Try parsing with timezone first
                                data_time = datetime.fromisoformat(timestamp_str)
                            except ValueError:
                                # If no timezone, assume UTC
                                data_time = datetime.fromisoformat(timestamp_str + '+00:00')
                            time_diff = abs((data_time - pred_date).total_seconds())

                            if time_diff < min_diff:
                                min_diff = time_diff
                                closest_price = data_point['price']

                        if closest_price:
                            conn.execute('''
                                UPDATE predictions
                                SET actual_price = ?
                                WHERE id = ?
                            ''', (closest_price, pred_id))

                conn.commit()
                logger.info(f"Updated actual prices for {len(predictions)} predictions")

        except Exception as e:
            logger.error(f"Failed to update actual prices: {e}")

    def calculate_metrics(self, model_version: str, coin_id: str,
                         days: int = 30) -> Dict:
        """Calculate performance metrics for a model over a time period"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)

            with sqlite3.connect(self.db_path) as conn:
                predictions = conn.execute('''
                    SELECT predicted_price, actual_price
                    FROM predictions
                    WHERE model_version = ? AND coin_id = ?
                      AND prediction_timestamp >= ?
                      AND actual_price IS NOT NULL
                ''', (model_version, coin_id, cutoff_date.isoformat())).fetchall()

                if not predictions:
                    return {'sample_size': 0}

                predicted = np.array([p['predicted_price'] for p in predictions])
                actual = np.array([p['actual_price'] for p in predictions])

                # Calculate metrics
                mse = np.mean((predicted - actual) ** 2)
                rmse = np.sqrt(mse)
                mae = np.mean(np.abs(predicted - actual))
                mape = np.mean(np.abs((actual - predicted) / actual)) * 100

                metrics = {
                    'rmse': rmse,
                    'mae': mae,
                    'mape': mape,
                    'sample_size': len(predictions),
                    'mse': mse
                }

                # Store metrics
                metric_date = datetime.now().date()
                conn.execute('''
                    INSERT OR REPLACE INTO performance_metrics
                    (model_version, coin_id, metric_date, period_days, rmse, mae, mape, sample_size)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (model_version, coin_id, metric_date.isoformat(), days,
                      rmse, mae, mape, len(predictions)))

                conn.commit()

                return metrics

        except Exception as e:
            logger.error(f"Failed to calculate metrics for {model_version}: {e}")
            return {}

    def get_performance_history(self, model_version: str, coin_id: str,
                               days: int = 90) -> List[Dict]:
        """Get historical performance metrics"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)

            with sqlite3.connect(self.db_path) as conn:
                metrics = conn.execute('''
                    SELECT metric_date, period_days, rmse, mae, mape, sample_size
                    FROM performance_metrics
                    WHERE model_version = ? AND coin_id = ?
                      AND metric_date >= ?
                    ORDER BY metric_date ASC
                ''', (model_version, coin_id, cutoff_date.date().isoformat())).fetchall()

                return [{
                    'date': row['metric_date'],
                    'period_days': row['period_days'],
                    'rmse': row['rmse'],
                    'mae': row['mae'],
                    'mape': row['mape'],
                    'sample_size': row['sample_size']
                } for row in metrics]

        except Exception as e:
            logger.error(f"Failed to get performance history: {e}")
            return []

    def detect_performance_degradation(self, model_version: str, coin_id: str,
                                      threshold_mape: float = 15.0) -> Dict:
        """Detect if model performance has degraded"""
        try:
            # Get recent metrics (last 7 days)
            recent_metrics = self.calculate_metrics(model_version, coin_id, days=7)

            if recent_metrics.get('sample_size', 0) < 5:
                return {'degraded': False, 'reason': 'Insufficient data'}

            recent_mape = recent_metrics.get('mape', 0)

            # Get baseline performance (last 30 days)
            baseline_metrics = self.calculate_metrics(model_version, coin_id, days=30)
            baseline_mape = baseline_metrics.get('mape', 0)

            if baseline_mape == 0:
                return {'degraded': False, 'reason': 'No baseline available'}

            # Check for degradation
            degradation_ratio = recent_mape / baseline_mape

            degraded = recent_mape > threshold_mape or degradation_ratio > 1.5

            return {
                'degraded': degraded,
                'recent_mape': recent_mape,
                'baseline_mape': baseline_mape,
                'degradation_ratio': degradation_ratio,
                'threshold_exceeded': recent_mape > threshold_mape,
                'relative_degradation': degradation_ratio > 1.5
            }

        except Exception as e:
            logger.error(f"Failed to detect performance degradation: {e}")
            return {'degraded': False, 'error': str(e)}

    def get_rolling_accuracy(self, model_version: str, coin_id: str) -> Dict:
        """Get rolling accuracy metrics for different time periods"""
        periods = [7, 30]  # 7-day and 30-day rolling accuracy
        results = {}

        for days in periods:
            metrics = self.calculate_metrics(model_version, coin_id, days)
            results[f'{days}_day'] = metrics

        return results

    def should_retrain_model(self, model_version: str, coin_id: str,
                            mape_threshold: float = 15.0) -> Dict:
        """Check if a model should be retrained based on performance"""
        try:
            # Get recent performance (last 7 days)
            recent_metrics = self.calculate_metrics(model_version, coin_id, days=7)

            if recent_metrics.get('sample_size', 0) < 5:
                return {
                    'should_retrain': False,
                    'reason': 'Insufficient recent data for retraining decision'
                }

            recent_mape = recent_metrics.get('mape', 0)

            # Check if MAPE exceeds threshold
            if recent_mape > mape_threshold:
                return {
                    'should_retrain': True,
                    'reason': f'MAPE ({recent_mape:.2f}%) exceeds threshold ({mape_threshold}%)',
                    'current_mape': recent_mape,
                    'threshold': mape_threshold
                }

            # Check for significant degradation
            degradation = self.detect_performance_degradation(model_version, coin_id)
            if degradation.get('degraded', False):
                return {
                    'should_retrain': True,
                    'reason': 'Performance degradation detected',
                    'degradation_info': degradation
                }

            return {
                'should_retrain': False,
                'reason': f'Model performing well (MAPE: {recent_mape:.2f}%)',
                'current_mape': recent_mape
            }

        except Exception as e:
            logger.error(f"Failed to check retraining need: {e}")
            return {
                'should_retrain': False,
                'reason': f'Error checking retraining: {str(e)}'
            }

    def get_model_health_score(self, model_version: str, coin_id: str) -> float:
        """Calculate overall model health score (0-100)"""
        try:
            degradation = self.detect_performance_degradation(model_version, coin_id)
            rolling_metrics = self.get_rolling_accuracy(model_version, coin_id)

            # Base score
            score = 100.0

            # Penalize for degradation
            if degradation.get('degraded', False):
                score -= 30

            # Penalize for high MAPE
            recent_mape = rolling_metrics.get('7_day', {}).get('mape', 0)
            if recent_mape > 20:
                score -= 20
            elif recent_mape > 10:
                score -= 10

            # Penalize for low sample size
            sample_size = rolling_metrics.get('7_day', {}).get('sample_size', 0)
            if sample_size < 10:
                score -= 15
            elif sample_size < 5:
                score -= 30

            return max(0, min(100, score))

        except Exception as e:
            logger.error(f"Failed to calculate health score: {e}")
            return 0.0
