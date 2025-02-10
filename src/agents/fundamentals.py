# src/agents/fundamentals.py

from data.api_client import APIClient
from data.data_models import AgentStateData
from utils.logger import logger
from typing import Dict, Optional


class FundamentalAnalyzer:
    """Analyzes fundamental metrics of a stock using multi-factor scoring."""

    def __init__(self):
        self.api_client = APIClient()

    def analyze_financials(self, ticker: str, end_date: str) -> Optional[AgentStateData]:
        """Fetches financial metrics and calculates multi-step scoring for a stock."""
        metrics_list = self.api_client.get_financial_metrics(ticker, end_date)

        if not metrics_list:
            return None

        metrics = metrics_list[0]  # Latest available financial data

        scores = {
            "profitability": self._compute_profitability_score(metrics),
            "growth": self._compute_growth_score(metrics),
            "health": self._compute_health_score(metrics),
            "valuation": self._compute_valuation_score(metrics)
        }

        overall_score = sum(scores.values()) / 4
        detailed_analysis = {
            "ticker": ticker,
            "overall_score": overall_score,
            "scores": scores,
            "reasoning": self._generate_reasoning(scores)
        }

        logger.info(f"[{ticker}] Fundamental Analysis Score: {overall_score:.2f}")
        return AgentStateData(**detailed_analysis)

    def _compute_profitability_score(self, metrics) -> float:
        """Calculates profitability score based on return on equity and net margin."""
        score = 0
        if metrics.return_on_equity and metrics.return_on_equity > 10:
            score += 1
        if metrics.net_margin and metrics.net_margin > 10:
            score += 1
        return score / 2  # Normalize to a 0-1 range

    def _compute_growth_score(self, metrics) -> float:
        """Evaluates growth potential using revenue and earnings growth."""
        score = 0
        if metrics.revenue_growth and metrics.revenue_growth > 5:
            score += 1
        if metrics.earnings_growth and metrics.earnings_growth > 5:
            score += 1
        return score / 2

    def _compute_health_score(self, metrics) -> float:
        """Assesses financial health based on debt-to-equity ratio and current ratio."""
        score = 0
        if metrics.debt_to_equity and metrics.debt_to_equity < 1:
            score += 1
        if metrics.current_ratio and metrics.current_ratio > 1.5:
            score += 1
        return score / 2

    def _compute_valuation_score(self, metrics) -> float:
        """Checks if the stock is undervalued using P/E and P/B ratios."""
        score = 0
        if metrics.price_to_earnings_ratio and metrics.price_to_earnings_ratio < 15:
            score += 1
        if metrics.price_to_book_ratio and metrics.price_to_book_ratio < 1.5:
            score += 1
        return score / 2

    def _generate_reasoning(self, scores: Dict[str, float]) -> str:
        """Generates a human-readable explanation of the scores."""
        return (
            f"Profitability Score: {scores['profitability']:.2f} - Indicates strong margins.\n"
            f"Growth Score: {scores['growth']:.2f} - Evaluates revenue and earnings expansion.\n"
            f"Health Score: {scores['health']:.2f} - Measures financial stability.\n"
            f"Valuation Score: {scores['valuation']:.2f} - Determines if the stock is undervalued."
        )
