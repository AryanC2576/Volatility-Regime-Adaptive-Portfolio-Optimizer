import pandas as pd
import numpy as np
from scipy.optimize import minimize

def calculate_covariance_matrix(returns: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates the covariance matrix of asset returns.
    """
    if returns.empty:
        return pd.DataFrame()
    cov_matrix = returns.cov()
    return cov_matrix

def calculate_expected_returns(returns: pd.DataFrame) -> pd.Series:
    """
    Calculates the expected returns (mean of historical returns).
    """
    if returns.empty:
        return pd.Series(dtype=float)
    expected_returns = returns.mean()
    return expected_returns

def mean_variance_optimization(
    expected_returns: pd.Series,
    cov_matrix: pd.DataFrame,
    target_risk: float = None, # Annualized target volatility
    risk_aversion_lambda: float = None, # Lambda for risk aversion in utility optimization
    constraints: dict = None
) -> np.ndarray:
    """
    Performs Mean-Variance Optimization to find optimal portfolio weights.
    Can optimize for a target risk or maximize utility with a risk aversion lambda.
    
    Args:
        expected_returns (pd.Series): Expected returns for each asset.
        cov_matrix (pd.DataFrame): Covariance matrix of asset returns.
        target_risk (float): Annualized target volatility for the portfolio. If provided, optimizes to meet this.
        risk_aversion_lambda (float): Lambda parameter for utility maximization (U = E[R] - 0.5 * lambda * sigma^2).
                                      If provided, maximizes utility.
        constraints (dict): Dictionary of constraints.
                            'sum_to_one': bool (weights sum to 1)
                            'long_only': bool (weights >= 0)
    
    Returns:
        np.ndarray: Optimal weights for each asset.
    """
    num_assets = len(expected_returns)
    if num_assets == 0:
        return np.array([])
        
    initial_weights = np.ones(num_assets) / num_assets

    # Annualization factor for daily data 
    annualization_factor = 252 # Typical for equities/bonds, use 365 for crypto if returns are daily calendar
    # Let's assume input returns are daily.
    annual_expected_returns = expected_returns * annualization_factor
    annual_cov_matrix = cov_matrix * annualization_factor

    # Define objective function based on the optimization goal
    if target_risk is not None:
        # Objective: Minimize volatility while achieving target risk.
        # This becomes a constrained optimization where target_risk is a constraint.
        def portfolio_variance(weights, cov_mat):
            return np.sqrt(weights.T @ cov_mat @ weights) # Annualized Std Dev

        # Target risk as a constraint: sqrt(w'Sigma w) - target_risk = 0
        cons = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1}, # Sum of weights = 1
                {'type': 'eq', 'fun': lambda w: portfolio_variance(w, annual_cov_matrix) - target_risk})
        
        # Maximize return given target risk (or minimize variance for given return & target risk)
        # Here, let's just minimize variance (portfolio_variance) subject to constraints
        objective_function = lambda w: portfolio_variance(w, annual_cov_matrix)
        
    elif risk_aversion_lambda is not None:
        # Objective: Maximize utility (expected return - risk aversion * variance)
        def utility_function(weights, exp_ret, cov_mat, lambda_val):
            port_return = weights.T @ exp_ret
            port_variance = weights.T @ cov_mat @ weights
            return -(port_return - 0.5 * lambda_val * port_variance) # Negative to minimize
        
        objective_function = lambda w: utility_function(w, annual_expected_returns, annual_cov_matrix, risk_aversion_lambda)
        
        # Define base constraints for utility maximization
        cons = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1}) # Sum of weights = 1
    else:
        raise ValueError("Either 'target_risk' or 'risk_aversion_lambda' must be provided.")

    # Define bounds: long-only (weights >= 0) if specified, otherwise no bounds.
    bounds = tuple((0, 1) for _ in range(num_assets)) if constraints and constraints.get('long_only', False) else None
    
    # Add sum_to_one constraint if not already added
    if constraints and constraints.get('sum_to_one', False) and not (target_risk is not None and len(cons) > 0 and cons[0]['fun'](initial_weights) == 0):
         # If target_risk is used, the sum_to_one is already there. Otherwise, add it.
        if target_risk is None: # Only add if we're not using the target_risk constraint which already includes sum_to_one
            cons = list(cons) if cons else []
            cons.append({'type': 'eq', 'fun': lambda w: np.sum(w) - 1})
            cons = tuple(cons)

    try:
        result = minimize(objective_function, initial_weights, method='SLSQP', bounds=bounds, constraints=cons)
        if result.success:
            optimal_weights = result.x
            # Normalize weights to ensure they sum to 1 due to potential float inaccuracies
            optimal_weights = np.clip(optimal_weights, 0, 1) # Ensure non-negative and <=1
            if np.sum(optimal_weights) != 0:
                optimal_weights = optimal_weights / np.sum(optimal_weights)
            else:
                optimal_weights = np.ones(num_assets) / num_assets # Fallback
            return optimal_weights
        else:
            print(f"Optimization failed: {result.message}")
            return np.ones(num_assets) / num_assets # Fallback to equal weights
    except Exception as e:
        print(f"Error during optimization: {e}")
        return np.ones(num_assets)