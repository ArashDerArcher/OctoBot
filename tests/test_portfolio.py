import ccxt

from backtesting.exchange_simulator import ExchangeSimulator
from tests.test_utils.config import load_test_config
from trading.trader.portfolio import Portfolio
from trading.trader.trader_simulator import TraderSimulator


class TestPortfolio:
    @staticmethod
    def init_default():
        config = load_test_config()
        exchange_inst = ExchangeSimulator(config, ccxt.binance)
        trader_inst = TraderSimulator(config, exchange_inst)
        portfolio_inst = Portfolio(config, trader_inst)
        return config, exchange_inst, trader_inst, portfolio_inst

    def test_load_portfolio(self):
        config, exchange_inst, trader_inst, portfolio_inst = self.init_default()
        portfolio_inst._load_portfolio()
        assert portfolio_inst.portfolio == {'BTC': {'available': 10, 'total': 10},
                                            'USDT': {'available': 1000, 'total': 1000}
                                            }

    def test_get_currency_portfolio(self):
        _, _, _, portfolio_inst = self.init_default()
        assert portfolio_inst.get_currency_portfolio("BTC", Portfolio.AVAILABLE) == 10
        assert portfolio_inst.get_currency_portfolio("BTC", Portfolio.TOTAL) == 10
        assert portfolio_inst.get_currency_portfolio("NANO", Portfolio.TOTAL) == 0

    def test_update_portfolio_data(self):
        _, _, _, portfolio_inst = self.init_default()
        portfolio_inst._update_portfolio_data("BTC", -5)
        assert portfolio_inst.get_currency_portfolio("BTC", Portfolio.TOTAL) == 5
        portfolio_inst._update_portfolio_data("BTC", -6, total=False, available=True)
        assert portfolio_inst.get_currency_portfolio("BTC", Portfolio.AVAILABLE) == 4
        portfolio_inst._update_portfolio_data("XRP", 4.5, total=True, available=True)
        assert portfolio_inst.get_currency_portfolio("XRP", Portfolio.AVAILABLE) == 4.5

    def update_portfolio_available(self):
        _, _, _, portfolio_inst = self.init_default()
