# Task List: Crypto Market Intelligence Dashboard

## Relevant Files

### Core Application
- `app.py` - Main Streamlit application entry point with navigation
- `pages/1_📊_Market_Overview.py` - Real-time price tracker and market overview
- `pages/2_💼_Portfolio.py` - Portfolio simulator and tracking
- `pages/3_📈_Predictions.py` - LSTM price predictions and forecasts
- `pages/4_🤖_AI_Insights.py` - Venice AI market analysis and trading signals
- `pages/5_📰_News_Sentiment.py` - News aggregation and sentiment analysis

### Utilities
- `utils/api_client.py` - CoinGecko API wrapper with retry logic and caching
- `utils/venice_client.py` - Venice AI API wrapper for market analysis
- `utils/data_processing.py` - Data cleaning, feature engineering, technical indicators
- `utils/ml_models.py` - LSTM model implementation and training
- `utils/visualizations.py` - Reusable Plotly chart components
- `utils/cache_manager.py` - Smart caching strategy implementation

### Configuration
- `config/settings.py` - Centralized configuration management
- `.env` - Environment variables (API keys, secrets)
- `requirements.txt` - Python dependencies with pinned versions

### Deployment
- `Dockerfile` - Multi-stage Docker build for production
- `docker-compose.yml` - Local development and Redis setup
- `deploy.yaml` - Akash SDL configuration for deployment
- `.dockerignore` - Files to exclude from Docker build

### Testing
- `tests/test_api_client.py` - Unit tests for CoinGecko API client
- `tests/test_ml_models.py` - Unit tests for LSTM models
- `tests/test_data_processing.py` - Unit tests for data processing functions
- `tests/test_venice_client.py` - Unit tests for Venice AI client

### Documentation
- `README.md` - Comprehensive project documentation
- `ARCHITECTURE.md` - System architecture and design decisions
- `DEPLOYMENT.md` - Deployment guide for Akash Network

### Notes
- All API clients must implement retry logic with exponential backoff
- Cache TTLs: Price data (2min), Historical (1hr), AI insights (15min), News (30min)
- LSTM models should be saved to disk and reused for 24 hours
- All user-facing errors must be friendly and actionable
- Docker image should be optimized for size (<1GB)

## Instructions for Completing Tasks

**IMPORTANT:** As you complete each task, you must check it off in this markdown file by changing `- [ ]` to `- [x]`. This helps track progress and ensures you don't skip any steps.

Example:
- `- [ ] 1.1 Read file` → `- [x] 1.1 Read file` (after completing)

Update the file after completing each sub-task, not just after completing an entire parent task.

## Tasks

- [x] 0.0 Create feature branch
  - [x] 0.1 Create and checkout a new branch for this feature (e.g., `git checkout -b feature/crypto-dashboard-production`)

- [x] 1.0 Project Setup & Configuration
  - [x] 1.1 Create project directory structure (pages/, utils/, config/, tests/)
  - [x] 1.2 Update requirements.txt with all dependencies and pinned versions
  - [x] 1.3 Create .env.example file with required environment variables
  - [x] 1.4 Create config/settings.py with configuration management class
  - [x] 1.5 Create .gitignore file (exclude venv/, .env, __pycache__, *.pyc, models/)
  - [x] 1.6 Initialize Git repository and make initial commit

- [x] 2.0 Docker & Infrastructure Setup
  - [x] 2.1 Create Dockerfile with multi-stage build (builder + runtime)
  - [x] 2.2 Create docker-compose.yml with app and Redis services
  - [x] 2.3 Create .dockerignore file to optimize build context
  - [x] 2.4 Add health check endpoint to Streamlit app
  - [ ] 2.5 Test Docker build locally (`docker-compose up`)
  - [ ] 2.6 Verify Redis connection and caching works in container

- [x] 3.0 API Client Implementation (CoinGecko)
  - [x] 3.1 Create utils/api_client.py with CoinGeckoClient class
  - [x] 3.2 Implement get_current_prices(coin_ids: list) method with error handling
  - [x] 3.3 Implement get_historical_data(coin_id: str, days: int) method
  - [x] 3.4 Implement get_trending_coins() method
  - [x] 3.5 Implement get_coin_details(coin_id: str) method for metadata
  - [x] 3.6 Add retry logic with exponential backoff (3 attempts, 2^n seconds)
  - [x] 3.7 Add rate limiting (50 calls/min for CoinGecko free tier)
  - [ ] 3.8 Implement response caching with configurable TTL (will be done in cache_manager)
  - [x] 3.9 Add comprehensive error handling and custom exceptions
  - [ ] 3.10 Write unit tests in tests/test_api_client.py

- [ ] 4.0 Cache Manager Implementation
  - [ ] 4.1 Create utils/cache_manager.py with CacheManager class
  - [ ] 4.2 Implement Redis connection with fallback to in-memory cache
  - [ ] 4.3 Create cache decorators for different TTL strategies
  - [ ] 4.4 Implement cache invalidation methods
  - [ ] 4.5 Add cache statistics tracking (hit rate, miss rate)
  - [ ] 4.6 Create manual cache refresh functionality

- [ ] 5.0 Data Processing Utilities
  - [ ] 5.1 Create utils/data_processing.py with data cleaning functions
  - [ ] 5.2 Implement calculate_moving_averages(df, periods=[7,30,90]) function
  - [ ] 5.3 Implement calculate_rsi(df, period=14) function
  - [ ] 5.4 Implement calculate_macd(df) function
  - [ ] 5.5 Implement calculate_bollinger_bands(df, period=20) function
  - [ ] 5.6 Create normalize_prices(df) function for comparison charts
  - [ ] 5.7 Implement data validation and sanitization functions
  - [ ] 5.8 Write unit tests in tests/test_data_processing.py

- [ ] 6.0 Visualization Components
  - [ ] 6.1 Create utils/visualizations.py with reusable chart functions
  - [ ] 6.2 Implement create_price_chart(df, title) with Plotly
  - [ ] 6.3 Implement create_comparison_chart(dfs, coin_names) for multi-coin comparison
  - [ ] 6.4 Implement create_portfolio_pie_chart(holdings) for allocation
  - [ ] 6.5 Implement create_sentiment_gauge(score) for sentiment visualization
  - [ ] 6.6 Implement create_prediction_chart(historical, predicted) with confidence intervals
  - [ ] 6.7 Implement create_technical_indicators_chart(df) with RSI, MACD overlays
  - [ ] 6.8 Add consistent styling and dark theme to all charts

- [ ] 7.0 Feature 1: Real-Time Price Tracker (Market Overview Page)
  - [ ] 7.1 Create pages/1_📊_Market_Overview.py
  - [ ] 7.2 Implement page header with title and last updated timestamp
  - [ ] 7.3 Fetch top 10 cryptocurrencies data using CoinGeckoClient
  - [ ] 7.4 Create metric cards displaying: name, price, 24h change, market cap, volume
  - [ ] 7.5 Add color-coded change indicators (green/red)
  - [ ] 7.6 Implement 7-day sparkline charts for each coin
  - [ ] 7.7 Add manual refresh button with loading state
  - [ ] 7.8 Implement auto-refresh every 60 seconds using st.rerun()
  - [ ] 7.9 Add error handling with fallback to cached data
  - [ ] 7.10 Test page loads in <3 seconds

- [ ] 8.0 Feature 2: Portfolio Simulator
  - [ ] 8.1 Create pages/2_💼_Portfolio.py
  - [ ] 8.2 Create sidebar inputs for coin holdings (number inputs for each coin)
  - [ ] 8.3 Add input for purchase price per coin (optional, for gain/loss calculation)
  - [ ] 8.4 Implement "Calculate Portfolio" button
  - [ ] 8.5 Calculate total portfolio value in real-time
  - [ ] 8.6 Create portfolio allocation pie chart
  - [ ] 8.7 Display portfolio breakdown table (coin, amount, value, allocation %)
  - [ ] 8.8 Calculate and display gain/loss if purchase prices provided
  - [ ] 8.9 Implement historical portfolio value chart (7d, 30d, 90d views)
  - [ ] 8.10 Add "Save Portfolio" to session state
  - [ ] 8.11 Add "Export to CSV" functionality
  - [ ] 8.12 Handle edge case: empty portfolio with helpful message

- [ ] 9.0 Feature 3: Price Comparison Tool
  - [ ] 9.1 Add price comparison section to Market Overview page
  - [ ] 9.2 Create multi-select dropdown for coin selection (2-5 coins)
  - [ ] 9.3 Fetch historical data for selected coins (30 days)
  - [ ] 9.4 Implement normalized price chart (starting at 100)
  - [ ] 9.5 Add toggle between absolute prices and normalized view
  - [ ] 9.6 Create comparison metrics table (price, 24h, 7d, market cap, volume)
  - [ ] 9.7 Add "Export Comparison" CSV download button
  - [ ] 9.8 Implement interactive tooltips with exact values

- [ ] 10.0 LSTM Model Implementation
  - [ ] 10.1 Create utils/ml_models.py with LSTMPredictor class
  - [ ] 10.2 Implement data preprocessing for LSTM (scaling, windowing)
  - [ ] 10.3 Build LSTM architecture (2 LSTM layers + Dense output)
  - [ ] 10.4 Implement train_model(historical_data, epochs=50) method
  - [ ] 10.5 Implement predict_future(days=7) method with confidence intervals
  - [ ] 10.6 Calculate accuracy metrics (RMSE, MAE, MAPE)
  - [ ] 10.7 Implement model saving/loading to disk (models/ directory)
  - [ ] 10.8 Add model versioning and metadata tracking
  - [ ] 10.9 Implement automatic retraining logic (daily)
  - [ ] 10.10 Write unit tests in tests/test_ml_models.py

- [ ] 11.0 Feature 4: LSTM Price Predictions Page
  - [ ] 11.1 Create pages/3_📈_Predictions.py
  - [ ] 11.2 Add coin selection dropdown
  - [ ] 11.3 Add "Generate Forecast" button with loading spinner
  - [ ] 11.4 Fetch 90 days of historical data for training
  - [ ] 11.5 Train or load cached LSTM model
  - [ ] 11.6 Generate 7-day price predictions
  - [ ] 11.7 Create prediction chart with historical + predicted prices
  - [ ] 11.8 Display confidence intervals as shaded area
  - [ ] 11.9 Show model accuracy metrics (RMSE, MAE, MAPE)
  - [ ] 11.10 Display model training status and last update time
  - [ ] 11.11 Add educational disclaimer about prediction limitations
  - [ ] 11.12 Implement error handling for model training failures

- [ ] 12.0 Venice AI Client Implementation
  - [ ] 12.1 Create utils/venice_client.py with VeniceAIClient class
  - [ ] 12.2 Implement generate_market_summary(crypto_data) method
  - [ ] 12.3 Implement generate_trading_signals(coin_data) method (BUY/HOLD/SELL)
  - [ ] 12.4 Implement assess_risk(coin_data, market_data) method (LOW/MED/HIGH)
  - [ ] 12.5 Implement analyze_trends(historical_data) method
  - [ ] 12.6 Implement analyze_correlations(multi_coin_data) method
  - [ ] 12.7 Add retry logic and error handling
  - [ ] 12.8 Implement response caching (15-minute TTL)
  - [ ] 12.9 Add API usage tracking and cost estimation
  - [ ] 12.10 Write unit tests in tests/test_venice_client.py

- [ ] 13.0 Feature 5: AI-Powered Market Insights Page
  - [ ] 13.1 Create pages/4_🤖_AI_Insights.py
  - [ ] 13.2 Add "Generate Insights" button with loading state
  - [ ] 13.3 Fetch current market data for all tracked coins
  - [ ] 13.4 Call Venice AI to generate comprehensive market summary
  - [ ] 13.5 Display overall market sentiment with icon (📈/📉/➡️)
  - [ ] 13.6 Show trading signals for each coin with confidence scores
  - [ ] 13.7 Display risk assessment with color-coded badges
  - [ ] 13.8 Show identified trends and key support/resistance levels
  - [ ] 13.9 Display correlation analysis between coins
  - [ ] 13.10 Add "Regenerate Insights" button to bypass cache
  - [ ] 13.11 Show timestamp and data sources used
  - [ ] 13.12 Implement error handling with fallback message

- [ ] 14.0 News Sentiment Analysis Implementation
  - [ ] 14.1 Add news fetching to utils/api_client.py (CryptoPanic API)
  - [ ] 14.2 Implement get_crypto_news(coin, limit=10) method
  - [ ] 14.3 Add Venice AI sentiment analysis for headlines
  - [ ] 14.4 Implement batch sentiment analysis for efficiency
  - [ ] 14.5 Calculate aggregate sentiment score (0-100)
  - [ ] 14.6 Cache news data for 30 minutes

- [ ] 15.0 Feature 6: News Sentiment Page
  - [ ] 15.1 Create pages/5_📰_News_Sentiment.py
  - [ ] 15.2 Add coin selection dropdown
  - [ ] 15.3 Fetch top 10 news headlines for selected coin
  - [ ] 15.4 Analyze sentiment for each headline using Venice AI
  - [ ] 15.5 Display overall sentiment gauge (0-100 with color gradient)
  - [ ] 15.6 Show list of headlines with sentiment badges (🟢/🟡/🔴)
  - [ ] 15.7 Add links to original articles (open in new tab)
  - [ ] 15.8 Create sentiment distribution bar chart
  - [ ] 15.9 Add auto-refresh every 30 minutes
  - [ ] 15.10 Handle API errors gracefully

- [ ] 16.0 Main App Navigation & Layout
  - [ ] 16.1 Update app.py with proper page configuration
  - [ ] 16.2 Add custom CSS for dark theme and styling
  - [ ] 16.3 Create sidebar navigation with page links
  - [ ] 16.4 Add app header with title and tagline
  - [ ] 16.5 Add footer with attribution and links
  - [ ] 16.6 Implement responsive layout for mobile/tablet/desktop
  - [ ] 16.7 Add loading states and skeleton loaders
  - [ ] 16.8 Implement global error boundary

- [ ] 17.0 Error Handling & User Experience
  - [ ] 17.1 Create custom exception classes in utils/exceptions.py
  - [ ] 17.2 Implement user-friendly error messages for all API failures
  - [ ] 17.3 Add fallback to cached data when APIs are unavailable
  - [ ] 17.4 Create error logging system (console + file)
  - [ ] 17.5 Add "Report Issue" link in error messages
  - [ ] 17.6 Implement graceful degradation for missing features
  - [ ] 17.7 Add input validation for all user inputs
  - [ ] 17.8 Test all edge cases (empty data, invalid inputs, API timeouts)

- [ ] 18.0 Performance Optimization
  - [ ] 18.1 Profile app performance and identify bottlenecks
  - [ ] 18.2 Optimize data fetching with parallel requests where possible
  - [ ] 18.3 Implement lazy loading for heavy components
  - [ ] 18.4 Optimize LSTM model size and inference time
  - [ ] 18.5 Minimize Streamlit reruns with proper caching
  - [ ] 18.6 Optimize Docker image size (multi-stage build, Alpine base)
  - [ ] 18.7 Verify load time is <3 seconds

- [ ] 19.0 Testing & Quality Assurance
  - [ ] 19.1 Write unit tests for all API client methods
  - [ ] 19.2 Write unit tests for data processing functions
  - [ ] 19.3 Write unit tests for LSTM model training/prediction
  - [ ] 19.4 Write unit tests for Venice AI client
  - [ ] 19.5 Run all tests and achieve 80%+ coverage
  - [ ] 19.6 Perform manual testing of all features
  - [ ] 19.7 Test error scenarios (API failures, invalid inputs)
  - [ ] 19.8 Test on different screen sizes (mobile, tablet, desktop)

- [ ] 20.0 Akash Network Deployment Preparation
  - [ ] 20.1 Create deploy.yaml with Akash SDL configuration
  - [ ] 20.2 Configure resource requirements (CPU, memory, storage)
  - [ ] 20.3 Set up persistent storage for LSTM models
  - [ ] 20.4 Configure environment variables in SDL
  - [ ] 20.5 Add health check endpoints for Akash monitoring
  - [ ] 20.6 Create deployment script (deploy.sh)
  - [ ] 20.7 Test deployment locally with Akash CLI

- [ ] 21.0 Documentation
  - [ ] 21.1 Update README.md with comprehensive project overview
  - [ ] 21.2 Add installation instructions (local + Docker)
  - [ ] 21.3 Document all environment variables in README
  - [ ] 21.4 Create ARCHITECTURE.md with system design diagrams
  - [ ] 21.5 Create DEPLOYMENT.md with Akash deployment guide
  - [ ] 21.6 Add docstrings to all functions and classes
  - [ ] 21.7 Create API documentation for utility functions
  - [ ] 21.8 Add inline comments for complex logic

- [ ] 22.0 Final Polish & Deployment
  - [ ] 22.1 Review all code for consistency and best practices
  - [ ] 22.2 Run linter (flake8/pylint) and fix issues
  - [ ] 22.3 Format code with black
  - [ ] 22.4 Create demo screenshots for README
  - [ ] 22.5 Record demo GIF showing key features
  - [ ] 22.6 Deploy to Akash Network
  - [ ] 22.7 Verify production deployment works correctly
  - [ ] 22.8 Test all features on production URL
  - [ ] 22.9 Monitor performance and error logs
  - [ ] 22.10 Create LinkedIn/portfolio post with demo link

---

## Progress Tracking

**Total Tasks:** 22 parent tasks, ~180 sub-tasks
**Estimated Time:** 16-20 hours
**Current Status:** Ready to begin implementation

## Next Steps

1. Start with Task 0.0 (Create feature branch)
2. Work through tasks sequentially, checking off each sub-task
3. Test thoroughly after each major feature
4. Deploy to Akash Network after all features are complete
5. Share on LinkedIn and add to portfolio
