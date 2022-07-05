from crypto_definitions import Coin
from typing import List

from crypto_portfolio_exceptions import InsufficientFundsError


class Portfolio:
    EXAMPLE_STARTING_BALANCE = 1.00e6

    def __init__(self, portfolio_id: int = 0):
        pass

    def get_top_coins(self, how_many: int = 3) -> List[Coin]:
        pass

    def should_trade(self, coin: Coin, coin_av: float) -> bool:
        pass

    def get_coin_avg(self, coin_id: str) -> float:
        pass

    def make_trade(self, coin: Coin) -> None:
        pass

    def make_trade_decision(self) -> None:
        coins = self.get_top_coins()

        for coin in coins:
            coin_avg = self.get_coin_avg(coin.id)

            if self.should_trade(coin, coin_avg):
                try:
                    self.make_trade(coin)
                except InsufficientFundsError:
                    pass
