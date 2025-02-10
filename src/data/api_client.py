# src/data/api_client.py

import os
import requests
import pandas as pd
from typing import List, Optional
from datetime import datetime
from data.cache import get_cache
from data.data_models import (
    Price, PriceResponse, FinancialMetrics, LineItem, LineItemResponse,
    InsiderTrade, InsiderTradeResponse, CompanyNews, CompanyNewsResponse
)
from utils.exceptions import APIError
from utils.logger import logger


class APIClient:
    """Handles API requests to fetch stock prices, financial metrics, insider trades, and company news."""

    BASE_URL = "https://api.financialdatasets.ai"

    def __init__(self):
        self.cache = get_cache()
        self.headers = {"X-API-KEY": os.getenv("API_KEY", "")}

    def _get(self, endpoint: str, params: dict) -> Optional[dict]:
        """Internal method to send GET requests to the API with error handling."""
        try:
            response = requests.get(f"{self.BASE_URL}{endpoint}", params=params, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API Request failed: {e}")
            raise APIError(f"API Request failed: {e}")

    def _post(self, endpoint: str, json_body: dict) -> Optional[dict]:
        """Internal method to send POST requests to the API with error handling."""
        try:
            response = requests.post(f"{self.BASE_URL}{endpoint}", json=json_body, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API Request failed: {e}")
            raise APIError(f"API Request failed: {e}")

    def get_prices(self, ticker: str, start_date: str, end_date: str) -> Optional[PriceResponse]:
        """Fetch historical stock prices, ensuring interval parameters match the original logic."""
        if cached := self.cache.get_prices(ticker):
            filtered_prices = sorted(
                [price for price in cached if start_date <= price["time"] <= end_date],
                key=lambda x: x["time"]
            )
            return PriceResponse(ticker=ticker, prices=[Price(**p) for p in filtered_prices])

        params = {
            "ticker": ticker,
            "start_date": start_date,
            "end_date": end_date,
            "interval": "day",
            "interval_multiplier": 1  # Restored missing parameters
        }

        data = self._get("/prices/", params)
        if data:
            price_objects = [Price(**item) for item in data]
            self.cache.set_prices(ticker, [p.model_dump() for p in price_objects])
            return PriceResponse(ticker=ticker, prices=price_objects)
        return None

    def get_financial_metrics(self, ticker: str, end_date: str, period: str = "annual", limit: int = 10) -> List[FinancialMetrics]:
        """Fetch financial metrics for a stock, ensuring correct filtering, sorting, and period inclusion."""
        if cached := self.cache.get_financial_metrics(ticker):
            filtered_metrics = sorted(
                [FinancialMetrics(**m) for m in cached if m["report_period"] <= end_date],
                key=lambda x: x.report_period,
                reverse=True
            )
            return filtered_metrics[:limit]

        params = {
            "ticker": ticker,
            "end_date": end_date,
            "period": period,
            "limit": limit
        }

        data = self._get("/financial-metrics/", params)
        if data:
            metrics = [FinancialMetrics(**item) for item in data]
            self.cache.set_financial_metrics(ticker, [m.model_dump() for m in metrics])
            return metrics
        return []

    def get_insider_trades(self, ticker: str, start_date: str, end_date: str, limit: int = 1000) -> InsiderTradeResponse:
        """Fetch insider trades with pagination, filtering, and sorting."""
        if cached := self.cache.get_insider_trades(ticker):
            filtered_trades = sorted(
                [InsiderTrade(**t) for t in cached if start_date <= t["filing_date"] <= end_date],
                key=lambda x: x.filing_date,
                reverse=True
            )
            return InsiderTradeResponse(insider_trades=filtered_trades)

        all_trades = []
        while True:
            params = {"ticker": ticker, "start_date": start_date, "end_date": end_date, "limit": limit}
            data = self._get("/insider-trades/", params)

            if not data:
                break

            trades = [InsiderTrade(**item) for item in data]
            all_trades.extend(trades)

            # Update end_date to the oldest trade found
            end_date = min(t.filing_date for t in trades)

            if len(trades) < limit:
                break  # Stop if no more results

        self.cache.set_insider_trades(ticker, [t.model_dump() for t in all_trades])
        return InsiderTradeResponse(insider_trades=all_trades)

    def get_company_news(self, ticker: str, start_date: str, end_date: str, limit: int = 1000) -> CompanyNewsResponse:
        """Fetch company news with pagination, filtering, and sorting."""
        if cached := self.cache.get_company_news(ticker):
            filtered_news = sorted(
                [CompanyNews(**n) for n in cached if start_date <= n["date"] <= end_date],
                key=lambda x: x.date,
                reverse=True
            )
            return CompanyNewsResponse(news=filtered_news)

        all_news = []
        while True:
            params = {"ticker": ticker, "start_date": start_date, "end_date": end_date, "limit": limit}
            data = self._get("/news/", params)

            if not data:
                break

            news_items = [CompanyNews(**item) for item in data]
            all_news.extend(news_items)

            # Update end_date to the oldest article found
            end_date = min(n.date for n in news_items)

            if len(news_items) < limit:
                break  # Stop if no more results

        self.cache.set_company_news(ticker, [n.model_dump() for n in all_news])
        return CompanyNewsResponse(news=all_news)

    def search_line_items(self, ticker: str, end_date: str) -> LineItemResponse:
        """Fetch financial line items using a POST request with a JSON body."""
        data = self._post("/financial-line-items/", {"ticker": ticker, "end_date": end_date})

        if data:
            return LineItemResponse(search_results=[LineItem(**item) for item in data])
        return LineItemResponse(search_results=[])

    def get_market_cap(self, ticker: str, end_date: str) -> Optional[float]:
        """Fetch market capitalization separately if needed."""
        metrics = self.get_financial_metrics(ticker, end_date, limit=1)
        return metrics[0].market_cap if metrics else None
