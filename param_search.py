import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any
import pandas as pd
import yfinance as yf
import multiprocessing as mp
import logging
import seaborn as sns

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class XStrategyBacktest:
    def __init__(
        self,
        data: pd.DataFrame,
        start_date: datetime,
        end_date: datetime,
        up_threshold: float = 0.8,
        down_threshold: float = 0.5,
    ):
        logger.info(
            f"Initializing XStrategyBacktest with start_date: {start_date}, end_date: {end_date}"
        )
        self.start_date = start_date
        self.end_date = end_date
        self.data = data.loc[
            start_date.replace(
                hour=9, minute=30, second=0, microsecond=0
            ) : end_date.replace(hour=16, minute=0, second=0, microsecond=0)
        ]
        self.position = 0
        self.base_price = self.data["Close"].iloc[0]
        self.entry_price = None
        self.trades = []
        self.pnl = 0
        self.pnls = []
        self.up_threshold = up_threshold
        self.down_threshold = down_threshold
        logger.info(f"Initialization complete. Base price: {self.base_price}")

    def on_tick(self, tick):
        current_price = tick["Close"]
        logger.debug(f"Processing tick at {tick.name}. Current price: {current_price}")

        if self.position == 0:
            self.base_price = max(current_price, self.base_price)
            logger.debug(f"No position. Updated base price: {self.base_price}")

        if self.position > 0:
            self.base_price = min(current_price, self.base_price)
            logger.debug(f"Long position. Updated base price: {self.base_price}")

        if self.position > 0 and current_price > self.base_price + self.up_threshold:
            logger.info(
                f"Selling at {current_price}, base price is {self.base_price}, previous position is {self.position}"
            )
            self.position = 0
            self.base_price = current_price
            self.trades.append(
                {"type": "sell", "price": current_price, "timestamp": tick.name}
            )
            self.pnl += current_price - self.entry_price
            logger.info(f"Trade executed. New PNL: {self.pnl}")
            self.entry_price = None

        if self.position <= 0 and current_price < self.base_price - self.down_threshold:
            logger.info(
                f"Buying at {current_price}, base price is {self.base_price}, previous position is {self.position}"
            )
            self.position = 1
            self.base_price = current_price
            self.trades.append(
                {"type": "buy", "price": current_price, "timestamp": tick.name}
            )
            # self.pnl += current_price - self.entry_price
            logger.info(f"Trade executed. New PNL: {self.pnl}")
            self.entry_price = current_price

    def run(self):
        logger.info("Starting backtest run")
        for _, row in self.data.iterrows():
            self.on_tick(row)
        logger.info(f"Backtest complete. Final PNL: {self.pnl}")

    def pnl_table(self):
        df = pd.DataFrame(self.trades)
        summary_table = (
            df.set_index("type")
            .loc["buy"]
            .reset_index()
            .merge(
                df.set_index("type").loc["sell"].reset_index(),
                left_index=True,
                right_index=True,
                suffixes=("_buy", "_sell"),
            )
        )
        summary_table["return"] = (
            summary_table["price_sell"] / summary_table["price_buy"] - 1
        )
        summary_table["cum_return"] = (1 + summary_table["return"]).cumprod()
        return summary_table


def get_data(ticker: str, days: int):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)  # Max 7 days for 5-minute data

    # Fetch the data
    data = yf.download(ticker, start=start_date, end=end_date, interval="5m")
    return data


# do parameter search on up_threshold and down_threshold using multiprocessing
def run_backtest(params):
    up_threshold, down_threshold, data = params
    backtest = XStrategyBacktest(
        data,
        data.index.min(),
        data.index.max(),
        up_threshold=up_threshold,
        down_threshold=down_threshold,
    )
    backtest.run()
    return {
        "up_threshold": up_threshold,
        "down_threshold": down_threshold,
        "cum_return": backtest.pnl_table()["cum_return"].iloc[-1],
    }


if __name__ == "__main__":
    up_thresholds = np.arange(0.1, 1, 0.1)
    down_thresholds = np.arange(0.1, 1, 0.1)
    data = get_data("FFIE", 35)
    params = [(round(up, 2), round(down, 2), data) for up in up_thresholds for down in down_thresholds]

    with mp.Pool(processes=mp.cpu_count()) as pool:
        search_results = pool.map(run_backtest, params)

    search_results_df = pd.DataFrame(search_results)
    # plot heatmap of the search results
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        search_results_df.pivot(
            index="up_threshold", columns="down_threshold", values="cum_return"
        ),
        annot=True,
        fmt=".2f",
        cmap="viridis",
    )
    plt.title("Heatmap of Search Results")
    plt.xlabel("Down Threshold")
    plt.ylabel("Up Threshold")
    # save the image
    plt.tight_layout()  # Adjust the plot to ensure everything fits without overlapping
    plt.savefig("search_results.png", dpi=300, bbox_inches="tight")  # Increase resolution and trim whitespace
    plt.close()  # Close the plot to free up memory
    search_results_df.to_csv("search_results.csv", index=False)
