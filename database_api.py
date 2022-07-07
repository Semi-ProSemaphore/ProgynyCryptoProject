from typing import List, Dict
from schema_objects import Portfolio, Coin
from dotenv import load_dotenv
from datetime import datetime
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
        _cursor.execute("SELECT * FROM Portfolio WHERE ID = {0};".format(portfolio_id))

        results = _cursor.fetchall()
        _cursor.close()
        return True if results else False

    def get_portfolio(self, portfolio_id: int) -> Portfolio:
        _cursor = self.conn.cursor()
        _cursor.execute("SELECT * FROM Portfolio WHERE ID = {0};".format(portfolio_id))

        results = _cursor.fetchall()
        _cursor.close()
        return Portfolio(results[0][0], results[0][1])

    def create_portfolio(self, cash_balance: float) -> Portfolio:
        _cursor = self.conn.cursor()
        _cursor.execute("INSERT INTO Portfolio (CASH_BALANCE) VALUES ({0});".format(cash_balance))
        _cursor.execute("SELECT * FROM Portfolio WHERE ID = LAST_INSERT_ID();")

        results = _cursor.fetchall()
        _cursor.close()
        return Portfolio(results[0][0], results[0][1])

    def update_portfolio(self, portfolio_id: int, less_cash: float) -> Portfolio:
        _cursor = self.conn.cursor()
        _cursor.execute("UPDATE Portfolio SET CASH_BALANCE = CASH_BALANCE - {0};".format(less_cash))
        _cursor.execute("SELECT * FROM Portfolio WHERE ID = {0};".format(portfolio_id))

        results = _cursor.fetchall()
        _cursor.close()
        return Portfolio(results[0][0], results[0][1])

    # This call may need to be revised.
    def get_portfolio_holdings(self, portfolio_id: int) -> Dict[str, float]:
        _cursor = self.conn.cursor()
        _cursor.execute("""SELECT c.ALTERNATE_ID, h.BALANCE 
                        FROM Holdings h 
                        LEFT JOIN Coin c ON c.ID = h.COIN_ID 
                        WHERE PORTFOLIO_ID = {0};"""
                        .format(portfolio_id))

        results = _cursor.fetchall()
        _cursor.close()
        holdings = {}
        for entry in results:
            print("entry: ", entry)
            holdings[entry[0]] = entry[1]
        return holdings

    def is_coin_in_portfolio_holdings(self, portfolio_id: int, alternate_coin_id: str) -> bool:
        _cursor = self.conn.cursor()
        _cursor.execute("""SELECT * FROM Holdings WHERE PORTFOLIO_ID = {0} AND COIN_ID = 
                        (SELECT ID FROM Coin WHERE ALTERNATE_ID = '{1}');"""
                        .format(portfolio_id, alternate_coin_id))

        results = _cursor.fetchall()
        _cursor.close()
        return True if results else False

    def add_to_portfolio_holdings(self, portfolio_id: int, alternate_coin_id: str, amount: float) -> None:
        _cursor = self.conn.cursor()
        # _cursor.execute("SELECT ID FROM Coin WHERE ALTERNATE_ID = '{0}';".format(alternate_coin_id))

        # db_coin = _cursor.fetchall()
        _cursor.execute("""INSERT INTO Holdings (PORTFOLIO_ID, COIN_ID, BALANCE) 
                        VALUES ({0},(SELECT ID FROM Coin WHERE ALTERNATE_ID = '{1}'),{2});"""
                        .format(portfolio_id, alternate_coin_id, amount))
        _cursor.close()

    def update_portfolio_holdings(self, portfolio_id: int, alternate_coin_id: str, change: float) -> None:
        _cursor = self.conn.cursor()
        _cursor.execute("""UPDATE Holdings 
                        SET BALANCE = BALANCE + {0} 
                        WHERE PORTFOLIO_ID = {1} 
                        AND COIN_ID = (
                            SELECT ID FROM Coin WHERE ALTERNATE_ID = '{2}'
                        );"""
                        .format(change, portfolio_id, alternate_coin_id))
        _cursor.close()

    # This call may also need to be revised.
    def get_coin_history(self, alternate_coin_id: str) -> List[List[str]]:
        _cursor = self.conn.cursor()
        _cursor.execute("""SELECT * 
                        FROM HistoricalCoinData 
                        WHERE COIN_ID = (
                            SELECT ID FROM Coin WHERE ALTERNATE_ID = '{0}
                        );"""
                        .format(alternate_coin_id))
        results = _cursor.fetchall()
        _cursor.close()

        return [list(result) for result in results]

    # Entire set of coin information is not needed yet, but may be in the future. Thus adding Coin obj.
    def add_coin_history(self, coin: Coin) -> None:
        _cursor = self.conn.cursor()
        _cursor.execute("""INSERT INTO HistoricalCoinData 
                        (COIN_ID, CURRENT_PRICE, DATE) 
                        VALUES ((
                            SELECT ID FROM Coin WHERE ALTERNATE_ID = '{0}')
                            ,{1},'{2}');"""
                        .format(
                            coin.id, coin.current_price, datetime.strptime(coin.date, "%Y-%m-%dT%H:%M:%S.%fZ")))
        _cursor.close()

    def is_existing_coin(self, coin: Coin) -> bool:
        _cursor = self.conn.cursor()
        _cursor.execute("SELECT * FROM Coin WHERE ALTERNATE_ID = '{0}';".format(coin.id))

        results = _cursor.fetchall()
        _cursor.close()
        return True if results else False

    def create_coin(self, coin: Coin) -> None:
        _cursor = self.conn.cursor()
        _cursor.execute("INSERT INTO Coin (ALTERNATE_ID, SYMBOL, NAME) VALUES ('{0}','{1}','{2}');".format(
            coin.id, coin.symbol, coin.name))
        _cursor.close()
