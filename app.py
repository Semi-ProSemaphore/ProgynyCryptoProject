"""Crypto Interview Assessment Module."""

import os
import time
from dotenv import find_dotenv, load_dotenv
from portfolio import Portfolio


load_dotenv(find_dotenv(raise_error_if_not_found=True))

# You can access the environment variables as such, and any variables from the .env file will be loaded in for you to use.
# os.getenv("DB_HOST")

# Start Here


class App:

    @staticmethod
    def run_app():
        portfolio = Portfolio()

        while True:
            portfolio.make_trade_decision()
            time.sleep(3600)
