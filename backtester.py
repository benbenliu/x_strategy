import pandas as pd
from strategy import Strategy, Order
from dataclasses import asdict


class Backtester:
    def __init__(self, strategy: Strategy, data: pd.DataFrame):
        self.strategy = strategy
        self.data = data
        self.pnl = 0
        self.position = 0
        self.trades = []

    def on_order(self, order: Order):
        if order.type == "buy":
            self.position += 1
        elif order.type == "sell":
            self.position -= 1
        self.trades.append(order)

    def run(self):
        for _, row in self.data.iterrows():
            order = self.strategy.on_tick(row, self.position)
            if order is not None:
                self.on_order(order)

    def pnl_table(self):
        df = pd.DataFrame([asdict(trade) for trade in self.trades])
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


if __name__ == "__main__":
    from data import get_backtest_data
    from strategy import XStrategy

    data = get_backtest_data("FFIE", 35, "5m")
    strategy = XStrategy(
        base_price=data.iloc[0]["Close"], up_threshold=0.3, down_threshold=0.7
    )
    backtester = Backtester(strategy, data)
    backtester.run()
    print(backtester.pnl_table())
