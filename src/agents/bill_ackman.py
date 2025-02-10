# src/agents/bill_ackman.py

from data.api_client import APIClient
from data.data_models import AgentStateData
from utils.logger import logger
from llm.llm import run_llm_analysis
from typing import Dict, Optional


class BillAckmanStrategy:
    """Implements Bill Ackman's activist investment strategy."""

    def __init__(self):
        self.api_client = APIClient()

    def get_financial_data(self, ticker: str, end_date: str) -> Optional[Dict[str, float]]:
        """Fetches multi-year financial metrics and key valuation data."""
        metrics_list = self.api_client.get_financial_metrics(ticker, end_date, limit=5)
        if not metrics_list:
            return None

        financial_line_items = self.api_client.search_line_items(
            ticker, end_date, ["netIncome", "totalDebt", "freeCashFlow"]
        )

        net_income = financial_line_items.get("netIncome")
        free_cash_flow = financial_line_items.get("freeCashFlow")
        total_debt = financial_line_items.get("totalDebt")

        metrics = metrics_list[0]  # Latest available data
        return {
            "revenue_growth": metrics.revenue_growth,
            "earnings_growth": metrics.earnings_growth,
            "free_cash_flow": free_cash_flow,
            "debt_to_equity": metrics.debt_to_equity,
            "market_cap": self.api_client.get_market_cap(ticker, end_date),
            "total_debt": total_debt
        }

    def analyze_stock(self, ticker: str, end_date: str) -> Optional[AgentStateData]:
        """Evaluates a stock based on Ackman's strategy with catalysts."""
        financials = self.get_financial_data(ticker, end_date)
        if not financials or not financials["free_cash_flow"] or not financials["market_cap"]:
            logger.warning(f"[{ticker}] Missing key financial data for analysis.")
            return None

        is_cash_flow_positive = financials["free_cash_flow"] > 0
        is_high_growth = (
            financials["revenue_growth"] and financials["earnings_growth"]
            and financials["revenue_growth"] > 10 and financials["earnings_growth"] > 10
        )
        has_reasonable_debt = financials["debt_to_equity"] and financials["debt_to_equity"] < 2

        # Activist catalysts
        catalyst_present = self.api_client.check_mna_activity(ticker, end_date)

        signal = "Bullish" if is_cash_flow_positive and is_high_growth and has_reasonable_debt else "Neutral"
        if catalyst_present:
            signal = "Bullish"

        reasoning = (
            f"Revenue Growth: {financials['revenue_growth']}%, Earnings Growth: {financials['earnings_growth']}%, "
            f"FCF Per Share: ${financials['free_cash_flow']:.2f}, Total Debt: ${financials['total_debt']:.2f}, "
            f"Debt-to-Equity: {financials['debt_to_equity']}."
        )

        final_decision = run_llm_analysis(ticker, reasoning)

        logger.info(f"[{ticker}] Ackman Analysis: {final_decision}")

        return AgentStateData(
            tickers=[ticker],
            start_date=end_date,
            end_date=end_date,
            ticker_analyses={ticker: {"investment_signal": final_decision, "reasoning": reasoning}},
        )
