import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict
import os

class ModelRegistry:
    def __init__(self, db_path="models/models.db"):
        """Initialize model registry with SQLite database"""
        self.db_path = db_path
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        """Create database and tables if they don't exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS model_registry (
                    version TEXT PRIMARY KEY,
                    coin_id TEXT NOT NULL,
                    created_at DATETIME NOT NULL,
                    rmse REAL,
                    mae REAL,
                    mape REAL,
                    hyperparameters TEXT,
                    model_path TEXT NOT NULL
                )
            ''')
            conn.commit()

    def _get_next_version(self, coin_id):
        """Get next semantic version for a coin's models"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT version FROM model_registry
                WHERE coin_id = ?
                ORDER BY created_at DESC
                LIMIT 1
            ''', (coin_id,))

            result = cursor.fetchone()

            if not result:
                return "v1.0.0"

            # Parse current version
            current_version = result[0].replace('v', '')
            major, minor, patch = map(int, current_version.split('.'))

            # Increment patch version
            patch += 1
            return f"v{major}.{minor}.{patch}"

    def register_model(self, coin_id, model_path, metrics, hyperparameters):
        """Register a new model version"""
        version = self._get_next_version(coin_id)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO model_registry
                (version, coin_id, created_at, rmse, mae, mape, hyperparameters, model_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                version,
                coin_id,
                datetime.now(),
                metrics.get('rmse'),
                metrics.get('mae'),
                metrics.get('mape'),
                json.dumps(hyperparameters),
                model_path
            ))
            conn.commit()

        return version

    def get_model_versions(self, coin_id=None):
        """Get all model versions, optionally filtered by coin_id"""
        with sqlite3.connect(self.db_path) as conn:
            if coin_id:
                cursor = conn.execute('''
                    SELECT * FROM model_registry
                    WHERE coin_id = ?
                    ORDER BY created_at DESC
                ''', (coin_id,))
            else:
                cursor = conn.execute('''
                    SELECT * FROM model_registry
                    ORDER BY created_at DESC
                ''')

            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_latest_version(self, coin_id):
        """Get the latest model version for a coin"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT * FROM model_registry
                WHERE coin_id = ?
                ORDER BY created_at DESC
                LIMIT 1
            ''', (coin_id,))

            result = cursor.fetchone()
            if result:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, result))
            return None

    def get_model_by_version(self, version):
        """Get model details by version"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT * FROM model_registry
                WHERE version = ?
            ''', (version,))

            result = cursor.fetchone()
            if result:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, result))
            return None

    def rollback_to_version(self, version: str) -> Dict:
        """Rollback to a specific model version"""
        try:
            model = self.get_model_by_version(version)
            if not model:
                return {
                    'success': False,
                    'error': f'Model version {version} not found'
                }

            # Mark this version as active (you could add an 'active' column to the table)
            # For now, just return the model info for the application to use
            return {
                'success': True,
                'model': model,
                'message': f'Rolled back to version {version}'
            }

        except Exception as e:
            logger.error(f"Failed to rollback to version {version}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_rollback_candidates(self, coin_id: str, current_version: str) -> List[Dict]:
        """Get candidate versions for rollback (excluding current version)"""
        try:
            models = self.get_model_versions(coin_id)
            # Exclude current version and return others as rollback candidates
            candidates = [m for m in models if m['version'] != current_version]
            return candidates

        except Exception as e:
            logger.error(f"Failed to get rollback candidates: {e}")
            return []

    def export_metadata(self, format='json'):
        """Export all model metadata"""
        models = self.get_model_versions()

        if format == 'json':
            return json.dumps(models, indent=2, default=str)
        elif format == 'csv':
            import csv
            import io

            output = io.StringIO()
            if models:
                writer = csv.DictWriter(output, fieldnames=models[0].keys())
                writer.writeheader()
                writer.writerows(models)
            return output.getvalue()
        else:
            raise ValueError("Format must be 'json' or 'csv'")
