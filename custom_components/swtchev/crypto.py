"""Request body encryption used by the charger web UI (firmware v1.3.x)."""

from __future__ import annotations

import base64
import hashlib
import json
import os
from typing import Any

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

# Both values are hard-coded in the charger web UI's JavaScript
BODY_IV = b"7kR9mX2pL5qW8vN1"
SERVER_PUBLIC_KEY = "AAAAC3NzaC1lZDI1NTE5AAAAIDOUw9J5Vy3L24LNIzxzOjUcYTiLxssLHCPYMSegxoMm"

_P = 2**255 - 19


def _ed25519_to_x25519(public_key: bytes) -> bytes:
    """Convert an Ed25519 public key to its X25519 (Montgomery) form."""
    y = int.from_bytes(public_key, "little") & ((1 << 255) - 1)
    u = (1 + y) * pow(1 - y, -1, _P) % _P
    return u.to_bytes(32, "little")


def _server_public_key() -> X25519PublicKey:
    """Extract the 32-byte key from the ssh-ed25519 blob and convert it."""
    blob = base64.b64decode(SERVER_PUBLIC_KEY)
    name_len = int.from_bytes(blob[0:4], "big")
    key_start = 4 + name_len + 4
    ed_key = blob[key_start : key_start + 32]
    return X25519PublicKey.from_public_bytes(_ed25519_to_x25519(ed_key))


def encrypt_body(payload: Any) -> dict[str, str]:
    """Encrypt a request body the same way the charger web UI does.

    The body is AES-256-CBC encrypted with a random key (``d``). That key is
    wrapped with AES-GCM using an ephemeral X25519 exchange against the
    charger's public key (``k`` = ephemeral public key || nonce || ciphertext).
    """
    body_key = os.urandom(32)
    plaintext = json.dumps(payload, separators=(",", ":")).encode()

    padder = padding.PKCS7(128).padder()
    padded = padder.update(plaintext) + padder.finalize()
    encryptor = Cipher(algorithms.AES(body_key), modes.CBC(BODY_IV)).encryptor()
    data = encryptor.update(padded) + encryptor.finalize()

    ephemeral = X25519PrivateKey.generate()
    shared = ephemeral.exchange(_server_public_key())
    nonce = os.urandom(12)
    wrapped_key = AESGCM(hashlib.sha256(shared).digest()).encrypt(nonce, body_key, None)
    ephemeral_public = ephemeral.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)

    return {
        "k": base64.b64encode(ephemeral_public + nonce + wrapped_key).decode(),
        "d": base64.b64encode(data).decode(),
    }
