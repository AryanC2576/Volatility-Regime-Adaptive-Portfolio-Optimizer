
import pandas as pd
import numpy as np
from config import settings

class Backtester:
    def __init__(self, initial_capital: float = settings.INITIAL_CAPITAL,
                 transaction_cost_bps: float = settings.TRANSACTION_COST_BPS,
                 slippage_bps: float = settings.SLIPPAGE_BPS):
        """
        Initializes the backtester with starting capital and costs.
        """
        self.initial_capital = initial_capital
        self.transaction_cost_rate = transaction_cost_bps / 10000
        self.slippage_rate = slippage_bps / 10000
        self.portfolio_history = pd.DataFrame(columns=['Total_Value', 'Cash', 'Asset_Value'] + [f'Weight_{s}' for s in settings.ASSET_SYMBOLS])
        self.trades_history = pd.DataFrame(columns=['Date', 'Symbol', 'Action', 'Shares', 'Price', 'Cost'])

    def _calculate_trade_cost(self, old_weights: np.ndarray, new_weights: np.ndarray, current_portfolio_value: float) -> float:
        """
        Calculates transaction costs based on the change in weights.
        """
        old_allocation = old_weights * current_portfolio_value
        new_allocation = new_weights * current_portfolio_value
        capital_traded = np.sum(np.abs(new_allocation - old_allocation))
        total_cost = capital_traded * (self.transaction_cost_rate + self.slippage_rate)
        return total_cost

    def run_backtest(self, df_prices: pd.DataFrame, df_optimal_weights: pd.DataFrame) -> pd.DataFrame:
        """
        Runs the portfolio backtest simulation by explicitly calculating shares to trade.
        """
        portfolio_value = self.initial_capital
        cash_balance = self.initial_capital
        current_holdings = pd.Series(0.0, index=settings.ASSET_SYMBOLS)
        
        portfolio_history_list = []

        # --- CORRECTED MERGE ---
        # Concatenate the DataFrames along the columns, creating a MultiIndex to avoid column name conflicts
        df_prices.columns = pd.MultiIndex.from_product([['Price'], df_prices.columns])
        df_optimal_weights.columns = pd.MultiIndex.from_product([['Weight'], df_optimal_weights.columns])
        df_merged = pd.concat([df_prices, df_optimal_weights], axis=1)
        df_merged = df_merged.dropna()
        # --- END CORRECTED MERGE ---
        
        asset_symbols_ordered = settings.ASSET_SYMBOLS

        print(f"Starting backtest from {df_merged.index.min().strftime('%Y-%m-%d')} to {df_merged.index.max().strftime('%Y-%m-%d')}")

        previous_weights = pd.Series(0.0, index=asset_symbols_ordered)
        trade_cost = 0.0

        for i, (date, row) in enumerate(df_merged.iterrows()):
            # --- CORRECTED SLICING ---
            # Get current prices and target weights from the MultiIndex row
            current_prices = row['Price']
            target_weights = row['Weight']
            # --- END CORRECTED SLICING ---
            
            if current_prices.isnull().any():
                print(f"Skipping {date.strftime('%Y-%m-%d')} due to missing prices.")
                continue

            current_asset_values = current_holdings * current_prices
            portfolio_value = current_asset_values.sum() + cash_balance

            trade_cost = self._calculate_trade_cost(previous_weights.values, target_weights.values, portfolio_value)
            
            portfolio_value_after_cost = portfolio_value - trade_cost
            cash_balance -= trade_cost

            target_shares = (target_weights * portfolio_value_after_cost) / current_prices
            shares_to_trade = target_shares - current_holdings
            
            for symbol in asset_symbols_ordered:
                if shares_to_trade[symbol] > 0:
                    buy_amount = shares_to_trade[symbol] * current_prices[symbol]
                    if cash_balance >= buy_amount:
                        current_holdings[symbol] += shares_to_trade[symbol]
                        cash_balance -= buy_amount
                    else:
                        print(f"Warning: Insufficient cash to buy {shares_to_trade[symbol]:.2f} of {symbol} on {date.strftime('%Y-%m-%d')}")

                elif shares_to_trade[symbol] < 0:
                    sell_amount = shares_to_trade[symbol] * current_prices[symbol]
                    current_holdings[symbol] += shares_to_trade[symbol]
                    cash_balance -= sell_amount
            
            final_asset_value = (current_holdings * current_prices).sum()
            final_portfolio_value = final_asset_value + cash_balance

            portfolio_history_list.append({
                'Date': date,
                'Total_Value': final_portfolio_value,
                'Cash': cash_balance,
                'Asset_Value': final_asset_value,
                **{f'Weight_{s}': current_asset_values[s] / final_portfolio_value if final_portfolio_value != 0 else 0 for s in asset_symbols_ordered}
            })
            
            current_weights = pd.Series(
                [current_asset_values[s] / final_portfolio_value if final_portfolio_value != 0 else 0 for s in asset_symbols_ordered],
                index=asset_symbols_ordered
            )
            previous_weights = current_weights.copy()
            if final_portfolio_value == 0:
                previous_weights.loc[:] = 0

        self.portfolio_history = pd.DataFrame(portfolio_history_list).set_index('Date')
        print("Backtest simulation completed with realistic share-based rebalancing.")
        return self.portfolio_history