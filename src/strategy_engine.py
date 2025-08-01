import pandas as pd
import numpy as np
from config import settings
from src.portfolio_optimizer import mean_variance_optimization # Import the optimizer

def generate_regime_specific_weights(
    current_regime: str,
    lookback_returns: pd.DataFrame,
    initial_weights: np.ndarray = None # For warm-starting optimization
) -> np.ndarray:

    num_assets = lookback_returns.shape[1]
    # Default to equal weights if no specific strategy is defined for a regime
    weights = np.ones(num_assets) / num_assets

    if lookback_returns.empty:
        print(f"Warning: No lookback returns for regime {current_regime}. Returning equal weights.")
        return weights


    expected_returns = lookback_returns.mean()
    cov_matrix = lookback_returns.cov()

    if current_regime == 'High_Vol':
        # Example: In high vol, might target lower risk or shift to less correlated assets
        print(f"Generating weights for HIGH VOLATILITY regime.")

        weights = mean_variance_optimization(
            expected_returns, cov_matrix, target_risk=settings.TARGET_RISK_ANNUAL * 0.5,
            constraints={'sum_to_one': True, 'long_only': True}
        )
    elif current_regime == 'Low_Vol':
        # Example: In low vol, might increase equity exposure or target higher risk
        print(f"Generating weights for LOW VOLATILITY regime.")

        weights = mean_variance_optimization(
            expected_returns, cov_matrix, risk_aversion_lambda=settings.LAMBDA_RISK_AVERSION * 1.5,
            constraints={'sum_to_one': True, 'long_only': True}
        )
    else: # 'Normal_Vol'
        # Example: Standard mean-variance optimization
        print(f"Generating weights for NORMAL VOLATILITY regime.")
        weights = mean_variance_optimization(
            expected_returns, cov_matrix, risk_aversion_lambda=settings.LAMBDA_RISK_AVERSION,
            constraints={'sum_to_one': True, 'long_only': True}
        )

    weights = np.clip(weights, 0, 1)
    if np.sum(weights) != 0:
        weights = weights / np.sum(weights) # Re-normalize if needed
    else: # Fallback if optimization fails to produce valid weights
        weights = np.ones(num_assets) / num_assets
        print("Warning: Optimization failed or resulted in zero sum, defaulting to equal weights.")

    return weights
