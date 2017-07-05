import copy
import json
import base64
from decimal import Decimal

import aiohttp
import pytest
from asynctest import patch, CoroutineMock, call

import gdax
import gdax.orderbook

from tests.helpers import AsyncContextManagerMock, generate_id


id1 = generate_id()
id2 = generate_id()


bids1 = [
    [Decimal("2525.00"), Decimal("1.5"), generate_id()],
    [Decimal("2595.52"), Decimal("100"), id2],
    [Decimal("2595.52"), Decimal("2"), id1],
    [Decimal("2595.62"), Decimal("1.41152763"), id2],
    [Decimal("2595.70"), Decimal("1.5"), generate_id()],
]
asks1 = [
    [Decimal("2596.74"), Decimal("0.2"), generate_id()],
    [Decimal("2596.77"), Decimal("0.07670504"), generate_id()],
    [Decimal("2615.1"), Decimal("0.011"), generate_id()],
    [Decimal("2620.05"), Decimal("0.02"), id1],
    [Decimal("2620.1"), Decimal("100"), generate_id()],
    [Decimal("2620.18"), Decimal("0.01"), id1],
    [Decimal("2620.18"), Decimal("0.02"), id2],
]
sequence = 3419033239


def _book():
    return copy.deepcopy({
        "sequence": sequence,
        "bids": bids1,
        "asks": asks1,
    })


bids1_internal = {
    Decimal("2525.00"): [{
        'price': Decimal('2525.00'),
        'side': 'buy',
        'size': Decimal('1.5'),
        'id': bids1[0][2]}],
    Decimal('2595.52'): [{
        'price': Decimal('2595.52'),
        'side': 'buy',
        'size': Decimal('100'),
        'id': id2}, {
        'price': Decimal('2595.52'),
        'side': 'buy',
        'size': Decimal('2'),
        'id': id1}],
    Decimal('2595.62'): [{
        'price': Decimal('2595.62'),
        'side': 'buy',
        'size': Decimal('1.41152763'),
        'id': id2}],
    Decimal('2595.70'): [{
        'price': Decimal('2595.70'),
        'side': 'buy',
        'size': Decimal('1.5'),
        'id': bids1[4][2]}],
}

asks1_internal = {
    Decimal("2596.74"): [{
         'price': Decimal("2596.74"),
         'side': 'sell',
         'size': Decimal("0.2"),
         'id': asks1[0][2]}],
    Decimal("2596.77"): [{
         'price': Decimal("2596.77"),
         'side': 'sell',
         'size': Decimal("0.07670504"),
         'id': asks1[1][2]}],
    Decimal("2620.05"): [{
         'price': Decimal("2620.05"),
         'side': 'sell',
         'size': Decimal("0.02"),
         'id': id1}],
    Decimal("2620.1"): [{
          'price': Decimal("2620.1"),
          'side': 'sell',
          'size': Decimal("100"),
          'id': asks1[4][2],
          }],
    Decimal("2620.18"): [{
        'price': Decimal("2620.18"),
        'side': 'sell',
        'size': Decimal("0.01"),
        'id': id1}, {
        'price': Decimal("2620.18"),
        'side': 'sell',
        'size': Decimal("0.02"),
        'id': id2}],
    Decimal("2615.1"): [{
          'price': Decimal("2615.1"),
          'side': 'sell',
          'size': Decimal("0.011"),
          'id': asks1[2][2]}],
}


@pytest.mark.asyncio
@patch('aiohttp.ClientSession.ws_connect',
       new_callable=AsyncContextManagerMock)
class TestOrderbook(object):
    @patch('gdax.trader.Trader.get_product_order_book')
    async def test_basic_init(self, mock_book, mock_connect):
        mock_connect.return_value.aenter.send_json = CoroutineMock()
        mock_book.return_value = _book()

        product_id = 'ETH-USD'
        product_ids = [product_id]
        async with gdax.orderbook.OrderBook(product_ids) as orderbook:
            msg = {'type': 'subscribe', 'product_ids': product_ids}
            mock_connect.return_value.aenter.send_json.assert_called_with(msg)

            mock_book.assert_called_with(level=3)

            assert dict(orderbook._asks[product_id].items()) == asks1_internal
            assert dict(orderbook._bids[product_id].items()) == bids1_internal
            assert orderbook._sequences[product_id] == sequence

            assert orderbook.get_current_book(product_id) == {
                "sequence": 3419033239,
                "bids": bids1,
                "asks": asks1,
            }

            assert orderbook.get_ask(product_id) == Decimal('2596.74')
            assert orderbook.get_bid(product_id) == Decimal('2595.70')

            assert orderbook.get_asks(product_id, Decimal("2620.18")) == [{
                'price': Decimal("2620.18"),
                'side': 'sell',
                'size': Decimal("0.01"),
                'id': id1}, {
                'price': Decimal("2620.18"),
                'side': 'sell',
                'size': Decimal("0.02"),
                'id': id2}]
            assert orderbook.get_bids(product_id, Decimal("2595.52")) == [{
                'price': Decimal('2595.52'),
                'side': 'buy',
                'size': Decimal('100'),
                'id': id2}, {
                'price': Decimal('2595.52'),
                'side': 'buy',
                'size': Decimal('2'),
                'id': id1}]
            assert orderbook.get_asks(product_id, Decimal("123")) is None
            assert orderbook.get_bids(product_id, Decimal("123")) is None

            assert orderbook.get_min_ask_depth(product_id) == Decimal('0.2')
            assert orderbook.get_max_bid_depth(product_id) == Decimal('1.5')

    @patch('gdax.trader.Trader.get_product_order_book')
    async def test_heartbeat(self, mock_book, mock_connect):
        mock_connect.return_value.aenter.send_json = CoroutineMock()
        mock_connect.return_value.aenter.receive_str = CoroutineMock()

        mock_book.return_value = {'bids': [], 'asks': [], 'sequence': 1}
        message_expected = {
          "type": "heartbeat",
          "last_trade_id": 17393422,
          "product_id": "ETH-USD",
          "sequence": 2,
          "time": "2017-06-25T11:23:14.838000Z"
        }
        mock_connect.return_value.aenter.receive_str.side_effect = [
            json.dumps(message_expected),
        ]
        product_ids = ['ETH-USD']
        async with gdax.orderbook.OrderBook(product_ids,
                                            use_heartbeat=True) as orderbook:
            subscribe_msg = {'type': 'subscribe', 'product_ids': product_ids}
            heartbeat_msg = {'type': 'heartbeat', 'on': True}
            calls = [call(subscribe_msg), call(heartbeat_msg)]
            mock_connect.return_value.aenter.send_json.assert_has_calls(calls)

            message = await orderbook.handle_message()
            assert message == message_expected

    @patch('gdax.trader.Trader.get_product_order_book')
    async def test_authentication(self, mock_book, mock_connect, mocker):
        mock_connect.return_value.aenter.send_json = CoroutineMock()
        mock_book.return_value = {'bids': [], 'asks': [], 'sequence': 1}
        timestamp = '1493343391.076892'
        mocker.patch('time.time', return_value=timestamp)
        product_ids = ['ETH-USD']
        async with gdax.orderbook.OrderBook(
            product_ids,
            api_key='a',
            api_secret=base64.b64encode(b'a' * 64),
            passphrase='b',
        ) as orderbook:
            msg = {
                'type': 'subscribe',
                'product_ids': product_ids,
                'signature': '5qne58tAXSW3OJlU/GoC+/mTLF1xgT8vucjJWFZzhsU=',
                'timestamp': timestamp,
                'key': 'a',
                'passphrase': 'b',
                }
            assert orderbook._authenticated
            mock_connect.return_value.aenter.send_json.assert_called_with(msg)

    @patch('gdax.trader.Trader.get_product_order_book')
    async def test_basic_message(self, mock_book, mock_connect):
        mock_connect.return_value.aenter.receive_str = CoroutineMock()
        mock_connect.return_value.aenter.send_json = CoroutineMock()
        mock_book.return_value = {'bids': [], 'asks': [], 'sequence': 1}
        message_expected = {
              "type": "done",
              "side": "sell",
              "order_id": "4eef1226-4b38-422c-a5b1-56def7107f9a",
              "reason": "canceled",
              "product_id": "BTC-USD",
              "price": "2601.76000000",
              "remaining_size": "3.09000000",
              "sequence": 2,
              "time": "2017-06-25T11:23:14.775000Z"
            }
        mock_connect.return_value.aenter.receive_str.side_effect = [
            json.dumps(message_expected),
        ]
        async with gdax.orderbook.OrderBook('BTC-USD') as orderbook:
            assert orderbook.product_ids == ['BTC-USD']
            message = await orderbook.handle_message()
            assert message == message_expected

    @patch('gdax.trader.Trader.get_product_order_book')
    async def test_logfile(self, mock_book, mock_connect):
        mock_connect.return_value.aenter.receive_str = CoroutineMock()
        mock_connect.return_value.aenter.send_json = CoroutineMock()
        message_expected = {
              "type": "done",
              "side": "sell",
              "order_id": "4eef1226-4b38-422c-a5b1-56def7107f9a",
              "reason": "canceled",
              "product_id": "ETH-USD",
              "price": "2601.76000000",
              "remaining_size": "3.09000000",
              "sequence": 2,
              "time": "2017-06-25T11:23:14.775000Z"
            }
        mock_connect.return_value.aenter.receive_str.side_effect = [
            json.dumps(message_expected)
        ]
        product_id = 'ETH-USD'
        book = {'bids': [], 'asks': [], 'sequence': 1}
        mock_book.return_value = book
        calls = [call(f'B {product_id} {json.dumps(book)}\n')]
        with patch('aiofiles.open',
                   new_callable=AsyncContextManagerMock) as mock_open:
            mock_open.return_value.aenter.write = CoroutineMock()
            mock_write = mock_open.return_value.aenter.write
            async with gdax.orderbook.OrderBook(
                    [product_id],
                    trade_log_file_path='trades.txt') as orderbook:

                mock_write.assert_has_calls(calls)

                await orderbook.handle_message()
                calls.append(call(f'W {json.dumps(message_expected)}\n'))
                mock_write.assert_has_calls(calls)

    @patch('gdax.trader.Trader.get_product_order_book')
    async def test_orderbook_advanced(self, mock_book, mock_connect):
        product_id = 'BTC-USD'
        mock_book.return_value = _book()
        mock_connect.return_value.aenter.receive_str = CoroutineMock()
        mock_connect.return_value.aenter.send_json = CoroutineMock()
        messages_expected = [
            {  # ignored
              "type": "received",
              "product_id": product_id,
              "sequence": sequence - 1,
            },
            {  # ignored
              "type": "received",
              "order_id": "26c22ff5-01b1-4ca3-859c-6349d6eb06b4",
              "order_type": "limit",
              "size": "0.10000000",
              "price": "2602.22000000",
              "side": "sell",
              "product_id": product_id,
              "sequence": sequence + 1,
              "time": "2017-06-25T11:23:14.792000Z"
            },
            {
              "type": "match",
              "trade_id": 17545513,
              "maker_order_id": asks1[1][2],
              "taker_order_id": "bf07445d-03e3-4293-b5e6-26e34ce643b0",
              "side": "sell",
              "size": "0.01",
              "price": "2596.77",
              "product_id": product_id,
              "sequence": sequence + 2,
              "time": "2017-06-29T01:45:36.865000Z"
            },
            {
              "type": "match",
              "trade_id": 17545514,
              "maker_order_id": id2,
              "taker_order_id": "bf07445d-03e3-4293-b5e6-26e34ce643b0",
              "side": "buy",
              "size": "0.41152763",
              "price": "2595.62",
              "product_id": product_id,
              "sequence": sequence + 3,
              "time": "2017-06-29T01:45:36.865000Z"
            },
            {
              "type": "open",
              "side": "sell",
              "price": "2602.22000000",
              "order_id": "26c22ff5-01b1-4ca3-859c-6349d6eb06b4",
              "remaining_size": "0.10000000",
              "product_id": product_id,
              "sequence": sequence + 4,
              "time": "2017-06-25T11:23:14.792000Z"
            },
        ]
        mock_connect.return_value.aenter.receive_str.side_effect = [
            json.dumps(message_expected)
            for message_expected in messages_expected
        ]
        async with gdax.orderbook.OrderBook(product_id) as orderbook:
            # ignore because of sequence number
            current_book = orderbook.get_current_book(product_id)
            message = await orderbook.handle_message()
            assert message == messages_expected[0]
            assert orderbook.get_current_book(product_id) == current_book

            # ignore because receive
            message = await orderbook.handle_message()
            assert message == messages_expected[1]
            current_book['sequence'] += 1
            assert orderbook.get_current_book(product_id) == current_book

            # match
            price = Decimal('2596.74')
            price2 = Decimal('2596.77')
            current_book = orderbook.get_current_book(product_id)
            assert orderbook.get_min_ask_depth(product_id) == \
                Decimal('0.2')
            assert orderbook.get_ask(product_id) == price
            assert orderbook.get_asks(product_id, price2) == \
                asks1_internal[price2]

            message = await orderbook.handle_message()
            assert message == messages_expected[2]
            assert orderbook.get_min_ask_depth(product_id) == \
                Decimal('0.2')
            assert orderbook.get_ask(product_id) == price
            asks = copy.deepcopy(asks1_internal[price2])
            asks[0]['size'] = Decimal('0.06670504')
            assert orderbook.get_asks(product_id, price2) == \
                asks
            current_book['sequence'] += 1
            assert orderbook.get_current_book(product_id) != current_book

            price3 = Decimal('2595.62')
            price4 = Decimal('2595.70')
            # match 2
            current_book = orderbook.get_current_book(product_id)
            assert orderbook.get_bids(product_id, price3) == \
                bids1_internal[price3]
            assert orderbook.get_bids(product_id, price4) == \
                bids1_internal[price4]
            assert orderbook.get_bid(product_id) == price4
            message = await orderbook.handle_message()
            assert message == messages_expected[3]
            bids1_internal[price3][0]['size'] = Decimal('1.0')
            assert orderbook.get_bids(product_id, price3) == \
                bids1_internal[price3]
            assert orderbook.get_bids(product_id, price4) == \
                bids1_internal[price4]
            assert orderbook.get_bid(product_id) == price4
            current_book['sequence'] += 1
            assert orderbook.get_current_book(product_id) != current_book

            # open
            current_book = orderbook.get_current_book(product_id)
            message = await orderbook.handle_message()
            assert message == messages_expected[4]
            current_book['sequence'] += 1
            assert orderbook.get_current_book(product_id) != current_book
            # TODO

    @patch('gdax.trader.Trader.get_product_order_book')
    async def test_error_message(self, mock_book, mock_connect):
        mock_connect.return_value.aenter.receive_str = CoroutineMock()
        mock_connect.return_value.aenter.send_json = CoroutineMock()
        mock_book.return_value = {'bids': [], 'asks': [], 'sequence': 1}
        messages_expected = [
          {
            "type": "error",
            "message": "test error",
          },
          {
            "type": "unknownmsgtype",
            'product_id': 'ETH-USD',
            'sequence': 2,
          },
        ]
        mock_connect.return_value.aenter.receive_str.side_effect = [
            json.dumps(message_expected)
            for message_expected in messages_expected
        ]
        async with gdax.orderbook.OrderBook() as orderbook:
            with pytest.raises(gdax.orderbook.OrderBookError):
                await orderbook.handle_message()

            with pytest.raises(gdax.orderbook.OrderBookError):
                await orderbook.handle_message()

    @patch('gdax.trader.Trader.get_product_order_book')
    async def test_disconnect(self, mock_book, mock_connect):
        mock_connect.return_value.aenter.receive_str = CoroutineMock()
        mock_connect.return_value.aenter.send_json = CoroutineMock()
        mock_book.return_value = {'bids': [], 'asks': [], 'sequence': 1}

        messages_expected = [
            json.dumps({
              "type": "done",
              "side": "sell",
              "order_id": "4eef1226-4b38-422c-a5b1-56def7107f9a",
              "reason": "canceled",
              "product_id": "ETH-USD",
              "price": "2601.76000000",
              "remaining_size": "3.09000000",
              "sequence": 2,
              "time": "2017-06-25T11:23:14.775000Z"
            }),
            aiohttp.ServerDisconnectedError('error'),
            json.dumps({
              "type": "done",
              "side": "sell",
              "order_id": "4eef1226-4b38-422c-a5b1-56def7107f9a",
              "reason": "canceled",
              "product_id": "ETH-USD",
              "price": "2601.76000000",
              "remaining_size": "3.09000000",
              "sequence": 2,
              "time": "2017-06-25T11:23:14.775000Z"
            })
        ]
        mock_connect.return_value.aenter.receive_str.side_effect = \
            messages_expected
        async with gdax.orderbook.OrderBook() as orderbook:
            message = await orderbook.handle_message()
            assert message == json.loads(messages_expected[0])

            message = await orderbook.handle_message()
            assert message is None

            message = await orderbook.handle_message()
            assert message == json.loads(messages_expected[2])

    @patch('gdax.trader.Trader.get_product_order_book')
    async def test_out_of_order(self, mock_book, mock_connect):
        mock_connect.return_value.aenter.receive_str = CoroutineMock()
        mock_connect.return_value.aenter.send_json = CoroutineMock()
        mock_book.return_value = {'bids': [], 'asks': [], 'sequence': 1}

        messages_expected = [
            {
              "type": "done",
              "side": "sell",
              "order_id": "4eef1226-4b38-422c-a5b1-56def7107f9a",
              "reason": "canceled",
              "product_id": "ETH-USD",
              "price": "2601.76000000",
              "remaining_size": "3.09000000",
              "sequence": 2,
              "time": "2017-06-25T11:23:14.775000Z"
            },
            {
              "type": "done",
              "side": "sell",
              "order_id": "4eef1226-4b38-422c-a5b1-56def7107f9a",
              "reason": "canceled",
              "product_id": "ETH-USD",
              "price": "2601.76000000",
              "remaining_size": "3.09000000",
              "sequence": 4,
              "time": "2017-06-25T11:23:14.775000Z"
            },
            {
              "type": "done",
              "side": "sell",
              "order_id": "4eef1226-4b38-422c-a5b1-56def7107f9a",
              "reason": "canceled",
              "product_id": "ETH-USD",
              "price": "2601.76000000",
              "remaining_size": "3.09000000",
              "sequence": 2,
              "time": "2017-06-25T11:23:14.775000Z"
            },
        ]
        mock_connect.return_value.aenter.receive_str.side_effect = [
            json.dumps(message_expected)
            for message_expected in messages_expected
        ]
        async with gdax.orderbook.OrderBook() as orderbook:
            message = await orderbook.handle_message()
            assert message == messages_expected[0]

            message = await orderbook.handle_message()
            assert message is None

            message = await orderbook.handle_message()
            assert message == messages_expected[2]

    @patch('gdax.trader.Trader.get_product_order_book')
    async def test_orderbook_change(self, mock_book, mock_connect):
        product_id = 'BTC-USD'
        mock_connect.return_value.aenter.receive_str = CoroutineMock()
        mock_connect.return_value.aenter.send_json = CoroutineMock()
        messages_expected = [
            {
              "type": "change",
              "time": "2014-11-07T08:19:27.028459Z",
              "sequence": sequence + 1,
              "order_id": id2,
              "product_id": product_id,
              "new_size": "101",
              "old_size": "100",
              "price": "2595.52",
              "side": "buy"
            },
            {
              "type": "change",
              "time": "2014-11-07T08:19:27.028459Z",
              "sequence": sequence + 2,
              "order_id": asks1[1][2],
              "product_id": product_id,
              "new_size": "0.1",
              "old_size": "0.07670504",
              "price": "2596.77",
              "side": "sell"
            },
        ]
        mock_connect.return_value.aenter.receive_str.side_effect = [
            json.dumps(message_expected)
            for message_expected in messages_expected
        ]
        mock_book.return_value = _book()
        async with gdax.orderbook.OrderBook(product_id) as orderbook:
            # change1
            current_book = orderbook.get_current_book(product_id)
            price = Decimal("2595.52")
            assert orderbook.get_bids(product_id, price) == \
                bids1_internal[price]

            message = await orderbook.handle_message()
            assert message == messages_expected[0]
            bids = copy.deepcopy(bids1_internal[price])
            bids[0]['size'] = Decimal('101')
            assert orderbook.get_bids(product_id, price) == \
                bids
            current_book['sequence'] += 1
            assert orderbook.get_current_book(product_id) != current_book

            # change2
            current_book = orderbook.get_current_book(product_id)
            price2 = Decimal("2596.77")
            assert orderbook.get_asks(product_id, price2) == \
                asks1_internal[price2]

            message = await orderbook.handle_message()
            assert message == messages_expected[1]
            asks = copy.deepcopy(asks1_internal[price2])
            asks[0]['size'] = Decimal('0.1')
            assert orderbook.get_asks(product_id, price2) == \
                asks
            current_book['sequence'] += 1
            assert orderbook.get_current_book(product_id) != current_book

    @patch('gdax.trader.Trader.get_product_order_book')
    async def test_orderbook_done(self, mock_book, mock_connect):
        product_id = 'BTC-USD'
        mock_book.return_value = _book()
        mock_connect.return_value.aenter.receive_str = CoroutineMock()
        mock_connect.return_value.aenter.send_json = CoroutineMock()
        messages_expected = [
            {
              "type": "done",
              "side": "sell",
              "order_id": asks1[0][2],
              "reason": "canceled",
              "product_id": product_id,
              "price": "2596.74",
              "remaining_size": "0.00000000",
              "sequence": sequence + 1,
              "time": "2017-06-25T11:23:14.775000Z"
            },
            {
              "type": "done",
              "side": "buy",
              "order_id": bids1[4][2],
              "reason": "canceled",
              "product_id": product_id,
              "price": "2595.70",
              "remaining_size": "0.00000000",
              "sequence": sequence + 2,
              "time": "2017-06-25T11:23:16.937000Z"
            },
            {
              "type": "done",
              "side": "sell",
              "order_id": asks1[1][2],
              "reason": "canceled",
              "product_id": product_id,
              # no price specified
              "remaining_size": "0.20000000",
              "sequence": sequence + 3,
              "time": "2017-06-25T11:23:15.937000Z"
            },
        ]
        mock_connect.return_value.aenter.receive_str.side_effect = [
            json.dumps(message_expected)
            for message_expected in messages_expected
        ]
        async with gdax.orderbook.OrderBook(product_id) as orderbook:
            # done
            current_book = orderbook.get_current_book(product_id)
            price = Decimal('2596.74')
            price2 = Decimal('2596.77')
            assert orderbook.get_asks(product_id, price) == \
                asks1_internal[price]
            assert orderbook.get_ask(product_id) == price

            message = await orderbook.handle_message()
            assert message == messages_expected[0]
            assert orderbook.get_asks(product_id, price) is None
            assert orderbook.get_ask(product_id) == price2
            current_book['sequence'] += 1
            assert orderbook.get_current_book(product_id) != current_book

            # done2
            current_book = orderbook.get_current_book(product_id)
            price2 = Decimal('2595.70')
            price3 = Decimal('2595.62')
            assert orderbook.get_bids(product_id, price2) == \
                bids1_internal[price2]
            assert orderbook.get_bid(product_id) == price2

            message = await orderbook.handle_message()
            assert message == messages_expected[1]
            assert orderbook.get_bids(product_id, price2) is None
            assert orderbook.get_bid(product_id) == price3
            current_book['sequence'] += 1
            assert orderbook.get_current_book(product_id) != current_book

            # done3, market order ignored
            current_book = orderbook.get_current_book(product_id)
            message = await orderbook.handle_message()
            assert message == messages_expected[2]
            current_book['sequence'] += 1
            assert orderbook.get_current_book(product_id) == current_book
