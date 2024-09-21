import yfinance as yf
from datetime import datetime, timedelta
from alpaca.data.live import StockDataStream
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.enums import AssetClass
import asyncio
import os


def get_backtest_data(ticker: str, days: int, frequency: str = "5m"):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)  # Max 7 days for 5-minute data

    # Fetch the data
    data = yf.download(ticker, start=start_date, end=end_date, interval=frequency)
    return data


# Alpaca API credentials
API_KEY = os.environ.get("ALPACA_API_KEY")
SECRET_KEY = os.environ.get("ALPACA_SECRET_KEY")
# Use 'https://paper-api.alpaca.markets' for paper trading
BASE_URL = "https://paper-api.alpaca.markets"

async def main():
    # Initialize the trading client
    trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True)

    # Initialize the data stream
    stock_stream = StockDataStream(API_KEY, SECRET_KEY)

    # Function to handle incoming quote data
    async def quote_handler(quote):
        print(f"Quote for {quote.symbol}: Bid: ${quote.bid_price}, Ask: ${quote.ask_price}")

    # Choose a stock symbol (e.g., 'AAPL' for Apple Inc.)
    symbol = "AAPL"

    # Subscribe to the quote stream for the chosen symbol
    stock_stream.subscribe_quotes(quote_handler, symbol)

    # Connect to the stream
    await stock_stream.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stream interrupted. Exiting...")
