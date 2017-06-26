import base64
import pytest

import gdax.utils


def test_get_signature():
    path = '/test'
    method = 'POST'
    body = '[1, 2, 3]'
    timestamp = '1493343391.076892'
    api_secret = base64.b64encode(b'a' * 64)
    signature = gdax.utils.get_signature(
        path, method, body, timestamp, api_secret)
    assert signature == 'nEihM3ziTAsVXB0LvueOO/t0a6GY50cmwiY4zwLL6BM='

    with pytest.raises(AssertionError):
        gdax.utils.get_signature(path, method, body, timestamp,
                                 base64.b64encode(b'a'))
