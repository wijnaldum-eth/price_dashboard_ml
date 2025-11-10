"""
Configuration management for Crypto Intelligence Dashboard.
Centralizes all application settings and environment variables.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Application configuration settings."""
    
    # Base paths
    BASE_DIR = Path(__file__).parent.parent
    MODEL_DIR = BASE_DIR / "models"
    
    # Venice AI Configuration
    VENICE_API_KEY: str = os.getenv("VENICE_API_KEY", "")
    VENICE_API_URL: str = "https://api.venice.ai/v1"
    
    # Redis Configuration
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    
    # Application Configuration
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Cache TTL Settings (in seconds)
    CACHE_TTL_PRICES: int = int(os.getenv("CACHE_TTL_PRICES", "120"))  # 2 minutes
    CACHE_TTL_HISTORICAL: int = int(os.getenv("CACHE_TTL_HISTORICAL", "3600"))  # 1 hour
    CACHE_TTL_AI_INSIGHTS: int = int(os.getenv("CACHE_TTL_AI_INSIGHTS", "900"))  # 15 minutes
    CACHE_TTL_NEWS: int = int(os.getenv("CACHE_TTL_NEWS", "1800"))  # 30 minutes
    CACHE_TTL_MODELS: int = int(os.getenv("CACHE_TTL_MODELS", "86400"))  # 24 hours
    
    # API Rate Limits (requests per minute)
    COINGECKO_RATE_LIMIT: int = int(os.getenv("COINGECKO_RATE_LIMIT", "50"))
    VENICE_AI_RATE_LIMIT: int = int(os.getenv("VENICE_AI_RATE_LIMIT", "100"))
    
    # CoinGecko API Configuration
    COINGECKO_API_URL: str = "https://api.coingecko.com/api/v3"
    COINGECKO_TIMEOUT: int = 10  # seconds
    COINGECKO_RETRY_ATTEMPTS: int = 3
    COINGECKO_RETRY_DELAY: int = 2  # seconds
    
    # CryptoPanic API Configuration
    CRYPTOPANIC_API_URL: str = "https://cryptopanic.com/api/v1"
    CRYPTOPANIC_API_KEY: str = os.getenv("CRYPTOPANIC_API_KEY", "")
    
    # Pyth Network API Configuration
    PYTH_API_URL: str = "https://api.pyth.network"
    PYTH_API_TIMEOUT: int = 10  # seconds
    PYTH_API_RETRY_ATTEMPTS: int = 3
    PYTH_API_RETRY_DELAY: int = 2  # seconds
    
    # Model Configuration
    LSTM_EPOCHS: int = int(os.getenv("LSTM_EPOCHS", "50"))
    LSTM_BATCH_SIZE: int = int(os.getenv("LSTM_BATCH_SIZE", "32"))
    LSTM_SEQUENCE_LENGTH: int = 60  # days of historical data for training
    LSTM_PREDICTION_DAYS: int = 7  # days to predict into future
    MODEL_SAVE_PATH: Path = Path(os.getenv("MODEL_SAVE_PATH", "./models"))
    
    # Tracked cryptocurrencies (Pyth Network compatible IDs)
    TRACKED_COINS = [
        'bitcoin', 'ethereum', 'solana', 'cardano', 'polkadot',
        'avalanche-2', 'polygon', 'chainlink', 'uniswap', 'cosmos'
    ]
    
    # API Provider (pyth or coingecko)
    API_PROVIDER = os.getenv('API_PROVIDER', 'pyth')
    
    COIN_DISPLAY_NAMES = {
        "bitcoin": "Bitcoin (BTC)",
        "ethereum": "Ethereum (ETH)",
        "solana": "Solana (SOL)",
        "cardano": "Cardano (ADA)",
        "polkadot": "Polkadot (DOT)",
        "avalanche-2": "Avalanche (AVAX)",
        "polygon": "Polygon (POL)",
        "chainlink": "Chainlink (LINK)",
        "uniswap": "Uniswap (UNI)",
        "cosmos": "Cosmos (ATOM)"
    }
    
    # UI Configuration
    PAGE_TITLE: str = "CryptoInsight Pro"
    PAGE_ICON: str = "📊"
    LAYOUT: str = "wide"
    
    # Performance Targets
    TARGET_LOAD_TIME: float = 3.0  # seconds
    MAX_MEMORY_MB: int = 512
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration settings."""
        errors = []
        
        if not cls.VENICE_API_KEY:
            errors.append("VENICE_API_KEY is not set")
        
        if not cls.MODEL_DIR.exists():
            cls.MODEL_DIR.mkdir(parents=True, exist_ok=True)
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        return True
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production environment."""
        return cls.APP_ENV == "production"
    
    @classmethod
    def get_redis_url(cls) -> str:
        """Get Redis connection URL."""
        if cls.REDIS_PASSWORD:
            return f"redis://:{cls.REDIS_PASSWORD}@{cls.REDIS_HOST}:{cls.REDIS_PORT}/{cls.REDIS_DB}"
        return f"redis://{cls.REDIS_HOST}:{cls.REDIS_PORT}/{cls.REDIS_DB}"


# Create settings instance
settings = Settings()
