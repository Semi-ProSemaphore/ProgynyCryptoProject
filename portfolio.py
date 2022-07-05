from crypto_definitions import Coin
from crypto_portfolio_exceptions import InsufficientFundsError
from typing import List

import crypto_api


class Portfolio:
    EXAMPLE_STARTING_BALANCE = 1.00e6

    def __init__(self, portfolio_id: int = 0):
        pass

    '''
    Crypto api's call gives us coins in order of market cap. If that changes, so should this function.
    '''
    @staticmethod
    def _get_top_coins(how_many: int = 3) -> List[Coin]:
        coins = crypto_api.get_coins()
        how_many = len(coins) if how_many > len(coins) else how_many
        coins = coins[:how_many]

        return [Coin(id=coin["id"],
                     symbol=coin["symbol"],
                     name=coin["name"],
                     current_price=coin["current_price"],
                     date=coin["date"])
                for coin in coins]

    @staticmethod
    def _should_trade(coin: Coin, coin_avg: float) -> bool:
        if coin.current_price < coin_avg:
            return True
        return False

    '''
    Note: Averages are based on midnight GMT timezone saves. If there are large swings in the price (as there are), 
          this will become very inaccurate. There are a lot of assumptions inherent in averages in general. To discuss.
          
          Another note: crypto API's call actually does a 9-day request, along with the current value. 
          That is a problem because the specs in README request for a 10-day average.
          If we'd like actual 10-day average, the function in crypto_api should be changed. Unsure if I can do so
          for purposes of this test, so leaving alone for now.
    '''
    @staticmethod
    def _get_coin_avg(coin_id: str) -> float:
        prices = crypto_api.get_coin_price_history(coin_id)
        coin_avg = sum([price[0] for price in prices])/10  # Not performant, but quick and easy to understand.

        return coin_avg

    def make_trade(self, coin: Coin) -> None:
        pass

    def make_trade_decision(self) -> None:
        coins = self._get_top_coins()

        for coin in coins:
            coin_avg = self._get_coin_avg(coin.id)

            if self._should_trade(coin, coin_avg):
                try:
                    self.make_trade(coin)
                except InsufficientFundsError:
                    pass
