# new_project/src/agents/risk_manager.py

import pandas as pd
from data.api_client import APIClient
from data.data_models import AgentStateData, Portfolio
from utils.logger import logger
from typing import Dict, Optional

class RiskManager:
    """Handles portfolio risk management based on portfolio value and position limits."""
    def __init__(self, portfolio: Dict):
        self.api_client = APIClient()
        self.portfolio = portfolio

    def manage_risk(self, ticker: str, start_date: str, end_date: str) -> Optional[AgentStateData]:
        price_data = self.api_client.get_prices(ticker, start_date, end_date)
        if not price_data or not price_data.prices:
            logger.warning(f"[{ticker}] No price data available for risk management.")
            return None
        df = pd.DataFrame([p.model_dump() for p in price_data.prices])
        df["time"] = pd.to_datetime(df["time"])
        df.set_index("time", inplace=True)
        current_price = df["close"].iloc[-1]
        current_shares = self.portfolio.get("positions", {}).get(ticker, {}).get("shares", 0)
        current_position_value = current_shares * current_price
        total_portfolio_value = self.portfolio["cash"] + sum(
            pos["shares"] * current_price for pos in self.portfolio.get("positions", {}).values()
        )
        position_limit = total_portfolio_value * 0.20
        remaining_position_limit = position_limit - current_position_value
        max_position_size = min(remaining_position_limit, self.portfolio["cash"])
        reasoning = (
            f"Total portfolio value: ${total_portfolio_value:.2f}, "
            f"Position limit (20%): ${position_limit:.2f}, "
            f"Current position value: ${current_position_value:.2f}, "
            f"Remaining limit: ${remaining_position_limit:.2f}, "
            f"Max position size: ${max_position_size:.2f}"
        )
        logger.info(f"[{ticker}] Risk Management: {reasoning}")
        return AgentStateData(
            tickers=[ticker],
            start_date=start_date,
            end_date=end_date,
            portfolio=Portfolio(positions={}, total_cash=0, portfolio_value=0),
            ticker_analyses={
                ticker: {
                    "remaining_position_limit": float(max_position_size),
                    "current_price": float(current_price),
                    "reasoning": reasoning
                }
            }
        )
