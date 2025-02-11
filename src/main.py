# new_project/src/main.py

import argparse
import questionary
from agents.analyst import AIAnalyst
from backtester import Backtester
from utils.display import BacktestVisualizer
from utils.progress import ProgressTracker
from data.state import HedgeFundState
from utils.logger import logger

def main():
    parser = argparse.ArgumentParser(description="Run AI Hedge Fund Backtesting.")
    parser.add_argument("--tickers", type=str, required=True, help="Comma-separated list of stock ticker symbols (e.g., AAPL, MSFT, GOOGL)")
    parser.add_argument("--start-date", type=str, required=True, help="Start date in YYYY-MM-DD format")
    parser.add_argument("--end-date", type=str, required=True, help="End date in YYYY-MM-DD format")
    parser.add_argument("--initial-capital", type=float, default=100000, help="Initial portfolio capital (default: 100000)")
    args = parser.parse_args()
    
    tickers = [ticker.strip().upper() for ticker in args.tickers.split(",")]
    logger.info(f"Initializing AI Hedge Fund Backtest for {tickers}")
    
    # Interactive selection of analysts (simulate old project's selection)
    analyst_choices = ["Buffett", "Ackman", "Technical", "Fundamentals", "Sentiment"]
    selected_analysts = questionary.checkbox("Select your AI analysts:", choices=analyst_choices).ask()
    if not selected_analysts:
        logger.info("No analysts selected. Exiting.")
        return
    logger.info(f"Selected analysts: {selected_analysts}")
    
    # For simplicity, our AIAnalyst aggregates signals from available strategies
    analyst = AIAnalyst()
    hedge_fund_state = HedgeFundState()
    progress_tracker = ProgressTracker()
    backtester = Backtester(
        agent=analyst.collect_signals,
        tickers=tickers,
        start_date=args.start_date,
        end_date=args.end_date,
        initial_capital=args.initial_capital,
    )
    
    performance_metrics = backtester.run_backtest()
    BacktestVisualizer.plot_portfolio_value(backtester.portfolio_values)
    BacktestVisualizer.print_performance_summary(performance_metrics.get("sharpe_ratio", 0), performance_metrics.get("max_drawdown", 0))
    logger.info("AI Hedge Fund backtest completed successfully!")

if __name__ == "__main__":
    main()
