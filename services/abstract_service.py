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

from abc import *

from backtesting.backtesting import Backtesting


class AbstractService:
    __metaclass__ = ABCMeta

    BACKTESTING_ENABLED = False
    REQUIRED_CONFIG = {}

    def __init__(self):
        super().__init__()
        self.logger = None
        self.config = None
        self.enabled = True

    @classmethod
    def get_name(cls):
        return cls.__name__

    # Returns true if all the service has an instance in config
    @staticmethod
    @abstractmethod
    def is_setup_correctly(config):
        raise NotImplementedError("is_setup_correctly not implemented")

    @classmethod
    def should_be_ready(cls, config):
        on_backtesting = Backtesting.enabled(config)
        return not on_backtesting or (on_backtesting and cls.BACKTESTING_ENABLED)

    # Used to provide a new logger for this particular indicator
    def set_logger(self, logger):
        self.logger = logger

    # Used to provide the global config
    def set_config(self, config):
        self.config = config

    # If this indicator is enabled
    def get_is_enabled(self):
        return self.enabled

    # implement locally if the service has thread(s) to stop
    def stop(self):
        pass

    # implement locally if the service shouldn't raise warning at startup if configuration is not set
    @staticmethod
    def get_should_warn():
        return True

    # Returns true if all the configuration is available
    @abstractmethod
    def has_required_configuration(self):
        raise NotImplementedError("has_required_configuration not implemented")

    # Returns the service's endpoint
    @abstractmethod
    def get_endpoint(self) -> None:
        raise NotImplementedError("get_endpoint not implemented")

    # Called to put in the right service in config
    @abstractmethod
    def get_type(self) -> None:
        raise NotImplementedError("get_type not implemented")

    # Called after service setup
    @abstractmethod
    def prepare(self) -> None:
        raise NotImplementedError("prepare not implemented")

    # Called by say_hello after service is prepared, return relevant service information
    @abstractmethod
    def get_successful_startup_message(self):
        raise NotImplementedError("get_successful_startup_message not implemented")

    def check_required_config(self, config):
        return all(key in config for key in self.REQUIRED_CONFIG)

    def say_hello(self):
        self.logger.info(self.get_successful_startup_message())
