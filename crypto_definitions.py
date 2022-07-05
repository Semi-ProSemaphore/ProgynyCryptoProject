from dataclasses import dataclass


@dataclass
class Coin:
    id: str
    symbol: str
    name: str
    current_price: float
    date: str
