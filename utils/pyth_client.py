"""
Pyth Network API client for real-time cryptocurrency price data.
Uses Hermes API for fast, reliable price feeds.
"""

import requests
import logging
from typing import Dict, List, Optional
from datetime import datetime, timezone
import time

from config.settings import settings
from utils.exceptions import APIError
from utils.cache_manager import cached

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Pyth Network price feed IDs for major cryptocurrencies
# Verified against Hermes API v2 - Last updated: 2025-01-09
PYTH_PRICE_FEED_IDS = {
    'bitcoin': '0xe62df6c8b4a85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43',  # BTC/USD
    'ethereum': '0xff61491a931112ddf1bd8147cd1b641375f79f5825126d665480874634fd0ace',  # ETH/USD
    'solana': '0xef0d8b6fda2ceba41da15d4095d1da392a0d2f8ed0c6c7bc0f4cfac8c280b56d',  # SOL/USD
    'cardano': '0x2a01deaec9e51a579277b34b122399984d0bbf57e2458a7e42fecd2829867a0d',  # ADA/USD
    'polkadot': '0xca3eed9b267293f6595901c734c7525ce8ef49adafe8284606ceb307afa2ca5b',  # DOT/USD (UPDATED)
    'avalanche-2': '0x93da3352f9f1d105fdfe4971cfa80e9dd777bfc5d0f683ebb6e1294b92137bb7',  # AVAX/USD
    'polygon': '0xffd11c5a1cfd42f80afb2df4d9f264c15f956d68153335374ec10722edd70472',  # POL/USD (formerly MATIC)
    'chainlink': '0x8ac0c70fff57e9aefdf5edf44b51d62c2d433653cbb2cf5cc06bb115af04d221',  # LINK/USD
    'uniswap': '0x78d185a741d07edb3412b09008b7c5cfb9bbbd7d568bf00ba737b456ba171501',  # UNI/USD
    'cosmos': '0xb00b60f88b03a6a625a8d1c048c3f66653edf217439983d037e7222c4e612819',  # ATOM/USD
}

# Reverse mapping for display names
PYTH_COIN_NAMES = {
    'bitcoin': 'Bitcoin',
    'ethereum': 'Ethereum',
    'solana': 'Solana',
    'cardano': 'Cardano',
    'polkadot': 'Polkadot',
    'avalanche-2': 'Avalanche',
    'polygon': 'Polygon',
    'chainlink': 'Chainlink',
    'uniswap': 'Uniswap',
    'cosmos': 'Cosmos',
}

PYTH_COIN_SYMBOLS = {
    'bitcoin': 'BTC',
    'ethereum': 'ETH',
    'solana': 'SOL',
    'cardano': 'ADA',
    'polkadot': 'DOT',
    'avalanche-2': 'AVAX',
    'polygon': 'POL',
    'chainlink': 'LINK',
    'uniswap': 'UNI',
    'cosmos': 'ATOM',
}


class PythNetworkClient:
    """Client for interacting with Pyth Network Hermes API."""
    
    BASE_URL = "https://hermes.pyth.network"
    
    def __init__(self):
        """Initialize the Pyth Network client."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CryptoInsight-Pro/1.0',
            'Accept': 'application/json'
        })
        self.request_count = 0
        self.last_request_time = 0
    
    def _rate_limit(self):
        """
        Implement rate limiting to avoid overwhelming the API.
        Pyth Network Hermes is generally more permissive than CoinGecko.
        """
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        # Minimum 100ms between requests (10 requests/second)
        min_interval = 0.1
        if time_since_last_request < min_interval:
            time.sleep(min_interval - time_since_last_request)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make a request to the Pyth Network API with error handling.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            JSON response data
            
        Raises:
            APIError: If the request fails
        """
        self._rate_limit()
        
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.Timeout:
            logger.error(f"Timeout requesting {url}")
            raise APIError(f"Request timeout for {endpoint}")
        
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error {e.response.status_code} for {url}: {e}")
            raise APIError(f"HTTP {e.response.status_code}: {str(e)}")
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            raise APIError(f"Request failed: {str(e)}")
        
        except ValueError as e:
            logger.error(f"Invalid JSON response from {url}: {e}")
            raise APIError(f"Invalid JSON response: {str(e)}")
    
    @cached(ttl=settings.CACHE_TTL_PRICES, key_prefix="pyth_prices")
    def get_current_prices(self, coin_ids: List[str]) -> Dict:
        """
        Fetch current prices for multiple cryptocurrencies.
        
        Args:
            coin_ids: List of coin IDs (e.g., ['bitcoin', 'ethereum'])
            
        Returns:
            Dictionary mapping coin IDs to price data
        """
        # Get price feed IDs for requested coins
        feed_ids = [PYTH_PRICE_FEED_IDS[coin_id] for coin_id in coin_ids if coin_id in PYTH_PRICE_FEED_IDS]
        
        if not feed_ids:
            logger.warning(f"No valid price feeds found for coins: {coin_ids}")
            return {}
        
        # Build query parameters - Pyth uses 'ids[]' array notation
        # requests library requires a list of tuples for repeated parameters
        params = [('ids[]', feed_id) for feed_id in feed_ids]
        
        try:
            data = self._make_request('/api/latest_price_feeds', params=params)
            
            # Transform Pyth response to match our expected format
            result = {}
            
            # Create reverse mapping of feed IDs to coin IDs
            feed_id_to_coin = {v: k for k, v in PYTH_PRICE_FEED_IDS.items()}
            
            # Pyth API returns array directly, not nested in 'parsed'
            price_feeds = data if isinstance(data, list) else data.get('parsed', [])
            
            for price_feed in price_feeds:
                feed_id = price_feed['id']
                # API returns IDs without 0x prefix, but our dict has them with 0x
                feed_id_with_prefix = f"0x{feed_id}" if not feed_id.startswith('0x') else feed_id
                coin_id = feed_id_to_coin.get(feed_id_with_prefix)
                
                if not coin_id:
                    logger.warning(f"Unknown feed ID: {feed_id}")
                    continue
                
                price_data = price_feed.get('price', {})
                ema_price_data = price_feed.get('ema_price', {})
                
                # Convert price (Pyth uses different exponent format)
                price_raw = int(price_data.get('price', 0))
                expo = int(price_data.get('expo', -8))
                current_price = price_raw * (10 ** expo)
                
                # EMA price for comparison
                ema_price_raw = int(ema_price_data.get('price', 0))
                ema_price = ema_price_raw * (10 ** expo)
                
                # Calculate 24h change (approximation using EMA)
                price_change_24h = ((current_price - ema_price) / ema_price * 100) if ema_price > 0 else 0
                
                result[coin_id] = {
                    'id': coin_id,
                    'symbol': PYTH_COIN_SYMBOLS.get(coin_id, coin_id.upper()),
                    'name': PYTH_COIN_NAMES.get(coin_id, coin_id.title()),
                    'current_price': current_price,
                    'price_change_percentage_24h': price_change_24h,
                    'market_cap': current_price * 1000000000,  # Placeholder
                    'total_volume': current_price * 100000000,  # Placeholder
                    'last_updated': datetime.fromtimestamp(price_data.get('publish_time', time.time()), tz=timezone.utc).isoformat(),
                    'confidence': int(price_data.get('conf', 0)) * (10 ** expo),
                    'ema_price': ema_price,
                    'sparkline_7d': None,  # Not available from Pyth
                }
            
            logger.info(f"Fetched prices for {len(result)} coins from Pyth Network")
            return result
        
        except Exception as e:
            logger.error(f"Error fetching prices from Pyth Network: {e}")
            raise APIError(f"Failed to fetch prices: {str(e)}")
    
    def get_historical_data(self, coin_id: str, days: int = 30) -> 'pd.DataFrame':
        """
        Fetch historical price data for a cryptocurrency.
        
        Note: Pyth Network focuses on real-time data. For historical data,
        we'll need to either:
        1. Use a different API (like CoinGecko) for historical data
        2. Store our own historical snapshots
        3. Use Pyth's on-chain historical data (more complex)
        
        For now, this returns a placeholder that fetches current price repeatedly.
        
        Args:
            coin_id: Coin identifier
            days: Number of days of historical data
            
        Returns:
            DataFrame with columns: timestamp, price
        """
        # Try to generate simulated historical data without relying on heavy binary
        # dependencies (pandas/numpy). Return a simple dict with a 'prices' list so
        # callers can handle both pandas DataFrame and lightweight dict returns.
        import random
        from datetime import timedelta

        logger.warning(f"Pyth Network doesn't provide historical REST API. Returning simulated data for {coin_id}")

        # Get current price
        current_data = self.get_current_prices([coin_id])
        if not current_data or coin_id not in current_data:
            raise APIError(f"Could not fetch current price for {coin_id}")

        current_price = float(current_data[coin_id]['current_price'])

        total_hours = max(1, days * 24)
        now = datetime.now()

        # Generate hourly timestamps and simulated prices using geometric Brownian motion
        timestamps = []
        prices = []
        price = current_price
        volatility = 0.02  # 2% hourly volatility

        for i in range(total_hours):
            # step backwards from now
            ts = now - timedelta(hours=(total_hours - 1 - i))
            # simple random return
            r = random.gauss(0, volatility)
            price = price * (2.718281828459045 ** r)
            timestamps.append(ts)
            prices.append(float(price))

        # Return a lightweight structure consumable by app.get_coin_data
        prices_ms = [[int(ts.timestamp() * 1000), p] for ts, p in zip(timestamps, prices)]

        return {'prices': prices_ms, 'market_caps': [], 'total_volumes': []}
    
    def get_trending_coins(self) -> List[Dict]:
        """
        Get trending cryptocurrencies.
        
        Note: Pyth Network doesn't provide trending data.
        Returns top coins by default.
        """
        logger.info("Pyth Network doesn't provide trending data. Returning top coins.")
        
        top_coins = list(PYTH_PRICE_FEED_IDS.keys())[:7]
        prices = self.get_current_prices(top_coins)
        
        return [
            {
                'item': {
                    'id': coin_id,
                    'name': data['name'],
                    'symbol': data['symbol'],
                    'market_cap_rank': idx + 1,
                    'price_btc': data['current_price'] / prices.get('bitcoin', {}).get('current_price', 1) if 'bitcoin' in prices else 0,
                }
            }
            for idx, (coin_id, data) in enumerate(prices.items())
        ]
    
    def get_coin_details(self, coin_id: str) -> Dict:
        """
        Get detailed information about a specific cryptocurrency.
        
        Args:
            coin_id: Coin identifier
            
        Returns:
            Dictionary with coin details
        """
        prices = self.get_current_prices([coin_id])
        
        if coin_id not in prices:
            raise APIError(f"Coin {coin_id} not found")
        
        data = prices[coin_id]
        
        return {
            'id': coin_id,
            'symbol': data['symbol'],
            'name': data['name'],
            'description': f"{data['name']} price feed powered by Pyth Network",
            'market_data': {
                'current_price': {'usd': data['current_price']},
                'market_cap': {'usd': data['market_cap']},
                'total_volume': {'usd': data['total_volume']},
                'price_change_percentage_24h': data['price_change_percentage_24h'],
                'confidence_interval': data['confidence'],
            },
            'last_updated': data['last_updated'],
        }


# Global client instance
pyth_client = PythNetworkClient()
