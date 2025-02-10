# src/agents/fundamentals.py

from data.api_client import APIClient
from data.data_models import AgentStateData
from utils.logger import logger
from utils.progress import progress
from typing import Dict, Optional


class FundamentalAnalyzer:
    """Analyzes fundamental metrics of a stock using multi-factor scoring."""

    def __init__(self):
        self.api_client = APIClient()

    def analyze_financials(self, ticker: str, end_date: str) -> Optional[AgentStateData]:
        """Fetches financial metrics and calculates multi-step scoring for a stock."""
        progress.update_status("fundamentals_agent", ticker, "Fetching financial data")
        metrics_list = self.api_client.get_financial_metrics(ticker, end_date)

        if not metrics_list:
            return None

        metrics = metrics_list[0]
        insider_trades = self.api_client.get_insider_trades(ticker, end_date)
        macro_data = self.api_client.get_macro_data(end_date)

        scores = {
            "profitability": self._compute_profitability_score(metrics),
            "growth": self._compute_growth_score(metrics),
            "health": self._compute_health_score(metrics),
            "valuation": self._compute_valuation_score(metrics),
            "insider_activity": 1 if insider_trades else 0,
            "macro_trend": macro_data
        }

        overall_score = sum(scores.values()) / len(scores)
        logger.info(f"[{ticker}] Fundamental Analysis Score: {overall_score:.2f}")

        return AgentStateData(
            tickers=[ticker],
            start_date=end_date,
            end_date=end_date,
            ticker_analyses={ticker: {"fundamental_score": overall_score, "detailed_scores": scores}}
        )
