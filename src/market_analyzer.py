import pandas as pd
import numpy as np
from config import settings

def calculate_returns(df_prices: pd.DataFrame | pd.Series) -> pd.DataFrame | pd.Series:
    """
    Calculates daily logarithmic returns for a DataFrame or Series.
    Input df_prices should be a DataFrame with asset symbols as columns or a Series of prices.
    """
    if isinstance(df_prices, pd.Series):
        # If the input is a Series, just calculate the returns on it directly
        log_returns = np.log(df_prices / df_prices.shift(1))
        print("Calculated logarithmic returns for a Series.")
        return log_returns.dropna()
    elif isinstance(df_prices, pd.DataFrame):
        # If the input is a DataFrame, iterate through columns as before
        log_returns = pd.DataFrame(index=df_prices.index)
        for symbol in df_prices.columns:
            log_returns[symbol] = np.log(df_prices[symbol] / df_prices[symbol].shift(1))
        
        log_returns.columns.name = 'Symbol'
        print("Calculated logarithmic returns for a DataFrame.")
        return log_returns.dropna()
    else:
        raise TypeError("Input must be a Pandas Series or DataFrame.")


def calculate_volatility(df_returns: pd.DataFrame, window: int = settings.VOL_WINDOW) -> pd.Series:
    """
    Calculates the rolling annualized volatility of the portfolio based on asset returns.
    """
    if df_returns.empty:
        return pd.Series(dtype=float)

    individual_asset_vol = df_returns.rolling(window=window).std()
    
    avg_asset_daily_vol = individual_asset_vol.mean(axis=1)

    print(f"Calculated rolling daily volatility over {window} days.")
    return avg_asset_daily_vol.dropna()

def identify_regimes(df: pd.DataFrame, vol_col: str = 'Volatility',
                     high_threshold: float = settings.REGIME_THRESHOLD_HIGH_VOL,
                     low_threshold: float = settings.REGIME_THRESHOLD_LOW_VOL) -> pd.Series:
    """
    Classifies each period into a volatility regime (Low_Vol, Normal_Vol, High_Vol).
    """
    if vol_col not in df.columns:
        raise ValueError(f"DataFrame must contain a '{vol_col}' column.")

    regime = pd.Series('Normal_Vol', index=df.index, dtype=str)
    regime[df[vol_col] >= high_threshold] = 'High_Vol'
    regime[df[vol_col] <= low_threshold] = 'Low_Vol'

    print("Identified volatility regimes.")
    return regime