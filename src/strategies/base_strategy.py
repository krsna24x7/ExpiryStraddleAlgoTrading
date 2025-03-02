"""
File:           base_strategy.py
Author:         Dibyaranjan Sathua
Created on:     22/08/22, 9:29 pm
"""
from typing import Optional
from abc import ABC, abstractmethod
import datetime
import os

from dotenv import load_dotenv

from src import BASE_DIR
from src.brokerapi.angelbroking import AngelBrokingApi
from src.strategies.instrument import Instrument, PairInstrument, Action
from src.utils.logger import LogFacade


logger: LogFacade = LogFacade.get_logger("base_strategy")


class BaseStrategy(ABC):
    """ Abstract class contains common functions that needs to be implemented in the child class """
    STRATEGY_CODE: str = ""

    def __init__(
            self,
            api_key: str,
            client_id: str,
            password: str,
            totp_key: str,
            dry_run: bool = False,
            clean_up: bool = False
    ):
        self._api_key = api_key
        self._client_id = client_id
        self._password = password
        self._totp_key = totp_key
        self.dry_run: bool = dry_run
        self.clean_up_flag: bool = clean_up
        self._broker_api: Optional[AngelBrokingApi] = None

    @abstractmethod
    def entry(self) -> None:
        pass

    @abstractmethod
    def exit(self) -> None:
        pass

    @abstractmethod
    def execute(self) -> None:
        self.setup_broking_api()

    def process_live_tick(self) -> None:
        pass

    def setup_broking_api(self):
        """ Setup broking API """
        self._broker_api = AngelBrokingApi(
            api_key=self._api_key,
            client_id=self._client_id,
            password=self._password,
            totp_key=self._totp_key
        )
        self._broker_api.login()

    def get_initial_capital(self) -> float:
        """ Get the available capital from broker API """
        funds = self._broker_api.get_funds_and_margin()
        return float(funds["availablecash"])

    def get_used_margin(self) -> float:
        """ Get used margin from broker API """
        funds = self._broker_api.get_funds_and_margin()
        return float(funds["utiliseddebits"])

    def get_orderbook(self) -> list:
        """ Get list of orders placed in the day """
        return self._broker_api.get_order_book()

    def place_pair_instrument_order(self, pair_instrument: PairInstrument):
        """ Place the order using broker API """
        if self.dry_run:
            logger.info(
                f"Skipping placing order for pair instrument {pair_instrument} as running in "
                f"dry-run mode"
            )
            return None
        self._broker_api.place_intraday_options_order(pair_instrument.ce_instrument)
        self._broker_api.place_intraday_options_order(pair_instrument.pe_instrument)

    def place_instrument_order(self, instrument: Instrument):
        """ Place the order using broker API """
        if self.dry_run:
            logger.info(
                f"Skipping placing order for instrument {instrument} as running in dry-run mode"
            )
            return None
        self._broker_api.place_intraday_options_order(instrument)

    @staticmethod
    def is_market_hour(dt: datetime.datetime) -> bool:
        """ Return True if dt is in market hour 9:15:01 to 3:29:59. dt is IST timezone """
        start_time = datetime.time(hour=9, minute=15)
        end_time = datetime.time(hour=15, minute=30)
        return start_time < dt.time() < end_time

    @staticmethod
    def trading_session_ends(now: datetime.datetime):
        """ Return true if the time is greater than 3:36 PM else false """
        return now.time().hour == 15 and now.time().minute > 35
