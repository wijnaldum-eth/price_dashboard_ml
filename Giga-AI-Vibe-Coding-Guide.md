# THE COMPLETE GIGA AI VIBE-CODING GUIDE
## From Zero to Deployed Crypto Dashboard in One Weekend

**Target:** Crypto Market Intelligence Dashboard  
**Time:** 16-20 hours  
**Tool:** Giga AI IDE (Agent Mode)  
**Outcome:** Live Streamlit app + Portfolio-ready GitHub repo

---

## PART 1: SETUP (30 minutes)

### Step 1: Install Giga AI IDE

1. **Download the extension:**
   - Open VS Code (or Cursor/Windsurf)
   - Go to Extensions (Cmd/Ctrl + Shift + X)
   - Search for "Giga AI Context Manager"
   - Click Install

2. **Open Project Manager:**
   - Press `Cmd/Ctrl + Shift + P`
   - Type "Giga: Open Project Manager"
   - Create new project folder: `crypto-dashboard`

3. **Let Giga Analyze (The Magic Part):**
   ```
   Cmd/Ctrl + Shift + P → "Giga: Generate Rules"
   ```
   - Giga will scan your (empty) project and create context files
   - This takes 30-60 seconds

### Step 2: Set Up Your Environment

Create a new terminal in VS Code and run:

```bash
# Create project folder
mkdir crypto-dashboard
cd crypto-dashboard

# Create virtual environment
python -m venv venv

# Activate it
# On Mac/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Create basic file structure
touch app.py
touch requirements.txt
touch README.md
touch .env
```

### Step 3: Configure Venice AI API Key

In your `.env` file:
```
VENICE_API_KEY=your_api_key_here
```

---

## PART 2: THE VIBE-CODING WORKFLOW

### The Golden Rule of Agent Mode

**NEVER** just say "build me a crypto dashboard." That's amateur hour.

**ALWAYS** follow this structure:

1. **PLAN** → Let AI create the blueprint
2. **REVIEW** → You approve/edit the plan
3. **IMPLEMENT** → AI codes feature-by-feature
4. **TEST** → You verify it works
5. **ITERATE** → Fix bugs, add features

---

## PHASE 1: INITIAL PROMPT (Saturday 9am - 11am)

### The Master Prompt Template

Open Giga AI chat and paste this EXACT prompt:

```
ROLE: You are an expert Python data science developer specializing in Streamlit dashboards and financial data visualization.

CONTEXT: I'm building a portfolio project - a real-time cryptocurrency market intelligence dashboard. This will be deployed publicly and needs to look professional.

TECH STACK:
- Python 3.10+
- Streamlit for UI
- Plotly for interactive charts
- Pandas for data manipulation
- requests for API calls
- CoinGecko API (free, no auth)
- Venice AI API for AI-powered insights

PROJECT STRUCTURE:
crypto-dashboard/
├── app.py (main Streamlit app)
├── utils/
│   ├── api_client.py (CoinGecko + Venice API wrappers)
│   ├── data_processing.py (data cleaning, feature engineering)
│   └── visualizations.py (all Plotly chart functions)
├── requirements.txt
├── .env (API keys)
└── README.md

TASK: Before implementing anything, I need you to create a detailed PLAN.md file that outlines:

1. Complete feature breakdown (what we'll build)
2. Technical architecture (how components interact)
3. Data flow diagram (API → Processing → Display)
4. Implementation order (step-by-step build sequence)
5. File structure with function signatures

DO NOT write any code yet. Just create the plan as a markdown file called PLAN.md.

REQUIREMENTS:
- The dashboard must load in under 3 seconds
- All API calls must have error handling and retry logic
- Charts must be interactive (zoom, pan, hover tooltips)
- Mobile-responsive layout
- Dark mode theme
- Clean, professional UI

Start by creating PLAN.md with the detailed implementation plan.
```

### What Happens Next

Giga will:
1. Analyze your prompt
2. Create `PLAN.md` with detailed architecture
3. Show you the file contents
4. Wait for your approval

### Your Job: Review the Plan

Open the generated `PLAN.md` and check:

✅ **Does it include all 6 core features?**
- Live price tracker
- Portfolio simulator
- Price comparison
- Basic ML prediction
- Venice AI market insights
- Sentiment analysis

✅ **Is the tech stack correct?**
✅ **Are the API calls properly structured?**

### Approval Prompt

Once you're happy with the plan:

```
This plan looks great! A few adjustments:

1. In the data_processing.py file, add a function to calculate 7-day and 30-day moving averages for the ML prediction feature.

2. In the api_client.py, make sure the Venice AI calls have caching to avoid hitting rate limits.

3. Add a "Last Updated" timestamp to the dashboard header.

Now, let's start implementation. Begin with Phase 1 from your plan: Set up project structure and API clients.

Remember:
- Implement ONE feature at a time
- Show me the code after each feature
- Include error handling for all API calls
- Add console logs for debugging
```

---

## PHASE 2: IMPLEMENTATION (Saturday 11am - 5pm)

### Feature 1: Project Setup + API Clients (1 hour)

**Prompt:**

```
Implement Phase 1 from PLAN.md:

1. Create requirements.txt with exact versions:
   - streamlit==1.29.0
   - pandas==2.1.0
   - plotly==5.18.0
   - requests==2.31.0
   - python-dotenv==1.0.0

2. Create utils/api_client.py with:
   - CoinGeckoClient class with methods:
     - get_current_prices(coin_ids: list) -> dict
     - get_historical_data(coin_id: str, days: int) -> pd.DataFrame
     - get_trending_coins() -> list
   
   - VeniceAIClient class with methods:
     - generate_market_summary(data: dict) -> str
     - analyze_sentiment(headlines: list) -> dict
   
   - Both clients must have:
     - Retry logic (3 attempts with exponential backoff)
     - Error handling with custom exceptions
     - Response caching (5 minutes for CoinGecko, 1 hour for Venice)
     - Rate limiting

3. Create a simple test in app.py that:
   - Imports both clients
   - Fetches Bitcoin price
   - Prints it to console

After implementation, show me the code and I'll test it locally.
```

### Feature 2: Live Price Tracker (2 hours)

**After Feature 1 works, prompt:**

```
Great! Now implement Feature 2: Live Price Tracker

Requirements:
1. In app.py, create a Streamlit layout with:
   - Page title: "🚀 Crypto Market Intelligence"
   - Subtitle with last updated time
   - 5 metric cards showing: BTC, ETH, SOL, ADA, DOT
   
2. Each metric card displays:
   - Coin name with emoji
   - Current price ($XX,XXX.XX)
   - 24h change percentage (green if positive, red if negative)
   - Small sparkline chart (7-day trend)

3. Add a refresh button that re-fetches data

4. Use @st.cache_data decorator with 60 second TTL

5. Style with custom CSS:
   - Dark background (#0e1117)
   - Metric cards with subtle borders
   - Responsive grid (mobile: 1 column, tablet: 2, desktop: 5)

Show me the complete app.py code when done.
```

### The Iterative Testing Loop

**After each feature implementation:**

1. **Run the code:**
   ```bash
   streamlit run app.py
   ```

2. **Test in browser:**
   - Check if feature works
   - Look for errors in console
   - Test edge cases (no internet, API errors)

3. **If bugs exist, prompt:**
   ```
   I'm getting this error:
   [paste error message]
   
   The issue seems to be in [file name] at line [X].
   
   Fix this bug and ensure proper error handling.
   ```

4. **If it works, move to next feature!**

### Feature 3: Portfolio Simulator (2 hours)

**Prompt:**

```
Implement Feature 3: Portfolio Simulator

Add a new section to app.py:

1. Section header: "💼 Portfolio Simulator"

2. User inputs (in sidebar):
   - Number input for each of 5 coins (BTC, ETH, SOL, ADA, DOT)
   - Default values: BTC=0.1, ETH=2, SOL=10, ADA=100, DOT=50
   - "Calculate Portfolio" button

3. When button clicked, display:
   - Current total value ($XX,XXX.XX)
   - Value breakdown by coin (table)
   - Pie chart showing portfolio allocation
   - Initial investment vs current value comparison

4. Add a feature to save portfolio (use st.session_state)

5. Show portfolio performance:
   - If prices go up/down, show gain/loss in real-time

Use Plotly for the pie chart with custom colors.
```

### Feature 4: Price Comparison Tool (1 hour)

**Prompt:**

```
Implement Feature 4: Price Comparison

1. Add a dropdown to select 2-3 coins to compare

2. Create a line chart showing:
   - 30-day price history for selected coins
   - Normalized to start at 100 (to compare % changes)
   - Different color for each coin
   - Hover tooltips with exact values

3. Below chart, show a table:
   | Metric | Coin 1 | Coin 2 | Coin 3 |
   |--------|--------|--------|--------|
   | Current Price | $X | $Y | $Z |
   | 24h Change | +X% | -Y% | +Z% |
   | 7d Change | +X% | -Y% | +Z% |
   | Market Cap | $Xbn | $Ybn | $Zbn |

4. Add export button to download data as CSV

Use st.multiselect for coin selection (max 3 coins).
```

---

## PHASE 3: ML + AI FEATURES (Saturday 7pm - 10pm, Sunday 9am - 12pm)

### Feature 5: Basic ML Price Prediction (3 hours)

**Prompt:**

```
Implement Feature 5: ML Price Prediction

Create utils/ml_model.py with:

1. Function: train_price_predictor(historical_data: pd.DataFrame) -> LinearRegression
   - Calculate 7-day moving average
   - Use last 30 days as training data
   - Return trained sklearn LinearRegression model

2. Function: predict_future_prices(model, days: int = 7) -> pd.DataFrame
   - Predict next N days
   - Return DataFrame with dates and predicted prices
   - Include confidence intervals (±10%)

3. In app.py, add section:
   - "📈 7-Day Price Forecast"
   - Dropdown to select coin
   - Button to "Generate Forecast"
   - Line chart showing:
     - Historical prices (solid line)
     - Predicted prices (dashed line)
     - Confidence interval (shaded area)
   - Disclaimer: "For educational purposes only"

4. Add model accuracy metrics:
   - Mean Absolute Percentage Error (MAPE)
   - R² score on validation data

Make sure to split data: 80% train, 20% validation.
```

### Feature 6: Venice AI Market Insights (3 hours)

**Prompt:**

```
Implement Feature 6: AI-Powered Market Insights

1. In utils/venice_client.py, create method:
   generate_market_insights(crypto_data: dict, news_headlines: list) -> dict
   
   This should call Venice AI API with prompt:
   "You are a crypto market analyst. Given this data: [data], provide:
   1. Overall market sentiment (bullish/bearish/neutral)
   2. Key trends in the last 24 hours
   3. Top 3 coins to watch
   4. Risk factors to consider
   Keep response under 200 words."

2. In app.py, add section:
   - "🧠 AI Market Analysis"
   - Button: "Generate Insights"
   - Display AI response in a styled box with:
     - Custom background color
     - Icon for sentiment (📈 bullish, 📉 bearish, ➡️ neutral)
     - Timestamp when generated
   
3. Add option to regenerate insights

4. Cache insights for 15 minutes to save API calls

5. Handle Venice API errors gracefully:
   - If API fails, show: "Unable to generate insights. Try again."
   - Log error to console for debugging

Include loading spinner while generating insights.
```

### Feature 7: News Sentiment Analysis (2 hours)

**Prompt:**

```
Implement Feature 7: News Sentiment Analysis

1. Create utils/news_scraper.py:
   - Function: get_crypto_news(coin: str) -> list
   - Scrape top 10 headlines from CryptoPanic API (free tier)
   - Return list of dicts: [{"title": "...", "url": "...", "published": "..."}]

2. Add Venice AI sentiment analysis:
   - For each headline, get sentiment: positive/negative/neutral
   - Aggregate to overall sentiment score (0-100)

3. In app.py, add section:
   - "📰 News Sentiment Analysis"
   - Select coin from dropdown
   - Display:
     - Overall sentiment gauge (0-100 with color gradient)
     - List of headlines with sentiment badges
     - Link to read full article
   
4. Add chart:
   - Bar chart showing sentiment distribution (positive/neutral/negative)

5. Auto-refresh every 30 minutes

Use Plotly gauge chart for sentiment visualization.
```

---

## PHASE 4: POLISH + DEPLOY (Sunday 1pm - 8pm)

### UI Polish (2 hours)

**Prompt:**

```
Let's polish the UI to make it portfolio-ready:

1. Add custom CSS in app.py:
   - Dark theme (#0e1117 background)
   - All metric cards have gradient borders
   - Smooth hover effects on buttons
   - Professional font (Inter or Roboto)
   - Consistent spacing (20px margins)

2. Add navigation:
   - Sidebar with sections:
     - 🏠 Home (overview)
     - 💼 Portfolio
     - 📊 Analysis
     - 🤖 AI Insights
     - 📰 News
   - Use st.sidebar.radio() for navigation

3. Add footer:
   - "Built with Streamlit + Venice AI"
   - GitHub link (we'll add this later)
   - Last updated timestamp

4. Make mobile-responsive:
   - Single column layout on mobile
   - Collapsible sidebar
   - Larger touch targets

5. Add loading states:
   - Skeleton loaders for data fetching
   - Spinners with messages ("Fetching prices...")

Show me the complete updated app.py with all styling.
```

### Error Handling & Edge Cases (1 hour)

**Prompt:**

```
Implement robust error handling:

1. In all API clients:
   - If CoinGecko API fails → show cached data + warning banner
   - If Venice AI fails → display: "AI insights unavailable"
   - If user has no internet → show: "Offline mode - showing cached data"

2. Add try-except blocks around:
   - All API calls
   - All data processing
   - All chart rendering

3. Create custom error messages:
   - User-friendly (no technical jargon)
   - Actionable (tell user what to do)
   - Include "Report Issue" link

4. Add logging:
   - Log all errors to console
   - Log API response times
   - Log user actions (button clicks, selections)

5. Test edge cases:
   - Empty portfolio
   - Invalid coin selections
   - API rate limits exceeded
   - Slow network

Show me the updated code with complete error handling.
```

### README + Documentation (1 hour)

**Prompt:**

```
Create a professional README.md:

Structure:
1. Project title with badges:
   - Python version
   - Streamlit
   - License (MIT)
   - Status (Active)

2. Demo section:
   - Link to live app (we'll deploy next)
   - 3 screenshots showing main features
   - Demo GIF (we'll record later)

3. Features list with checkboxes:
   ✅ Real-time price tracking
   ✅ Portfolio simulator
   ✅ ML price predictions
   ✅ AI-powered insights
   ✅ News sentiment analysis

4. Tech Stack:
   - List all libraries with versions
   - Explain why each was chosen

5. Installation:
   ```bash
   git clone ...
   cd crypto-dashboard
   pip install -r requirements.txt
   streamlit run app.py
   ```

6. Configuration:
   - How to get Venice API key
   - How to set up .env file

7. Project Structure:
   - Tree view of all files
   - Brief description of each

8. Usage:
   - Step-by-step guide with screenshots

9. Future Improvements:
   - [ ] Add more coins
   - [ ] Historical portfolio tracking
   - [ ] Price alerts
   - [ ] Connect to wallet APIs

10. License + Contact

Make it visually appealing with emojis and proper formatting.
```

---

## PHASE 5: DEPLOYMENT (Sunday 6pm - 7pm)

### Deploy to Streamlit Cloud

**Prompt:**

```
Help me prepare for deployment to Streamlit Cloud:

1. Create .streamlit/config.toml:
   - Set theme colors
   - Configure server settings
   - Set max upload size

2. Create .gitignore:
   - Add: venv/, .env, __pycache__/, *.pyc
   - Add: .DS_Store, *.log

3. Update requirements.txt:
   - Pin all versions
   - Remove any dev dependencies
   - Add comments explaining each package

4. Create app_config.py:
   - Move all hardcoded values here
   - API endpoints, timeouts, cache durations
   - Make it easy to configure

5. Add deployment checklist to README:
   - [ ] Push code to GitHub
   - [ ] Go to share.streamlit.io
   - [ ] Connect GitHub repo
   - [ ] Add Venice API key to secrets
   - [ ] Deploy!

Show me all the config files needed.
```

### Manual Deployment Steps

1. **Create GitHub repo:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Crypto Market Intelligence Dashboard"
   git branch -M main
   git remote add origin https://github.com/yourusername/crypto-dashboard.git
   git push -u origin main
   ```

2. **Deploy to Streamlit:**
   - Go to https://share.streamlit.io
   - Click "New app"
   - Select your GitHub repo
   - Main file: `app.py`
   - Add secrets: `VENICE_API_KEY = "your_key"`
   - Click "Deploy"

3. **Wait 2-3 minutes** → Your app is live! 🎉

---

## PHASE 6: DEMO CREATION (Sunday 7pm - 8pm)

### Create Demo Video

**Using Loom or QuickTime:**

1. **Script (30 seconds per feature):**
   ```
   "Hi! This is my Crypto Market Intelligence Dashboard.
   
   [Show live prices]
   It tracks real-time prices for top cryptocurrencies.
   
   [Click portfolio simulator]
   You can simulate your portfolio and see current value.
   
   [Show price prediction]
   I built ML models to forecast prices 7 days out.
   
   [Click AI insights]
   Venice AI generates market analysis based on current data.
   
   [Show sentiment]
   And it analyzes news sentiment to gauge market mood.
   
   I built this in a weekend using Python, Streamlit, and AI.
   Link in description - thanks for watching!"
   ```

2. **Record:** 
   - Open your deployed app
   - Record screen while narrating
   - Click through all features
   - Keep it under 3 minutes

3. **Edit:**
   - Trim awkward pauses
   - Add text overlays for key features
   - Export as MP4

4. **Create GIF:**
   - Use ezgif.com
   - Upload first 10 seconds of video
   - Optimize for web (under 5MB)
   - Download GIF

5. **Add to README:**
   ```markdown
   ## Demo
   
   ![Demo](assets/demo.gif)
   
   [Watch full demo (3 min)](https://youtu.be/your_video)
   ```

---

## ADVANCED GIGA AI TIPS

### 1. Context Management

**If Giga "forgets" earlier decisions:**

```
CONTEXT REMINDER:
We're building Feature 6 (AI Insights).
In Feature 2, we used CoinGeckoClient from utils/api_client.py.
In PLAN.md, we decided to cache Venice AI responses for 1 hour.

Now implement Feature 6 following these existing patterns.
```

### 2. Parallel Development

**If you want to speed up (advanced):**

```
I'm going to work on the UI while you work on Feature 7.

Create Feature 7 (News Sentiment) in a NEW FILE: news_feature.py

Do NOT modify app.py yet. I'll integrate it later.

Focus only on the sentiment analysis logic.
```

Then you manually merge the files.

### 3. Code Review Mode

**After finishing:**

```
Act as a senior developer reviewing this codebase.

Check for:
1. Security issues (hardcoded secrets, SQL injection risks)
2. Performance bottlenecks (slow loops, missing caching)
3. Code smells (duplicate code, long functions >50 lines)
4. Missing error handling
5. Lack of comments/docstrings

Generate a CODE_REVIEW.md with:
- Issues found (severity: high/medium/low)
- Suggested fixes with code examples
- Priority order for refactoring

Be harsh but constructive.
```

### 4. Testing Generation

**For thoroughness:**

```
Generate pytest tests for all functions in utils/api_client.py

Tests should cover:
- Happy path (API returns valid data)
- Error cases (API timeout, 404, 500 errors)
- Edge cases (empty responses, malformed JSON)
- Mock all external API calls using unittest.mock

Create tests/test_api_client.py with at least 80% code coverage.
```

---

## TROUBLESHOOTING GIGA AI

### Problem: "AI is hallucinating code that doesn't exist"

**Solution:**

```
STOP. You're referencing functions that don't exist yet.

Let's take this step by step:

1. First, show me the CURRENT state of utils/api_client.py
2. Then, explain what NEW functions you want to add
3. Finally, implement ONLY the new functions

Don't assume anything exists unless you created it in this conversation.
```

### Problem: "AI generated a 500-line file"

**Solution:**

```
This file is too long. Refactor it:

1. Split utils/data_processing.py into:
   - data_fetcher.py (API calls)
   - data_cleaner.py (preprocessing)
   - data_analyzer.py (calculations)

2. Each file should be under 200 lines

3. Create an __init__.py that imports everything

Show me the refactored structure first, then implement.
```

### Problem: "AI won't stop generating"

**Solution:**

Press `Escape` or type:

```
PAUSE. 

What you've done so far looks good. 

Before continuing, let me test this locally.

Wait for my feedback before implementing more features.
```

---

## THE ULTIMATE PROMPT CHECKLIST

**Before EVERY Giga AI prompt, verify:**

✅ **ROLE:** Who is the AI? (expert, senior dev, code reviewer)  
✅ **CONTEXT:** What are we building? What stage are we at?  
✅ **CONSTRAINTS:** What should AI NOT do? (file length, dependencies)  
✅ **REQUIREMENTS:** What MUST the feature have?  
✅ **FORMAT:** How should the output look?  
✅ **VALIDATION:** How will I know it worked?

**Good Prompt Example:**

```
ROLE: Senior Python developer
CONTEXT: Feature 3 of crypto dashboard - portfolio simulator
CONSTRAINTS: Keep functions under 50 lines, use existing CoinGeckoClient
REQUIREMENTS: User inputs, real-time calculation, pie chart, table
FORMAT: Update app.py with new section, show complete code
VALIDATION: I'll test by entering portfolio values and checking calculations
```

**Bad Prompt Example:**

```
Add portfolio thing
```

---

## POST-DEPLOYMENT CHECKLIST

### LinkedIn Post

```
🚀 Just shipped my latest portfolio project!

Built a real-time Crypto Market Intelligence Dashboard using:
- Python + Streamlit for the UI
- Venice AI for market insights
- ML price predictions
- News sentiment analysis

From idea to deployment in one weekend 💪

Tech stack: Python, Pandas, Plotly, scikit-learn
Live demo: [your-app.streamlit.app]
GitHub: [your-repo-url]

#DataScience #Python #MachineLearning #AI #Portfolio

[attach demo GIF]
```

### Resume Update

```
Crypto Market Intelligence Dashboard | Python, Streamlit, AI
- Built real-time dashboard processing 50K+ data points daily
- Integrated Venice AI API for automated market insights
- Implemented ML price prediction models (Linear Regression)
- Deployed on Streamlit Cloud with 99.9% uptime
- Live demo: [link]
```

### Portfolio Website

```html
<div class="project-card">
  <img src="demo.gif" alt="Crypto Dashboard Demo">
  <h3>Crypto Market Intelligence</h3>
  <p>
    Real-time cryptocurrency tracking dashboard with AI-powered 
    insights and ML price predictions. Built in 48 hours.
  </p>
  <div class="tech-stack">
    <span>Python</span>
    <span>Streamlit</span>
    <span>Venice AI</span>
    <span>ML</span>
  </div>
  <a href="[deployed-app]">Live Demo</a>
  <a href="[github]">GitHub</a>
</div>
```

---

## FINAL THOUGHTS

### What You Just Learned

✅ How to structure AI prompts for complex projects  
✅ How to break down features into manageable chunks  
✅ How to use Giga AI's context management effectively  
✅ How to iterate on AI-generated code  
✅ How to deploy and document a portfolio project  

### The Real Skill

**Vibe-coding isn't about letting AI do everything.**

It's about:
1. **Knowing what to build** (your product sense)
2. **Breaking it into steps** (your engineering mind)
3. **Communicating clearly** (your prompt skills)
4. **Testing relentlessly** (your quality standards)
5. **Shipping fast** (your bias toward action)

**AI writes the code. You write the prompts. Together, you ship products.**

---

## YOU'RE READY. GO BUILD! 🚀

**Saturday 9am:** Start with the Master Prompt  
**Sunday 8pm:** Push to GitHub, deploy to Streamlit, post on LinkedIn

**By Monday:** You have a working, deployed, portfolio-ready project.

**That's what separates you from the 99% who just talk about building.**

Now close this document and start prompting. 💪