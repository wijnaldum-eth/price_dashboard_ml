# Product Requirements Document: Crypto Market Intelligence Dashboard

## Introduction/Overview

A production-ready, real-time cryptocurrency market intelligence dashboard that serves as both a personal investment tracking tool and a public-facing community resource. The platform combines live market data, advanced LSTM-based price predictions, and Venice AI-powered trading signals to provide comprehensive market analysis. Built with Streamlit, deployed via Docker Compose on Akash Network for decentralized hosting.

**Problem Statement:** Crypto investors lack a unified platform that combines real-time data, AI-powered insights, and advanced ML predictions in an accessible, educational format.

**Solution:** A professional-grade dashboard that democratizes access to institutional-level market intelligence while serving as a portfolio showcase and learning tool.

## Goals

1. **Technical Excellence:** Build a production-ready application with proper architecture, error handling, and performance optimization
2. **Educational Value:** Demonstrate proficiency in Python, ML (LSTM), AI integration (Venice AI), and modern deployment (Docker + Akash)
3. **Community Impact:** Provide free, accessible crypto market intelligence to help users make informed decisions
4. **Personal Investment Tool:** Track and analyze personal crypto portfolio with real-time updates
5. **Deployment Success:** Successfully deploy to Akash Network with 99%+ uptime and <3s load times

## User Stories

### Primary Users: Crypto Investors (Beginner to Intermediate)
- **As a crypto investor**, I want to see real-time prices for top cryptocurrencies so I can monitor market movements
- **As a portfolio holder**, I want to simulate different investment scenarios to understand potential returns
- **As a trader**, I want AI-powered trading signals and risk assessments to inform my decisions
- **As a learner**, I want to understand how ML predictions work through transparent, educational visualizations

### Secondary Users: Recruiters/Technical Evaluators
- **As a recruiter**, I want to see clean, professional code architecture to evaluate technical skills
- **As a technical evaluator**, I want to see proper error handling, testing, and deployment practices

### Tertiary User: Developer (You)
- **As the developer**, I want to learn LSTM implementation, Venice AI integration, and Akash deployment
- **As the maintainer**, I want modular, well-documented code for easy updates and feature additions

## Functional Requirements

### Core Features (Must Have)

#### 1. Real-Time Price Tracker
- **FR-1.1:** Display current prices for top 10 cryptocurrencies (BTC, ETH, SOL, ADA, DOT, AVAX, MATIC, LINK, UNI, ATOM)
- **FR-1.2:** Show 24h price change with color-coded indicators (green: positive, red: negative)
- **FR-1.3:** Display market cap, 24h volume, and circulating supply
- **FR-1.4:** Include 7-day sparkline charts for quick trend visualization
- **FR-1.5:** Auto-refresh every 60 seconds with manual refresh option
- **FR-1.6:** Smart caching: 2-minute cache for price data, manual override available

#### 2. Portfolio Simulator
- **FR-2.1:** Allow users to input holdings for any tracked cryptocurrency
- **FR-2.2:** Calculate real-time portfolio value in USD
- **FR-2.3:** Show portfolio allocation via interactive pie chart
- **FR-2.4:** Display gain/loss calculations based on user-defined purchase prices
- **FR-2.5:** Save portfolio to session state (persist during session)
- **FR-2.6:** Export portfolio data as CSV
- **FR-2.7:** Show historical portfolio value over time (7d, 30d, 90d)

#### 3. Price Comparison Tool
- **FR-3.1:** Multi-select dropdown to compare 2-5 cryptocurrencies
- **FR-3.2:** Normalized price chart (starting at 100) to compare percentage changes
- **FR-3.3:** Side-by-side metrics table (price, 24h change, 7d change, market cap, volume)
- **FR-3.4:** Export comparison data as CSV
- **FR-3.5:** Toggle between absolute prices and normalized view

#### 4. LSTM Price Prediction
- **FR-4.1:** Train LSTM model on 90 days of historical price data
- **FR-4.2:** Generate 7-day price forecasts with confidence intervals
- **FR-4.3:** Display prediction accuracy metrics (RMSE, MAE, MAPE)
- **FR-4.4:** Visualize predictions with historical data overlay
- **FR-4.5:** Show model training status and last update timestamp
- **FR-4.6:** Include educational disclaimer about prediction limitations
- **FR-4.7:** Cache trained models for 24 hours, retrain daily
- **FR-4.8:** Support predictions for all tracked cryptocurrencies

#### 5. Venice AI Market Analysis
- **FR-5.1:** Generate comprehensive market summaries using Venice AI API
- **FR-5.2:** Provide trading signals (BUY/HOLD/SELL) with confidence scores
- **FR-5.3:** Conduct risk assessment (LOW/MEDIUM/HIGH) for each cryptocurrency
- **FR-5.4:** Identify market trends and key support/resistance levels
- **FR-5.5:** Analyze correlation between different cryptocurrencies
- **FR-5.6:** Generate personalized insights based on portfolio holdings
- **FR-5.7:** Cache AI insights for 15 minutes to manage API costs
- **FR-5.8:** Display AI reasoning and data sources for transparency

#### 6. News Sentiment Analysis
- **FR-6.1:** Aggregate crypto news from multiple sources (CryptoPanic, CoinDesk)
- **FR-6.2:** Use Venice AI to analyze sentiment (positive/negative/neutral)
- **FR-6.3:** Calculate overall sentiment score (0-100) per cryptocurrency
- **FR-6.4:** Display top 10 headlines with sentiment badges
- **FR-6.5:** Show sentiment distribution chart
- **FR-6.6:** Link to original articles for full context
- **FR-6.7:** Auto-refresh news every 30 minutes

#### 7. Technical Indicators Dashboard
- **FR-7.1:** Calculate and display RSI (Relative Strength Index)
- **FR-7.2:** Calculate and display MACD (Moving Average Convergence Divergence)
- **FR-7.3:** Show 7-day, 30-day, and 90-day moving averages
- **FR-7.4:** Display Bollinger Bands on price charts
- **FR-7.5:** Provide interpretation of indicators (overbought/oversold signals)

### Infrastructure & Performance

#### 8. API Management
- **FR-8.1:** Implement retry logic with exponential backoff (3 attempts)
- **FR-8.2:** Handle rate limits gracefully with queue system
- **FR-8.3:** Provide fallback to cached data when APIs are unavailable
- **FR-8.4:** Log all API calls with timestamps and response times
- **FR-8.5:** Display API status indicators (operational/degraded/offline)

#### 9. Caching Strategy
- **FR-9.1:** Price data: 2-minute cache with manual refresh
- **FR-9.2:** Historical data: 1-hour cache
- **FR-9.3:** AI insights: 15-minute cache
- **FR-9.4:** News data: 30-minute cache
- **FR-9.5:** LSTM models: 24-hour cache with daily retraining
- **FR-9.6:** Display "Last Updated" timestamps for all cached data

#### 10. Docker & Deployment
- **FR-10.1:** Create multi-stage Dockerfile for optimized image size
- **FR-10.2:** Docker Compose setup with separate services (app, redis for caching)
- **FR-10.3:** Environment variable configuration for API keys
- **FR-10.4:** Health check endpoints for monitoring
- **FR-10.5:** Akash SDL configuration for deployment
- **FR-10.6:** Automated deployment script
- **FR-10.7:** Load time under 3 seconds on initial load

#### 11. UI/UX
- **FR-11.1:** Dark theme optimized for extended viewing
- **FR-11.2:** Mobile-responsive layout (works on phones, tablets, desktop)
- **FR-11.3:** Sidebar navigation with clear sections
- **FR-11.4:** Loading states with progress indicators
- **FR-11.5:** Error messages that are user-friendly and actionable
- **FR-11.6:** Consistent color scheme and typography
- **FR-11.7:** Accessibility: proper contrast ratios, keyboard navigation

#### 12. Error Handling & Logging
- **FR-12.1:** Graceful degradation when APIs fail
- **FR-12.2:** User-friendly error messages (no technical jargon)
- **FR-12.3:** Comprehensive logging to console and file
- **FR-12.4:** Error tracking with context (what user was doing)
- **FR-12.5:** Automatic error recovery where possible

## Non-Goals (Out of Scope)

1. **User Authentication:** No login system (public dashboard, session-based portfolio only)
2. **Database Persistence:** No permanent storage of user data (session state only)
3. **Real Trading Integration:** No connection to exchanges or actual trading
4. **Payment Processing:** No monetization or subscription features
5. **Mobile App:** Web-only, no native mobile applications
6. **Social Features:** No comments, sharing, or community features
7. **Historical Data Beyond 90 Days:** Limited to recent data for LSTM training
8. **Support for All Cryptocurrencies:** Limited to top 10-20 coins
9. **Real-Time WebSocket Feeds:** Polling-based updates only
10. **Advanced Portfolio Features:** No tax reporting, DCA calculators, or rebalancing tools

## Design Considerations

### UI/UX Design
- **Color Scheme:** Dark theme (#0e1117 background, #1E293B cards, #4F46E5 primary accent)
- **Typography:** Inter or Roboto for clean, professional look
- **Layout:** Sidebar navigation + main content area with responsive grid
- **Charts:** Plotly for interactive, professional visualizations
- **Icons:** Use emojis for quick visual recognition (🚀, 📊, 🤖, 📰)

### Component Structure
```
app.py (main Streamlit app)
├── pages/
│   ├── 1_📊_Market_Overview.py
│   ├── 2_💼_Portfolio.py
│   ├── 3_📈_Predictions.py
│   ├── 4_🤖_AI_Insights.py
│   └── 5_📰_News_Sentiment.py
├── utils/
│   ├── api_client.py (CoinGecko wrapper)
│   ├── venice_client.py (Venice AI wrapper)
│   ├── data_processing.py (data cleaning, feature engineering)
│   ├── ml_models.py (LSTM implementation)
│   ├── visualizations.py (Plotly chart functions)
│   └── cache_manager.py (smart caching logic)
├── config/
│   └── settings.py (configuration management)
└── tests/
    ├── test_api_client.py
    ├── test_ml_models.py
    └── test_data_processing.py
```

## Technical Considerations

### Technology Stack
- **Frontend:** Streamlit 1.32.0
- **Data Processing:** Pandas 2.1.4, NumPy 1.26.0
- **Visualization:** Plotly 5.18.0
- **ML Framework:** TensorFlow 2.15.0 (for LSTM), scikit-learn 1.3.2
- **API Clients:** requests 2.31.0, aiohttp 3.9.0 (async requests)
- **Caching:** Redis 5.0.1 (via Docker Compose)
- **Environment:** python-dotenv 1.0.0
- **Deployment:** Docker, Docker Compose, Akash Network

### API Dependencies
- **CoinGecko API:** Free tier, no authentication (rate limit: 50 calls/min)
- **Venice AI API:** Requires API key (store in .env)
- **CryptoPanic API:** Free tier for news aggregation

### Performance Targets
- **Initial Load Time:** < 3 seconds
- **API Response Time:** < 500ms (with caching)
- **LSTM Prediction Time:** < 5 seconds per coin
- **Venice AI Response Time:** < 3 seconds (cached: instant)
- **Memory Usage:** < 512MB RAM
- **Docker Image Size:** < 1GB

### Security Considerations
- **API Keys:** Store in environment variables, never commit to Git
- **Input Validation:** Sanitize all user inputs (portfolio values, coin selections)
- **Rate Limiting:** Implement client-side rate limiting to respect API quotas
- **Error Exposure:** Never expose internal errors or API keys in UI
- **HTTPS Only:** Enforce secure connections in production

### Deployment Architecture
```
Akash Network
├── Docker Container (Streamlit App)
├── Redis Container (Caching)
└── Persistent Volume (Model storage)
```

## Success Metrics

### Technical Metrics
1. **Performance:** 95% of page loads under 3 seconds
2. **Uptime:** 99%+ availability on Akash Network
3. **Error Rate:** < 1% of API calls fail
4. **Prediction Accuracy:** LSTM MAPE < 15% for 7-day forecasts
5. **Code Quality:** 80%+ test coverage, no critical security issues

### User Engagement (if tracking)
1. **Session Duration:** Average 5+ minutes per session
2. **Feature Usage:** 70%+ of users interact with AI insights
3. **Return Rate:** 30%+ of users return within 7 days

### Portfolio/Career Metrics
1. **GitHub Stars:** Target 50+ stars within first month
2. **LinkedIn Engagement:** 100+ views on project post
3. **Interview Mentions:** Feature in technical interviews
4. **Learning Outcomes:** Proficiency in LSTM, Venice AI, Akash deployment

## Open Questions

1. **Venice AI API Costs:** What's the monthly budget for API calls? Need to optimize caching strategy accordingly.
2. **Akash Pricing:** What's the expected monthly cost for hosting? Need to size resources appropriately.
3. **Model Retraining:** Should LSTM models retrain automatically or require manual trigger?
4. **Data Retention:** How long should we cache historical data in Redis?
5. **Monitoring:** Do we need external monitoring (UptimeRobot, Sentry) or is basic logging sufficient?
6. **Backup Strategy:** Should we implement automated backups for trained models?

## Implementation Timeline (This Weekend)

### Saturday (8 hours)
- **Hours 1-2:** Project setup, Docker configuration, API client implementation
- **Hours 3-4:** Real-time price tracker + portfolio simulator
- **Hours 5-6:** Price comparison tool + technical indicators
- **Hours 7-8:** LSTM model implementation and training

### Sunday (8 hours)
- **Hours 1-2:** Venice AI integration (market analysis + trading signals)
- **Hours 3-4:** News sentiment analysis
- **Hours 5-6:** UI polish, error handling, testing
- **Hours 7-8:** Docker Compose setup, Akash deployment, documentation

### Total: 16 hours (aggressive but achievable with AI assistance)

## Acceptance Criteria

The feature is considered complete when:
1. ✅ All 12 functional requirement categories are implemented
2. ✅ Dashboard loads in < 3 seconds on Akash Network
3. ✅ LSTM predictions generate successfully for all tracked coins
4. ✅ Venice AI insights display with trading signals and risk assessment
5. ✅ All API errors are handled gracefully with user-friendly messages
6. ✅ Docker Compose runs locally without errors
7. ✅ Akash SDL deploys successfully with public URL
8. ✅ README includes setup instructions, architecture diagram, and demo GIF
9. ✅ Code is well-documented with docstrings and comments
10. ✅ At least 3 unit tests per major component

## Next Steps

1. Generate detailed task list using `generate-tasks.md`
2. Begin implementation starting with Docker setup and API clients
3. Iterate feature-by-feature with testing at each step
4. Deploy to Akash Network and verify production readiness
5. Create demo video and portfolio documentation
