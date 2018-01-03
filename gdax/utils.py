"""Utils for message signing, etc."""

import base64
import decimal
import hashlib
import hmac
import json


def get_signature(path, method, body, timestamp, api_secret):
    """Generate a signature for a request.

    Reference implementation at https://docs.gdax.com/#signing-a-message.

    """
    message = timestamp + method + path + body
    message = message.encode('ascii')
    hmac_key = base64.b64decode(api_secret)
    assert len(hmac_key) == 64
    signature = hmac.new(hmac_key, message, hashlib.sha256)
    signature_b64 = base64.b64encode(signature.digest())

    return signature_b64.decode('ascii')


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)

