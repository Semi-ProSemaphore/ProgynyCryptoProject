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
        self._create_tables()

    def _create_tables(self):
        self._create_coin_table()
        self._create_portfolio_table()
        self._create_holdings_table()
        self._create_historical_coin_data_table()

    def _create_coin_table(self):
        creation_string = """
            CREATE TABLE IF NOT EXISTS Coin
            (
                ID INT NOT NULL AUTO_INCREMENT,
                ALTERNATE_ID VARCHAR(15),
                SYMBOL VARCHAR(6),
                NAME VARCHAR(15),
                CURRENT_PRICE FLOAT,
            
                PRIMARY KEY (ID)
            );
        """
        _cursor = self.conn.cursor()
        _cursor.execute(creation_string)
        _cursor.close()

    def _create_portfolio_table(self):
        creation_string = """
            CREATE TABLE IF NOT EXISTS Portfolio
            (
                ID INT NOT NULL AUTO_INCREMENT,
                CASH_BALANCE FLOAT,
                STARTING_CASH_BALANCE FLOAT,
            
                PRIMARY KEY (ID)
            );
        """
        _cursor = self.conn.cursor()
        _cursor.execute(creation_string)
        _cursor.close()

    def _create_holdings_table(self):
        creation_string = """
            CREATE TABLE IF NOT EXISTS Holdings
            (
                PORTFOLIO_ID INT,
                COIN_ID INT,
                BALANCE FLOAT,
            
                FOREIGN KEY (PORTFOLIO_ID) REFERENCES Portfolio(ID),
                FOREIGN KEY (COIN_ID) REFERENCES Coin(ID)
            );
        """
        _cursor = self.conn.cursor()
        _cursor.execute(creation_string)
        _cursor.close()

    def _create_historical_coin_data_table(self):
        creation_string = """
            CREATE TABLE IF NOT EXISTS HistoricalCoinData
            (
                COIN_ID INT,
                CURRENT_PRICE FLOAT,
                DATE DATE,
            
                FOREIGN KEY (COIN_ID) REFERENCES Coin(ID)
            );
        """
        _cursor = self.conn.cursor()
        _cursor.execute(creation_string)
        _cursor.close()

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
        print("res: ", results)
        return Portfolio(results[0][0], results[0][1])

    def create_portfolio(self, cash_balance: float) -> Portfolio:
        _cursor = self.conn.cursor()
        _cursor.execute("""INSERT INTO 
                        Portfolio (CASH_BALANCE, STARTING_CASH_BALANCE) 
                        VALUES ({0}, {0});"""
                        .format(cash_balance))
        _cursor.execute("SELECT * FROM Portfolio WHERE ID = LAST_INSERT_ID();")

        results = _cursor.fetchall()
        _cursor.close()
        return Portfolio(results[0][0], results[0][1])

    def get_portfolio_pnl(self, portfolio_id: int) -> float:
        _cursor = self.conn.cursor()
        _cursor.execute("SELECT CASH_BALANCE, STARTING_CASH_BALANCE FROM Portfolio WHERE ID = {0};".format(portfolio_id))

        balances = _cursor.fetchall()

        _cursor.execute("""SELECT SUM(h.BALANCE * c.CURRENT_PRICE) 
                        FROM Holdings h 
                        INNER JOIN Coin c ON c.ID = h.COIN_ID
                        WHERE h.PORTFOLIO_ID = {0};""".format(portfolio_id))

        coin_total = _cursor.fetchall()
        _cursor.close()
        return (balances[0][0] + coin_total[0][0]) / balances[0][1]

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
                        WHERE h.PORTFOLIO_ID = {0};"""
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

    def update_coin(self, coin: Coin) -> None:
        _cursor = self.conn.cursor()
        _cursor.execute("""UPDATE Coin 
                        SET CURRENT_PRICE = {0} 
                        WHERE ALTERNATE_ID = '{1}';"""
                        .format(coin.current_price, coin.id))
        _cursor.close()

