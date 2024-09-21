import pandas as pd
from abc import ABC, abstractmethod
from typing import Optional
from utils.logger import Logger
from dataclasses import dataclass

logger = Logger("strategy")



@dataclass
class Order:
    type: str
    price: float
    timestamp: pd.Timestamp


class Strategy(ABC):
    @abstractmethod
    def on_tick(self, tick: pd.Series, position: int):
        pass


class XStrategy(Strategy):
    def __init__(self, base_price: float, up_threshold: float = 0.8, down_threshold: float = 0.5):
        """
        XStrategy class implements a trading strategy based on price thresholds.

        This strategy monitors the current price in relation to a base price and
        generates buy or sell orders when certain thresholds are crossed.

        Attributes:
            up_threshold (float): The threshold above the base price for selling.
            down_threshold (float): The threshold below the base price for buying.
            base_price (float): The reference price for making trading decisions.
            entry_price (float): The price at which the current position was entered.

        Args:
            base_price (float): Initial base price for the strategy.
            up_threshold (float, optional): Threshold for selling. Defaults to 0.8.
            down_threshold (float, optional): Threshold for buying. Defaults to 0.5.
        """
        self.up_threshold = up_threshold
        self.down_threshold = down_threshold
        self.base_price = base_price
        self.entry_price = None

    def on_tick(self, tick: pd.Series, position: int, slippage: float = 0.0) -> Optional[Order]:
        current_price = tick["Close"]
        logger.info(f"Processing tick at {tick.name}. Current price: {current_price}")
        
        trade = None
        if position == 0:
            self.base_price = max(current_price, self.base_price)
            logger.info(f"No position. Updated base price: {self.base_price}")

        if position > 0:
            self.base_price = min(current_price, self.base_price)
            logger.info(f"Long position. Updated base price: {self.base_price}")
        if position > 0 and current_price > self.base_price + self.up_threshold:
            logger.info(
                f"Selling at {current_price}, base price is {self.base_price}, previous position is {position}"
            )
            self.base_price = current_price
            trade = Order(
                type="sell",
                price=current_price * (1 - slippage),
                timestamp=tick.name,
            )
            self.entry_price = None

        if position <= 0 and current_price < self.base_price - self.down_threshold:
            logger.info(
                f"Buying at {current_price}, base price is {self.base_price}, previous position is {position}"
            )
            self.base_price = current_price
            trade = Order(
                type="buy",
                price=current_price * (1 + slippage),
                timestamp=tick.name,
            )
            self.entry_price = current_price
        return trade
