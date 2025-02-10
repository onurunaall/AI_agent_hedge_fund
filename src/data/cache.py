# src/data/cache.py

import threading
from typing import List, Dict, Optional

class DataCache:
    """In-memory cache system to store and retrieve API responses efficiently."""

    def __init__(self):
        """Initialize cache storage for different types of financial data with thread safety."""
        self._lock = threading.Lock()
        self._price_cache: Dict[str, List[Dict[str, any]]] = {}
        self._financial_metrics_cache: Dict[str, List[Dict[str, any]]] = {}
        self._line_items_cache: Dict[str, List[Dict[str, any]]] = {}
        self._insider_trades_cache: Dict[str, List[Dict[str, any]]] = {}
        self._company_news_cache: Dict[str, List[Dict[str, any]]] = {}

    def _merge_data(self, existing_data: Optional[List[Dict[str, any]]], new_data: List[Dict[str, any]], key_field: str) -> List[Dict[str, any]]:
        """Merges new data with existing cache to avoid duplicates based on a key field."""
        if not existing_data:
            return new_data

        existing_keys = {item[key_field] for item in existing_data}
        return existing_data + [item for item in new_data if item[key_field] not in existing_keys]

    def get_prices(self, ticker: str) -> Optional[List[Dict[str, any]]]:
        """Retrieve cached stock price data for a given ticker."""
        with self._lock:
            return self._price_cache.get(ticker)

    def set_prices(self, ticker: str, prices: List[Dict[str, any]]) -> None:
        """Store stock prices in the cache."""
        with self._lock:
            self._price_cache[ticker] = self._merge_data(self._price_cache.get(ticker), prices, "time")

    def get_financial_metrics(self, ticker: str) -> Optional[List[Dict[str, any]]]:
        """Retrieve cached financial metrics for a given ticker."""
        with self._lock:
            return self._financial_metrics_cache.get(ticker)

    def set_financial_metrics(self, ticker: str, metrics: List[Dict[str, any]]) -> None:
        """Store financial metrics in the cache."""
        with self._lock:
            self._financial_metrics_cache[ticker] = self._merge_data(
                self._financial_metrics_cache.get(ticker), metrics, "report_period"
            )

    def get_line_items(self, ticker: str) -> Optional[List[Dict[str, any]]]:
        """Retrieve cached financial line items for a given ticker."""
        with self._lock:
            return self._line_items_cache.get(ticker)

    def set_line_items(self, ticker: str, line_items: List[Dict[str, any]]) -> None:
        """Store financial line items in the cache."""
        with self._lock:
            self._line_items_cache[ticker] = self._merge_data(
                self._line_items_cache.get(ticker), line_items, "report_period"
            )

    def get_insider_trades(self, ticker: str) -> Optional[List[Dict[str, any]]]:
        """Retrieve cached insider trading data for a given ticker."""
        with self._lock:
            return self._insider_trades_cache.get(ticker)

    def set_insider_trades(self, ticker: str, trades: List[Dict[str, any]]) -> None:
        """Store insider trading data in the cache (Uses 'filing_date' as key)."""
        with self._lock:
            self._insider_trades_cache[ticker] = self._merge_data(
                self._insider_trades_cache.get(ticker), trades, "filing_date"
            )

    def get_company_news(self, ticker: str) -> Optional[List[Dict[str, any]]]:
        """Retrieve cached company news for a given ticker."""
        with self._lock:
            return self._company_news_cache.get(ticker)

    def set_company_news(self, ticker: str, news: List[Dict[str, any]]) -> None:
        """Store company news in the cache (Uses 'date' as key)."""
        with self._lock:
            self._company_news_cache[ticker] = self._merge_data(
                self._company_news_cache.get(ticker), news, "date"
            )

    def clear_cache(self) -> None:
        """Completely clears all cached data."""
        with self._lock:
            self._price_cache.clear()
            self._financial_metrics_cache.clear()
            self._line_items_cache.clear()
            self._insider_trades_cache.clear()
            self._company_news_cache.clear()


# Provide a global cache instance
_cache_instance = DataCache()

def get_cache() -> DataCache:
    """Returns the global cache instance."""
    return _cache_instance
