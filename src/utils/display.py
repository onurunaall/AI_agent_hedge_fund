# new_project/src/utils/display.py

import matplotlib.pyplot as plt
import pandas as pd
from colorama import Fore, Style
from typing import List, Dict

class BacktestVisualizer:
    """Handles backtest result visualization and reporting."""
    @staticmethod
    def plot_portfolio_value(portfolio_values: List[Dict[str, float]]) -> None:
        df = pd.DataFrame(portfolio_values).set_index("Date")
        plt.figure(figsize=(12, 6))
        plt.plot(df.index, df["Portfolio Value"], color="blue", linewidth=2)
        plt.title("Portfolio Value Over Time")
        plt.xlabel("Date")
        plt.ylabel("Portfolio Value ($)")
        plt.grid(True)
        plt.show()

    @staticmethod
    def print_performance_summary(sharpe_ratio: float, max_drawdown: float) -> None:
        print(f"\n{Fore.WHITE}{Style.BRIGHT}BACKTEST PERFORMANCE SUMMARY:{Style.RESET_ALL}")
        print(f"Sharpe Ratio: {Fore.YELLOW}{sharpe_ratio:.2f}{Style.RESET_ALL}")
        print(f"Maximum Drawdown: {Fore.RED}{max_drawdown:.2f}%{Style.RESET_ALL}")

    @staticmethod
    def print_trade_log(trade_log: List[Dict[str, str]]) -> None:
        print(f"\n{Fore.WHITE}{Style.BRIGHT}TRADE LOG:{Style.RESET_ALL}")
        for trade in trade_log:
            action_color = Fore.GREEN if trade["action"].upper() == "BUY" else Fore.RED
            print(
                f"{trade['date']} | {trade['ticker']} | {action_color}{trade['action'].upper()}{Style.RESET_ALL} | "
                f"Shares: {trade['shares']} @ ${trade['price']:.2f}"
            )
