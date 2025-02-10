# src/main.py

import argparse
from agents.analysts import AIAnalyst
from backtester import Backtester
from utils.display import BacktestVisualizer
from utils.progress import ProgressTracker
from data.state import HedgeFundState
from utils.logger import logger


def main():
    """Runs the AI hedge fund backtesting system."""
    parser = argparse.ArgumentParser(description="Run AI Hedge Fund backtesting.")
    
    parser.add_argument(
        "--tickers",
        type=str,
        required=True,
        help="Comma-separated list of stock ticker symbols (e.g., AAPL, MSFT, GOOGL)"
    )
    parser.add_argument(
        "--start-date",
        type=str,
        required=True,
        help="Start date in YYYY-MM-DD format"
    )
    parser.add_argument(
        "--end-date",
        type=str,
        required=True,
        help="End date in YYYY-MM-DD format"
    )
    parser.add_argument(
        "--initial-capital",
        type=float,
        default=100000,
        help="Initial portfolio capital (default: 100000)"
    )

    args = parser.parse_args()
    tickers = [ticker.strip().upper() for ticker in args.tickers.split(",")]

    logger.info(f"Initializing AI Hedge Fund Backtest for {tickers}")

    # Initialize components
    analyst = AIAnalyst()
    hedge_fund_state = HedgeFundState()
    progress_tracker = ProgressTracker()

    # Run backtest
    backtester = Backtester(
        agent=analyst.collect_signals,
        tickers=tickers,
        start_date=args.start_date,
        end_date=args.end_date,
        initial_capital=args.initial_capital,
    )

    performance_metrics = backtester.run_backtest()
    
    # Display results
    BacktestVisualizer.plot_portfolio_performance(backtester.portfolio_values)
    BacktestVisualizer.print_summary_statistics(performance_metrics)

    logger.info("AI Hedge Fund backtest completed successfully!")


if __name__ == "__main__":
    main()
