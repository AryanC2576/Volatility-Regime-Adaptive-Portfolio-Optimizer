import os
from datetime import datetime

# config/settings.py

import os
from datetime import datetime

# --- API Configuration ---
# Set the default API source first
FINANCE_API_SOURCE = 'yfinance' # Options: 'yfinance', 'alphavantage'

# Then, load the API key and check if it's needed based on the source
ALPHA_VANTAGE_API_KEY = os.environ.get('ALPHA_VANTAGE_API_KEY')
if ALPHA_VANTAGE_API_KEY is None and FINANCE_API_SOURCE == 'alphavantage':
    print("Warning: ALPHA_VANTAGE_API_KEY not found in environment variables. Alpha Vantage API might not work.")

# --- Data Configuration ---
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data/')
RAW_DATA_FILE = os.path.join(DATA_DIR, 'raw_market_data.pkl')

# --- Market Data Parameters ---
ASSET_SYMBOLS = ['SPY', 'QQQ', 'GLD', 'TLT', 'EEM', 'VNQ']
START_DATE = datetime(2010, 1, 1)
END_DATE = datetime.now()

# --- Strategy Parameters ---
VOL_WINDOW = 20
REGIME_THRESHOLD_HIGH_VOL = 0.015
REGIME_THRESHOLD_LOW_VOL = 0.005

# --- Optimization Parameters ---
OPTIMIZATION_WINDOW = 60
RISK_FREE_RATE_ANNUAL = 0.02
TARGET_RISK_ANNUAL = 0.15
LAMBDA_RISK_AVERSION = 0.5

# --- Backtesting Parameters ---
INITIAL_CAPITAL = 1000000000
TRANSACTION_COST_BPS = 2
SLIPPAGE_BPS = 1

# --- Dashboard Configuration ---
DASHBOARD_TITLE = "Volatility-Regime Adaptive Portfolio Optimizer"