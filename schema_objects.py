from dataclasses import dataclass


@dataclass
class Portfolio:
    id: int
    cash_balance: float


@dataclass
class Coin:
    id: str
    symbol: str
    name: str
    current_price: float
    date: str
