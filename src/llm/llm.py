# src/llm/llm.py

from utils.logger import logger
from typing import Dict


class LLMAnalyzer:
    """Handles interaction with an LLM to generate investment insights."""

    def __init__(self, model_name: str = "gpt-4"):
        self.model_name = model_name

    def generate_prompt(self, ticker: str, reasoning: str) -> str:
        """Formats the LLM prompt with structured financial analysis data."""
        return (
            f"Analyze the following stock: {ticker}.\n"
            f"Based on the provided data, provide an investment recommendation "
            f"with reasoning:\n\n{reasoning}\n\n"
            "Output format:\n"
            "- Decision: Bullish, Neutral, or Bearish\n"
            "- Confidence: A percentage between 0-100%\n"
            "- Justification: Explanation of the reasoning."
        )

    def run_llm_analysis(self, ticker: str, reasoning: str) -> Dict[str, str]:
        """Simulates an LLM response (this would call an API in production)."""
        prompt = self.generate_prompt(ticker, reasoning)
        logger.info(f"LLM Prompt Generated for {ticker}: {prompt}")

        # Simulated AI response (replace with actual API call in production)
        simulated_response = {
            "decision": "Bullish",
            "confidence": "85%",
            "justification": "The stock is undervalued based on its intrinsic value and growth potential."
        }

        return simulated_response
