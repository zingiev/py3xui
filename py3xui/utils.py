from random import choice
from base64 import urlsafe_b64encode
from datetime import datetime, timedelta
from string import hexdigits, ascii_lowercase, digits

from pytz import timezone
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives import serialization


def bytes_from_gb(gb: int) -> int:
    return gb * 1024 ** 3 if gb > 0 else 0


def random_string(length=8) -> str:
    charset = ascii_lowercase + digits
    return ''.join(choice(charset) for _ in range(length))


def generate_short_ids() -> list[str]:
    lengths = [8, 6, 16, 2, 10, 4, 14, 10]
    hex_chars = hexdigits.lower()[:16]
    return [''.join(choice(hex_chars) for _ in range(length)) for length in lengths]


def expiry_timestamp(days: int) -> int:
    if days <= 0:
        return 0
    current_date = datetime.now(timezone("Europe/Moscow"))
    future_time = current_date + timedelta(days=days)
    return int(future_time.timestamp() * 1000)


def generate_x25519_keys() -> dict[str, str]:
    private_key = x25519.X25519PrivateKey.generate()
    public_key = private_key.public_key()

    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )

    private_key_b64 = urlsafe_b64encode(private_bytes).decode().rstrip("=")
    public_key_b64 = urlsafe_b64encode(public_bytes).decode().rstrip("=")

    return {"privateKey": private_key_b64, "publicKey": public_key_b64}
