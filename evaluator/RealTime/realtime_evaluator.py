#  Drakkar-Software OctoBot
#  Copyright (c) Drakkar-Software, All rights reserved.
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3.0 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library.

import os
import threading
import time
from abc import *

from backtesting.backtesting import Backtesting
from config.config import load_config
from config import *
from evaluator.abstract_evaluator import AbstractEvaluator
from tools.time_frame_manager import TimeFrameManager


class RealTimeEvaluator(AbstractEvaluator, threading.Thread):
    __metaclass__ = AbstractEvaluator

    def __init__(self):
        super().__init__()
        self.specific_config = None
        self.refresh_time = 0
        self.data = None
        self.evaluator_thread_managers = []
        self.keep_running = True
        self.load_config()

    @classmethod
    def get_config_file_name(cls, config_evaluator_type=CONFIG_EVALUATOR_REALTIME):
        return super().get_config_file_name(config_evaluator_type)

    def stop(self):
        self.keep_running = False

    def load_config(self):
        config_file = self.get_config_file_name()
        if os.path.isfile(config_file):
            self.set_default_config()
            self.specific_config = {**self.specific_config, **load_config(config_file)}
        else:
            self.set_default_config()

    def add_evaluator_thread_manager(self, evaluator_thread):
        self.evaluator_thread_managers.append(evaluator_thread)

    def notify_evaluator_thread_managers(self, notifier_name, force_TA_refresh=False):
        for thread in self.evaluator_thread_managers:
            thread.notify(notifier_name, force_TA_refresh=force_TA_refresh)

    # to implement in subclasses if config necessary
    def set_default_config(self):
        pass

    @abstractmethod
    def _refresh_data(self):
        raise NotImplementedError("_refresh_data not implemented")

    @abstractmethod
    def _should_eval(self):
        raise NotImplementedError("_should_eval not implemented")

    @abstractmethod
    def _define_refresh_time(self):
        raise NotImplementedError("_define_refresh_time not implemented")

    @abstractmethod
    def eval_impl(self) -> None:
        raise NotImplementedError("eval_impl not implemented")

    def run(self):
        while self.keep_running:
            now = time.time()
            if self.is_active:
                try:
                    self._refresh_data()
                except Exception as e:
                    self.logger.error("error when refreshing data for {0}: {1}".format(self.symbol, e))

                if self._should_eval():
                    self.eval()

            if not Backtesting.enabled(self.config):
                sleeping_time = self.specific_config[CONFIG_REFRESH_RATE] - (time.time() - now)
                if sleeping_time > 0:
                    time.sleep(sleeping_time)


class RealTimeTAEvaluator(RealTimeEvaluator):
    __metaclass__ = RealTimeEvaluator

    def __init__(self, exchange_inst, symbol):
        self.exchange = exchange_inst
        super().__init__()
        self.symbol = symbol
        self._define_refresh_time()

    @abstractmethod
    def _refresh_data(self):
        raise NotImplementedError("_refresh_data not implemented")

    @abstractmethod
    def eval_impl(self):
        raise NotImplementedError("eval_impl not implemented")

    def valid_refresh_time(self, config_refresh_time):
        if config_refresh_time > self.exchange.get_exchange_manager().get_rate_limit() or \
                self.exchange.get_exchange_manager().websocket_available():
            return config_refresh_time
        else:
            return self.exchange.get_exchange_manager().get_rate_limit()

    def _define_refresh_time(self):
        self.refresh_time = self.valid_refresh_time(self.specific_config[CONFIG_REFRESH_RATE])

    def _get_data_from_exchange(self, time_frame, limit=None, return_list=False):
        return self.exchange.get_symbol_prices(self.symbol, time_frame,
                                               limit=limit, return_list=return_list)

    @staticmethod
    def _compare_data(new_data, old_data):
        try:
            if new_data[PriceIndexes.IND_PRICE_CLOSE.value][-1] != old_data[PriceIndexes.IND_PRICE_CLOSE.value][-1]:
                return False
            return True
        except Exception:
            return False

    def set_default_config(self):
        time_frames = self.exchange.get_exchange_manager().get_config_time_frame()
        min_time_frame = TimeFrameManager.find_min_time_frame(time_frames, MIN_EVAL_TIME_FRAME)
        refresh_rate = DEFAULT_WEBSOCKET_REAL_TIME_EVALUATOR_REFRESH_RATE_SECONDS if \
            self.exchange.get_exchange_manager().websocket_available() \
            else DEFAULT_REST_REAL_TIME_EVALUATOR_REFRESH_RATE_SECONDS

        self.specific_config = {
            CONFIG_TIME_FRAME: min_time_frame,
            CONFIG_REFRESH_RATE: refresh_rate,
        }
