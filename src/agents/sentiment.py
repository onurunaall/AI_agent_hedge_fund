# new_project/src/agents/sentiment.py

from data.api_client import APIClient
from utils.logger import logger
from utils.progress import ProgressTracker
from typing import Dict
import numpy as np

class SentimentAnalyzer:
    """Analyzes sentiment of company news and insider trading activity to generate trading signals."""
    def __init__(self):
        self.api_client = APIClient()
        self.progress_tracker = ProgressTracker()
    
    def get_insider_signals(self, ticker: str, start_date: str, end_date: str) -> Dict[str, int]:
        insider_data = self.api_client.get_insider_trades(ticker, start_date, end_date)
        bullish = 0
        bearish = 0
        if insider_data and insider_data.insider_trades:
            for trade in insider_data.insider_trades:
                if trade.transaction_shares and trade.transaction_shares > 0:
                    bullish += 1
                elif trade.transaction_shares and trade.transaction_shares < 0:
                    bearish += 1
        return {"bullish": bullish, "bearish": bearish, "total": bullish + bearish}
    
    def get_news_signals(self, ticker: str, start_date: str, end_date: str) -> Dict[str, int]:
        news_data = self.api_client.get_company_news(ticker, start_date, end_date)
        bullish = 0
        bearish = 0
        neutral = 0
        if news_data and news_data.news:
            for article in news_data.news:
                sentiment = article.sentiment.lower() if article.sentiment else "neutral"
                if sentiment == "negative":
                    bearish += 1
                elif sentiment == "positive":
                    bullish += 1
                else:
                    neutral += 1
        return {"bullish": bullish, "bearish": bearish, "neutral": neutral, "total": bullish + bearish + neutral}
    
    def analyze_sentiment(self, ticker: str, start_date: str, end_date: str) -> Dict[str, float]:
        insider = self.get_insider_signals(ticker, start_date, end_date)
        news = self.get_news_signals(ticker, start_date, end_date)
        insider_weight = 0.3
        news_weight = 0.7
        weighted_bullish = insider.get("bullish", 0) * insider_weight + news.get("bullish", 0) * news_weight
        weighted_bearish = insider.get("bearish", 0) * insider_weight + news.get("bearish", 0) * news_weight
        if weighted_bullish > weighted_bearish:
            overall_signal = "bullish"
        elif weighted_bearish > weighted_bullish:
            overall_signal = "bearish"
        else:
            overall_signal = "neutral"
        total_weight = insider.get("total", 0) * insider_weight + news.get("total", 0) * news_weight
        confidence = round((max(weighted_bullish, weighted_bearish) / total_weight) * 100, 2) if total_weight > 0 else 0.0
        reasoning = f"Weighted Bullish: {weighted_bullish:.1f}, Weighted Bearish: {weighted_bearish:.1f} based on insider and news data."
        self.progress_tracker.update_status(ticker, "Sentiment Analysis Complete")
        logger.info(f"[{ticker}] Sentiment Analysis: Signal: {overall_signal}, Confidence: {confidence}%")
        return {
            "signal": overall_signal,
            "confidence": confidence,
            "reasoning": reasoning
        }
