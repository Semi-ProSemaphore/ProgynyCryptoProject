from typing import List, Dict
from schema_objects import Portfolio, Coin
from dotenv import load_dotenv
import os
import pymysql


class Database:
    def __init__(self):
        load_dotenv()

        self.conn = pymysql.connect(host='db',
                                    user=os.getenv('DB_USERNAME'),
                                    password=os.getenv('DB_PASSWORD'),
                                    database=os.getenv('DB_DATABASE'),
                                    port=int(os.getenv('DB_PORT')))

    def is_existing_portfolio(self, portfolio_id: int) -> bool:
        _cursor = self.conn.cursor()
        _cursor.execute("SELECT * FROM Portfolio WHERE ID = {0}".format(portfolio_id))

        results = _cursor.fetchall()
        _cursor.close()
        return True if results else False

    def get_portfolio(self, portfolio_id: int) -> Portfolio:
        _cursor = self.conn.cursor()
        _cursor.execute("SELECT * FROM Portfolio WHERE ID = {0}".format(portfolio_id))

        results = _cursor.fetchall()
        _cursor.close()
        return Portfolio(results[0][0], results[0][1])

    def create_portfolio(self, cash_balance: float) -> Portfolio:
        _cursor = self.conn.cursor()
        _cursor.execute("INSERT INTO Portfolio (CASH_BALANCE) VALUES ({0});".format(cash_balance))
        _cursor.execute("SELECT * FROM Portfolio WHERE ID = LAST_INSERT_ID()")

        results = _cursor.fetchall()
        _cursor.close()
        return Portfolio(results[0][0], results[0][1])

    def update_portfolio(self, portfolio_id: int, less_cash: float) -> Portfolio:
        _cursor = self.conn.cursor()
        _cursor.execute("UPDATE Portfolio SET CASH_BALANCE = CASH_BALANCE - {0};".format(less_cash))
        _cursor.execute("SELECT * FROM Portfolio WHERE ID = {0}".format(portfolio_id))

        results = _cursor.fetchall()
        _cursor.close()
        return Portfolio(results[0][0], results[0][1])

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
