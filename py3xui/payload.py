from random import randint
from uuid import uuid4
from json import dumps

from .utils import (generate_short_ids, bytes_from_gb,
                    random_string, generate_x25519_keys, expiry_timestamp)


def generate_payload(**kwargs):
    name_inbound: str = kwargs.get('name_inbound', 'New')
    port: int | None = kwargs.get('port', None)
    email: str | None = kwargs.get('email', None)
    enable: bool = kwargs.get('enable', True)
    expiry_time: int = kwargs.get('expiry_time', 0)
    total_gb: int = kwargs.get('total_gb', 0)
    tg_id: str = kwargs.get('tg_id', '')
    
    expiry_time = expiry_timestamp(expiry_time)
    keys: dict[str, str] = generate_x25519_keys()
    short_ids: list[str] = generate_short_ids()
    total_gb_bytes: int = bytes_from_gb(total_gb)
    sub_id: str = random_string(16)

    if email is None:
        email = random_string(8)

    client_settings = {
        "clients": [
            {
                "id": str(uuid4()),
                "flow": "xtls-rprx-vision",
                "email": email,
                "limitIp": 0,
                "totalGB": total_gb_bytes,
                "expiryTime": expiry_time,
                "enable": enable,
                "tgId": tg_id,
                "subId": sub_id,
                "reset": 0
            }
        ],
        "decryption": "none",
        "fallbacks": []
    }

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
            "privateKey": keys.get('privateKey'),
            "minClient": "",
            "maxClient": "",
            "maxTimediff": 0,
            "shortIds": short_ids,
            "settings": {
                "publicKey": keys.get('publicKey'),
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

    sniffing = {
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

    allocate = {
        "strategy": "always",
        "refresh": 5,
        "concurrency": 3
    }
    
    port = randint(12345, 54321) if port is None else port
    payload = {
        "up": 0,
        "down": 0,
        "total": 0,
        "remark": name_inbound,
        "enable": enable,
        "expiryTime": expiry_time,
        "listen": "",
        "port": port,
        "protocol": "vless",
        "settings": dumps(client_settings),
        "streamSettings": dumps(stream_settings),
        "sniffing": dumps(sniffing),
        "allocate": dumps(allocate)
    }

    return (payload, client_settings)
