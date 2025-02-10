# src/agents/warren_buffett.py

from data.api_client import APIClient
from data.data_models import AgentStateData
from utils.logger import logger
from llm.llm import run_llm_analysis
from typing import Dict, Optional


class WarrenBuffettStrategy:
    """Implements Warren Buffett's fundamental value investing principles."""

    def __init__(self):
        self.api_client = APIClient()

    def get_financial_data(self, ticker: str, end_date: str) -> Optional[Dict[str, float]]:
        """Fetches key financial data including historical free cash flow and net income."""
        metrics_list = self.api_client.get_financial_metrics(ticker, end_date)
        if not metrics_list:
            return None

        financial_line_items = self.api_client.search_line_items(ticker, end_date, ["freeCashFlow", "netIncome"])
        net_income = financial_line_items.get("netIncome")
        free_cash_flow = financial_line_items.get("freeCashFlow")

        metrics = metrics_list[0]  # Latest available data
        return {
            "pe_ratio": metrics.price_to_earnings_ratio,
            "pb_ratio": metrics.price_to_book_ratio,
            "roe": metrics.return_on_equity,
            "free_cash_flow": free_cash_flow,
            "net_income": net_income,
            "market_cap": self.api_client.get_market_cap(ticker, end_date),
            "growth_rate": metrics.earnings_growth or 5.0,
            "discount_rate": 10.0  # Buffett’s assumed discount rate
        }

    def calculate_intrinsic_value(self, fcf: float, growth_rate: float, discount_rate: float, years: int = 10) -> float:
        """Estimates intrinsic value using a Discounted Free Cash Flow model."""
        if fcf is None:
            return 0.0
        return sum(fcf * ((1 + growth_rate / 100) ** i) / ((1 + discount_rate / 100) ** i) for i in range(1, years + 1))

    def calculate_expected_return(self, roe: float, pb_ratio: float) -> float:
        """Estimates long-term return using Buffett’s formula: ROE / P/B Ratio."""
        if pb_ratio == 0:
            return 0.0
        return roe / pb_ratio

    def analyze_stock(self, ticker: str, end_date: str) -> Optional[AgentStateData]:
        """Applies Buffett’s principles to analyze a stock using valuation and safety margin criteria."""
        financials = self.get_financial_data(ticker, end_date)
        if not financials or not financials["market_cap"] or not financials["free_cash_flow"]:
            logger.warning(f"[{ticker}] Missing financial data for analysis.")
            return None

        intrinsic_value = self.calculate_intrinsic_value(financials["free_cash_flow"], financials["growth_rate"], financials["discount_rate"])
        margin_of_safety = (intrinsic_value - financials["market_cap"]) / financials["market_cap"]
        expected_return = self.calculate_expected_return(financials["roe"], financials["pb_ratio"])

        if margin_of_safety > 0.15 and expected_return > 10:
            signal = "Bullish"
        else:
            signal = "Neutral"

        reasoning = (
            f"Intrinsic Value: ${intrinsic_value:.2f}, Market Cap: ${financials['market_cap']:.2f}, "
            f"Margin of Safety: {margin_of_safety:.2%}, Expected Return: {expected_return:.2f}%, "
            f"P/E Ratio: {financials['pe_ratio']}, P/B Ratio: {financials['pb_ratio']}, ROE: {financials['roe']}%."
        )

        # Run LLM for enhanced investment reasoning
        final_decision = run_llm_analysis(ticker, reasoning)

        logger.info(f"[{ticker}] Buffett Analysis: {final_decision}")

        return AgentStateData(
            tickers=[ticker],
            start_date=end_date,
            end_date=end_date,
            ticker_analyses={ticker: {"investment_signal": final_decision, "reasoning": reasoning}},
        )
