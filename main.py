"""
File:           main.py
Author:         Dibyaranjan Sathua
Created on:     29/08/22, 1:31 am
"""
import os
from dotenv import load_dotenv
import argparse

from src import BASE_DIR
from src.market_feeds.market_feeds import MarketFeeds
from src.strategies.strategy1 import Strategy1
from src.price_monitor.price_monitor import PriceMonitor


def run_market_feed():
    """ Run market feed """
    dotenv_path = BASE_DIR / 'env' / '.env'
    load_dotenv(dotenv_path=dotenv_path)
    api_key = os.environ.get("ANGEL_BROKING_API_KEY")
    client_id = os.environ.get("ANGEL_BROKING_CLIENT_ID")
    password = os.environ.get("ANGEL_BROKING_PASSWORD")
    market_feeds = MarketFeeds(api_key=api_key, client_id=client_id, password=password)
    market_feeds.setup()


def run_strategy1():
    """ Run strategy1 """
    price_monitor = PriceMonitor()
    price_monitor.setup()
    price_monitor.run_in_background()
    strategy = Strategy1(price_monitor=price_monitor)
    strategy.execute()


def main():
    """ Main function """
    parser = argparse.ArgumentParser()
    parser.add_argument("--market_feeds", action="store_true")
    parser.add_argument("--trading", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--clean-up", action="store_true")
    args = parser.parse_args()
    if args.trading:
        run_strategy1()
    if args.market_feeds:
        run_market_feed()


if __name__ == "__main__":
    main()
