"""Implements an order book based on GDAX's Websocket endpoint.

See: https://docs.gdax.com/#websocket-feed.

"""

import asyncio
from decimal import Decimal
import json
import logging
from operator import itemgetter

from sortedcontainers import SortedDict
import aiohttp

import gdax.trader
import gdax.utils
from gdax.websocket_feed_listener import WebSocketFeedListener


class OrderBookError(Exception):
    pass


class OrderBook(WebSocketFeedListener):
    def __init__(self, product_ids='ETH-USD', api_key=None, api_secret=None,
                 passphrase=None, use_heartbeat=False,
                 trade_log_file_path=None):

        super().__init__(product_ids=product_ids,
                         api_key=api_key,
                         api_secret=api_secret,
                         passphrase=passphrase,
                         use_heartbeat=use_heartbeat,
                         trade_log_file_path=trade_log_file_path)

        if not isinstance(product_ids, list):
            product_ids = [product_ids]

        self.traders = {product_id: gdax.trader.Trader(product_id=product_id)
                        for product_id in product_ids}
        self._asks = {product_id: SortedDict() for product_id in product_ids}
        self._bids = {product_id: SortedDict() for product_id in product_ids}
        self._sequences = {product_id: None for product_id in product_ids}

    async def __aenter__(self):
        await super().__aenter__()

        # get order book snapshot
        books = await asyncio.gather(
            *[trader.get_product_order_book(level=3)
              for trader in self.traders.values()]
        )
        if self._trade_file:
            await asyncio.gather(
                *[self._trade_file.write(
                    f'B {product_id} {json.dumps(book)}\n')
                  for product_id, book in zip(self.product_ids, books)])

        for product_id, book in zip(self.product_ids, books):
            for bid in book['bids']:
                self.add(product_id, {
                    'id': bid[2],
                    'side': 'buy',
                    'price': Decimal(bid[0]),
                    'size': Decimal(bid[1])
                })
            for ask in book['asks']:
                self.add(product_id, {
                    'id': ask[2],
                    'side': 'sell',
                    'price': Decimal(ask[0]),
                    'size': Decimal(ask[1])
                })
            self._sequences[product_id] = book['sequence']
        return self

    async def handle_message(self):
        try:
            message = await self._recv()
        except aiohttp.ServerDisconnectedError as exc:
            logging.error(
                f'Error: Exception: f{exc}. Re-initializing websocket.')
            await self.__aexit__(None, None, None)
            await self.__aenter__()
            return

        msg_type = message['type']

        if msg_type == 'error':
            raise OrderBookError(f'Error: {message["message"]}')

        if msg_type == 'subscriptions':
            return  # must filter out here because the subscriptions message does not have a product_id key

        product_id = message['product_id']
        assert self._sequences[product_id] is not None
        sequence = message['sequence']

        if sequence <= self._sequences[product_id]:
            # ignore older messages (e.g. before order book initialization
            # from getProductOrderBook)
            return message
        elif sequence > self._sequences[product_id] + 1:
            logging.error(
                'Error: messages missing ({} - {}). Re-initializing websocket.'
                .format(sequence, self._sequences[product_id]))
            await self.__aexit__(None, None, None)
            await self.__aenter__()
            return

        if msg_type == 'open':
            self.add(product_id, message)
        elif msg_type == 'done' and 'price' in message:
            self.remove(product_id, message)
        elif msg_type == 'match':
            self.match(product_id, message)
        elif msg_type == 'change':
            self.change(product_id, message)
        elif msg_type == 'heartbeat':
            pass
        elif msg_type == 'received':
            pass
        elif msg_type == 'done':
            pass
        else:
            raise OrderBookError(f'unknown message type {msg_type}')

        self._sequences[product_id] = sequence
        return message

    def add(self, product_id, order):
        order = {
            'id': order.get('order_id') or order['id'],
            'side': order['side'],
            'price': Decimal(order['price']),
            'size': Decimal(order.get('size') or order['remaining_size'])
        }
        if order['side'] == 'buy':
            bids = self.get_bids(product_id, order['price'])
            if bids is None:
                bids = [order]
            else:
                bids.append(order)
            self.set_bids(product_id, order['price'], bids)
        else:
            asks = self.get_asks(product_id, order['price'])
            if asks is None:
                asks = [order]
            else:
                asks.append(order)
            self.set_asks(product_id, order['price'], asks)

    def remove(self, product_id, order):
        price = Decimal(order['price'])
        if order['side'] == 'buy':
            bids = self.get_bids(product_id, price)
            if bids is not None:
                bids = [o for o in bids if o['id'] != order['order_id']]
                if bids:
                    self.set_bids(product_id, price, bids)
                else:
                    self.remove_bids(product_id, price)
        else:
            asks = self.get_asks(product_id, price)
            if asks is not None:
                asks = [o for o in asks if o['id'] != order['order_id']]
                if asks:
                    self.set_asks(product_id, price, asks)
                else:
                    self.remove_asks(product_id, price)

    def match(self, product_id, order):
        size = Decimal(order['size'])
        price = Decimal(order['price'])

        if order['side'] == 'buy':
            bids = self.get_bids(product_id, price)
            if not bids:
                return
            assert bids[0]['id'] == order['maker_order_id']
            if bids[0]['size'] == size:
                self.set_bids(product_id, price, bids[1:])
            else:
                bids[0]['size'] -= size
                self.set_bids(product_id, price, bids)
        else:
            asks = self.get_asks(product_id, price)
            if not asks:
                return
            assert asks[0]['id'] == order['maker_order_id']
            if asks[0]['size'] == size:
                self.set_asks(product_id, price, asks[1:])
            else:
                asks[0]['size'] -= size
                self.set_asks(product_id, price, asks)

    def change(self, product_id, order):
        if 'new_size' not in order:
            # market order
            # TODO
            raise NotImplementedError(
                'change operation not implemented with missing new_size')
        else:
            new_size = Decimal(order['new_size'])

        tree = (self._asks[product_id] if order['side'] == 'sell'
                else self._bids[product_id])

        if 'price' in order:
            price = Decimal(order['price'])
        else:
            # missing price means market price
            price = (tree.min_key() if order['side'] == 'sell'
                     else tree.max_key())

        node = tree.get(price)

        # TODO: check old_size
        if node is None or not any(o['id'] == order['order_id'] for o in node):
            return

        index = list(map(itemgetter('id'), node)).index(order['order_id'])
        if 'new_size' in order:
            node[index]['size'] = new_size
        if 'new_funds' in order:  # pragma: no cover
            assert False, 'This should not happen.'

    def get_current_book(self, product_id):
        result = {
            'sequence': self._sequences[product_id],
            'asks': [],
            'bids': [],
        }
        for ask in self._asks[product_id]:
            try:
                # There can be a race condition here, where a price point is
                # removed between these two ops
                this_ask = self._asks[product_id][ask]
            except KeyError:
                continue
            for order in this_ask:
                result['asks'].append(
                    [order['price'], order['size'], order['id']])
        for bid in self._bids[product_id]:
            try:
                # There can be a race condition here, where a price point is
                # removed between these two ops
                this_bid = self._bids[product_id][bid]
            except KeyError:
                continue
            for order in this_bid:
                result['bids'].append(
                    [order['price'], order['size'], order['id']])
        return result

    def get_ask(self, product_id):
        return self._asks[product_id].iloc[0]

    def get_asks(self, product_id, price):
        return self._asks[product_id].get(price)

    def remove_asks(self, product_id, price):
        del self._asks[product_id][price]

    def set_asks(self, product_id, price, asks):
        self._asks[product_id].update({price: asks})

    def get_bid(self, product_id):
        return self._bids[product_id].iloc[-1]

    def get_bids(self, product_id, price):
        return self._bids[product_id].get(price)

    def remove_bids(self, product_id, price):
        del self._bids[product_id][price]

    def set_bids(self, product_id, price, bids):
        self._bids[product_id].update({price: bids})

    def get_min_ask_depth(self, product_id):
        orders = self._asks[product_id].get(self._asks[product_id].iloc[0])
        return sum([order['size'] for order in orders])

    def get_max_bid_depth(self, product_id):
        orders = self._bids[product_id].get(self._bids[product_id].iloc[-1])
        return sum([order['size'] for order in orders])


async def run_orderbook():  # pragma: no cover
    async with OrderBook(
        ['ETH-USD', 'BTC-USD'],
        api_key=None,
        api_secret=None,
        passphrase=None,
        # trade_log_file_path='trades.txt',
    ) as orderbook:
        while True:
            message = await orderbook.handle_message()
            if message is None:
                continue
            product_id = message['product_id']
            logging.info('%20s %10s %10s %10s %10s',
                         orderbook._sequences[product_id],
                         orderbook.get_bid('ETH-USD'),
                         orderbook.get_ask('ETH-USD'),
                         orderbook.get_bid('BTC-USD'),
                         orderbook.get_ask('BTC-USD'))
            logging.info('ask: %s bid: %s',
                         orderbook.get_min_ask_depth('ETH-USD'),
                         orderbook.get_max_bid_depth('ETH-USD'))

if __name__ == "__main__":  # pragma: no cover
    logging.getLogger().setLevel(logging.INFO)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_orderbook())
