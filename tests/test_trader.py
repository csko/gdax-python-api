import base64
import asyncio
from decimal import Decimal

from asynctest import patch, CoroutineMock
import pytest

import gdax
from tests.helpers import AsyncContextManagerMock, \
    AsyncContextManagerMockPagination, generate_id


@pytest.yield_fixture
def event_loop():
    """Create an instance of the default event loop for each test case."""
    policy = asyncio.get_event_loop_policy()
    res = policy.new_event_loop()
    asyncio.set_event_loop(res)
    res._close = res.close
    res.close = lambda: None

    yield res

    res._close()


@patch('aiohttp.ClientSession.get', new_callable=AsyncContextManagerMock)
@pytest.mark.usefixtures('event_loop')
@pytest.mark.asyncio
class TestPublicClient:
    def init(self):
        self.client = gdax.trader.Trader()

    async def test_get_products(self, mock_get):
        products = [
            {
              "id": "LTC-EUR",
              "base_currency": "LTC",
              "quote_currency": "EUR",
              "base_min_size": "0.01",
              "base_max_size": "1000000",
              "quote_increment": "0.01",
              "display_name": "LTC/EUR"
            },
            {
              "id": "LTC-BTC",
              "base_currency": "LTC",
              "quote_currency": "BTC",
              "base_min_size": "0.01",
              "base_max_size": "1000000",
              "quote_increment": "0.00001",
              "display_name": "LTC/BTC"
            },
            {
              "id": "BTC-GBP",
              "base_currency": "BTC",
              "quote_currency": "GBP",
              "base_min_size": "0.01",
              "base_max_size": "250",
              "quote_increment": "0.01",
              "display_name": "BTC/GBP"
            },
            {
              "id": "BTC-EUR",
              "base_currency": "BTC",
              "quote_currency": "EUR",
              "base_min_size": "0.01",
              "base_max_size": "250",
              "quote_increment": "0.01",
              "display_name": "BTC/EUR"
            },
            {
              "id": "ETH-EUR",
              "base_currency": "ETH",
              "quote_currency": "EUR",
              "base_min_size": "0.01",
              "base_max_size": "5000",
              "quote_increment": "0.01",
              "display_name": "ETH/EUR"
            },
            {
              "id": "ETH-BTC",
              "base_currency": "ETH",
              "quote_currency": "BTC",
              "base_min_size": "0.01",
              "base_max_size": "5000",
              "quote_increment": "0.00001",
              "display_name": "ETH/BTC"
            },
            {
              "id": "LTC-USD",
              "base_currency": "LTC",
              "quote_currency": "USD",
              "base_min_size": "0.01",
              "base_max_size": "1000000",
              "quote_increment": "0.01",
              "display_name": "LTC/USD"
            },
            {
              "id": "BTC-USD",
              "base_currency": "BTC",
              "quote_currency": "USD",
              "base_min_size": "0.01",
              "base_max_size": "250",
              "quote_increment": "0.01",
              "display_name": "BTC/USD"
            },
            {
              "id": "ETH-USD",
              "base_currency": "ETH",
              "quote_currency": "USD",
              "base_min_size": "0.01",
              "base_max_size": "5000",
              "quote_increment": "0.01",
              "display_name": "ETH/USD"
            }
        ]
        expected_products = [
            {
              "id": "LTC-EUR",
              "base_currency": "LTC",
              "quote_currency": "EUR",
              "base_min_size": Decimal("0.01"),
              "base_max_size": Decimal("1000000"),
              "quote_increment": Decimal("0.01"),
              "display_name": "LTC/EUR"
            },
            {
              "id": "LTC-BTC",
              "base_currency": "LTC",
              "quote_currency": "BTC",
              "base_min_size": Decimal("0.01"),
              "base_max_size": Decimal("1000000"),
              "quote_increment": Decimal("0.00001"),
              "display_name": "LTC/BTC"
            },
            {
              "id": "BTC-GBP",
              "base_currency": "BTC",
              "quote_currency": "GBP",
              "base_min_size": Decimal("0.01"),
              "base_max_size": Decimal("250"),
              "quote_increment": Decimal("0.01"),
              "display_name": "BTC/GBP"
            },
            {
              "id": "BTC-EUR",
              "base_currency": "BTC",
              "quote_currency": "EUR",
              "base_min_size": Decimal("0.01"),
              "base_max_size": Decimal("250"),
              "quote_increment": Decimal("0.01"),
              "display_name": "BTC/EUR"
            },
            {
              "id": "ETH-EUR",
              "base_currency": "ETH",
              "quote_currency": "EUR",
              "base_min_size": Decimal("0.01"),
              "base_max_size": Decimal("5000"),
              "quote_increment": Decimal("0.01"),
              "display_name": "ETH/EUR"
            },
            {
              "id": "ETH-BTC",
              "base_currency": "ETH",
              "quote_currency": "BTC",
              "base_min_size": Decimal("0.01"),
              "base_max_size": Decimal("5000"),
              "quote_increment": Decimal("0.00001"),
              "display_name": "ETH/BTC"
            },
            {
              "id": "LTC-USD",
              "base_currency": "LTC",
              "quote_currency": "USD",
              "base_min_size": Decimal("0.01"),
              "base_max_size": Decimal("1000000"),
              "quote_increment": Decimal("0.01"),
              "display_name": "LTC/USD"
            },
            {
              "id": "BTC-USD",
              "base_currency": "BTC",
              "quote_currency": "USD",
              "base_min_size": Decimal("0.01"),
              "base_max_size": Decimal("250"),
              "quote_increment": Decimal("0.01"),
              "display_name": "BTC/USD"
            },
            {
              "id": "ETH-USD",
              "base_currency": "ETH",
              "quote_currency": "USD",
              "base_min_size": Decimal("0.01"),
              "base_max_size": Decimal("5000"),
              "quote_increment": Decimal("0.01"),
              "display_name": "ETH/USD"
            }
        ]
        mock_get.return_value.aenter.json = CoroutineMock(
            return_value=products)
        self.init()
        r = await self.client.get_products()
        assert r == expected_products

    async def test_get_product_ticker(self, mock_get):
        ticker = {
            "trade_id": 17429442,
            "price": "2483.64000000",
            "size": "0.80809483",
            "bid": "2481.18",
            "ask": "2483.61",
            "volume": "13990.13083225",
            "time": "2017-06-26T06:29:06.993000Z"
        }
        expected_ticker = {
            "trade_id": 17429442,
            "price": Decimal("2483.64000000"),
            "size": Decimal("0.80809483"),
            "bid": Decimal("2481.18"),
            "ask": Decimal("2483.61"),
            "volume": Decimal("13990.13083225"),
            "time": "2017-06-26T06:29:06.993000Z"
        }
        mock_get.return_value.aenter.json = CoroutineMock(return_value=ticker)
        self.init()
        r = await self.client.get_product_ticker('BTC-USD')
        assert r == expected_ticker

    async def test_get_product_trades(self, mock_get):
        trades = [
          {
            "time": "2017-06-26T06:32:53.79Z",
            "trade_id": 17429512,
            "price": "2479.98000000",
            "size": "0.01997424",
            "side": "sell"
          },
          {
            "time": "2017-06-26T06:32:24.113Z",
            "trade_id": 17429508,
            "price": "2479.97000000",
            "size": "0.54415961",
            "side": "buy"
          }
        ]
        expected_trades = [
          {
            "time": "2017-06-26T06:32:53.79Z",
            "trade_id": 17429512,
            "price": Decimal("2479.98000000"),
            "size": Decimal("0.01997424"),
            "side": "sell"
          },
          {
            "time": "2017-06-26T06:32:24.113Z",
            "trade_id": 17429508,
            "price": Decimal("2479.97000000"),
            "size": Decimal("0.54415961"),
            "side": "buy"
          }
        ]
        mock_get.return_value.aenter.json = CoroutineMock(return_value=trades)
        self.init()
        r = await self.client.get_product_trades('BTC-USD')
        assert r == expected_trades

    async def test_get_product_order_book(self, mock_get):
        orderbook = {
          "sequence": 3424558479,
          "bids": [
            [
              "2483.8",
              "0.01",
              1
            ]
          ],
          "asks": [
            [
              "2486.28",
              "0.01455",
              1
            ]
          ]
        }

        expected_orderbook = {
          "sequence": 3424558479,
          "bids": [
            [
              Decimal("2483.8"),
              Decimal("0.01"),
              1
            ]
          ],
          "asks": [
            [
              Decimal("2486.28"),
              Decimal("0.01455"),
              1
            ]
          ]
        }
        mock_get.return_value.aenter.json = CoroutineMock(
            return_value=orderbook)
        self.init()
        r = await self.client.get_product_order_book('BTC-USD')
        assert r == expected_orderbook

        orderbook = {
          "sequence": 3424562473,
          "bids": [
            [
              "2483.99",
              "0.01",
              1
            ],
            [
              "2483.98",
              "0.9798",
              5
            ]
          ],
          "asks": [
            [
              "2486.48",
              "1.65567931",
              1
            ],
            [
              "2487.72",
              "0.03",
              3
            ]
          ]
        }
        expected_orderbook = {
          "sequence": 3424562473,
          "bids": [
            [
              Decimal("2483.99"),
              Decimal("0.01"),
              1
            ],
            [
              Decimal("2483.98"),
              Decimal("0.9798"),
              5
            ]
          ],
          "asks": [
            [
              Decimal("2486.48"),
              Decimal("1.65567931"),
              1
            ],
            [
              Decimal("2487.72"),
              Decimal("0.03"),
              3
            ]
          ]
        }
        mock_get.return_value.aenter.json = CoroutineMock(
            return_value=orderbook)
        r = await self.client.get_product_order_book('BTC-USD', level=2)
        assert r == expected_orderbook

        id1, id2, id3, id4 = (generate_id() for _ in range(4))
        orderbook = {
          "sequence": 3424562473,
          "bids": [
            [
              "2483.99",
              "0.01",
              id1
            ],
            [
              "2483.98",
              "0.9798",
              id2
            ]
          ],
          "asks": [
            [
              "2486.48",
              "1.65567931",
              id3
            ],
            [
              "2487.72",
              "0.03",
              id4
            ]
          ]
        }
        expected_orderbook = {
          "sequence": 3424562473,
          "bids": [
            [
              Decimal("2483.99"),
              Decimal("0.01"),
              id1
            ],
            [
              Decimal("2483.98"),
              Decimal("0.9798"),
              id2
            ]
          ],
          "asks": [
            [
              Decimal("2486.48"),
              Decimal("1.65567931"),
              id3
            ],
            [
              Decimal("2487.72"),
              Decimal("0.03"),
              id4
            ]
          ]
        }
        mock_get.return_value.aenter.json = CoroutineMock(
            return_value=orderbook)
        r = await self.client.get_product_order_book('BTC-USD', level=3)
        assert r == expected_orderbook

    async def test_get_product_historic_rates(self, mock_get):
        rates = [
              [
                1498459140,
                2488.79,
                2489.96,
                2489.47,
                2489.96,
                9.332934549999997
              ],
              [
                1498459080,
                2486.24,
                2489.97,
                2486.24,
                2489.96,
                6.937264829999997
              ],
            ]
        expected_rates = [
              [
                1498459140,
                Decimal('2488.79'),
                Decimal('2489.96'),
                Decimal('2489.47'),
                Decimal('2489.96'),
                Decimal('9.332934549999997')
              ],
              [
                1498459080,
                Decimal('2486.24'),
                Decimal('2489.97'),
                Decimal('2486.24'),
                Decimal('2489.96'),
                Decimal('6.937264829999997')
              ],
            ]
        mock_get.return_value.aenter.json = CoroutineMock(return_value=rates)
        self.init()
        r = await self.client.get_product_historic_rates('BTC-USD')
        assert r == expected_rates

    async def test_get_product_24hr_stats(self, mock_get):
        stats = {
          "open": "2586.26000000",
          "high": "2625.00000000",
          "low": "2430.05000000",
          "volume": "14063.90737841",
          "last": "2489.89000000",
          "volume_30day": "568418.24079392"
        }
        expected_stats = {
          "open": Decimal("2586.26000000"),
          "high": Decimal("2625.00000000"),
          "low": Decimal("2430.05000000"),
          "volume": Decimal("14063.90737841"),
          "last": Decimal("2489.89000000"),
          "volume_30day": Decimal("568418.24079392")
        }
        mock_get.return_value.aenter.json = CoroutineMock(return_value=stats)
        self.init()
        r = await self.client.get_product_24hr_stats('BTC-USD')
        assert r == expected_stats

    async def test_get_currencies(self, mock_get):
        currencies = [
          {
            "id": "BTC",
            "name": "Bitcoin",
            "min_size": "0.00000001"
          },
          {
            "id": "EUR",
            "name": "Euro",
            "min_size": "0.01000000"
          },
          {
            "id": "LTC",
            "name": "Litecoin",
            "min_size": "0.00000001"
          },
          {
            "id": "GBP",
            "name": "British Pound",
            "min_size": "0.01000000"
          },
          {
            "id": "USD",
            "name": "United States Dollar",
            "min_size": "0.01000000"
          },
          {
            "id": "ETH",
            "name": "Ether",
            "min_size": "0.00000001"
          }
        ]
        expected_currencies = [
          {
            "id": "BTC",
            "name": "Bitcoin",
            "min_size": Decimal("0.00000001")
          },
          {
            "id": "EUR",
            "name": "Euro",
            "min_size": Decimal("0.01000000")
          },
          {
            "id": "LTC",
            "name": "Litecoin",
            "min_size": Decimal("0.00000001")
          },
          {
            "id": "GBP",
            "name": "British Pound",
            "min_size": Decimal("0.01000000")
          },
          {
            "id": "USD",
            "name": "United States Dollar",
            "min_size": Decimal("0.01000000")
          },
          {
            "id": "ETH",
            "name": "Ether",
            "min_size": Decimal("0.00000001")
          }
        ]
        mock_get.return_value.aenter.json = CoroutineMock(
            return_value=currencies)
        self.init()
        r = await self.client.get_currencies()
        assert r == expected_currencies

    async def test_get_time(self, mock_get):
        r_time = {'iso': '2017-06-26T06:47:55.168Z', 'epoch': 1498459675.168}
        mock_get.return_value.aenter.json = CoroutineMock(return_value=r_time)
        self.init()
        r = await self.client.get_time()
        assert r == r_time


@pytest.mark.usefixtures('event_loop')
@pytest.mark.asyncio
class TestPublicClientNotAuthenticated:
    def init(self):
        self.client = gdax.trader.Trader()

    async def test_get_account(self):
        self.init()
        with pytest.raises(AssertionError):
            await self.client.get_account()

    async def test_get_account_history(self):
        self.init()
        with pytest.raises(AssertionError):
            await self.client.get_account_history('account_id')

    async def test_get_account_holds(self):
        self.init()
        with pytest.raises(AssertionError):
            await self.client.get_account_holds('account_id')

    async def test_buy(self):
        self.init()
        with pytest.raises(AssertionError):
            await self.client.buy(product_id='product_id')

    async def test_sell(self):
        self.init()
        with pytest.raises(AssertionError):
            await self.client.sell(product_id='product_id')

    async def test_cancel_order(self):
        self.init()
        with pytest.raises(AssertionError):
            await self.client.cancel_order('order_id')

    async def test_cancel_all(self):
        self.init()
        with pytest.raises(AssertionError):
            await self.client.cancel_all('product_id')

    async def test_get_order(self):
        self.init()
        with pytest.raises(AssertionError):
            await self.client.get_order('order_id')

    async def test_get_orders(self):
        self.init()
        with pytest.raises(AssertionError):
            await self.client.get_orders()

    async def test_get_fills(self):
        self.init()
        with pytest.raises(AssertionError):
            await self.client.get_fills()

    async def test_get_fundings(self):
        self.init()
        with pytest.raises(AssertionError):
            await self.client.get_fundings('status')

    async def test_repay_funding(self):
        self.init()
        with pytest.raises(AssertionError):
            await self.client.repay_funding(Decimal('10'), 'USD')

    async def test_margin_transfer(self):
        self.init()
        with pytest.raises(AssertionError):
            await self.client.margin_transfer('id', 'deposit',
                                              'USD', Decimal('10'))

    async def test_get_position(self):
        self.init()
        with pytest.raises(AssertionError):
            await self.client.get_position()

    async def test_close_position(self):
        self.init()
        with pytest.raises(AssertionError):
            await self.client.close_position()

    async def test_deposit(self):
        self.init()
        with pytest.raises(AssertionError):
            await self.client.deposit(Decimal('10'), 'USD', 'id')

    async def test_coinbase_deposit(self):
        self.init()
        with pytest.raises(AssertionError):
            await self.client.coinbase_deposit(Decimal('10'), 'USD', 'id')

    async def test_withdraw(self):
        self.init()
        with pytest.raises(AssertionError):
            await self.client.withdraw(Decimal('10'), 'USD', 'id')

    async def test_coinbase_withdraw(self):
        self.init()
        with pytest.raises(AssertionError):
            await self.client.coinbase_withdraw(Decimal('10'), 'USD', 'id')

    async def test_crypto_withdraw(self):
        self.init()
        with pytest.raises(AssertionError):
            await self.client.crypto_withdraw(Decimal('10'), 'USD', 'addr')

    async def test_get_payment_methods(self):
        self.init()
        with pytest.raises(AssertionError):
            await self.client.get_payment_methods()

    async def test_get_coinbase_accounts(self):
        self.init()
        with pytest.raises(AssertionError):
            await self.client.get_coinbase_accounts()

    async def test_create_report(self):
        self.init()
        with pytest.raises(AssertionError):
            await self.client.create_report('fills', 'start', 'end')

    async def test_get_report(self):
        self.init()
        with pytest.raises(AssertionError):
            await self.client.get_report('report_id')

    async def test_get_trailing_volume(self):
        self.init()
        with pytest.raises(AssertionError):
            await self.client.get_trailing_volume()


def test_auth_headers(mocker):
    client = gdax.trader.Trader(
        api_key='a',
        api_secret=base64.b64encode(b'a' * 64),
        passphrase='b',
    )
    path = '/test'
    method = 'DELETE'
    body = 'hello'
    timestamp = '1493343391.076892'
    mocker.patch('time.time', return_value=timestamp)
    auth_headers = client._auth_headers(path, method, body)
    expected_auth_headers = {
        'Content-Type': 'application/json',
        'CB-ACCESS-SIGN': 'a7ailLNCPtunAmPW4JlpJT02rSLtXP9O6JnEU+wSVMs=',
        'CB-ACCESS-TIMESTAMP': timestamp,
        'CB-ACCESS-KEY': 'a',
        'CB-ACCESS-PASSPHRASE': 'b',
    }

    assert auth_headers == expected_auth_headers


@pytest.mark.asyncio
class TestAuthClient(object):
    def init(self):
        self.client = gdax.trader.Trader(
            api_key='a',
            api_secret=base64.b64encode(b'a' * 64),
            passphrase='b',
        )

    @patch('aiohttp.ClientSession.get', new_callable=AsyncContextManagerMock)
    async def test_get_account(self, mock_get):
        mock_get.return_value.aenter.json = CoroutineMock(return_value={})
        self.init()
        r = await self.client.get_account()
        assert type(r) is dict

    @patch('aiohttp.ClientSession.get', new_callable=AsyncContextManagerMock)
    async def test_get_account_history(self, mock_get):
        mock_get.return_value.aenter.json = CoroutineMock(return_value={})
        self.init()
        r = await self.client.get_account_history('id')
        assert type(r) is list

    @patch('aiohttp.ClientSession.get', new_callable=AsyncContextManagerMock)
    async def test_get_account_holds(self, mock_get):
        mock_get.return_value.aenter.json = CoroutineMock(return_value={})
        self.init()
        r = await self.client.get_account_holds('id')
        assert type(r) is list

    @patch('aiohttp.ClientSession.post', new_callable=AsyncContextManagerMock)
    async def test_buy(self, mock_post):
        message = {
          "id": "d0c5340b-6d6c-49d9-b567-48c4bfca13d2",
          "price": "0.10000000",
          "size": "0.01000000",
          "product_id": "BTC-USD",
          "side": "buy",
          "stp": "dc",
          "type": "limit",
          "time_in_force": "GTC",
          "post_only": False,
          "created_at": "2016-12-08T20:02:28.53864Z",
          "fill_fees": "0.0000000000000000",
          "filled_size": "0.00000000",
          "executed_value": "0.0000000000000000",
          "status": "pending",
          "settled": False
        }
        expected_message = {
          "id": "d0c5340b-6d6c-49d9-b567-48c4bfca13d2",
          "price": Decimal("0.10000000"),
          "size": Decimal("0.01000000"),
          "product_id": "BTC-USD",
          "side": "buy",
          "stp": "dc",
          "type": "limit",
          "time_in_force": "GTC",
          "post_only": False,
          "created_at": "2016-12-08T20:02:28.53864Z",
          "fill_fees": Decimal("0.0000000000000000"),
          "filled_size": Decimal("0.00000000"),
          "executed_value": Decimal("0.0000000000000000"),
          "status": "pending",
          "settled": False
        }
        mock_post.return_value.aenter.json = CoroutineMock(
            return_value=message)
        self.init()
        r = await self.client.buy(product_id='product_id',
                                  price=Decimal('250.52'),
                                  size=Decimal('5.0'),
                                  funds=Decimal('500'))
        assert r == expected_message

    @patch('aiohttp.ClientSession.post', new_callable=AsyncContextManagerMock)
    async def test_sell(self, mock_post):
        message = {
          "id": "d0c5340b-6d6c-49d9-b567-48c4bfca13d2",
          "price": "0.10000000",
          "size": "0.01000000",
          "product_id": "BTC-USD",
          "side": "sell",
          "stp": "dc",
          "type": "limit",
          "time_in_force": "GTC",
          "post_only": False,
          "created_at": "2016-12-08T20:02:28.53864Z",
          "fill_fees": "0.0000000000000000",
          "filled_size": "0.00000000",
          "executed_value": "0.0000000000000000",
          "status": "pending",
          "settled": False
        }
        expected_message = {
          "id": "d0c5340b-6d6c-49d9-b567-48c4bfca13d2",
          "price": Decimal("0.10000000"),
          "size": Decimal("0.01000000"),
          "product_id": "BTC-USD",
          "side": "sell",
          "stp": "dc",
          "type": "limit",
          "time_in_force": "GTC",
          "post_only": False,
          "created_at": "2016-12-08T20:02:28.53864Z",
          "fill_fees": Decimal("0.0000000000000000"),
          "filled_size": Decimal("0.00000000"),
          "executed_value": Decimal("0.0000000000000000"),
          "status": "pending",
          "settled": False
        }
        mock_post.return_value.aenter.json = CoroutineMock(
            return_value=message)
        self.init()
        r = await self.client.sell(product_id='product_id',
                                   price=Decimal('250.52'),
                                   size=Decimal('5.0'),
                                   funds=Decimal('500'))
        assert r == expected_message

    @patch('aiohttp.ClientSession.delete',
           new_callable=AsyncContextManagerMock)
    async def test_cancel_order(self, mock_delete):
        mock_delete.return_value.aenter.json = CoroutineMock(return_value={})
        self.init()
        r = await self.client.cancel_order(order_id='order_id')
        assert type(r) is dict

    @patch('aiohttp.ClientSession.delete',
           new_callable=AsyncContextManagerMock)
    async def test_cancel_all(self, mock_delete):
        message = [
            "144c6f8e-713f-4682-8435-5280fbe8b2b4",
            "debe4907-95dc-442f-af3b-cec12f42ebda",
            "cf7aceee-7b08-4227-a76c-3858144323ab",
            "dfc5ae27-cadb-4c0c-beef-8994936fde8a",
            "34fecfbf-de33-4273-b2c6-baf8e8948be4"
        ]
        mock_delete.return_value.aenter.json = CoroutineMock(
            return_value=message)
        self.init()
        r = await self.client.cancel_all()
        assert r == message

    @patch('aiohttp.ClientSession.get', new_callable=AsyncContextManagerMock)
    async def test_get_order(self, mock_get):
        message = {
            "id": "68e6a28f-ae28-4788-8d4f-5ab4e5e5ae08",
            "price": "250.0000000",
            "size": "1.00000000",
            "product_id": "BTC-USD",
            "side": "buy",
            "stp": "dc",
            "funds": "9.9750623400000000",
            "specified_funds": "10.0000000000000000",
            "type": "limit",
            "post_only": False,
            "created_at": "2016-12-08T20:09:05.508883Z",
            "done_at": "2016-12-08T20:09:05.527Z",
            "done_reason": "filled",
            "fill_fees": "0.0249376391550000",
            "filled_size": "0.01291771",
            "executed_value": "9.9750556620000000",
            "status": "done",
            "settled": False
        }
        expected_message = {
            "id": "68e6a28f-ae28-4788-8d4f-5ab4e5e5ae08",
            "price": Decimal("250.0000000"),
            "size": Decimal("1.00000000"),
            "product_id": "BTC-USD",
            "side": "buy",
            "stp": "dc",
            "funds": Decimal("9.9750623400000000"),
            "specified_funds": Decimal("10.0000000000000000"),
            "type": "limit",
            "post_only": False,
            "created_at": "2016-12-08T20:09:05.508883Z",
            "done_at": "2016-12-08T20:09:05.527Z",
            "done_reason": "filled",
            "fill_fees": Decimal("0.0249376391550000"),
            "filled_size": Decimal("0.01291771"),
            "executed_value": Decimal("9.9750556620000000"),
            "status": "done",
            "settled": False
        }
        mock_get.return_value.aenter.json = CoroutineMock(return_value=message)
        self.init()
        r = await self.client.get_order('order_id')
        assert r == expected_message

    @patch('aiohttp.ClientSession.get', new_callable=AsyncContextManagerMock)
    async def test_get_orders(self, mock_get):
        message = [
            {
                "id": "d0c5340b-6d6c-49d9-b567-48c4bfca13d2",
                "price": "0.10000000",
                "size": "0.01000000",
                "product_id": "BTC-USD",
                "side": "buy",
                "stp": "dc",
                "type": "limit",
                "time_in_force": "GTC",
                "post_only": False,
                "created_at": "2016-12-08T20:02:28.53864Z",
                "fill_fees": "0.0000000000000000",
                "filled_size": "0.00000000",
                "executed_value": "0.0000000000000000",
                "status": "open",
                "settled": False
            },
            {
                "id": "8b99b139-58f2-4ab2-8e7a-c11c846e3022",
                "price": "1.00000000",
                "size": "1.00000000",
                "product_id": "BTC-USD",
                "side": "buy",
                "stp": "dc",
                "type": "limit",
                "time_in_force": "GTC",
                "post_only": False,
                "created_at": "2016-12-08T20:01:19.038644Z",
                "fill_fees": "0.0000000000000000",
                "filled_size": "0.00000000",
                "executed_value": "0.0000000000000000",
                "status": "open",
                "settled": False
            }
        ]
        expected_message = [
            {
                "id": "d0c5340b-6d6c-49d9-b567-48c4bfca13d2",
                "price": Decimal("0.10000000"),
                "size": Decimal("0.01000000"),
                "product_id": "BTC-USD",
                "side": "buy",
                "stp": "dc",
                "type": "limit",
                "time_in_force": "GTC",
                "post_only": False,
                "created_at": "2016-12-08T20:02:28.53864Z",
                "fill_fees": Decimal("0.0000000000000000"),
                "filled_size": Decimal("0.00000000"),
                "executed_value": Decimal("0.0000000000000000"),
                "status": "open",
                "settled": False
            },
            {
                "id": "8b99b139-58f2-4ab2-8e7a-c11c846e3022",
                "price": Decimal("1.00000000"),
                "size": Decimal("1.00000000"),
                "product_id": "BTC-USD",
                "side": "buy",
                "stp": "dc",
                "type": "limit",
                "time_in_force": "GTC",
                "post_only": False,
                "created_at": "2016-12-08T20:01:19.038644Z",
                "fill_fees": Decimal("0.0000000000000000"),
                "filled_size": Decimal("0.00000000"),
                "executed_value": Decimal("0.0000000000000000"),
                "status": "open",
                "settled": False
            }
        ]

        mock_get.return_value.aenter.json = CoroutineMock(return_value=message)
        self.init()
        r = await self.client.get_orders()
        assert r == expected_message

    @patch('aiohttp.ClientSession.get', new_callable=AsyncContextManagerMock)
    async def test_get_fills(self, mock_get):
        message = [
            {
                "trade_id": 74,
                "product_id": "BTC-USD",
                "price": "10.00",
                "size": "0.01",
                "order_id": "d50ec984-77a8-460a-b958-66f114b0de9b",
                "created_at": "2014-11-07T22:19:28.578544Z",
                "liquidity": "T",
                "fee": "0.00025",
                "settled": True,
                "side": "buy"
            }
        ]
        expected_message = [
            {
                "trade_id": 74,
                "product_id": "BTC-USD",
                "price": Decimal("10.00"),
                "size": Decimal("0.01"),
                "order_id": "d50ec984-77a8-460a-b958-66f114b0de9b",
                "created_at": "2014-11-07T22:19:28.578544Z",
                "liquidity": "T",
                "fee": Decimal("0.00025"),
                "settled": True,
                "side": "buy"
            }
        ]
        mock_get.return_value.aenter.json = CoroutineMock(return_value=message)
        self.init()
        r = await self.client.get_fills(
            order_id='d50ec984-77a8-460a-b958-66f114b0de9b',
            product_id='BTC-USD')
        assert r == expected_message

    @patch('aiohttp.ClientSession.get', new_callable=AsyncContextManagerMock)
    async def test_get_fundings(self, mock_get):
        message = [
          {
            "id": "b93d26cd-7193-4c8d-bfcc-446b2fe18f71",
            "order_id": "b93d26cd-7193-4c8d-bfcc-446b2fe18f71",
            "profile_id": "d881e5a6-58eb-47cd-b8e2-8d9f2e3ec6f6",
            "amount": "1057.6519956381537500",
            "status": "settled",
            "created_at": "2017-03-17T23:46:16.663397Z",
            "currency": "USD",
            "repaid_amount": "1057.6519956381537500",
            "default_amount": "0",
            "repaid_default": False
          },
          {
            "id": "280c0a56-f2fa-4d3b-a199-92df76fff5cd",
            "order_id": "280c0a56-f2fa-4d3b-a199-92df76fff5cd",
            "profile_id": "d881e5a6-58eb-47cd-b8e2-8d9f2e3ec6f6",
            "amount": "545.2400000000000000",
            "status": "outstanding",
            "created_at": "2017-03-18T00:34:34.270484Z",
            "currency": "USD",
            "repaid_amount": "532.7580047716682500"
          },
          {
            "id": "d6ec039a-00eb-4bec-a3e1-f5c6a97c4afc",
            "order_id": "d6ec039a-00eb-4bec-a3e1-f5c6a97c4afc",
            "profile_id": "d881e5a6-58eb-47cd-b8e2-8d9f2e3ec6f6",
            "amount": "9.9999999958500000",
            "status": "outstanding",
            "created_at": "2017-03-19T23:16:11.615181Z",
            "currency": "USD",
            "repaid_amount": "0"
          }
        ]
        expected_message = [
          {
            "id": "b93d26cd-7193-4c8d-bfcc-446b2fe18f71",
            "order_id": "b93d26cd-7193-4c8d-bfcc-446b2fe18f71",
            "profile_id": "d881e5a6-58eb-47cd-b8e2-8d9f2e3ec6f6",
            "amount": Decimal("1057.6519956381537500"),
            "status": "settled",
            "created_at": "2017-03-17T23:46:16.663397Z",
            "currency": "USD",
            "repaid_amount": Decimal("1057.6519956381537500"),
            "default_amount": Decimal("0"),
            "repaid_default": False
          },
          {
            "id": "280c0a56-f2fa-4d3b-a199-92df76fff5cd",
            "order_id": "280c0a56-f2fa-4d3b-a199-92df76fff5cd",
            "profile_id": "d881e5a6-58eb-47cd-b8e2-8d9f2e3ec6f6",
            "amount": Decimal("545.2400000000000000"),
            "status": "outstanding",
            "created_at": "2017-03-18T00:34:34.270484Z",
            "currency": "USD",
            "repaid_amount": Decimal("532.7580047716682500")
          },
          {
            "id": "d6ec039a-00eb-4bec-a3e1-f5c6a97c4afc",
            "order_id": "d6ec039a-00eb-4bec-a3e1-f5c6a97c4afc",
            "profile_id": "d881e5a6-58eb-47cd-b8e2-8d9f2e3ec6f6",
            "amount": Decimal("9.9999999958500000"),
            "status": "outstanding",
            "created_at": "2017-03-19T23:16:11.615181Z",
            "currency": "USD",
            "repaid_amount": Decimal("0")
          }
        ]

        mock_get.return_value.aenter.json = CoroutineMock(return_value=message)
        self.init()
        r = await self.client.get_fundings('status')
        assert r == expected_message

    @patch('aiohttp.ClientSession.post', new_callable=AsyncContextManagerMock)
    async def test_repay_funding(self, mock_post):
        mock_post.return_value.aenter.json = CoroutineMock(return_value={})
        self.init()
        r = await self.client.repay_funding(Decimal('10'), 'USD')
        assert type(r) is dict

    @patch('aiohttp.ClientSession.post', new_callable=AsyncContextManagerMock)
    async def test_margin_transfer(self, mock_post):
        message = {
          "created_at": "2017-01-25T19:06:23.415126Z",
          "id": "80bc6b74-8b1f-4c60-a089-c61f9810d4ab",
          "user_id": "521c20b3d4ab09621f000011",
          "profile_id": "cda95996-ac59-45a3-a42e-30daeb061867",
          "margin_profile_id": "45fa9e3b-00ba-4631-b907-8a98cbdf21be",
          "type": "deposit",
          "amount": "2",
          "currency": "USD",
          "account_id": "23035fc7-0707-4b59-b0d2-95d0c035f8f5",
          "margin_account_id": "e1d9862c-a259-4e83-96cd-376352a9d24d",
          "margin_product_id": "BTC-USD",
          "status": "completed",
          "nonce": 25
        }
        expected_message = {
          "created_at": "2017-01-25T19:06:23.415126Z",
          "id": "80bc6b74-8b1f-4c60-a089-c61f9810d4ab",
          "user_id": "521c20b3d4ab09621f000011",
          "profile_id": "cda95996-ac59-45a3-a42e-30daeb061867",
          "margin_profile_id": "45fa9e3b-00ba-4631-b907-8a98cbdf21be",
          "type": "deposit",
          "amount": Decimal("2"),
          "currency": "USD",
          "account_id": "23035fc7-0707-4b59-b0d2-95d0c035f8f5",
          "margin_account_id": "e1d9862c-a259-4e83-96cd-376352a9d24d",
          "margin_product_id": "BTC-USD",
          "status": "completed",
          "nonce": 25
        }
        mock_post.return_value.aenter.json = CoroutineMock(
            return_value=message)
        self.init()
        r = await self.client.margin_transfer('id', 'deposit',
                                              'USD', Decimal('2'))
        assert r == expected_message

    @patch('aiohttp.ClientSession.get', new_callable=AsyncContextManagerMock)
    async def test_get_position(self, mock_get):
        message = {
          "status": "active",
          "funding": {
            "max_funding_value": "10000",
            "funding_value": "622.48199522418175",
            "oldest_outstanding": {
              "id": "280c0a56-f2fa-4d3b-a199-92df76fff5cd",
              "order_id": "280c0a56-f2fa-4d3b-a199-92df76fff5cd",
              "created_at": "2017-03-18T00:34:34.270484Z",
              "currency": "USD",
              "account_id": "202af5e9-1ac0-4888-bdf5-15599ae207e2",
              "amount": "545.2400000000000000"
            }
          },
          "accounts": {
            "USD": {
              "id": "202af5e9-1ac0-4888-bdf5-15599ae207e2",
              "balance": "0.0000000000000000",
              "hold": "0.0000000000000000",
              "funded_amount": "622.4819952241817500",
              "default_amount": "0"
            },
            "BTC": {
              "id": "1f690a52-d557-41b5-b834-e39eb10d7df0",
              "balance": "4.7051564815292853",
              "hold": "0.6000000000000000",
              "funded_amount": "0.0000000000000000",
              "default_amount": "0"
            }
          },
          "margin_call": {
            "active": True,
            "price": "175.96000000",
            "side": "sell",
            "size": "4.70515648",
            "funds": "624.04210048"
          },
          "user_id": "521c20b3d4ab09621f000011",
          "profile_id": "d881e5a6-58eb-47cd-b8e2-8d9f2e3ec6f6",
          "position": {
            "type": "long",
            "size": "0.59968368",
            "complement": "-641.91999958602800000000000000",
            "max_size": "1.49000000"
          },
          "product_id": "BTC-USD"
        }
        expected_message = {
          "status": "active",
          "funding": {
            "max_funding_value": Decimal("10000"),
            "funding_value": Decimal("622.48199522418175"),
            "oldest_outstanding": {
              "id": "280c0a56-f2fa-4d3b-a199-92df76fff5cd",
              "order_id": "280c0a56-f2fa-4d3b-a199-92df76fff5cd",
              "created_at": "2017-03-18T00:34:34.270484Z",
              "currency": "USD",
              "account_id": "202af5e9-1ac0-4888-bdf5-15599ae207e2",
              "amount": Decimal("545.2400000000000000")
            }
          },
          "accounts": {
            "USD": {
              "id": "202af5e9-1ac0-4888-bdf5-15599ae207e2",
              "balance": Decimal("0.0000000000000000"),
              "hold": Decimal("0.0000000000000000"),
              "funded_amount": Decimal("622.4819952241817500"),
              "default_amount": Decimal("0")
            },
            "BTC": {
              "id": "1f690a52-d557-41b5-b834-e39eb10d7df0",
              "balance": Decimal("4.7051564815292853"),
              "hold": Decimal("0.6000000000000000"),
              "funded_amount": Decimal("0.0000000000000000"),
              "default_amount": Decimal("0")
            }
          },
          "margin_call": {
            "active": True,
            "price": Decimal("175.96000000"),
            "side": "sell",
            "size": Decimal("4.70515648"),
            "funds": Decimal("624.04210048")
          },
          "user_id": "521c20b3d4ab09621f000011",
          "profile_id": "d881e5a6-58eb-47cd-b8e2-8d9f2e3ec6f6",
          "position": {
            "type": "long",
            "size": Decimal("0.59968368"),
            "complement": Decimal("-641.91999958602800000000000000"),
            "max_size": Decimal("1.49000000")
          },
          "product_id": "BTC-USD"
        }
        mock_get.return_value.aenter.json = CoroutineMock(return_value=message)
        self.init()
        r = await self.client.get_position()
        assert r == expected_message

    @patch('aiohttp.ClientSession.post', new_callable=AsyncContextManagerMock)
    async def test_close_position(self, mock_post):
        mock_post.return_value.aenter.json = CoroutineMock(return_value={})
        self.init()
        r = await self.client.close_position()
        assert type(r) is dict

    @patch('aiohttp.ClientSession.post', new_callable=AsyncContextManagerMock)
    async def test_deposit(self, mock_post):
        message = {
            "amount": "10.00",
            "currency": "USD",
            "payment_method_id": "bc677162-d934-5f1a-968c-a496b1c1270b"
        }
        expected_message = {
            "amount": Decimal('10.00'),
            "currency": "USD",
            "payment_method_id": "bc677162-d934-5f1a-968c-a496b1c1270b"
        }
        mock_post.return_value.aenter.json = CoroutineMock(
            return_value=message)
        self.init()
        r = await self.client.deposit(Decimal('10.0'), 'id', 'USD')
        assert r == expected_message

    @patch('aiohttp.ClientSession.post', new_callable=AsyncContextManagerMock)
    async def test_coinbase_deposit(self, mock_post):
        message = {
            "amount": "10.00",
            "currency": "BTC",
            "payment_method_id": "bc677162-d934-5f1a-968c-a496b1c1270b"
        }
        expected_message = {
            "amount": Decimal('10.00'),
            "currency": "BTC",
            "payment_method_id": "bc677162-d934-5f1a-968c-a496b1c1270b"
        }
        mock_post.return_value.aenter.json = CoroutineMock(
            return_value=message)
        self.init()
        r = await self.client.coinbase_deposit(Decimal('10'), 'BTC', 'id')
        assert r == expected_message

    @patch('aiohttp.ClientSession.post', new_callable=AsyncContextManagerMock)
    async def test_withdraw(self, mock_post):
        message = {
            "id": "593533d2-ff31-46e0-b22e-ca754147a96a",
            "amount": "10.00",
            "currency": "USD",
            "payout_at": "2016-08-20T00:31:09Z"
        }
        expected_message = {
            "id": "593533d2-ff31-46e0-b22e-ca754147a96a",
            "amount": Decimal("10.00"),
            "currency": "USD",
            "payout_at": "2016-08-20T00:31:09Z"
        }
        mock_post.return_value.aenter.json = CoroutineMock(
            return_value=message)
        self.init()
        r = await self.client.withdraw(Decimal('10'), 'USD', 'id')
        assert r == expected_message

    @patch('aiohttp.ClientSession.post', new_callable=AsyncContextManagerMock)
    async def test_coinbase_withdraw(self, mock_post):
        message = {
            "amount": "10.00",
            "currency": "BTC",
            "payment_method_id": "bc677162-d934-5f1a-968c-a496b1c1270b"
        }
        expected_message = {
            "amount": Decimal('10.00'),
            "currency": "BTC",
            "payment_method_id": "bc677162-d934-5f1a-968c-a496b1c1270b"
        }
        mock_post.return_value.aenter.json = CoroutineMock(
            return_value=message)
        self.init()
        r = await self.client.coinbase_withdraw(Decimal('10'), 'USD', 'id')
        assert r == expected_message

    @patch('aiohttp.ClientSession.post', new_callable=AsyncContextManagerMock)
    async def test_crypto_withdraw(self, mock_post):
        message = {
            "amount": "10.00",
            "currency": "BTC",
            "payment_method_id": "bc677162-d934-5f1a-968c-a496b1c1270b"
        }
        expected_message = {
            "amount": Decimal('10.00'),
            "currency": "BTC",
            "payment_method_id": "bc677162-d934-5f1a-968c-a496b1c1270b"
        }
        mock_post.return_value.aenter.json = CoroutineMock(
            return_value=message)
        self.init()
        r = await self.client.crypto_withdraw(Decimal('10'), 'USD', 'addr')
        assert r == expected_message

    @patch('aiohttp.ClientSession.get', new_callable=AsyncContextManagerMock)
    async def test_get_payment_methods(self, mock_get):
        # NOTE: return values not converted
        message = [
            {
                "id": "bc6d7162-d984-5ffa-963c-a493b1c1370b",
                "type": "ach_bank_account",
                "name": "Bank of America - eBan... ********7134",
                "currency": "USD",
                "primary_buy": True,
                "primary_sell": True,
                "allow_buy": True,
                "allow_sell": True,
                "allow_deposit": True,
                "allow_withdraw": True,
                "limits": {
                    "buy": [
                        {
                            "period_in_days": 1,
                            "total": {
                                "amount": "10000.00",
                                "currency": "USD"
                            },
                            "remaining": {
                                "amount": "10000.00",
                                "currency": "USD"
                            }
                        }
                    ],
                    "instant_buy": [
                        {
                            "period_in_days": 7,
                            "total": {
                                "amount": "0.00",
                                "currency": "USD"
                            },
                            "remaining": {
                                "amount": "0.00",
                                "currency": "USD"
                            }
                        }
                    ],
                    "sell": [
                        {
                            "period_in_days": 1,
                            "total": {
                                "amount": "10000.00",
                                "currency": "USD"
                            },
                            "remaining": {
                                "amount": "10000.00",
                                "currency": "USD"
                            }
                        }
                    ],
                    "deposit": [
                        {
                            "period_in_days": 1,
                            "total": {
                                "amount": "10000.00",
                                "currency": "USD"
                            },
                            "remaining": {
                                "amount": "10000.00",
                                "currency": "USD"
                            }
                        }
                    ]
                }
            },
        ]
        mock_get.return_value.aenter.json = CoroutineMock(return_value=message)
        self.init()
        r = await self.client.get_payment_methods()
        assert r == message

    @patch('aiohttp.ClientSession.get', new_callable=AsyncContextManagerMock)
    async def test_get_coinbase_accounts(self, mock_get):
        message = [
            {
                "id": "fc3a8a57-7142-542d-8436-95a3d82e1622",
                "name": "ETH Wallet",
                "balance": "0.00000000",
                "currency": "ETH",
                "type": "wallet",
                "primary": False,
                "active": True
            },
            {
                "id": "2ae3354e-f1c3-5771-8a37-6228e9d239db",
                "name": "USD Wallet",
                "balance": "0.00",
                "currency": "USD",
                "type": "fiat",
                "primary": False,
                "active": True,
                "wire_deposit_information": {
                    "account_number": "0199003122",
                    "routing_number": "026013356",
                    "bank_name": "Metropolitan Commercial Bank",
                    "bank_address": "99 Park Ave 4th Fl New York, NY 10016",
                    "bank_country": {
                        "code": "US",
                        "name": "United States"
                    },
                    "account_name": "Coinbase, Inc",
                    "account_address": "548 Market Street, #23008, SF",
                    "reference": "BAOCAEUX"
                }
            },
            {
                "id": "1bfad868-5223-5d3c-8a22-b5ed371e55cb",
                "name": "BTC Wallet",
                "balance": "0.00000000",
                "currency": "BTC",
                "type": "wallet",
                "primary": True,
                "active": True
            },
            {
                "id": "2a11354e-f133-5771-8a37-622be9b239db",
                "name": "EUR Wallet",
                "balance": "0.00",
                "currency": "EUR",
                "type": "fiat",
                "primary": False,
                "active": True,
                "sepa_deposit_information": {
                    "iban": "EE957700771001355096",
                    "swift": "LHVBEE22",
                    "bank_name": "AS LHV Pank",
                    "bank_address": "Tartu mnt 2, 10145 Tallinn, Estonia",
                    "bank_country_name": "Estonia",
                    "account_name": "Coinbase UK, Ltd.",
                    "account_address": "9th Floor, 107 Cheapside, London",
                    "reference": "CBAEUXOVFXOXYX"
                }
            },
        ]
        expected_message = [
            {
                "id": "fc3a8a57-7142-542d-8436-95a3d82e1622",
                "name": "ETH Wallet",
                "balance": Decimal("0.00000000"),
                "currency": "ETH",
                "type": "wallet",
                "primary": False,
                "active": True
            },
            {
                "id": "2ae3354e-f1c3-5771-8a37-6228e9d239db",
                "name": "USD Wallet",
                "balance": Decimal("0.00"),
                "currency": "USD",
                "type": "fiat",
                "primary": False,
                "active": True,
                "wire_deposit_information": {
                    "account_number": "0199003122",
                    "routing_number": "026013356",
                    "bank_name": "Metropolitan Commercial Bank",
                    "bank_address": "99 Park Ave 4th Fl New York, NY 10016",
                    "bank_country": {
                        "code": "US",
                        "name": "United States"
                    },
                    "account_name": "Coinbase, Inc",
                    "account_address": "548 Market Street, #23008, SF",
                    "reference": "BAOCAEUX"
                }
            },
            {
                "id": "1bfad868-5223-5d3c-8a22-b5ed371e55cb",
                "name": "BTC Wallet",
                "balance": Decimal("0.00000000"),
                "currency": "BTC",
                "type": "wallet",
                "primary": True,
                "active": True
            },
            {
                "id": "2a11354e-f133-5771-8a37-622be9b239db",
                "name": "EUR Wallet",
                "balance": Decimal("0.00"),
                "currency": "EUR",
                "type": "fiat",
                "primary": False,
                "active": True,
                "sepa_deposit_information": {
                    "iban": "EE957700771001355096",
                    "swift": "LHVBEE22",
                    "bank_name": "AS LHV Pank",
                    "bank_address": "Tartu mnt 2, 10145 Tallinn, Estonia",
                    "bank_country_name": "Estonia",
                    "account_name": "Coinbase UK, Ltd.",
                    "account_address": "9th Floor, 107 Cheapside, London",
                    "reference": "CBAEUXOVFXOXYX"
                }
            },
        ]
        mock_get.return_value.aenter.json = CoroutineMock(return_value=message)
        self.init()
        r = await self.client.get_coinbase_accounts()
        assert r == expected_message

    @patch('aiohttp.ClientSession.post', new_callable=AsyncContextManagerMock)
    async def test_create_report(self, mock_post):
        message = {
            "id": "0428b97b-bec1-429e-a94c-59232926778d",
            "type": "fills",
            "status": "pending",
            "created_at": "2015-01-06T10:34:47.000Z",
            "completed_at": None,
            "expires_at": "2015-01-13T10:35:47.000Z",
            "file_url": None,
            "params": {
                "start_date": "2014-11-01T00:00:00.000Z",
                "end_date": "2014-11-30T23:59:59.000Z"
            }
        }
        mock_post.return_value.aenter.json = CoroutineMock(
            return_value=message)
        self.init()
        r = await self.client.create_report('fills', 'start', 'end',
                                            product_id='product_id',
                                            report_format='csv',
                                            email='email')
        assert r == message
        r = await self.client.create_report('account', 'start', 'end',
                                            account_id='account_id')
        assert r == message

        with pytest.raises(AssertionError):
            await self.client.create_report('fills', 'start', 'end')
        with pytest.raises(AssertionError):
            await self.client.create_report('account', 'start', 'end')
        with pytest.raises(AssertionError):
            await self.client.create_report('test', 'start', 'end')

    @patch('aiohttp.ClientSession.get', new_callable=AsyncContextManagerMock)
    async def test_get_report(self, mock_get):
        message = {
            "id": "0428b97b-bec1-429e-a94c-59232926778d",
            "type": "fills",
            "status": "ready",
            "created_at": "2015-01-06T10:34:47.000Z",
            "completed_at": "2015-01-06T10:35:47.000Z",
            "expires_at": "2015-01-13T10:35:47.000Z",
            "file_url": "https://example.com/0428b97b.../fills.pdf",
            "params": {
                "start_date": "2014-11-01T00:00:00.000Z",
                "end_date": "2014-11-30T23:59:59.000Z"
            }
        }
        mock_get.return_value.aenter.json = CoroutineMock(
            return_value=message)
        self.init()
        r = await self.client.get_report('report_id')
        assert r == message

    @patch('aiohttp.ClientSession.get', new_callable=AsyncContextManagerMock)
    async def test_get_trailing_volume(self, mock_get):
        message = [
            {
                "product_id": "BTC-USD",
                "exchange_volume": "11800.00000000",
                "volume": "100.00000000",
                "recorded_at": "1973-11-29T00:05:01.123456Z"
            },
            {
                "product_id": "LTC-USD",
                "exchange_volume": "51010.04100000",
                "volume": "2010.04100000",
                "recorded_at": "1973-11-29T00:05:02.123456Z"
            }
        ]
        expected_message = [
            {
                "product_id": "BTC-USD",
                "exchange_volume": Decimal("11800.00000000"),
                "volume": Decimal("100.00000000"),
                "recorded_at": "1973-11-29T00:05:01.123456Z"
            },
            {
                "product_id": "LTC-USD",
                "exchange_volume": Decimal("51010.04100000"),
                "volume": Decimal("2010.04100000"),
                "recorded_at": "1973-11-29T00:05:02.123456Z"
            }
        ]
        mock_get.return_value.aenter.json = CoroutineMock(return_value=message)
        self.init()
        r = await self.client.get_trailing_volume()
        assert r == expected_message

    @patch('aiohttp.ClientSession.get',
           new_callable=AsyncContextManagerMockPagination)
    async def test_pagination(self, mock_get):
        pages = [[{'id': 1}], [{'id': 2}]]
        mock_get.return_value.aenter.json = CoroutineMock(side_effect=pages)
        self.init()
        r = await self.client.get_account_history('id')
        assert r == [{'id': 1}, {'id': 2}]
