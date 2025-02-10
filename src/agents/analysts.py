# src/agents/analysts.py

from agents.warren_buffett import WarrenBuffettStrategy
from agents.bill_ackman import BillAckmanStrategy
from agents.technicals import TechnicalAnalyzer
from utils.logger import logger
from typing import Dict, Optional


class AIAnalyst:
    """Manages multiple AI analysts and aggregates investment decisions."""

    def __init__(self):
        self.buffett = WarrenBuffettStrategy()
        self.ackman = BillAckmanStrategy()
        self.technical = TechnicalAnalyzer()

    def collect_signals(self, ticker: str, end_date: str) -> Dict[str, Dict[str, str]]:
        """Collects trading signals from multiple AI analysts."""
        signals = {}

        buffett_analysis = self.buffett.analyze_stock(ticker, end_date)
        if buffett_analysis:
            signals["Buffett"] = buffett_analysis.ticker_analyses[ticker]

        ackman_analysis = self.ackman.analyze_stock(ticker, end_date)
        if ackman_analysis:
            signals["Ackman"] = ackman_analysis.ticker_analyses[ticker]

        technical_analysis = self.technical.analyze_technical_indicators(ticker, "2020-01-01", end_date)
        if technical_analysis:
            signals["Technical"] = technical_analysis.ticker_analyses[ticker]

        return signals

    def aggregate_signals(self, signals: Dict[str, Dict[str, str]]) -> Dict[str, str]:
        """Aggregates multiple AI signals into a final trading decision."""
        bullish_count = sum(1 for analysis in signals.values() if analysis["investment_signal"] == "Bullish")
        neutral_count = sum(1 for analysis in signals.values() if analysis["investment_signal"] == "Neutral")
        bearish_count = sum(1 for analysis in signals.values() if analysis["investment_signal"] == "Bearish")

        if bullish_count > bearish_count:
            final_signal = "Bullish"
        elif bearish_count > bullish_count:
            final_signal = "Bearish"
        else:
            final_signal = "Neutral"

        logger.info(f"Final aggregated signal: {final_signal}")

        return {
            "final_signal": final_signal,
            "bullish_count": bullish_count,
            "neutral_count": neutral_count,
            "bearish_count": bearish_count
        }
