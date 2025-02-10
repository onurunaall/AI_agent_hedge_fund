# src/data/state.py

from data.data_models import Portfolio, TickerAnalysis
from typing import Dict


class HedgeFundState:
    """Manages the global state of the AI hedge fund."""

    def __init__(self):
        self.portfolio = Portfolio(positions={}, total_cash=100000, portfolio_value=100000)
        self.analyst_signals: Dict[str, TickerAnalysis] = {}

    def update_portfolio(self, ticker: str, shares: int, avg_cost: float) -> None:
        """Updates portfolio holdings after a trade execution."""
        if ticker not in self.portfolio.positions:
            self.portfolio.positions[ticker] = {"shares": 0, "avg_cost": 0}

        position = self.portfolio.positions[ticker]
        position["shares"] = shares
        position["avg_cost"] = avg_cost

    def record_analyst_signal(self, ticker: str, analysis: TickerAnalysis) -> None:
        """Stores AI analyst signals for a given ticker."""
        self.analyst_signals[ticker] = analysis

    def get_portfolio_state(self) -> Portfolio:
        """Returns the current portfolio state."""
        return self.portfolio

    def get_analyst_signals(self) -> Dict[str, TickerAnalysis]:
        """Returns all stored AI analyst signals."""
        return self.analyst_signals
