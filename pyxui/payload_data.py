from uuid import uuid4

from .utils import (generate_short_ids, bytes_from_gb,
                    random_string, generate_x25519_keys)


def generate_settings(
    email: str = None,
    total_gb: int = 0,
    expiry_time: int = 0,
    enable: bool = True,
    tg_id: str = ""
):
    keys = generate_x25519_keys()
    short_ids = generate_short_ids()
    total_gb_bytes = bytes_from_gb(total_gb)
    sub_id = random_string(16)

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

    return (client_settings, stream_settings, sniffing, allocate)
