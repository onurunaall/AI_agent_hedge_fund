# src/data/data_models.py

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict


# ==================== Price Models ====================

class Price(BaseModel):
    """Represents stock price details (without ticker)."""
    time: str
    open: float
    close: float
    high: float
    low: float
    volume: int


class PriceResponse(BaseModel):
    """Represents stock price data including ticker."""
    ticker: str
    prices: List[Price]


# ==================== Financial Metrics ====================

class FinancialMetrics(BaseModel):
    """Represents a company's fundamental financial metrics."""
    ticker: str
    calendar_date: str
    report_period: str
    period: str
    currency: str
    market_cap: Optional[float] = None
    enterprise_value: Optional[float] = None
    price_to_earnings_ratio: Optional[float] = None
    price_to_book_ratio: Optional[float] = None
    price_to_sales_ratio: Optional[float] = None
    enterprise_value_to_ebitda_ratio: Optional[float] = None
    enterprise_value_to_revenue_ratio: Optional[float] = None
    free_cash_flow_yield: Optional[float] = None
    peg_ratio: Optional[float] = None
    gross_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    net_margin: Optional[float] = None
    return_on_equity: Optional[float] = None
    return_on_assets: Optional[float] = None
    return_on_invested_capital: Optional[float] = None
    asset_turnover: Optional[float] = None
    inventory_turnover: Optional[float] = None
    receivables_turnover: Optional[float] = None
    days_sales_outstanding: Optional[float] = None
    operating_cycle: Optional[float] = None
    working_capital_turnover: Optional[float] = None
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    cash_ratio: Optional[float] = None
    operating_cash_flow_ratio: Optional[float] = None
    debt_to_equity: Optional[float] = None
    debt_to_assets: Optional[float] = None
    interest_coverage: Optional[float] = None
    revenue_growth: Optional[float] = None
    earnings_growth: Optional[float] = None
    book_value_growth: Optional[float] = None
    earnings_per_share_growth: Optional[float] = None
    free_cash_flow_growth: Optional[float] = None
    operating_income_growth: Optional[float] = None
    ebitda_growth: Optional[float] = None
    payout_ratio: Optional[float] = None
    earnings_per_share: Optional[float] = None
    book_value_per_share: Optional[float] = None
    free_cash_flow_per_share: Optional[float] = None


class FinancialMetricsResponse(BaseModel):
    """Represents a response containing multiple financial metrics."""
    financial_metrics: List[FinancialMetrics]


# ==================== Line Items ====================

class LineItem(BaseModel):
    """Represents a financial line item (allows extra fields dynamically)."""
    ticker: str
    report_period: str
    period: str
    currency: str

    model_config = ConfigDict(extra="allow")


class LineItemResponse(BaseModel):
    """Represents a response containing multiple line items."""
    search_results: List[LineItem]


# ==================== Insider Trades ====================

class InsiderTrade(BaseModel):
    """Represents an insider trading transaction."""
    ticker: str
    issuer: Optional[str] = None
    name: Optional[str] = None
    title: Optional[str] = None
    is_board_director: Optional[bool] = None
    filing_date: str
    transaction_date: Optional[str] = None
    transaction_shares: Optional[float] = None  # Changed type
    transaction_price_per_share: Optional[float] = None
    transaction_value: Optional[float] = None
    shares_owned_before_transaction: Optional[float] = None
    shares_owned_after_transaction: Optional[float] = None
    security_title: Optional[str] = None


class InsiderTradeResponse(BaseModel):
    """Represents a response containing multiple insider trades."""
    insider_trades: List[InsiderTrade]


# ==================== Company News ====================

class CompanyNews(BaseModel):
    """Represents a news article related to a company."""
    ticker: str
    date: str
    title: str
    sentiment: str
    source: str
    author: Optional[str] = None
    url: Optional[str] = None


class CompanyNewsResponse(BaseModel):
    """Represents a response containing multiple company news articles."""
    news: List[CompanyNews]


# ==================== Additional Models ====================

class Position(BaseModel):
    """Represents stock holdings in a portfolio."""
    ticker: str
    shares: int = 0  # Changed type to int
    avg_cost: float
    cash: float = 0.0  # Restored field


class Portfolio(BaseModel):
    """Tracks stock positions, cash, and performance metrics."""
    positions: Dict[str, Position]
    total_cash: float  # Renamed from "cash"
    portfolio_value: float  # Renamed from "total_value"


class AnalystSignal(BaseModel):
    """Stores trading signals from AI agents."""
    signal: Optional[str] = None
    confidence: Optional[float] = None
    reasoning: Optional[str] = None
    max_position_size: Optional[float] = None  # Restored missing field


class TickerAnalysis(BaseModel):
    """Encapsulates per-ticker analysis."""
    ticker: str
    analyst_signals: Dict[str, AnalystSignal]  # Renamed from "signals"


class AgentStateData(BaseModel):
    """Maintains agent reasoning and metadata."""
    tickers: List[str]
    start_date: str  # Restored field
    end_date: str  # Restored field
    portfolio: Portfolio
    ticker_analyses: Dict[str, TickerAnalysis]  # Renamed from "analyst_signals"


class AgentStateMetadata(BaseModel):
    """Stores metadata related to agent execution."""
    show_reasoning: bool = False  # Replaced fields
    model_config = ConfigDict(extra="allow")  # Allow extra fields dynamically
