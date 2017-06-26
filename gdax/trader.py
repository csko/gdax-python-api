"""GDAX Trading API client.

JSON client for interacting with api.gdax.com.

"""

import copy
import json
import logging
import time
import hmac
import hashlib

import asyncio
import aiohttp
import async_timeout

import gdax.utils


class Trader(object):
    API_URL = "https://api.gdax.com"

    def __init__(self, product_id='ETH-USD', api_key=None, api_secret=None,
                 passphrase=None, timeout_sec=10):
        self.product_id = product_id
        if api_key is not None:
            self.authenticated = True
            self.api_key = api_key
            self.api_secret = api_secret
            self.passphrase = passphrase
        else:
            self.authenticated = False
        self._clientsession = aiohttp.ClientSession()
        self.session = self._clientsession.__enter__()
        self.timeout_sec = timeout_sec

    def __del__(self):
        self.session = self._clientsession.__exit__(None, None, None)

    def _auth_headers(self, path, method, body=''):
        timestamp = str(time.time())
        return {
            'Content-Type': 'application/json',
            'CB-ACCESS-SIGN': gdax.utils.get_signature(path, method, body,
                                                       timestamp,
                                                       self.api_secret),
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-PASSPHRASE': self.passphrase,
        }

    async def _get(self, path, params=None, pagination=False):
        if params is None:
            params_copy = {}
        else:
            params_copy = copy.deepcopy(params)

        results = []
        while True:
            with async_timeout.timeout(self.timeout_sec):
                path_with_params = path
                if params_copy:
                    path_with_params += '?'
                    path_with_params += '&'.join(
                        f'{k}={v}' for k, v in params_copy.items())

                if self.authenticated:
                    headers = self._auth_headers(path_with_params,
                                                 method='GET')
                else:
                    headers = None
                async with self.session.get(self.API_URL + path_with_params,
                                            headers=headers,
                                            encoding='ascii') as response:
                    response.raise_for_status()
                    res = await response.json()
                    if pagination:
                        results += res
                        resp_headers = response.headers
                        if "cb-after" in resp_headers:
                            params_copy['after'] = resp_headers['cb-after']
                        else:
                            return results
                    else:
                        return res

    async def _post(self, path, data=None):
        json_data = json.dumps(data)
        headers = self._auth_headers(path, method='POST', body=json_data)
        path_url = self.API_URL + path
        with async_timeout.timeout(self.timeout_sec):
            async with self.session.post(path_url,
                                         headers=headers,
                                         data=json_data) as response:
                res = await response.json()
                response.raise_for_status()
                return res

    async def _delete(self, path, data=None):
        json_data = json.dumps(data)
        headers = self._auth_headers(path, method='DELETE', body=json_data)
        path_url = self.API_URL + path
        with async_timeout.timeout(self.timeout_sec):
            async with self.session.delete(path_url,
                                           headers=headers,
                                           data=json_data) as response:
                response.raise_for_status()
                return await response.json()

    async def get_products(self):
        return await self._get('/products')

    async def get_product_ticker(self, product_id=None):
        return await self._get(
            '/products/{}/ticker'.format(product_id or self.product_id))

    async def get_product_trades(self, product_id=None):
        return await self._get(
            '/products/{}/trades'.format(product_id or self.product_id))

    async def get_product_order_book(self, product_id=None, level=1):
        params = {'level': level}
        return await self._get(
            '/products/{}/book'.format(product_id or self.product_id),
            params=params)

    async def get_product_historic_rates(self, product_id=None, start='',
                                         end='', granularity=''):
        payload = {}
        payload["start"] = start
        payload["end"] = end
        payload["granularity"] = granularity
        return await self._get(
            '/products/{}/candles'.format(product_id or self.product_id),
            params=payload)

    async def get_product_24hr_stats(self, product_id=None):
        return await self._get(
            '/products/{}/stats'.format(product_id or self.product_id))

    async def get_currencies(self):
        return await self._get('/currencies')

    async def get_time(self):
        return await self._get('/time')

    # authenticated API
    async def get_account(self, account_id=''):
        assert self.authenticated
        return await self._get(f'/accounts/{account_id}')

    async def get_account_history(self, account_id):
        assert self.authenticated
        return await self._get(f'/accounts/{account_id}/ledger',
                               pagination=True)

    async def get_account_holds(self, account_id):
        assert self.authenticated
        return await self._get(f'/accounts/{account_id}/holds',
                               pagination=True)

    async def buy(self, product_id=None, price=None, size=None, funds=None,
                  **kwargs):
        assert self.authenticated
        payload = {}
        payload['side'] = 'buy'
        payload['product_id'] = product_id or self.product_id

        if price is not None:
            payload['price'] = str(price)
        if size is not None:
            payload['size'] = str(size)
        if funds is not None:
            payload['funds'] = str(funds)
        payload.update(kwargs)

        return await self._post('/orders', data=payload)

    async def sell(self, product_id=None, price=None, size=None, funds=None,
                   **kwargs):
        assert self.authenticated
        payload = {}
        payload['side'] = 'sell'
        payload['product_id'] = product_id or self.product_id

        if price is not None:
            payload['price'] = str(price)
        if size is not None:
            payload['size'] = str(size)
        if funds is not None:
            payload['funds'] = str(funds)

        payload.update(kwargs)

        return await self._post('/orders', data=payload)

    async def cancel_order(self, order_id):
        assert self.authenticated
        return await self._delete(f'/orders/{order_id}')

    async def cancel_all(self, data=None, product_id=''):
        assert self.authenticated
        payload = {'product_id': product_id}
        return await self._delete('/orders/', data=payload)

    async def get_order(self, order_id):
        assert self.authenticated
        return await self._get(f'/orders/{order_id}')

    async def get_orders(self):
        assert self.authenticated
        return await self._get('/orders', pagination=True)

    async def get_fills(self, order_id='', product_id=''):
        assert self.authenticated
        params = {}
        if order_id:
            params['order_id'] = order_id
        if product_id:
            params['product_id'] = product_id or self.product_id
        return await self._get('/fills', params=params, pagination=True)

    async def get_fundings(self, status):
        assert self.authenticated
        params = {}
        if status:
            params['status'] = status
        return await self._get('/funding', params=params, pagination=True)

    async def repay_funding(self, amount, currency):
        assert self.authenticated
        payload = {
            "amount": str(amount),
            "currency": currency,  # example: USD
        }
        return await self._post('/funding/repay', data=payload)

    async def margin_transfer(self, margin_profile_id, transfer_type,
                              currency, amount):
        assert self.authenticated
        payload = {
            "margin_profile_id": margin_profile_id,
            "type": transfer_type,
            "currency": currency,  # example: USD
            "amount": str(amount),
        }
        return await self._post('/profiles/margin-transfer', data=payload)

    async def get_position(self):
        assert self.authenticated
        return await self._get('/position')

    async def close_position(self, repay_only=False):
        assert self.authenticated
        payload = {
            "repay_only": repay_only
        }
        return await self._post('/position/close', data=payload)

    async def deposit(self, amount, currency, payment_method_id):
        assert self.authenticated
        payload = {
            "amount": str(amount),
            "currency": currency,
            "payment_method_id": payment_method_id,
        }
        return await self._post('/deposits/payment-method', data=payload)

    async def coinbase_deposit(self, amount, currency, coinbase_account_id):
        assert self.authenticated
        payload = {
            "amount": str(amount),
            "currency": currency,
            "coinbase_account_id": coinbase_account_id,
        }
        return await self._post('/deposits/coinbase-account', data=payload)

    async def withdraw(self, amount, currency, payment_method_id):
        assert self.authenticated
        payload = {
            "amount": str(amount),
            "currency": currency,
            "payment_method_id": payment_method_id,
        }
        return await self._post('/withdrawals/payment-method', data=payload)

    async def coinbase_withdraw(self, amount, currency, coinbase_account_id):
        assert self.authenticated
        payload = {
            "amount": str(amount),
            "currency": currency,
            "coinbase_account_id": coinbase_account_id,
        }
        return await self._post('/withdrawals/coinbase', data=payload)

    async def crypto_withdraw(self, amount, currency, crypto_address):
        assert self.authenticated
        payload = {
            "amount": str(amount),
            "currency": currency,
            "crypto_address": crypto_address
        }
        return await self._post('/withdrawals/crypto', data=payload)

    async def get_payment_methods(self):
        assert self.authenticated
        return await self._get('/payment-methods')

    async def get_coinbase_accounts(self):
        assert self.authenticated
        return await self._get('/coinbase-accounts')

    async def create_report(self, report_type, start_date, end_date,
                            product_id=None, account_id=None,
                            report_format=None, email=None):
        assert self.authenticated
        payload = {
            "type": report_type,
            "start_date": start_date,
            "end_date": end_date,
        }
        if report_type == 'fills':
            assert product_id is not None, \
                'product_id is required if report_type is fills'
        elif report_type == 'account':
            assert account_id is not None, \
                'account_id is required if report_type is account'
        else:
            assert False, \
                f'report_type must be one of fills or account, {report_type}' \
                ' given'
        if product_id is not None:
            payload['product_id'] = product_id
        if account_id is not None:
            payload['account_id'] = account_id
        if report_format is not None:
            payload['format'] = report_format
        if email is not None:
            payload['email'] = email
        return await self._post('/reports', data=payload)

    async def get_report(self, report_id):
        assert self.authenticated
        return await self._get(f'/reports/{report_id}')

    async def get_trailing_volume(self):
        assert self.authenticated
        return await self._get("/users/self/trailing-volume")


async def main():
    trader = Trader(product_id='BTC-USD',
                    api_key=None,
                    api_secret=None,
                    passphrase=None,)
    res = await asyncio.gather(
        trader.get_products(),
        trader.get_product_ticker(),
        trader.get_time(),
        # trader.buy(type='limit', size='0.01', price='2500.12'),
    )
    logging.info(res)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
