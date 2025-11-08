"""
CoinGecko API client with retry logic, rate limiting, and caching.
Handles all cryptocurrency market data fetching.
"""

import requests
import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import pandas as pd

from config.settings import settings
from utils.exceptions import CoinGeckoAPIError, RateLimitError

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)


class CoinGeckoClient:
    """Client for interacting with CoinGecko API."""
    
    def __init__(self):
        """Initialize the CoinGecko API client."""
        self.base_url = settings.COINGECKO_API_URL
        self.timeout = settings.COINGECKO_TIMEOUT
        self.retry_attempts = settings.COINGECKO_RETRY_ATTEMPTS
        self.retry_delay = settings.COINGECKO_RETRY_DELAY
        self.rate_limit = settings.COINGECKO_RATE_LIMIT
        self.last_request_time = 0
        self.request_count = 0
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CryptoInsight-Dashboard/1.0'
        })
    
    def _rate_limit_check(self):
        """Enforce rate limiting."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        # Reset counter every minute
        if time_since_last_request > 60:
            self.request_count = 0
            self.last_request_time = current_time
        
        # Check if we've exceeded rate limit
        if self.request_count >= self.rate_limit:
            sleep_time = 60 - time_since_last_request
            if sleep_time > 0:
                logger.warning(f"Rate limit reached. Sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
                self.request_count = 0
                self.last_request_time = time.time()
        
        self.request_count += 1
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make HTTP request with retry logic and error handling.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            JSON response as dictionary
            
        Raises:
            CoinGeckoAPIError: If request fails after all retries
            RateLimitError: If rate limit is exceeded
        """
        url = f"{self.base_url}/{endpoint}"
        
        for attempt in range(self.retry_attempts):
            try:
                # Enforce rate limiting
                self._rate_limit_check()
                
                # Make request
                response = self.session.get(
                    url,
                    params=params,
                    timeout=self.timeout
                )
                
                # Check for rate limit
                if response.status_code == 429:
                    raise RateLimitError("CoinGecko API rate limit exceeded")
                
                # Raise for HTTP errors
                response.raise_for_status()
                
                # Log successful request
                logger.debug(f"Successfully fetched {endpoint}")
                
                return response.json()
                
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout on attempt {attempt + 1}/{self.retry_attempts}")
                if attempt < self.retry_attempts - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    raise CoinGeckoAPIError(f"Request timeout after {self.retry_attempts} attempts")
            
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    raise RateLimitError("CoinGecko API rate limit exceeded")
                logger.error(f"HTTP error: {e}")
                raise CoinGeckoAPIError(f"HTTP error: {e}")
            
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed on attempt {attempt + 1}/{self.retry_attempts}: {e}")
                if attempt < self.retry_attempts - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))
                else:
                    raise CoinGeckoAPIError(f"Request failed after {self.retry_attempts} attempts: {e}")
        
        raise CoinGeckoAPIError("Unexpected error in request handling")
    
    def get_current_prices(self, coin_ids: List[str]) -> Dict[str, Any]:
        """
        Get current prices for multiple cryptocurrencies.
        
        Args:
            coin_ids: List of CoinGecko coin IDs
            
        Returns:
            Dictionary with coin data including prices, market cap, volume, etc.
        """
        try:
            params = {
                'vs_currency': 'usd',
                'ids': ','.join(coin_ids),
                'order': 'market_cap_desc',
                'per_page': len(coin_ids),
                'page': 1,
                'sparkline': True,
                'price_change_percentage': '24h,7d,30d'
            }
            
            data = self._make_request('coins/markets', params)
            
            # Transform into more usable format
            result = {}
            for coin in data:
                result[coin['id']] = {
                    'name': coin['name'],
                    'symbol': coin['symbol'].upper(),
                    'current_price': coin['current_price'],
                    'market_cap': coin['market_cap'],
                    'market_cap_rank': coin['market_cap_rank'],
                    'total_volume': coin['total_volume'],
                    'high_24h': coin['high_24h'],
                    'low_24h': coin['low_24h'],
                    'price_change_24h': coin['price_change_24h'],
                    'price_change_percentage_24h': coin['price_change_percentage_24h'],
                    'price_change_percentage_7d': coin.get('price_change_percentage_7d_in_currency'),
                    'price_change_percentage_30d': coin.get('price_change_percentage_30d_in_currency'),
                    'circulating_supply': coin['circulating_supply'],
                    'total_supply': coin['total_supply'],
                    'max_supply': coin['max_supply'],
                    'ath': coin['ath'],
                    'ath_date': coin['ath_date'],
                    'atl': coin['atl'],
                    'atl_date': coin['atl_date'],
                    'last_updated': coin['last_updated'],
                    'sparkline_7d': coin.get('sparkline_in_7d', {}).get('price', [])
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching current prices: {e}")
            raise CoinGeckoAPIError(f"Failed to fetch current prices: {e}")
    
    def get_historical_data(self, coin_id: str, days: int = 30) -> pd.DataFrame:
        """
        Get historical price data for a cryptocurrency.
        
        Args:
            coin_id: CoinGecko coin ID
            days: Number of days of historical data (1-365)
            
        Returns:
            DataFrame with columns: timestamp, price, market_cap, volume
        """
        try:
            params = {
                'vs_currency': 'usd',
                'days': days,
                'interval': 'daily' if days > 1 else 'hourly'
            }
            
            data = self._make_request(f'coins/{coin_id}/market_chart', params)
            
            # Convert to DataFrame
            df = pd.DataFrame({
                'timestamp': [item[0] for item in data['prices']],
                'price': [item[1] for item in data['prices']],
                'market_cap': [item[1] for item in data['market_caps']],
                'volume': [item[1] for item in data['total_volumes']]
            })
            
            # Convert timestamp to datetime
            df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
            df = df.set_index('date')
            df = df.drop('timestamp', axis=1)
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {coin_id}: {e}")
            raise CoinGeckoAPIError(f"Failed to fetch historical data: {e}")
    
    def get_trending_coins(self) -> List[Dict]:
        """
        Get list of trending cryptocurrencies.
        
        Returns:
            List of trending coins with basic info
        """
        try:
            data = self._make_request('search/trending')
            
            trending = []
            for item in data.get('coins', []):
                coin = item.get('item', {})
                trending.append({
                    'id': coin.get('id'),
                    'name': coin.get('name'),
                    'symbol': coin.get('symbol'),
                    'market_cap_rank': coin.get('market_cap_rank'),
                    'thumb': coin.get('thumb'),
                    'score': coin.get('score')
                })
            
            return trending
            
        except Exception as e:
            logger.error(f"Error fetching trending coins: {e}")
            raise CoinGeckoAPIError(f"Failed to fetch trending coins: {e}")
    
    def get_coin_details(self, coin_id: str) -> Dict:
        """
        Get detailed information about a specific cryptocurrency.
        
        Args:
            coin_id: CoinGecko coin ID
            
        Returns:
            Dictionary with detailed coin information
        """
        try:
            params = {
                'localization': 'false',
                'tickers': 'false',
                'market_data': 'true',
                'community_data': 'true',
                'developer_data': 'false',
                'sparkline': 'false'
            }
            
            data = self._make_request(f'coins/{coin_id}', params)
            
            return {
                'id': data['id'],
                'name': data['name'],
                'symbol': data['symbol'].upper(),
                'description': data.get('description', {}).get('en', ''),
                'categories': data.get('categories', []),
                'links': {
                    'homepage': data.get('links', {}).get('homepage', []),
                    'blockchain_site': data.get('links', {}).get('blockchain_site', []),
                    'official_forum_url': data.get('links', {}).get('official_forum_url', []),
                    'twitter_screen_name': data.get('links', {}).get('twitter_screen_name'),
                    'subreddit_url': data.get('links', {}).get('subreddit_url')
                },
                'market_data': data.get('market_data', {}),
                'community_data': data.get('community_data', {}),
                'last_updated': data.get('last_updated')
            }
            
        except Exception as e:
            logger.error(f"Error fetching coin details for {coin_id}: {e}")
            raise CoinGeckoAPIError(f"Failed to fetch coin details: {e}")
    
    def get_crypto_news(self, coin: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """
        Get cryptocurrency news headlines.
        Note: CoinGecko doesn't have a news endpoint, so this is a placeholder
        for integration with CryptoPanic or other news APIs.
        
        Args:
            coin: Optional coin symbol to filter news
            limit: Number of news items to return
            
        Returns:
            List of news items with title, url, published date
        """
        # This is a placeholder - will be implemented with CryptoPanic API
        logger.warning("News API not yet implemented")
        return []
    
    def ping(self) -> bool:
        """
        Check if CoinGecko API is accessible.
        
        Returns:
            True if API is accessible, False otherwise
        """
        try:
            self._make_request('ping')
            return True
        except Exception:
            return False


# Create singleton instance
coingecko_client = CoinGeckoClient()
