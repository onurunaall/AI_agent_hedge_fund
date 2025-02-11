# AI Hedge Fund Backtesting System
This project is an AI-powered hedge fund backtesting system. It's not the most exciting README you'll ever read, but here it is.

## Overview
A collection of modules that:

Fetch and cache financial data (prices, metrics, news, etc.)
Analyze stocks using multiple strategies (Bill Ackman, Warren Buffett, Fundamentals, Sentiment, Risk Management, Technicals)
Simulate trading and backtest performance
Interact with an LLM for investment insights
Visualize portfolio performance and signals

## Installation
Clone the repo.
Create and activate a virtual environment.
Run pip install -r requirements.txt.
Set up your API keys in a .env file.

## Usage
Run the main script with required parameters:
python src/main.py --tickers "AAPL,MSFT" --start-date "2022-01-01" --end-date "2022-12-31" --initial-capital 100000
You’ll be prompted to select analysts via the terminal. Follow the on-screen instructions.

## Project Structure
### src/backtester.py – Backtesting engine for simulating trades.
#### src/agents/ – Contains all the strategy modules (Ackman, Buffett, Fundamentals, Risk Management, Sentiment, etc.).
src/data/ – API client, cache, data models, and global state management.
src/llm/ – LLM integration (simulated response, can be replaced with real API calls).
src/utils/ – Utilities for display, progress tracking, and visualization.
src/main.py – Entry point for running the backtest.

This project is designed to mirror the logic and functionality of a previous system. Some parts are simplified, but overall it should function identically.
