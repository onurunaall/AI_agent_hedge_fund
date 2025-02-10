from data.api_client import APIClient
from data.data_models import AgentStateData
from utils.logger import logger
from utils.progress import progress
from typing import Optional


class FundamentalAnalyzer:
    """Analyzes fundamental metrics of a stock using multi-factor scoring."""

    def __init__(self):
        self.api_client = APIClient()

    def _analyze_profitability(self, metrics) -> dict:
        roe = getattr(metrics, "return_on_equity", None)
        net_margin = getattr(metrics, "net_margin", None)
        op_margin = getattr(metrics, "operating_margin", None)

        score = 0
        if roe is not None and roe > 0.15:
            score += 1
        if net_margin is not None and net_margin > 0.20:
            score += 1
        if op_margin is not None and op_margin > 0.15:
            score += 1

        if score >= 2:
            signal = "bullish"
        elif score == 0:
            signal = "bearish"
        else:
            signal = "neutral"

        details = (
            (f"ROE: {roe:.2%}" if roe is not None else "ROE: N/A") + ", " +
            (f"Net Margin: {net_margin:.2%}" if net_margin is not None else "Net Margin: N/A") + ", " +
            (f"Op Margin: {op_margin:.2%}" if op_margin is not None else "Op Margin: N/A")
        )
        return {"signal": signal, "details": details}

    def _analyze_growth(self, metrics) -> dict:
        revenue_growth = getattr(metrics, "revenue_growth", None)
        earnings_growth = getattr(metrics, "earnings_growth", None)
        book_value_growth = getattr(metrics, "book_value_growth", None)

        score = 0
        if revenue_growth is not None and revenue_growth > 0.10:
            score += 1
        if earnings_growth is not None and earnings_growth > 0.10:
            score += 1
        if book_value_growth is not None and book_value_growth > 0.10:
            score += 1

        if score >= 2:
            signal = "bullish"
        elif score == 0:
            signal = "bearish"
        else:
            signal = "neutral"

        details = (
            (f"Revenue Growth: {revenue_growth:.2%}" if revenue_growth is not None else "Revenue Growth: N/A") + ", " +
            (f"Earnings Growth: {earnings_growth:.2%}" if earnings_growth is not None else "Earnings Growth: N/A")
        )
        return {"signal": signal, "details": details}

    def _analyze_health(self, metrics) -> dict:
        current_ratio = getattr(metrics, "current_ratio", None)
        debt_to_equity = getattr(metrics, "debt_to_equity", None)
        fcf_per_share = getattr(metrics, "free_cash_flow_per_share", None)
        eps = getattr(metrics, "earnings_per_share", None)

        score = 0
        if current_ratio is not None and current_ratio > 1.5:
            score += 1
        if debt_to_equity is not None and debt_to_equity < 0.5:
            score += 1
        if (fcf_per_share is not None and eps is not None and fcf_per_share > eps * 0.8):
            score += 1

        if score >= 2:
            signal = "bullish"
        elif score == 0:
            signal = "bearish"
        else:
            signal = "neutral"

        details = (
            (f"Current Ratio: {current_ratio:.2f}" if current_ratio is not None else "Current Ratio: N/A") + ", " +
            (f"D/E: {debt_to_equity:.2f}" if debt_to_equity is not None else "D/E: N/A")
        )
        return {"signal": signal, "details": details}

    def _analyze_valuation(self, metrics) -> dict:
        pe_ratio = getattr(metrics, "price_to_earnings_ratio", None)
        pb_ratio = getattr(metrics, "price_to_book_ratio", None)
        ps_ratio = getattr(metrics, "price_to_sales_ratio", None)

        score = 0
        if pe_ratio is not None and pe_ratio > 25:
            score += 1
        if pb_ratio is not None and pb_ratio > 3:
            score += 1
        if ps_ratio is not None and ps_ratio > 5:
            score += 1

        if score >= 2:
            signal = "bullish"
        elif score == 0:
            signal = "bearish"
        else:
            signal = "neutral"

        details = (
            (f"P/E: {pe_ratio:.2f}" if pe_ratio is not None else "P/E: N/A") + ", " +
            (f"P/B: {pb_ratio:.2f}" if pb_ratio is not None else "P/B: N/A") + ", " +
            (f"P/S: {ps_ratio:.2f}" if ps_ratio is not None else "P/S: N/A")
        )
        return {"signal": signal, "details": details}

    def analyze_financials(self, ticker: str, end_date: str) -> Optional[AgentStateData]:
        progress.update_status("fundamentals_agent", ticker, "Fetching financial data")
        metrics_list = self.api_client.get_financial_metrics(ticker, end_date, period="ttm", limit=10)
        if not metrics_list:
            progress.update_status("fundamentals_agent", ticker, "Failed: No financial metrics found")
            return None

        metrics = metrics_list[0]

        progress.update_status("fundamentals_agent", ticker, "Analyzing profitability")
        profitability = self._analyze_profitability(metrics)

        progress.update_status("fundamentals_agent", ticker, "Analyzing growth")
        growth = self._analyze_growth(metrics)

        progress.update_status("fundamentals_agent", ticker, "Analyzing financial health")
        health = self._analyze_health(metrics)

        progress.update_status("fundamentals_agent", ticker, "Analyzing valuation ratios")
        valuation = self._analyze_valuation(metrics)

        signals = [
            profitability["signal"],
            growth["signal"],
            health["signal"],
            valuation["signal"],
        ]
        bullish = signals.count("bullish")
        bearish = signals.count("bearish")

        if bullish > bearish:
            overall_signal = "bullish"
        elif bearish > bullish:
            overall_signal = "bearish"
        else:
            overall_signal = "neutral"

        confidence = round(max(bullish, bearish) / 4, 2) * 100

        reasoning = {
            "profitability_signal": profitability,
            "growth_signal": growth,
            "financial_health_signal": health,
            "price_ratios_signal": valuation,
        }

        progress.update_status("fundamentals_agent", ticker, "Calculating final signal")
        logger.info(f"[{ticker}] Fundamental Analysis Signal: {overall_signal}, Confidence: {confidence}%")
        progress.update_status("fundamentals_agent", ticker, "Done")

        return AgentStateData(
            tickers=[ticker],
            start_date=end_date,
            end_date=end_date,
            ticker_analyses={
                ticker: {
                    "signal": overall_signal,
                    "confidence": confidence,
                    "reasoning": reasoning,
                }
            }
        )
