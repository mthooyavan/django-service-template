import base64
import gzip
import json


def encode_token(token):
    custom_claim = token.get("custom_claim")
    if custom_claim:
        compressed_payload = gzip.compress(json.dumps(custom_claim).encode("utf-8"))
        encoded_payload = base64.b64encode(compressed_payload).decode("utf-8")
        token["custom_claim"] = encoded_payload

    return token


def decoded_token(token):
    custom_claim = token.get("custom_claim")
    if custom_claim:
        decoded_compressed_payload = base64.b64decode(custom_claim)
        decompressed_payload = gzip.decompress(decoded_compressed_payload)
        token["custom_claim"] = json.loads(decompressed_payload.decode("utf-8"))

    return token
