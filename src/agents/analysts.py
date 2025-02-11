# new_project/src/agents/analyst.py

from agents.warren_buffet import WarrenBuffettStrategy
from agents.bill_ackman import BillAckmanStrategy
from agents.technicals import TechnicalAnalyzer
from llm.llm import run_llm_analysis
from utils.logger import logger
from typing import Dict

class AIAnalyst:
    """Manages multiple AI analysts and aggregates investment decisions."""
    def __init__(self):
        self.buffett = WarrenBuffettStrategy()
        self.ackman = BillAckmanStrategy()
        self.technical = TechnicalAnalyzer()
    
    def collect_signals(self, ticker: str, start_date: str, end_date: str) -> Dict[str, Dict[str, str]]:
        """Collects trading signals from multiple AI analysts."""
        signals = {}
        buffett_analysis = self.buffett.analyze_stock(ticker, end_date)
        if buffett_analysis:
            signals["Buffett"] = buffett_analysis.ticker_analyses[ticker]
        ackman_analysis = self.ackman.analyze_stock(ticker, end_date)
        if ackman_analysis:
            signals["Ackman"] = ackman_analysis.ticker_analyses[ticker]
        technical_analysis = self.technical.analyze_technical_indicators(ticker, start_date, end_date)
        if technical_analysis:
            signals["Technical"] = technical_analysis.ticker_analyses[ticker]
        return signals

    def aggregate_signals(self, signals: Dict[str, Dict[str, str]]) -> Dict[str, str]:
        """Aggregates multiple AI signals into a final trading decision with LLM-generated reasoning."""
        bullish_count = sum(1 for analysis in signals.values() if analysis.get("investment_signal", "").lower() == "bullish")
        bearish_count = sum(1 for analysis in signals.values() if analysis.get("investment_signal", "").lower() == "bearish")
        total_signals = len(signals)
        confidence = round(max(bullish_count, bearish_count) / total_signals, 2) * 100 if total_signals > 0 else 0
        if bullish_count > bearish_count:
            preliminary_signal = "bullish"
        elif bearish_count > bullish_count:
            preliminary_signal = "bearish"
        else:
            preliminary_signal = "neutral"
        
        llm_response = run_llm_analysis("Investment Decision", f"Aggregated signals: {signals}")
        final_signal = llm_response.get("decision", preliminary_signal).lower()
        reasoning = llm_response.get("justification", f"Preliminary signal based on counts: {preliminary_signal}")
        logger.info(f"Final aggregated signal: {final_signal} with {confidence}% confidence.")
        return {
            "final_signal": final_signal,
            "confidence": confidence,
            "reasoning": reasoning
        }
