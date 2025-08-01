import pandas as pd
import numpy as np
import yfinance as yf
import os
from datetime import datetime
import time # For rate limiting

from config import settings

def get_sample_data() -> pd.DataFrame:
    """
    Generates a hardcoded sample DataFrame with a MultiIndex for testing purposes.
    This bypasses the yfinance API to allow the backtest to run.
    """
    print("Warning: Using hardcoded sample data for debugging purposes.")
    dates = pd.to_datetime(pd.date_range(start="2020-01-01", end="2022-01-01", freq="B"))
    num_assets = len(settings.ASSET_SYMBOLS)
    
    # Create sample data for each asset
    data = {}
    for symbol in settings.ASSET_SYMBOLS:
        # Create random walk prices
        prices = 100 + np.cumsum(np.random.randn(len(dates)) * 0.5)
        volume = np.random.randint(100000, 500000, len(dates))
        data[symbol] = pd.DataFrame({
            'Open': prices - np.random.rand(len(dates)),
            'High': prices + np.random.rand(len(dates)),
            'Low': prices - np.random.rand(len(dates)),
            'Close': prices,
            'Volume': volume
        }, index=dates)

    # Combine into a MultiIndex DataFrame
    df_combined = pd.concat([data[symbol] for symbol in settings.ASSET_SYMBOLS], keys=settings.ASSET_SYMBOLS, axis=1)
    
    # This will have a MultiIndex, but the symbols are at level 0 and the metrics at level 1
    # We need to swap them to match the expected format for the backtester
    # The expected format is ('SPY', 'Close'), not ('Close', 'SPY')
    df_combined.columns = df_combined.columns.swaplevel(0, 1)
    df_combined = df_combined.sort_index(axis=1, level=[0, 1])

    # The backtester expects the MultiIndex to be (Symbol, Metric)
    # The from_product will create (Metric, Symbol), so we need to swap levels.
    df_final = pd.DataFrame(df_combined.values, index=df_combined.index, columns=df_combined.columns)

    # Let's rebuild the multi-index correctly
    all_data = []
    for symbol in settings.ASSET_SYMBOLS:
        df = data[symbol]
        df.columns = pd.MultiIndex.from_tuples([(symbol, col) for col in df.columns])
        all_data.append(df)
    
    df_final = pd.concat(all_data, axis=1)
    df_final = df_final.sort_index(axis=1, level=[0,1])

    return df_final


def fetch_historical_data(symbol: str, start_date: datetime, end_date: datetime, interval: str = '1d') -> pd.DataFrame:
    """
    Fetches historical OHLCV data for a single symbol from Yahoo Finance.
    """
    print(f"Fetching data for {symbol} from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}...")
    try:
        data = yf.download(symbol, start=start_date, end=end_date, interval=interval)
        if data.empty:
            print(f"Warning: No data fetched for {symbol}.")
            return pd.DataFrame()
        return data
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame()

def fetch_multiple_assets_data(symbols: list, start_date: datetime, end_date: datetime, interval: str = '1d') -> pd.DataFrame:
    """
    Fetches historical OHLCV data for multiple symbols and combines them into a MultiIndex DataFrame.
    """
    all_data = []
    for symbol in symbols:
        df = fetch_historical_data(symbol, start_date, end_date, interval)
        if not df.empty:
            df.columns = pd.MultiIndex.from_tuples([(symbol, col) for col in df.columns])
            all_data.append(df)
        time.sleep(1) # Be nice to APIs, especially yfinance sometimes has limits

    if not all_data:
        print("No data fetched for any symbols.")
        return pd.DataFrame()

    combined_df = pd.concat(all_data, axis=1)
    
    combined_df = combined_df.sort_index(axis=1, level=[0,1])

    print(f"Combined data for {len(symbols)} assets from {combined_df.index.min().strftime('%Y-%m-%d')} to {combined_df.index.max().strftime('%Y-%m-%d')}")
    return combined_df

def save_data(df: pd.DataFrame, file_path: str):
    """
    Saves a DataFrame to a Pickle file, but only if it's not empty.
    """
    if df.empty:
        print("Warning: DataFrame is empty, not saving.")
        return
        
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    df.to_pickle(file_path)
    print(f"Data saved to {file_path}")

def load_data(file_path: str) -> pd.DataFrame:
    """
    Loads a DataFrame from a Pickle file with validation.
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return pd.DataFrame()
    
    try:
        df = pd.read_pickle(file_path)
        if not df.empty and isinstance(df.columns, pd.MultiIndex) and 'Close' in df.columns.get_level_values(1):
            print(f"Data loaded from {file_path}.")
            return df
        else:
            print(f"Error: Loaded DataFrame is invalid. It might be empty or corrupt.")
            return pd.DataFrame()
    except Exception as e:
        print(f"Error loading pickle file: {e}")
        return pd.DataFrame()