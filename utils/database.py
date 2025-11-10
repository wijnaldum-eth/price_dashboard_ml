"""
SQL Database integration for cryptocurrency price data storage.
Provides SQLite-based historical price data management with data validation.
"""

import sqlite3
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from contextlib import contextmanager
import os

from config.settings import settings
from utils.exceptions import DatabaseError
from utils.pyth_client import pyth_client

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)


class DatabaseManager:
    """SQLite database manager for cryptocurrency price data."""

    def __init__(self, db_path: str = "crypto_prices.db"):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.execute("PRAGMA foreign_keys = ON")
            conn.row_factory = sqlite3.Row  # Enable column access by name
            yield conn
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise DatabaseError(f"Failed to connect to database: {str(e)}")
        finally:
            if conn:
                conn.close()

    def _init_db(self):
        """Initialize database schema."""
        try:
            with self.get_connection() as conn:
                # Create price_history table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS price_history (
                        id INTEGER PRIMARY KEY,
                        coin_id TEXT NOT NULL,
                        timestamp DATETIME NOT NULL,
                        price REAL NOT NULL,
                        volume_24h REAL,
                        market_cap REAL,
                        source TEXT DEFAULT 'pyth',
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # Create indexes for performance
                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_coin_timestamp
                    ON price_history(coin_id, timestamp)
                ''')

                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_timestamp
                    ON price_history(timestamp)
                ''')

                conn.commit()
                logger.info("Database initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise DatabaseError(f"Database initialization failed: {str(e)}")

    def insert_price_data(self, coin_id: str, price_data: Dict) -> bool:
        """
        Insert price data into database with validation.

        Args:
            coin_id: Cryptocurrency identifier
            price_data: Dictionary containing price information

        Returns:
            True if inserted successfully, False otherwise
        """
        try:
            # Validate data
            if not self._validate_price_data(price_data):
                logger.warning(f"Invalid price data for {coin_id}: {price_data}")
                return False

            with self.get_connection() as conn:
                # Check for duplicate entry (same coin_id and timestamp within 1 minute)
                existing = conn.execute('''
                    SELECT id FROM price_history
                    WHERE coin_id = ? AND timestamp >= ? AND timestamp < ?
                ''', (
                    coin_id,
                    price_data['timestamp'],
                    (datetime.fromisoformat(price_data['timestamp']) + timedelta(minutes=1)).isoformat()
                )).fetchone()

                if existing:
                    logger.debug(f"Duplicate price data for {coin_id} at {price_data['timestamp']}, skipping")
                    return False

                # Insert new price data
                conn.execute('''
                    INSERT INTO price_history (coin_id, timestamp, price, volume_24h, market_cap, source)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    coin_id,
                    price_data['timestamp'],
                    price_data['price'],
                    price_data.get('volume_24h'),
                    price_data.get('market_cap'),
                    price_data.get('source', 'pyth')
                ))

                conn.commit()
                logger.debug(f"Inserted price data for {coin_id}: ${price_data['price']}")
                return True

        except Exception as e:
            logger.error(f"Failed to insert price data for {coin_id}: {e}")
            return False

    def _validate_price_data(self, price_data: Dict) -> bool:
        """
        Validate price data before insertion.

        Args:
            price_data: Price data dictionary

        Returns:
            True if valid, False otherwise
        """
        required_fields = ['timestamp', 'price']

        # Check required fields
        for field in required_fields:
            if field not in price_data:
                logger.warning(f"Missing required field: {field}")
                return False

        # Validate price
        try:
            price = float(price_data['price'])
            if price <= 0:
                logger.warning(f"Invalid price: {price} (must be > 0)")
                return False
        except (ValueError, TypeError):
            logger.warning(f"Invalid price format: {price_data['price']}")
            return False

        # Validate timestamp
        try:
            timestamp_str = price_data['timestamp']
            # Handle different timestamp formats
            if timestamp_str.endswith('Z'):
                timestamp_str = timestamp_str[:-1] + '+00:00'
            elif '+' not in timestamp_str and timestamp_str.count('-') == 2:
                # ISO format without timezone, assume UTC
                timestamp_str += '+00:00'
            datetime.fromisoformat(timestamp_str)
        except (ValueError, AttributeError):
            logger.warning(f"Invalid timestamp format: {price_data['timestamp']}")
            return False

        return True

    def get_historical_prices(self, coin_id: str, days: int = 30) -> List[Dict]:
        """
        Get historical price data for a cryptocurrency.

        Args:
            coin_id: Cryptocurrency identifier
            days: Number of days of historical data

        Returns:
            List of price data dictionaries
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)

            with self.get_connection() as conn:
                rows = conn.execute('''
                    SELECT timestamp, price, volume_24h, market_cap, source
                    FROM price_history
                    WHERE coin_id = ? AND timestamp >= ?
                    ORDER BY timestamp ASC
                ''', (coin_id, cutoff_date.isoformat())).fetchall()

                return [{
                    'timestamp': row['timestamp'],
                    'price': row['price'],
                    'volume_24h': row['volume_24h'],
                    'market_cap': row['market_cap'],
                    'source': row['source']
                } for row in rows]

        except Exception as e:
            logger.error(f"Failed to get historical prices for {coin_id}: {e}")
            return []

    def get_latest_price(self, coin_id: str) -> Optional[Dict]:
        """
        Get the most recent price data for a cryptocurrency.

        Args:
            coin_id: Cryptocurrency identifier

        Returns:
            Latest price data dictionary or None if not found
        """
        try:
            with self.get_connection() as conn:
                row = conn.execute('''
                    SELECT timestamp, price, volume_24h, market_cap, source
                    FROM price_history
                    WHERE coin_id = ?
                    ORDER BY timestamp DESC
                    LIMIT 1
                ''', (coin_id,)).fetchone()

                if row:
                    return {
                        'timestamp': row['timestamp'],
                        'price': row['price'],
                        'volume_24h': row['volume_24h'],
                        'market_cap': row['market_cap'],
                        'source': row['source']
                    }
                return None

        except Exception as e:
            logger.error(f"Failed to get latest price for {coin_id}: {e}")
            return None

    def get_price_range(self, coin_id: str, start_date: str, end_date: str) -> List[Dict]:
        """
        Get price data within a date range.

        Args:
            coin_id: Cryptocurrency identifier
            start_date: Start date in ISO format
            end_date: End date in ISO format

        Returns:
            List of price data dictionaries
        """
        try:
            with self.get_connection() as conn:
                rows = conn.execute('''
                    SELECT timestamp, price, volume_24h, market_cap, source
                    FROM price_history
                    WHERE coin_id = ? AND timestamp >= ? AND timestamp <= ?
                    ORDER BY timestamp ASC
                ''', (coin_id, start_date, end_date)).fetchall()

                return [{
                    'timestamp': row['timestamp'],
                    'price': row['price'],
                    'volume_24h': row['volume_24h'],
                    'market_cap': row['market_cap'],
                    'source': row['source']
                } for row in rows]

        except Exception as e:
            logger.error(f"Failed to get price range for {coin_id}: {e}")
            return []

    def backfill_historical_data(self, coin_ids: List[str], days: int = 90) -> Dict[str, int]:
        """
        Backfill historical data by fetching current prices multiple times.

        Note: Since Pyth doesn't provide historical API, we'll simulate by
        fetching current prices and storing them with historical timestamps.

        Args:
            coin_ids: List of cryptocurrency identifiers
            days: Number of days to backfill

        Returns:
            Dictionary mapping coin_ids to number of records inserted
        """
        results = {}
        end_date = datetime.now()

        logger.info(f"Starting backfill for {len(coin_ids)} coins over {days} days")

        try:
            for coin_id in coin_ids:
                inserted_count = 0

                # Get current price to use as base
                current_data = pyth_client.get_current_prices([coin_id])
                if coin_id not in current_data:
                    logger.warning(f"Could not fetch current price for {coin_id}, skipping backfill")
                    results[coin_id] = 0
                    continue

                current_price = current_data[coin_id]['current_price']

                # Generate historical timestamps (every 4 hours for efficiency)
                timestamps = []
                current_time = end_date - timedelta(days=days)

                while current_time <= end_date:
                    timestamps.append(current_time)
                    current_time += timedelta(hours=4)

                # Insert historical data with simulated prices
                for timestamp in timestamps:
                    # Add some realistic volatility (±5%)
                    import random
                    volatility_factor = random.uniform(0.95, 1.05)
                    simulated_price = current_price * volatility_factor

                    price_data = {
                        'timestamp': timestamp.isoformat(),
                        'price': simulated_price,
                        'volume_24h': current_data[coin_id].get('total_volume', simulated_price * 1000000),
                        'market_cap': current_data[coin_id].get('market_cap', simulated_price * 10000000),
                        'source': 'pyth_simulated'
                    }

                    if self.insert_price_data(coin_id, price_data):
                        inserted_count += 1

                results[coin_id] = inserted_count
                logger.info(f"Backfilled {inserted_count} records for {coin_id}")

        except Exception as e:
            logger.error(f"Failed to backfill historical data: {e}")
            raise DatabaseError(f"Backfill failed: {str(e)}")

        return results

    def ingest_current_prices(self, coin_ids: List[str]) -> Dict[str, bool]:
        """
        Fetch current prices from Pyth and store in database.

        Args:
            coin_ids: List of cryptocurrency identifiers

        Returns:
            Dictionary mapping coin_ids to success status
        """
        results = {}

        try:
            # Fetch current prices
            price_data = pyth_client.get_current_prices(coin_ids)

            for coin_id in coin_ids:
                if coin_id in price_data:
                    data = price_data[coin_id]

                    # Transform to database format
                    db_data = {
                        'timestamp': data['last_updated'],
                        'price': data['current_price'],
                        'volume_24h': data.get('total_volume'),
                        'market_cap': data.get('market_cap'),
                        'source': 'pyth'
                    }

                    success = self.insert_price_data(coin_id, db_data)
                    results[coin_id] = success

                    if success:
                        logger.info(f"Successfully ingested price for {coin_id}: ${data['current_price']}")
                    else:
                        logger.warning(f"Failed to ingest price for {coin_id}")
                else:
                    logger.warning(f"No price data available for {coin_id}")
                    results[coin_id] = False

        except Exception as e:
            logger.error(f"Failed to ingest current prices: {e}")
            raise DatabaseError(f"Price ingestion failed: {str(e)}")

        return results

    def get_data_stats(self) -> Dict:
        """
        Get database statistics.

        Returns:
            Dictionary with database statistics
        """
        try:
            with self.get_connection() as conn:
                # Total records
                total_records = conn.execute('SELECT COUNT(*) FROM price_history').fetchone()[0]

                # Records per coin
                coin_stats = conn.execute('''
                    SELECT coin_id, COUNT(*) as count, MIN(timestamp) as oldest, MAX(timestamp) as newest
                    FROM price_history
                    GROUP BY coin_id
                    ORDER BY count DESC
                ''').fetchall()

                # Date range
                date_range = conn.execute('''
                    SELECT MIN(timestamp) as oldest, MAX(timestamp) as newest
                    FROM price_history
                ''').fetchone()

                return {
                    'total_records': total_records,
                    'coins_tracked': len(coin_stats),
                    'coin_breakdown': [{
                        'coin_id': row['coin_id'],
                        'record_count': row['count'],
                        'date_range': {
                            'oldest': row['oldest'],
                            'newest': row['newest']
                        }
                    } for row in coin_stats],
                    'overall_date_range': {
                        'oldest': date_range['oldest'],
                        'newest': date_range['newest']
                    }
                }

        except Exception as e:
            logger.error(f"Failed to get data stats: {e}")
            return {}


# Global database instance
db_manager = DatabaseManager()
