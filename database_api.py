from typing import List, Dict
from schema_objects import Portfolio, Coin


class Database:
    def __init__(self):
        pass

    def get_portfolio(self, portfolio_id: int) -> Portfolio:
        pass

    def create_portfolio(self, cash_balance: float) -> Portfolio:
        pass

    def update_portfolio(self, less_cash: float) -> Portfolio:
        pass

    # This call may need to be revised.
    def get_portfolio_holdings(self, portfolio_id: int) -> Dict[str, float]:
        pass

    def update_portfolio_holdings(self, portfolio_id: int, alternate_coin_id: str, change: float) -> None:
        pass

    # This call may also need to be revised.
    def get_coin_history(self, alternate_coin_id: str) -> List[str]:
        pass

    # Entire set of coin information is not needed yet, but may be in the future. Thus adding Coin obj.
    def add_coin_history(self, coin: Coin) -> None:
        pass
