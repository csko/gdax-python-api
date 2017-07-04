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
        mock_post.return_value.aenter.json = CoroutineMock(return_value={})
        self.init()
        r = await self.client.buy(product_id='product_id')
        assert type(r) is dict

    @patch('aiohttp.ClientSession.post', new_callable=AsyncContextManagerMock)
    async def test_sell(self, mock_post):
        mock_post.return_value.aenter.json = CoroutineMock(return_value={})
        self.init()
        r = await self.client.sell(product_id='product_id')
        assert type(r) is dict

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
        mock_delete.return_value.aenter.json = CoroutineMock(return_value={})
        self.init()
        r = await self.client.cancel_all()
        assert type(r) is dict

    @patch('aiohttp.ClientSession.get', new_callable=AsyncContextManagerMock)
    async def test_get_order(self, mock_get):
        mock_get.return_value.aenter.json = CoroutineMock(return_value={})
        self.init()
        r = await self.client.get_order('order_id')
        assert type(r) is dict

    @patch('aiohttp.ClientSession.get', new_callable=AsyncContextManagerMock)
    async def test_get_orders(self, mock_get):
        mock_get.return_value.aenter.json = CoroutineMock(return_value={})
        self.init()
        r = await self.client.get_orders()
        assert type(r) is list

    @patch('aiohttp.ClientSession.get', new_callable=AsyncContextManagerMock)
    async def test_get_fills(self, mock_get):
        mock_get.return_value.aenter.json = CoroutineMock(return_value={})
        self.init()
        r = await self.client.get_fills()
        assert type(r) is list

    @patch('aiohttp.ClientSession.get', new_callable=AsyncContextManagerMock)
    async def test_get_fundings(self, mock_get):
        mock_get.return_value.aenter.json = CoroutineMock(return_value={})
        self.init()
        r = await self.client.get_fundings('status')
        assert type(r) is list

    @patch('aiohttp.ClientSession.post', new_callable=AsyncContextManagerMock)
    async def test_repay_funding(self, mock_post):
        mock_post.return_value.aenter.json = CoroutineMock(return_value={})
        self.init()
        r = await self.client.repay_funding(Decimal('10'), 'USD')
        assert type(r) is dict

    @patch('aiohttp.ClientSession.post', new_callable=AsyncContextManagerMock)
    async def test_margin_transfer(self, mock_post):
        mock_post.return_value.aenter.json = CoroutineMock(return_value={})
        self.init()
        r = await self.client.margin_transfer('id', 'deposit',
                                              'USD', Decimal('10'))
        assert type(r) is dict

    @patch('aiohttp.ClientSession.get', new_callable=AsyncContextManagerMock)
    async def test_get_position(self, mock_get):
        mock_get.return_value.aenter.json = CoroutineMock(return_value={})
        self.init()
        r = await self.client.get_position()
        assert type(r) is dict

    @patch('aiohttp.ClientSession.post', new_callable=AsyncContextManagerMock)
    async def test_close_position(self, mock_post):
        mock_post.return_value.aenter.json = CoroutineMock(return_value={})
        self.init()
        r = await self.client.close_position()
        assert type(r) is dict

    @patch('aiohttp.ClientSession.post', new_callable=AsyncContextManagerMock)
    async def test_deposit(self, mock_post):
        mock_post.return_value.aenter.json = CoroutineMock(return_value={})
        self.init()
        r = await self.client.deposit(Decimal('10.0'), 'id', 'USD')
        assert type(r) is dict

    @patch('aiohttp.ClientSession.post', new_callable=AsyncContextManagerMock)
    async def test_coinbase_deposit(self, mock_post):
        mock_post.return_value.aenter.json = CoroutineMock(return_value={})
        self.init()
        r = await self.client.coinbase_deposit(Decimal('10'), 'USD', 'id')
        assert type(r) is dict

    @patch('aiohttp.ClientSession.post', new_callable=AsyncContextManagerMock)
    async def test_withdraw(self, mock_post):
        mock_post.return_value.aenter.json = CoroutineMock(return_value={})
        self.init()
        r = await self.client.withdraw(Decimal('10'), 'USD', 'id')
        assert type(r) is dict

    @patch('aiohttp.ClientSession.post', new_callable=AsyncContextManagerMock)
    async def test_coinbase_withdraw(self, mock_post):
        mock_post.return_value.aenter.json = CoroutineMock(return_value={})
        self.init()
        r = await self.client.coinbase_withdraw(Decimal('10'), 'USD', 'id')
        assert type(r) is dict

    @patch('aiohttp.ClientSession.post', new_callable=AsyncContextManagerMock)
    async def test_crypto_withdraw(self, mock_post):
        mock_post.return_value.aenter.json = CoroutineMock(return_value={})
        self.init()
        r = await self.client.crypto_withdraw(Decimal('10'), 'USD', 'addr')
        assert type(r) is dict

    @patch('aiohttp.ClientSession.get', new_callable=AsyncContextManagerMock)
    async def test_get_payment_methods(self, mock_get):
        mock_get.return_value.aenter.json = CoroutineMock(return_value={})
        self.init()
        r = await self.client.get_payment_methods()
        assert type(r) is dict

    @patch('aiohttp.ClientSession.get', new_callable=AsyncContextManagerMock)
    async def test_get_coinbase_accounts(self, mock_get):
        mock_get.return_value.aenter.json = CoroutineMock(return_value={})
        self.init()
        r = await self.client.get_coinbase_accounts()
        assert type(r) is dict

    @patch('aiohttp.ClientSession.post', new_callable=AsyncContextManagerMock)
    async def test_create_report(self, mock_post):
        mock_post.return_value.aenter.json = CoroutineMock(return_value={})
        self.init()
        r = await self.client.create_report('fills', 'start', 'end',
                                            product_id='product_id',
                                            report_format='csv',
                                            email='email')
        assert type(r) is dict
        r = await self.client.create_report('account', 'start', 'end',
                                            account_id='account_id')
        assert type(r) is dict

        with pytest.raises(AssertionError):
            await self.client.create_report('fills', 'start', 'end')
        with pytest.raises(AssertionError):
            await self.client.create_report('account', 'start', 'end')
        with pytest.raises(AssertionError):
            await self.client.create_report('test', 'start', 'end')

    @patch('aiohttp.ClientSession.get', new_callable=AsyncContextManagerMock)
    async def test_get_report(self, mock_get):
        mock_get.return_value.aenter.json = CoroutineMock(return_value={})
        self.init()
        r = await self.client.get_report('report_id')
        assert type(r) is dict

    @patch('aiohttp.ClientSession.get', new_callable=AsyncContextManagerMock)
    async def test_get_trailing_volume(self, mock_get):
        mock_get.return_value.aenter.json = CoroutineMock(return_value={})
        self.init()
        r = await self.client.get_trailing_volume()
        assert type(r) is dict

    @patch('aiohttp.ClientSession.get',
           new_callable=AsyncContextManagerMockPagination)
    async def test_pagination(self, mock_get):
        pages = [[{'id': 1}], [{'id': 2}]]
        mock_get.return_value.aenter.json = CoroutineMock(side_effect=pages)
        self.init()
        r = await self.client.get_account_history('id')
        assert r == [{'id': 1}, {'id': 2}]
