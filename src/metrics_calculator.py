import pandas as pd
import numpy as np
from config import settings

def calculate_returns(series: pd.Series) -> pd.Series:
    """Calculates daily percentage returns."""
    return series.pct_change().dropna()

def calculate_cumulative_returns(returns: pd.Series) -> pd.Series:
    """Calculates cumulative returns from a series of daily returns."""
    return (1 + returns).cumprod()

def calculate_sharpe_ratio(portfolio_returns: pd.Series, risk_free_rate_annual: float = settings.RISK_FREE_RATE_ANNUAL, annualization_factor: int = 252) -> float:
    """
    Calculates the annualized Sharpe Ratio.
    Assumes portfolio_returns are daily returns.
    """
    if portfolio_returns.empty or portfolio_returns.std() == 0:
        return np.nan

    # Convert annual risk-free rate to daily
    daily_risk_free_rate = (1 + risk_free_rate_annual)**(1/annualization_factor) - 1

    excess_returns = portfolio_returns - daily_risk_free_rate
    
    annualized_avg_excess_return = excess_returns.mean() * annualization_factor
    annualized_std_dev = excess_returns.std() * np.sqrt(annualization_factor)

    sharpe = annualized_avg_excess_return / annualized_std_dev
    return sharpe

def calculate_max_drawdown(portfolio_values: pd.Series) -> float:
    """
    Calculates the maximum drawdown of a portfolio value series.
    """
    if portfolio_values.empty:
        return np.nan
    
    # Calculate the running maximum value of the portfolio
    running_max = portfolio_values.cummax()
    
    # Calculate the daily drawdown (percentage from running max)
    drawdowns = (portfolio_values - running_max) / running_max
    
    # The maximum drawdown is the minimum (most negative) value in the drawdowns series
    max_dd = drawdowns.min()
    return max_dd

def calculate_calmar_ratio(portfolio_returns: pd.Series, max_drawdown: float, annualization_factor: int = 252) -> float:
    """
    Calculates the Calmar Ratio.
    """
    if max_drawdown == 0: # Avoid division by zero
        return np.inf if portfolio_returns.mean() > 0 else np.nan
    
    annualized_return = portfolio_returns.mean() * annualization_factor
    calmar = annualized_return / abs(max_drawdown)
    return calmar

def calculate_sortino_ratio(portfolio_returns: pd.Series, risk_free_rate_annual: float = settings.RISK_FREE_RATE_ANNUAL, annualization_factor: int = 252) -> float:
    """
    Calculates the annualized Sortino Ratio.
    Assumes portfolio_returns are daily returns.
    """
    if portfolio_returns.empty:
        return np.nan
        
    daily_risk_free_rate = (1 + risk_free_rate_annual)**(1/annualization_factor) - 1
    
    excess_returns = portfolio_returns - daily_risk_free_rate
    
    # Calculate downside deviation
    downside_returns = excess_returns[excess_returns < 0]
    if downside_returns.empty:
        return np.inf # No downside deviation, so Sortino is infinite if average excess return is positive
    
    downside_deviation = downside_returns.std()
    if downside_deviation == 0:
        return np.inf if excess_returns.mean() > 0 else np.nan # Avoid division by zero

    annualized_avg_excess_return = excess_returns.mean() * annualization_factor
    annualized_downside_deviation = downside_deviation * np.sqrt(annualization_factor)

    sortino = annualized_avg_excess_return / annualized_downside_deviation
    return sortino

def get_performance_summary(portfolio_values: pd.Series, benchmark_values: pd.Series,
                            risk_free_rate_annual: float = settings.RISK_FREE_RATE_ANNUAL) -> dict:
    """
    Generates a summary of key performance metrics.
    """
    summary = {}

    # Calculate daily returns
    portfolio_returns = calculate_returns(portfolio_values)
    benchmark_returns = calculate_returns(benchmark_values)

    # Cumulative Returns
    summary['Cumulative Return (Strategy)'] = calculate_cumulative_returns(portfolio_returns).iloc[-1]
    summary['Cumulative Return (Benchmark)'] = calculate_cumulative_returns(benchmark_returns).iloc[-1]
    
    # Annualized Returns
    summary['Annualized Return (Strategy)'] = portfolio_returns.mean() * 252 # Using 252 trading days
    summary['Annualized Return (Benchmark)'] = benchmark_returns.mean() * 252

    # Volatility (Annualized Standard Deviation)
    summary['Annualized Volatility (Strategy)'] = portfolio_returns.std() * np.sqrt(252)
    summary['Annualized Volatility (Benchmark)'] = benchmark_returns.std() * np.sqrt(252)

    # Max Drawdown
    summary['Max Drawdown (Strategy)'] = calculate_max_drawdown(portfolio_values)
    summary['Max Drawdown (Benchmark)'] = calculate_max_drawdown(benchmark_values)
    
    # Sharpe Ratio
    summary['Sharpe Ratio (Strategy)'] = calculate_sharpe_ratio(portfolio_returns, risk_free_rate_annual)
    summary['Sharpe Ratio (Benchmark)'] = calculate_sharpe_ratio(benchmark_returns, risk_free_rate_annual)
    
    # Calmar Ratio
    summary['Calmar Ratio (Strategy)'] = calculate_calmar_ratio(portfolio_returns, summary['Max Drawdown (Strategy)'])
    summary['Calmar Ratio (Benchmark)'] = calculate_calmar_ratio(benchmark_returns, summary['Max Drawdown (Benchmark)'])

    # Sortino Ratio
    summary['Sortino Ratio (Strategy)'] = calculate_sortino_ratio(portfolio_returns, risk_free_rate_annual)
    summary['Sortino Ratio (Benchmark)'] = calculate_sortino_ratio(benchmark_returns, risk_free_rate_annual)

    return summary
