# Testing Guide

## Prerequisites

Before testing, ensure you have:
- Python 3.10+ installed
- Docker and Docker Compose installed (for containerized testing)
- Virtual environment activated

## Local Testing (Without Docker)

### 1. Install Dependencies

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and set VENICE_API_KEY (optional for basic features)
# Note: Market Overview and Portfolio work without Venice AI
```

### 3. Run Application

```bash
streamlit run app.py
```

Expected output:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

### 4. Test Features

1. **Market Overview Page**:
   - Navigate to http://localhost:8501
   - Verify top 10 cryptocurrencies display with prices
   - Click "Refresh Data" button
   - Select 2-3 coins for comparison
   - Verify comparison chart renders
   - Export comparison data to CSV

2. **Portfolio Page**:
   - Click "💼 Portfolio" in sidebar
   - Enter holdings for multiple cryptocurrencies
   - Click "Save Portfolio"
   - Verify total value calculation
   - Check pie chart renders correctly
   - Export portfolio to CSV

## Docker Testing

### 1. Build Docker Image

```bash
docker build -t crypto-dashboard:test .
```

Expected: Build completes successfully with image size < 1GB

### 2. Run with Docker Compose

```bash
# Start services
docker-compose up --build

# In another terminal, check logs
docker-compose logs -f app

# Check Redis connection
docker-compose logs redis
```

### 3. Verify Services

```bash
# Check running containers
docker ps

# Expected output:
# - crypto-dashboard-app (port 8501)
# - crypto-dashboard-redis (port 6379)

# Test health check
curl http://localhost:8501/_stcore/health
```

### 4. Test Caching

1. Open http://localhost:8501
2. Load Market Overview page (first load - cache miss)
3. Refresh page (should be faster - cache hit)
4. Check cache stats in header

### 5. Stop Services

```bash
docker-compose down
```

## Unit Testing (Coming Soon)

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=utils --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Performance Testing

### Load Time Test

```bash
# Measure initial load time
time curl -s http://localhost:8501 > /dev/null

# Target: < 3 seconds
```

### Memory Usage

```bash
# Check Docker container memory
docker stats crypto-dashboard-app

# Target: < 512MB
```

## Common Issues

### Issue: ModuleNotFoundError

**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: Redis Connection Failed

**Solution**: 
- If running locally without Docker: App will use in-memory cache (fallback)
- If using Docker: Ensure Redis container is running
```bash
docker-compose up redis
```

### Issue: CoinGecko API Rate Limit

**Solution**: Wait 60 seconds or use cached data. Rate limit: 50 calls/min

### Issue: Port 8501 Already in Use

**Solution**: Stop other Streamlit instances or change port
```bash
streamlit run app.py --server.port 8502
```

## Test Checklist

Before committing:
- [ ] All dependencies install without errors
- [ ] App runs locally without crashes
- [ ] Market Overview page loads and displays data
- [ ] Portfolio page calculates correctly
- [ ] Price comparison charts render
- [ ] CSV export works
- [ ] Docker build completes successfully
- [ ] Docker Compose starts all services
- [ ] Redis caching works (check cache stats)
- [ ] No errors in console/logs
- [ ] Load time < 3 seconds (with cache)

## Next Steps

After basic testing passes:
1. Implement LSTM predictions
2. Add Venice AI integration
3. Create comprehensive unit tests
4. Deploy to Akash Network
5. Performance optimization
