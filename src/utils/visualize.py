# new_project/src/utils/visualize.py

import matplotlib.pyplot as plt
import pandas as pd
from typing import Dict, List

def save_graph_as_png(app, output_file_path: str) -> None:
    from langchain_core.runnables.graph import MermaidDrawMethod
    png_image = app.get_graph().draw_mermaid_png(draw_method=MermaidDrawMethod.API)
    file_path = output_file_path if output_file_path else "graph.png"
    with open(file_path, "wb") as f:
        f.write(png_image)

class AIVisualizer:
    """Handles visualization of AI trading signals and portfolio performance."""
    @staticmethod
    def plot_portfolio_performance(portfolio_values: List[Dict[str, float]]) -> None:
        if not portfolio_values:
            print("No portfolio data available for visualization.")
            return
        df = pd.DataFrame(portfolio_values).set_index("Date")
        plt.figure(figsize=(12, 6))
        plt.plot(df.index, df["Portfolio Value"], label="Portfolio Value", color="blue")
        plt.title("Portfolio Value Over Time")
        plt.xlabel("Date")
        plt.ylabel("Portfolio Value ($)")
        plt.legend()
        plt.grid(True)
        plt.show()

    @staticmethod
    def plot_ai_signals(ai_signals: Dict[str, Dict[str, str]]) -> None:
        if not ai_signals:
            print("No AI signal data available for visualization.")
            return
        df = pd.DataFrame(ai_signals).T
        df["Bullish"] = df["bullish_count"]
        df["Bearish"] = df["bearish_count"]
        df["Neutral"] = df["neutral_count"]
        df[["Bullish", "Bearish", "Neutral"]].plot(kind="bar", figsize=(12, 6), stacked=True, colormap="coolwarm")
        plt.title("AI Analyst Signal Distribution")
        plt.xlabel("Stock Tickers")
        plt.ylabel("Signal Counts")
        plt.legend()
        plt.grid(True)
        plt.show()
