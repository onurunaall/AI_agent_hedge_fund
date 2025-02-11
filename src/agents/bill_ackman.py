# new_project/src/agents/bill_ackman.py

import json
from typing import Dict, Optional, Any, List
from data.api_client import APIClient
from data.data_models import AgentStateData, Portfolio
from utils.logger import logger
from llm.llm import run_llm_analysis

class BillAckmanStrategy:
    """Implements Bill Ackman's activist investment strategy."""
    def __init__(self):
        self.api_client = APIClient()
    
    def get_financial_data(self, ticker: str, end_date: str) -> Optional[Dict[str, Any]]:
        metrics = self.api_client.get_financial_metrics(ticker, end_date, period="annual", limit=5)
        if not metrics:
            return None
        financial_line_items = self.api_client.search_line_items(ticker, end_date)
        market_cap = self.api_client.get_market_cap(ticker, end_date)
        return {
            "metrics": metrics,
            "financial_line_items": financial_line_items,
            "market_cap": market_cap,
        }
    
    def analyze_business_quality(self, metrics: List[Any], financial_line_items: List[Any]) -> Dict[str, Any]:
        score = 0
        details = []
        revenues = [getattr(item, "revenue", None) or item.get("revenue") for item in financial_line_items if (getattr(item, "revenue", None) is not None or item.get("revenue") is not None)]
        if len(revenues) >= 2:
            initial, final = revenues[0], revenues[-1]
            if initial and final and final > initial:
                growth_rate = (final - initial) / abs(initial)
                if growth_rate > 0.5:
                    score += 2
                    details.append(f"Revenue grew by {growth_rate*100:.1f}% over the period.")
                else:
                    score += 1
                    details.append(f"Revenue growth positive but under 50% ({growth_rate*100:.1f}%).")
            else:
                details.append("Revenue did not grow significantly.")
        else:
            details.append("Not enough revenue data for trend analysis.")
        
        op_margins = [getattr(item, "operating_margin", None) or item.get("operating_margin") for item in financial_line_items if (getattr(item, "operating_margin", None) is not None or item.get("operating_margin") is not None)]
        if op_margins:
            above_15 = sum(1 for m in op_margins if m > 0.15)
            if above_15 >= (len(op_margins) // 2 + 1):
                score += 2
                details.append("Operating margins exceeded 15% in most periods.")
            else:
                details.append("Operating margins not consistently above 15%.")
        else:
            details.append("No operating margin data available.")
        
        fcf_values = [getattr(item, "free_cash_flow", None) or item.get("free_cash_flow") for item in financial_line_items if (getattr(item, "free_cash_flow", None) is not None or item.get("free_cash_flow") is not None)]
        if fcf_values:
            positive_fcf = sum(1 for f in fcf_values if f > 0)
            if positive_fcf >= (len(fcf_values) // 2 + 1):
                score += 1
                details.append("Majority of periods show positive free cash flow.")
            else:
                details.append("Free cash flow not consistently positive.")
        else:
            details.append("No free cash flow data available.")
        
        latest = metrics[0]
        roe = getattr(latest, "return_on_equity", None) or latest.get("return_on_equity")
        if roe is not None:
            if roe > 0.15:
                score += 2
                details.append(f"High ROE of {roe:.1%} indicating competitive advantage.")
            else:
                details.append(f"ROE of {roe:.1%} is moderate.")
        else:
            details.append("ROE data not available.")
        return {"score": score, "details": "; ".join(details)}
    
    def analyze_financial_discipline(self, metrics: List[Any], financial_line_items: List[Any]) -> Dict[str, Any]:
        score = 0
        details = []
        de_list = [getattr(item, "debt_to_equity", None) or item.get("debt_to_equity") for item in financial_line_items if (getattr(item, "debt_to_equity", None) is not None or item.get("debt_to_equity") is not None)]
        if de_list:
            below_one = sum(1 for d in de_list if d < 1.0)
            if below_one >= (len(de_list) // 2 + 1):
                score += 2
                details.append("Debt-to-equity ratio below 1.0 in most periods.")
            else:
                details.append("Debt-to-equity ratio high in several periods.")
        else:
            ratios = []
            for item in financial_line_items:
                total_assets = getattr(item, "total_assets", None) or item.get("total_assets")
                total_liabilities = getattr(item, "total_liabilities", None) or item.get("total_liabilities")
                if total_assets and total_assets > 0 and total_liabilities is not None:
                    ratios.append(total_liabilities / total_assets)
            if ratios:
                below_half = sum(1 for r in ratios if r < 0.5)
                if below_half >= (len(ratios) // 2 + 1):
                    score += 2
                    details.append("Liabilities-to-assets ratio below 50% in majority of periods.")
                else:
                    details.append("Liabilities-to-assets ratio is high in many periods.")
            else:
                details.append("No leverage data available.")
        
        dividends = [getattr(item, "dividends_and_other_cash_distributions", None) or item.get("dividends_and_other_cash_distributions") for item in financial_line_items if (getattr(item, "dividends_and_other_cash_distributions", None) is not None or item.get("dividends_and_other_cash_distributions") is not None)]
        if dividends:
            paying_dividends = sum(1 for d in dividends if d < 0)
            if paying_dividends >= (len(dividends) // 2 + 1):
                score += 1
                details.append("Consistent capital return via dividends.")
            else:
                details.append("Dividends not consistently paid.")
        else:
            details.append("No dividend data available.")
        
        shares = [getattr(item, "outstanding_shares", None) or item.get("outstanding_shares") for item in financial_line_items if (getattr(item, "outstanding_shares", None) is not None or item.get("outstanding_shares") is not None)]
        if len(shares) >= 2:
            if shares[-1] < shares[0]:
                score += 1
                details.append("Decrease in outstanding shares observed (buybacks).")
            else:
                details.append("No decrease in outstanding shares.")
        else:
            details.append("Insufficient share count data.")
        
        return {"score": score, "details": "; ".join(details)}
    
    def analyze_valuation(self, financial_line_items: List[Any], market_cap: float) -> Dict[str, Any]:
        if not financial_line_items or market_cap is None:
            return {"score": 0, "details": "Insufficient data for valuation", "intrinsic_value": None}
        latest = financial_line_items[-1]
        fcf = getattr(latest, "free_cash_flow", None) or latest.get("free_cash_flow", 0)
        if not fcf or fcf <= 0:
            return {"score": 0, "details": f"No positive free cash flow for valuation; FCF = {fcf}", "intrinsic_value": None}
        growth_rate = 0.06
        discount_rate = 0.10
        terminal_multiple = 15
        projection_years = 5
        present_value = sum(fcf * ((1 + growth_rate) ** i) / ((1 + discount_rate) ** i) for i in range(1, projection_years + 1))
        terminal_value = (fcf * ((1 + growth_rate) ** projection_years) * terminal_multiple) / ((1 + discount_rate) ** projection_years)
        intrinsic_value = present_value + terminal_value
        margin_of_safety = (intrinsic_value - market_cap) / market_cap
        score = 0
        if margin_of_safety > 0.3:
            score += 3
        elif margin_of_safety > 0.1:
            score += 1
        details = f"Calculated intrinsic value: ~{intrinsic_value:,.2f}; Market cap: ~{market_cap:,.2f}; Margin of safety: {margin_of_safety:.2%}"
        return {"score": score, "details": details, "intrinsic_value": intrinsic_value, "margin_of_safety": margin_of_safety}
    
    def generate_ackman_output(self, ticker: str, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = (
            "You are a Bill Ackman AI agent, making investment decisions using his principles:\n"
            "1. Seek high-quality businesses with durable competitive advantages.\n"
            "2. Prioritize consistent free cash flow and growth potential.\n"
            "3. Ensure strong financial discipline and efficient capital allocation.\n"
            "4. Invest at a discount to intrinsic value for margin of safety.\n"
            "Based on the analysis data below, provide a trading signal in JSON format with keys:\n"
            '"signal" (bullish/bearish/neutral), "confidence" (0-100), and "reasoning".\n'
            f"Analysis Data for {ticker}:\n{json.dumps(analysis_data, indent=2)}"
        )
        return run_llm_analysis(prompt)
    
    def analyze_stock(self, ticker: str, end_date: str) -> Optional[AgentStateData]:
        data = self.get_financial_data(ticker, end_date)
        if not data or data["market_cap"] is None:
            logger.warning(f"[{ticker}] Missing key financial data for analysis.")
            return None
        metrics = data["metrics"]
        financial_line_items = data["financial_line_items"]
        market_cap = data["market_cap"]
        quality_analysis = self.analyze_business_quality(metrics, financial_line_items)
        discipline_analysis = self.analyze_financial_discipline(metrics, financial_line_items)
        valuation_analysis = self.analyze_valuation(financial_line_items, market_cap)
        total_score = quality_analysis["score"] + discipline_analysis["score"] + valuation_analysis["score"]
        max_possible_score = 15
        if total_score >= 0.7 * max_possible_score:
            preliminary_signal = "bullish"
        elif total_score <= 0.3 * max_possible_score:
            preliminary_signal = "bearish"
        else:
            preliminary_signal = "neutral"
        combined_reasoning = (
            f"Quality Analysis: {quality_analysis['details']}. "
            f"Financial Discipline Analysis: {discipline_analysis['details']}. "
            f"Valuation Analysis: {valuation_analysis['details']}. "
            f"Preliminary signal based on scores: {preliminary_signal}."
        )
        ackman_output = self.generate_ackman_output(ticker, {
            "quality_analysis": quality_analysis,
            "discipline_analysis": discipline_analysis,
            "valuation_analysis": valuation_analysis,
            "preliminary_signal": preliminary_signal,
            "total_score": total_score
        })
        final_signal = ackman_output.get("signal", preliminary_signal)
        confidence = ackman_output.get("confidence", 0.0)
        reasoning = ackman_output.get("reasoning", combined_reasoning)
        logger.info(f"[{ticker}] Ackman Analysis: Signal: {final_signal}, Confidence: {confidence}")
        return AgentStateData(
            tickers=[ticker],
            start_date=end_date,
            end_date=end_date,
            portfolio=Portfolio(positions={}, total_cash=0, portfolio_value=0),
            ticker_analyses={
                ticker: {
                    "investment_signal": final_signal,
                    "confidence": confidence,
                    "reasoning": reasoning,
                }
            }
        )
