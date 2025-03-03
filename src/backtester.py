# new_project/src/backtester.py

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from data.api_client import APIClient
from data.data_models import AgentStateData
from utils.logger import logger
from utils.progress import ProgressTracker
from typing import Dict, List, Optional, Callable

class Backtester:
    """Runs backtesting simulations on AI-based trading strategies."""
    def __init__(
        self,
        agent: Callable,
        tickers: List[str],
        start_date: str,
        end_date: str,
        initial_capital: float,
    ):
        self.agent = agent
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        self.api_client = APIClient()
        self.progress_tracker = ProgressTracker()
        # Portfolio tracking
        self.portfolio_values = []
        self.portfolio = {
            "cash": initial_capital,
            "positions": {ticker: {"shares": 0, "avg_cost": 0} for ticker in tickers},
            "realized_gains": {ticker: 0 for ticker in tickers},
        }

    def fetch_price_data(self, ticker: str) -> Optional[pd.DataFrame]:
        price_response = self.api_client.get_prices(ticker, self.start_date, self.end_date)
        if not price_response or not price_response.prices:
            return None
        df = pd.DataFrame([p.model_dump() for p in price_response.prices])
        df["time"] = pd.to_datetime(df["time"])
        df.set_index("time", inplace=True)
        return df

    def execute_trade(self, ticker: str, action: str, quantity: int, price: float) -> None:
        if quantity <= 0:
            return
        position = self.portfolio["positions"][ticker]
        if action.lower() == "buy":
            total_cost = quantity * price
            if self.portfolio["cash"] >= total_cost:
                new_total_shares = position["shares"] + quantity
                new_avg_cost = ((position["shares"] * position["avg_cost"]) + total_cost) / new_total_shares if new_total_shares > 0 else 0
                position["shares"] = new_total_shares
                position["avg_cost"] = new_avg_cost
                self.portfolio["cash"] -= total_cost
                logger.info(f"Bought {quantity} shares of {ticker} at ${price:.2f}")
            else:
                logger.warning(f"Not enough cash to buy {quantity} shares of {ticker}.")
        elif action.lower() == "sell":
            if position["shares"] >= quantity:
                total_sale_value = quantity * price
                realized_gain = (price - position["avg_cost"]) * quantity
                position["shares"] -= quantity
                self.portfolio["cash"] += total_sale_value
                self.portfolio["realized_gains"][ticker] += realized_gain
                logger.info(f"Sold {quantity} shares of {ticker} at ${price:.2f}, Gain: ${realized_gain:.2f}")
            else:
                logger.warning(f"Not enough shares to sell {quantity} of {ticker}.")

    def calculate_portfolio_value(self, current_prices: Dict[str, float]) -> float:
        total_value = self.portfolio["cash"]
        for ticker, position in self.portfolio["positions"].items():
            if ticker in current_prices:
                total_value += position["shares"] * current_prices[ticker]
        return total_value

    def run_backtest(self) -> Dict[str, float]:
        self.progress_tracker.update_status("Backtesting", "Starting backtest...")
        dates = pd.date_range(self.start_date, self.end_date, freq="B")
        for current_date in dates:
            current_date_str = current_date.strftime("%Y-%m-%d")
            previous_date_str = (current_date - timedelta(days=1)).strftime("%Y-%m-%d")
            current_prices = {}
            for ticker in self.tickers:
                price_data = self.fetch_price_data(ticker)
                if price_data is not None and previous_date_str in price_data.index:
                    current_prices[ticker] = price_data.loc[previous_date_str, "close"]
            if not current_prices:
                logger.warning(f"No valid price data for {current_date_str}. Skipping day.")
                continue
            agent_decisions = self.agent(
                tickers=self.tickers,
                start_date=self.start_date,
                end_date=current_date_str,
                portfolio=self.portfolio,
            )
            for ticker, decision in agent_decisions.items():
                action = decision.get("action", "hold")
                quantity = decision.get("quantity", 0)
                if ticker in current_prices:
                    self.execute_trade(ticker, action, quantity, current_prices[ticker])
            total_value = self.calculate_portfolio_value(current_prices)
            self.portfolio_values.append({"Date": current_date, "Portfolio Value": total_value})
        metrics = self._compute_performance_metrics()
        self.progress_tracker.update_status("Backtesting", "Backtest completed.")
        return metrics

    def _compute_performance_metrics(self) -> Dict[str, float]:
        df = pd.DataFrame(self.portfolio_values).set_index("Date")
        df["Daily Return"] = df["Portfolio Value"].pct_change().fillna(0)
        mean_daily_return = df["Daily Return"].mean()
        std_daily_return = df["Daily Return"].std()
        risk_free_rate = 0.0434 / 252
        sharpe_ratio = np.sqrt(252) * (mean_daily_return - risk_free_rate) / std_daily_return if std_daily_return > 0 else 0.0
        rolling_max = df["Portfolio Value"].cummax()
        drawdown = (df["Portfolio Value"] - rolling_max) / rolling_max
        max_drawdown = drawdown.min() * 100
        logger.info(f"Sharpe Ratio: {sharpe_ratio:.2f}, Max Drawdown: {max_drawdown:.2f}%")
        return {"sharpe_ratio": sharpe_ratio, "max_drawdown": max_drawdown}
