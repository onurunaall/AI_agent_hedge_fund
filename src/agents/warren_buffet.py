# new_project/src/agents/warren_buffet.py

from data.api_client import APIClient
from data.data_models import AgentStateData, Portfolio
from utils.logger import logger
from llm.llm import run_llm_analysis
from typing import Dict, Optional

class WarrenBuffettStrategy:
    """Implements Warren Buffett's fundamental value investing principles."""
    def __init__(self):
        self.api_client = APIClient()
    
    def get_financial_data(self, ticker: str, end_date: str) -> Optional[Dict[str, any]]:
        metrics_list = self.api_client.get_financial_metrics(ticker, end_date, period="ttm", limit=5)
        if not metrics_list:
            return None
        # Fetch line items (using the same list as in old project)
        line_items = self.api_client.search_line_items(ticker, end_date)
        market_cap = self.api_client.get_market_cap(ticker, end_date)
        return {
            "metrics": metrics_list,
            "line_items": line_items,
            "market_cap": market_cap,
        }
    
    def calculate_intrinsic_value(self, line_items: list, metrics) -> float:
        # Use a simple DCF model based on the latest free cash flow
        latest = line_items[-1]
        fcf = getattr(latest, "free_cash_flow", None) or latest.get("free_cash_flow", 0)
        if not fcf or fcf <= 0:
            return 0.0
        growth_rate = 0.06
        discount_rate = 0.10
        terminal_multiple = 15
        projection_years = 5
        present_value = sum(fcf * ((1 + growth_rate) ** i) / ((1 + discount_rate) ** i) for i in range(1, projection_years + 1))
        terminal_value = (fcf * ((1 + growth_rate) ** projection_years) * terminal_multiple) / ((1 + discount_rate) ** projection_years)
        intrinsic_value = present_value + terminal_value
        return intrinsic_value
    
    def analyze_stock(self, ticker: str, end_date: str) -> Optional[AgentStateData]:
        data = self.get_financial_data(ticker, end_date)
        if not data or data["market_cap"] is None:
            logger.warning(f"[{ticker}] Missing financial data for analysis.")
            return None
        metrics = data["metrics"]
        line_items = data["line_items"]
        market_cap = data["market_cap"]
        intrinsic_value = self.calculate_intrinsic_value(line_items, metrics)
        margin_of_safety = (intrinsic_value - market_cap) / market_cap if market_cap else 0
        # Basic quality check: use ROE and debt-to-equity from the latest metrics
        quality_score = 0
        roe = getattr(metrics[0], "return_on_equity", None) or metrics[0].get("return_on_equity", 0)
        if roe > 0.15:
            quality_score += 2
        debt_to_equity = getattr(metrics[0], "debt_to_equity", None) or metrics[0].get("debt_to_equity", 1)
        if debt_to_equity < 0.5:
            quality_score += 2
        op_margin = getattr(metrics[0], "operating_margin", None) or metrics[0].get("operating_margin", 0)
        if op_margin > 0.15:
            quality_score += 2
        if quality_score >= 4 and margin_of_safety > 0.15:
            preliminary_signal = "bullish"
        else:
            preliminary_signal = "neutral"
        reasoning = (
            f"Intrinsic Value: ${intrinsic_value:,.2f}, Market Cap: ${market_cap:,.2f}, "
            f"Margin of Safety: {margin_of_safety:.2%}, Quality Score: {quality_score}."
        )
        llm_response = run_llm_analysis(ticker, reasoning)
        final_signal = llm_response.get("decision", preliminary_signal).lower()
        confidence = llm_response.get("confidence", 0.0)
        justification = llm_response.get("justification", reasoning)
        logger.info(f"[{ticker}] Buffett Analysis: Signal: {final_signal}, Confidence: {confidence}")
        return AgentStateData(
            tickers=[ticker],
            start_date=end_date,
            end_date=end_date,
            portfolio=Portfolio(positions={}, total_cash=0, portfolio_value=0),
            ticker_analyses={
                ticker: {
                    "investment_signal": final_signal,
                    "confidence": confidence,
                    "reasoning": justification,
                }
            }
        )
