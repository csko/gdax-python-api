"""
Base class for listening to web socket feed messages based on GDAX's Websocket endpoint.

See: https://docs.gdax.com/#websocket-feed.

"""

import asyncio
import ujson as json

import time

import aiofiles
import aiohttp

import gdax.utils

from abc import ABC, abstractmethod


class WebSocketFeedListener(ABC):
    def __init__(self, product_ids='ETH-USD', channels=None, api_key=None, api_secret=None,
                 passphrase=None, use_heartbeat=False,
                 trade_log_file_path=None):
        if api_key is not None:
            self._authenticated = True
            self.api_key = api_key
            self.api_secret = api_secret
            self.passphrase = passphrase
        else:
            self._authenticated = False

        if not isinstance(product_ids, list):
            product_ids = [product_ids]
        self.product_ids = product_ids

        self.channels = None
        if channels is not None:
            if not isinstance(channels, list):
                channels = [channels]
            self.channels = channels

        self.use_heartbeat = use_heartbeat
        self.trade_log_file_path = trade_log_file_path
        self._trade_file = None

        self._ws_session = None
        self._ws_connect = None
        self._ws = None

    async def _init(self):
        self._ws_session = aiohttp.ClientSession()
        self._ws_connect = self._ws_session.ws_connect(
            'wss://ws-feed.gdax.com')
        self._ws = await self._ws_connect.__aenter__()

        # subscribe
        await self._subscribe()

        if self.use_heartbeat:
            await self._send(type="heartbeat", on=True)

    async def __aenter__(self):
        await asyncio.gather(self._init(), self._open_log_file())

        return self

    async def __aexit__(self, exc_type, exc, traceback):
        res = await asyncio.gather(
            self._ws_session.__aexit__(exc_type, exc, traceback),
            self._close_log_file(),
        )
        return res[0]

    async def _open_log_file(self):
        if self.trade_log_file_path is not None:
            self._trade_file = await aiofiles.open(self.trade_log_file_path,
                                                   mode='a').__aenter__()

    async def _close_log_file(self):
        if self._trade_file is not None:
            await self._trade_file.__aexit__(None, None, None)

    async def _send(self, **kwargs):
        await self._ws.send_json(kwargs)

    async def _recv(self):
        json_data = await self._ws.receive_str()
        if self._trade_file:
            await self._trade_file.write(f'W {json_data}\n')
        return json.loads(json_data)

    async def _subscribe(self):
        message = {
            'type': 'subscribe',
            'product_ids': self.product_ids,
        }

        if self.channels is not None:
            message['channels'] = self.channels

        if self._authenticated:
            path = '/users/self'
            method = 'GET'
            body = ''
            timestamp = str(time.time())

            message['signature'] = gdax.utils.get_signature(
                path, method, body, timestamp, self.api_secret)
            message['timestamp'] = timestamp
            message['key'] = self.api_key
            message['passphrase'] = self.passphrase

        return await self._send(**message)

    @abstractmethod
    async def handle_message(self):
        pass
