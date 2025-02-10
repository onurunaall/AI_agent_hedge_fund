# src/agents/sentiment.py

from data.api_client import APIClient
from utils.logger import logger
from utils.progress import ProgressTracker
from llm.llm import run_llm_analysis
from textblob import TextBlob
from typing import Dict, List, Optional


class SentimentAnalyzer:
    """Analyzes sentiment of company news, insider trading activity, and sector trends."""

    def __init__(self):
        self.api_client = APIClient()
        self.progress_tracker = ProgressTracker()

    def analyze_sentiment(self, text: str) -> float:
        """Performs sentiment analysis on a given text using TextBlob."""
        if not text:
            return 0.0
        return TextBlob(text).sentiment.polarity  # Ranges from -1 (negative) to +1 (positive)

    def get_news_sentiment(self, ticker: str, start_date: str, end_date: str) -> Dict[str, float]:
        """Fetches company news and calculates sentiment scores."""
        news_data = self.api_client.get_company_news(ticker, start_date, end_date)

        if not news_data or not news_data.news:
            return {"average_sentiment": 0.0, "articles_analyzed": 0}

        sentiments = [self.analyze_sentiment(article.title) for article in news_data.news]
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0

        return {
            "average_sentiment": avg_sentiment,
            "articles_analyzed": len(sentiments)
        }

    def get_insider_sentiment(self, ticker: str, start_date: str, end_date: str) -> float:
        """Analyzes insider trading activity for sentiment scoring."""
        insider_data = self.api_client.get_insider_trades(ticker, start_date, end_date)

        if not insider_data or not insider_data.insider_trades:
            return 0.0

        bullish_transactions = sum(1 for trade in insider_data.insider_trades if trade.transaction_shares > 0)
        bearish_transactions = sum(1 for trade in insider_data.insider_trades if trade.transaction_shares < 0)

        total_transactions = bullish_transactions + bearish_transactions
        if total_transactions == 0:
            return 0.0

        sentiment_score = (bullish_transactions - bearish_transactions) / total_transactions
        return sentiment_score

    def get_sector_sentiment(self, sector: str, start_date: str, end_date: str) -> float:
        """Fetches news for an entire sector and computes an aggregate sentiment score."""
        sector_news = self.api_client.get_sector_news(sector, start_date, end_date)

        if not sector_news or not sector_news.news:
            return 0.0

        sentiments = [self.analyze_sentiment(article.title) for article in sector_news.news]
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0
        return avg_sentiment

    def get_weighted_sentiment(self, ticker: str, sector: str, start_date: str, end_date: str) -> Dict[str, float]:
        """Combines news sentiment, insider trading sentiment, and sector sentiment into a weighted score."""
        news_sentiment = self.get_news_sentiment(ticker, start_date, end_date)
        insider_sentiment = self.get_insider_sentiment(ticker, start_date, end_date)
        sector_sentiment = self.get_sector_sentiment(sector, start_date, end_date)

        weighted_score = (0.6 * news_sentiment["average_sentiment"]) + (0.2 * insider_sentiment) + (0.2 * sector_sentiment)

        # Use LLM for enhanced interpretation of sentiment score
        reasoning = run_llm_analysis(
            "Sentiment Analysis",
            f"News Sentiment: {news_sentiment['average_sentiment']}, "
            f"Insider Sentiment: {insider_sentiment}, "
            f"Sector Sentiment: {sector_sentiment}."
        )

        self.progress_tracker.update_progress(ticker, "Sentiment Analysis Complete")
        logger.info(f"[{ticker}] Sentiment Score: {weighted_score:.2f}")

        return {
            "weighted_sentiment": weighted_score,
            "news_sentiment": news_sentiment["average_sentiment"],
            "insider_sentiment": insider_sentiment,
            "sector_sentiment": sector_sentiment,
            "articles_analyzed": news_sentiment["articles_analyzed"],
            "reasoning": reasoning
        }
