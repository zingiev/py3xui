from base64 import urlsafe_b64encode
from secrets import token_bytes
from uuid import uuid4
from random import choice
from string import ascii_lowercase, digits, hexdigits
from datetime import datetime, timedelta
from pytz import timezone


def generate_client_settings(
    email: str = None,
    total_gb: int = 0,
    expiry_time: int = 0,
    enable: bool = True,
    tg_id: str = ""
):
    charset = ascii_lowercase + digits
    if email is None:
        email = "".join(choice(charset) for _ in range(10))

    if expiry_time > 0:
        current_date = datetime.now(timezone("Europe/Moscow"))
        future_time = current_date + timedelta(days=expiry_time)
        expiry_time = int(future_time.timestamp() * 1000)

    if total_gb > 0:
        total_gb = (1024 ** 3) * total_gb

    client_settings = {
        "clients": [
            {
                "id": str(uuid4()),
                "flow": "xtls-rprx-vision",
                "email": email,
                "limitIp": 0,
                "totalGB": total_gb,
                "expiryTime": expiry_time,
                "enable": enable,
                "tgId": tg_id,
                "subId": "".join(choice(charset) for _ in range(16)),
                "reset": 0
            }
        ],
        "decryption": "none",
        "fallbacks": []
    }

    return client_settings


def generate_stream_settings():
    private_key = urlsafe_b64encode(
        token_bytes(32)).rstrip(b'=').decode('utf-8')
    public_key = urlsafe_b64encode(
        token_bytes(32)).rstrip(b'=').decode('utf-8')

    short_ids_length = [8, 6, 16, 2, 10, 4, 14, 10]
    hex_chars = hexdigits.lower()
    hex_chars = hex_chars[:16]
    short_ids = []
    for i in short_ids_length:
        short_ids.append(''.join(choice(hex_chars) for _ in range(i)))

    stream_settings = {
        "network": "tcp",
        "security": "reality",
        "externalProxy": [],
        "realitySettings": {
            "show": False,
            "xver": 0,
            "dest": "yahoo.com:443",
            "serverNames": [
                "yahoo.com",
                "www.yahoo.com"
            ],
            "privateKey": private_key,
            "minClient": "",
            "maxClient": "",
            "maxTimediff": 0,
            "shortIds": short_ids,
            "settings": {
                "publicKey": public_key,
                "fingerprint": "firefox",
                "serverName": "",
                "spiderX": "/"
            }
        },
        "tcpSettings": {
            "acceptProxyProtocol": False,
            "header": {
                "type": "none"
            }
        },
    }

    return stream_settings


def generate_sniffing():
    return {
        "enabled": True,
        "destOverride": [
            "http",
            "tls",
            "quic",
            "fakedns"
        ],
        "metadataOnly": False,
        "routeOnly": False
    }


def generate_allocate():
    return {
        "strategy": "always",
        "refresh": 5,
        "concurrency": 3
    }
