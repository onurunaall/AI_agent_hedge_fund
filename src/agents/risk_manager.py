# src/agents/risk_manager.py

import numpy as np
from data.api_client import APIClient
from data.data_models import AgentStateData
from utils.logger import logger
from typing import Dict, Optional


class RiskManager:
    """Handles portfolio risk management through position sizing, stop-loss rules, and volatility adjustments."""

    def __init__(self, initial_capital: float = 100000):
        self.api_client = APIClient()
        self.initial_capital = initial_capital

    def get_volatility(self, ticker: str, start_date: str, end_date: str) -> Optional[float]:
        """Fetches historical price data and computes volatility (standard deviation of daily returns)."""
        price_data = self.api_client.get_prices(ticker, start_date, end_date)
        if not price_data or not price_data.prices:
            return None

        closes = np.array([p.close for p in price_data.prices])
        returns = np.diff(closes) / closes[:-1]
        return np.std(returns)

    def get_beta(self, ticker: str, market_index: str, start_date: str, end_date: str) -> Optional[float]:
        """Computes the stock’s beta relative to the market index."""
        stock_prices = self.api_client.get_prices(ticker, start_date, end_date)
        market_prices = self.api_client.get_prices(market_index, start_date, end_date)

        if not stock_prices or not stock_prices.prices or not market_prices or not market_prices.prices:
            return None

        stock_returns = np.diff([p.close for p in stock_prices.prices]) / [p.close for p in stock_prices.prices][:-1]
        market_returns = np.diff([p.close for p in market_prices.prices]) / [p.close for p in market_prices.prices][:-1]

        if len(stock_returns) != len(market_returns):
            return None

        covariance = np.cov(stock_returns, market_returns)[0, 1]
        market_variance = np.var(market_returns)
        return covariance / market_variance if market_variance > 0 else None

    def calculate_var(self, ticker: str, start_date: str, end_date: str, confidence_level: float = 0.95) -> Optional[float]:
        """Calculates Value at Risk (VaR) at a given confidence level."""
        volatility = self.get_volatility(ticker, start_date, end_date)
        if volatility is None:
            return None

        z_score = 1.65 if confidence_level == 0.95 else 2.33  # 95% or 99% confidence
        daily_var = self.initial_capital * volatility * z_score
        return daily_var

    def determine_position_size(self, ticker: str, start_date: str, end_date: str) -> Optional[float]:
        """Calculates optimal position size based on volatility and beta-adjusted risk."""
        volatility = self.get_volatility(ticker, start_date, end_date)
        beta = self.get_beta(ticker, "SPY", start_date, end_date)

        if volatility is None or beta is None:
            return None

        risk_per_trade = 0.01  # 1% of capital risk per trade
        adjusted_risk = risk_per_trade / (volatility * beta if beta > 0 else 1)
        position_size = self.initial_capital * adjusted_risk
        return max(0, min(position_size, self.initial_capital * 0.1))  # Cap position at 10% of total capital

    def apply_stop_loss(self, entry_price: float, stop_loss_pct: float = 5.0) -> float:
        """Determines stop-loss price based on percentage drawdown."""
        return entry_price * (1 - stop_loss_pct / 100)

    def apply_take_profit(self, entry_price: float, take_profit_pct: float = 10.0) -> float:
        """Determines take-profit price based on percentage gain target."""
        return entry_price * (1 + take_profit_pct / 100)

    def rebalance_portfolio(self, portfolio: Dict[str, float], threshold: float = 0.05) -> Dict[str, float]:
        """Adjusts positions based on market conditions and risk parameters."""
        total_value = sum(portfolio.values())
        target_allocation = {ticker: total_value * 0.1 for ticker in portfolio.keys()}  # Equal weight portfolio

        adjustments = {}
        for ticker, value in portfolio.items():
            deviation = (value - target_allocation[ticker]) / target_allocation[ticker]
            if abs(deviation) > threshold:
                adjustments[ticker] = target_allocation[ticker] - value

        return adjustments

    def manage_risk(self, ticker: str, entry_price: float, start_date: str, end_date: str) -> Optional[AgentStateData]:
        """Executes risk management calculations and returns structured output."""
        position_size = self.determine_position_size(ticker, start_date, end_date)
        if position_size is None:
            logger.warning(f"[{ticker}] Unable to determine position size due to missing risk metrics.")
            return None

        stop_loss_price = self.apply_stop_loss(entry_price)
        take_profit_price = self.apply_take_profit(entry_price)
        var = self.calculate_var(ticker, start_date, end_date)

        reasoning = (
            f"Position Size: ${position_size:.2f}, "
            f"Stop Loss at: ${stop_loss_price:.2f}, "
            f"Take Profit at: ${take_profit_price:.2f}, "
            f"VaR (95%): ${var:.2f}."
        )

        logger.info(f"[{ticker}] Risk Management Decision: {reasoning}")

        return AgentStateData(
            tickers=[ticker],
            start_date=start_date,
            end_date=end_date,
            ticker_analyses={
                ticker: {
                    "position_size": position_size,
                    "stop_loss_price": stop_loss_price,
                    "take_profit_price": take_profit_price,
                    "value_at_risk": var,
                    "reasoning": reasoning
                }
            }
        )
