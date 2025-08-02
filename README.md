# Volatility-Regime Adaptive Portfolio Optimizer

## Project Overview

This repository contains an end-to-end quantitative backtesting pipeline for a Volatility-Regime Adaptive Portfolio Optimizer. The project is designed to demonstrate a sophisticated trading strategy that dynamically adjusts asset allocation based on the prevailing market volatility. Built in a modular Python framework, it simulates how an investment would have performed historically by systematically adapting to different market conditions.
This project goes beyond simple momentum strategies by integrating key concepts in quantitative finance, including modern portfolio theory, time-series analysis, and rigorous backtesting with realistic assumptions. It serves as a robust demonstration of core skills highly valued in top-tier quantitative finance and research roles.

## Methodology

### The Adaptive Strategy

The central hypothesis is that market efficiency and asset correlations change during periods of high and low volatility. A static portfolio, which maintains a fixed allocation regardless of market conditions, is therefore sub-optimal. This strategy addresses this by classifying the market into three distinct regimes using a rolling volatility metric:
1. Low Volatility (Low_Vol): This regime is characterized by stable, upward or downward trending markets where asset prices fluctuate within a narrow band. During these periods, the optimizer is configured to take on a higher risk tolerance, potentially allocating a larger portion of the portfolio to growth assets like equities to capitalize on sustained trends.

2. Normal Volatility (Normal_Vol): This represents the baseline, business-as-usual market condition. The strategy maintains a standard, balanced portfolio, often relying on a conventional mean-variance optimization to achieve a balanced risk-return profile.

3. High Volatility (High_Vol): This regime is defined by periods of market stress, panic, or uncertainty (e.g., economic crises). During these times, risk assets tend to perform poorly. The optimizer becomes highly defensive, reallocating capital to low-volatility assets such as government bonds or precious metals, or moving a significant portion to cash to protect against significant drawdowns and capital loss.

### Backtesting Assumptions

To ensure the backtest is as realistic as possible and to avoid common pitfalls, the simulation engine incorporates the following critical assumptions:
. Transaction Costs: Every trade incurs costs. The backtester simulates this by deducting a fee (specified in basis points, e.g., 0.02% of the traded capital) for every buy and sell order. Neglecting these costs, which can compound, would lead to an unrealistic overestimation of profitability.

. Slippage: This is the cost of a trade due to a difference between the expected execution price and the actual execution price. In a fast-moving or illiquid market, this can be significant. The backtester models this by deducting a small, percentage-based slippage fee from every trade, providing a more conservative and reliable performance metric.

. No Look-Ahead Bias: A fundamental principle of robust backtesting is to prevent the use of future data in past decisions. The strategy's rebalancing decisions for a given day T are based exclusively on data available up to day T-1. This simulates a real-world scenario where a trader must make decisions with incomplete information.

. Share-Based Rebalancing: Instead of conceptually reallocating capital, the backtesting engine explicitly calculates the number of shares to buy or sell for each asset. It meticulously manages the portfolio's cash balance, deducts trade costs, and ensures trades are only executed if sufficient cash is available. This provides a more accurate and robust simulation of a real brokerage account.

### Key Technologies

. Python: The core programming language for the entire pipeline, chosen for its vast ecosystem of libraries and readability.

. Pandas & NumPy: These are the workhorses of the project. NumPy is used for high-performance numerical computation, while Pandas is used for the efficient manipulation, analysis, and management of time-series financial data.

. yfinance: A reliable and free source for fetching historical market data, used for its simplicity and the ability to download clean OHLCV data without requiring an API key for this project's needs.

. SciPy: Utilized for advanced numerical optimization within the portfolio_optimizer.py module. Its powerful solvers are essential for finding the optimal asset weights in the portfolio based on complex constraints.

. Matplotlib: The chosen library for generating clear and professional visualizations of strategy performance and market conditions.

. .env file: A best practice for securely managing API keys. The project is structured to read keys from environment variables, ensuring that sensitive information is never committed to a public repository.

## Getting Started

### Prerequisites

Ensure you have Python 3.9+ installed and a working environment (e.g., Anaconda). You will also need to install the project dependencies:

terminal:
pip install pandas numpy matplotlib yfinance requests scipy python-dotenv

### File Structure

The project is designed in a modular fashion to promote clarity and reusability, a key principle of good software engineering.

project_root/
├── src/                      # Core Python modules for the backtesting pipeline
│   ├── backtester.py
│   ├── data_fetcher.py
│   ├── market_analyzer.py
│   ├── metrics_calculator.py
│   ├── portfolio_optimizer.py
│   └── strategy_engine.py
├── config/                   # Configuration files for the project
│   └── settings.py
├── data/                     # Data storage (raw and processed)
│   └── raw_market_data.pkl
├── main.py                   # Main entry point to run the pipeline
└── README.md                 # This file

#### How To Run

1. Set up the environment:

. Navigate to the project_root directory.

. Create a .env file for API keys (e.g., if you switch from yfinance to another API). This file is ignored by Git for security.

2. Execute the main script:

terminal:
python main.py

The script will automatically handle data fetching, backtesting, and output the final performance summary and plots.

## Key Results & Analysis

Results will vary based on the data and parameters used. The below is for illustrative purposes.
This section is where you would present a summary of your backtest's performance, including both quantitative metrics and a qualitative analysis of the results.

### Performance Summary

<img width="389" height="299" alt="image" src="https://github.com/user-attachments/assets/113634f7-21bf-4d9d-8d78-50b8352a8725" />


### Cumulative Performance

The cumulative return of the Volatility-Regime Adaptive Strategy versus a simple Buy & Hold benchmark.

<img width="1389" height="690" alt="image" src="https://github.com/user-attachments/assets/e6a6fa5d-220b-46c8-a74d-8e2b0f648596" />

### Volatility Regimes

An example asset (SPY) with volatility regimes overlaid. Green, blue, and red dots represent low, normal, and high volatility periods, respectively.

<img width="1389" height="690" alt="image" src="https://github.com/user-attachments/assets/77d6d8d3-7c25-4eab-a9e6-47b57f7224ea" />

## Limitations and Future Work

This project provides a robust foundation but has several opportunities for enhancement:
1. Dynamic Regime Identification: Implement a more advanced, adaptive model for identifying market regimes. Instead of fixed volatility thresholds, consider using unsupervised learning techniques like K-Means clustering on a set of market features (e.g., volatility, trading volume, and correlation) to let the data define the regimes dynamically.

2. Sophisticated Optimization: Explore more advanced portfolio optimization techniques beyond the classical mean-variance approach. Implement Risk Parity, which aims to distribute risk equally among assets, or Hierarchical Risk Parity, which uses asset correlations to build a more intuitive portfolio structure.

3. Multi-Factor Modeling: Incorporate a factor model (e.g., a Fama-French model) to understand and predict asset returns. Build a strategy to exploit mispricings relative to these factors (e.g., trading stocks with high exposure to a specific factor).

4. Alternative Data: Integrate external data sources beyond traditional price data. This could include news sentiment analysis, on-chain analytics for cryptocurrencies, or macroeconomic data to generate more sophisticated trading signals.

5. Monte Carlo Simulation: Use Monte Carlo methods to simulate portfolio performance under thousands of possible future scenarios, providing a more robust risk assessment than a single historical backtest. This demonstrates a deep understanding of probabilistic modeling.

## Disclaimer

This code is provided for educational and illustrative purposes only. It does not constitute financial advice, and past performance is not indicative of future results. Trading financial instruments carries substantial risk, and you could lose all of your capital. Always conduct your own thorough research and consult with a qualified financial professional before making any investment decisions.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author
Aryan Chakravorty - github.com/AryanC2576






