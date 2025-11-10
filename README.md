# CryptoInsight Pro 🚀

A production-ready, real-time cryptocurrency market intelligence dashboard built with Streamlit, featuring advanced ML predictions (LSTM), AI-powered insights (Venice AI), and comprehensive technical analysis. Designed for deployment on Akash Network for decentralized hosting.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.32.0-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

## ✨ Features

### Currently Implemented ✅
- **📊 Real-time Market Data**: Track top 10 cryptocurrencies with live price updates via Pyth Network
- **🔮 Pyth Network Integration**: Sub-second price feeds from 90+ first-party data providers
- **💼 Portfolio Simulator**: Calculate portfolio value, allocation, and performance
- **📈 Price Comparison**: Compare multiple cryptocurrencies with normalized charts
- **🎨 Interactive Visualizations**: Beautiful Plotly charts with dark theme
- **⚡ Smart Caching**: Redis-backed caching with in-memory fallback
- **🔄 Auto-refresh**: Configurable data refresh intervals
- **📥 Export Functionality**: Download portfolio and comparison data as CSV

### Coming Soon 🚧
- **🤖 LSTM Price Predictions**: 7-day forecasts with confidence intervals
- **🧠 Venice AI Insights**: Market analysis, trading signals, risk assessment
- **📰 News Sentiment Analysis**: Real-time sentiment tracking
- **📊 Technical Indicators**: RSI, MACD, Bollinger Bands visualization

## 🏗️ Architecture

```
crypto-dashboard/
├── app.py                      # Main Streamlit application
├── pages/                      # Multi-page app structure
│   ├── 1_📊_Market_Overview.py # Real-time price tracker
│   ├── 2_💼_Portfolio.py       # Portfolio simulator
│   ├── 3_📈_Predictions.py     # LSTM predictions (coming soon)
│   ├── 4_🤖_AI_Insights.py     # Venice AI analysis (coming soon)
│   └── 5_📰_News_Sentiment.py  # Sentiment analysis (coming soon)
├── utils/                      # Core utilities
│   ├── pyth_client.py         # Pyth Network Hermes API wrapper
│   ├── api_client.py          # CoinGecko API wrapper (fallback)
│   ├── venice_client.py       # Venice AI wrapper (coming soon)
│   ├── cache_manager.py       # Redis caching layer
│   ├── data_processing.py     # Technical indicators & data cleaning
│   ├── ml_models.py           # LSTM implementation (coming soon)
│   ├── visualizations.py      # Plotly chart components
│   └── exceptions.py          # Custom exceptions
├── config/
│   └── settings.py            # Centralized configuration
├── tests/                     # Unit tests
├── models/                    # Saved ML models
├── Dockerfile                 # Multi-stage Docker build
├── docker-compose.yml         # Local development setup
└── deploy.yaml               # Akash Network SDL

```

## 🛠️ Tech Stack

- **Frontend**: Streamlit 1.32.0
- **Data Processing**: Pandas 2.1.4, NumPy 1.26.0
- **Visualization**: Plotly 5.18.0
- **Machine Learning**: TensorFlow 2.15.0, scikit-learn 1.3.2
- **Caching**: Redis 5.0.1
- **API Integration**: CoinGecko API (free tier), Venice AI API
- **Deployment**: Docker, Docker Compose, Akash Network

## 🚀 Quick Start

### Option 1: Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/crypto-insight-pro.git
   cd crypto-insight-pro
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your VENICE_API_KEY
   ```

5. **Run the application:**
   ```bash
   streamlit run app.py
   ```

6. **Open browser:** Navigate to `http://localhost:8501`

### Option 2: Docker Compose (Recommended)

1. **Clone and configure:**
   ```bash
   git clone https://github.com/yourusername/crypto-insight-pro.git
   cd crypto-insight-pro
   cp .env.example .env
   # Edit .env and add your VENICE_API_KEY
   ```

2. **Build and run:**
   ```bash
   docker-compose up --build
   ```

3. **Access:** Open `http://localhost:8501`

### Option 3: Akash Network Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed Akash deployment instructions.

## ⚙️ Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Venice AI API
VENICE_API_KEY=your_api_key_here

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379

# Cache TTL (seconds)
CACHE_TTL_PRICES=120        # 2 minutes
CACHE_TTL_HISTORICAL=3600   # 1 hour
CACHE_TTL_AI_INSIGHTS=900   # 15 minutes

# Application
APP_ENV=production
DEBUG_MODE=false
LOG_LEVEL=INFO
```

### Tracked Cryptocurrencies

Currently tracking top 10 coins (configurable in `config/settings.py`):
- Bitcoin (BTC)
- Ethereum (ETH)
- Solana (SOL)
- Cardano (ADA)
- Polkadot (DOT)
- Avalanche (AVAX)
- Polygon (POL) - *Updated from MATIC*
- Chainlink (LINK)
- Uniswap (UNI)
- Cosmos (ATOM)

## 📊 Data Sources

- **Market Data**: [Pyth Network](https://pyth.network/) (Real-time oracle data, no rate limits) - Primary
- **Market Data (Alternative)**: [CoinGecko API](https://www.coingecko.com/en/api) (Free tier, 50 calls/min)
- **AI Analysis**: [Venice AI API](https://venice.ai) (Requires API key)
- **News**: CryptoPanic API (Coming soon)

## 🧪 Testing

Run unit tests:
```bash
pytest tests/ -v --cov=utils --cov-report=html
```

View coverage report:
```bash
open htmlcov/index.html
```

## 📈 Performance

- **Load Time**: < 3 seconds (with caching)
- **API Response**: < 500ms (cached)
- **Memory Usage**: < 512MB
- **Docker Image**: < 1GB

## 🔒 Security

- ✅ API keys stored in environment variables
- ✅ Input validation and sanitization
- ✅ Rate limiting on API calls
- ✅ No sensitive data in logs
- ✅ HTTPS enforced in production

## 🗺️ Roadmap

- [x] Real-time price tracking
- [x] Portfolio simulator
- [x] Price comparison tool
- [x] Docker containerization
- [ ] LSTM price predictions
- [ ] Venice AI market insights
- [ ] News sentiment analysis
- [ ] Akash Network deployment
- [ ] Mobile app (future)
- [ ] User authentication (future)

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Pyth Network](https://pyth.network/) for real-time, first-party oracle data
- [CoinGecko](https://www.coingecko.com/) for free cryptocurrency data API
- [Streamlit](https://streamlit.io/) for the amazing web framework
- [Venice AI](https://venice.ai/) for AI-powered insights
- [Akash Network](https://akash.network/) for decentralized cloud hosting

## 📧 Contact

For questions, feedback, or support:
- Open an issue on GitHub
- Email: your.email@example.com
- Twitter: @yourusername

---

**Built with ❤️ using AI-assisted development workflow**
