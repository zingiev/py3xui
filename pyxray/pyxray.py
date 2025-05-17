import random
from string import ascii_lowercase, digits
from http import HTTPStatus
from requests import Session

from .db import DB

db = DB()


class Client:
    def __init__(self, host: str, port: int, web_base_path: str) -> None:
        self.host = host
        self.port = port
        self.web_base_path = web_base_path.strip('/')
        self.base_url = 'panel/api/inbounds'
        self.session = Session()

        if db.exists_data(self.host):
            self._load_cookies_from_db()
        else:
            self._prompt_login()

    def _prompt_login(self) -> None:
        username = input('Username: ')
        password = input('Password: ')
        self._login_and_store_cookies(username, password)

    def _login_and_store_cookies(self, username: str, password: str) -> None:
        url = self._build_url('login')
        payload = {'username': username, 'password': password}
        response = self.session.post(url, data=payload)

        if response.status_code == HTTPStatus.OK:
            self._store_cookies()
        else:
            raise Exception(response.reason, response.status_code)

    def _build_url(self, path: str) -> str:
        return f'http://{self.host}:{self.port}/{self.web_base_path}/{path}'

    def _store_cookies(self) -> None:
        if not self.session.cookies:
            raise Exception(
                'No cookies found. Possibly incorrect credentials.')

        for cookie in self.session.cookies:
            cookie_data = {
                'name': cookie.name,
                'value': cookie.value,
                'domain': cookie.domain,
                'path': cookie.path,
                'secure': str(cookie.secure)
            }

            if db.exists_cookie(cookie.domain, cookie.name):
                db.update_data(**cookie_data)
            else:
                db.insert_data(**cookie_data)

    def _load_cookies_from_db(self) -> None:
        cookies = db.get_cookies_by_domain(self.host)
        if not cookies:
            raise Exception(
                "No cookies found in database. Please login again.")

        for c in cookies:
            self.session.cookies.set(
                name=c['name'],
                value=c['value'],
                domain=c['domain'],
                path=c['path']
            )

    def get_inbounds_request(self, url: str):
        headers = {'Accept': 'application/json'}
        response = self.session.get(url, headers=headers)
        if response.status_code == HTTPStatus.OK:
            self._store_cookies()
            return response.json()
        raise Exception(response.reason, response.status_code)

    def inbounds(self) -> dict:
        url = self._build_url(f'{self.base_url}/list')
        response = self.get_inbounds_request(url)
        return response

    def inbound(self, inbound_id: str) -> dict:
        url = self._build_url(f'{self.base_url}/get/{inbound_id}')
        response = self.get_inbounds_request(url)
        return response

    def get_traffics_with_email(self, email: str) -> dict:
        url = self._build_url(f'{self.base_url}/getClientTraffics/{email}')
        headers = {'Accept': 'application/json'}
        response = self.session.get(url, headers=headers)
        if response.status_code == HTTPStatus.OK:
            self._store_cookies()
            return response.json()
        raise Exception(response.reason, response.status_code)

    def add_inbound(
        self,
        name_inbound: str = 'New',
        enable: bool = True,
        expiry_time: int = 0,
        port: int = 55421,
        protocol: str = 'vless'
    ):
        url = self._build_url(f'{self.base_url}/add/')
        headers = {'Accept': 'application/json'}
        payload = {
            "success": 'true',
            "msg": "Create Successfully",
            "obj": {
                "up": 0,
                "down": 0,
                "total": 0,
                "remark": name_inbound,
                "enable": enable,
                "expiryTime": expiry_time,
                "clientStats": 'null',
                "listen": "",
                "port": port,
                "protocol": protocol,
                "settings": "{\"clients\": [{\"id\": \"b86c0cdc-8a02-4da4-8693-72ba27005587\",\"flow\": \"\",\"email\": \"nt3wz904\",\"limitIp\": 0,\"totalGB\": 0,\"expiryTime\": 0,\"enable\": true,\"tgId\": \"\",\"subId\": \"rqv5zw1ydutamcp0\",\"reset\": 0}],\"decryption\": \"none\",\"fallbacks\": []}",
                "streamSettings": "{\"network\": \"tcp\",\"security\": \"reality\",\"externalProxy\": [],\"realitySettings\": {\"show\": false,\"xver\": 0,\"dest\": \"yahoo.com:443\",\"serverNames\": [\"yahoo.com\",\"www.yahoo.com\"],\"privateKey\": \"wIc7zBUiTXBGxM7S7wl0nCZ663OAvzTDNqS7-bsxV3A\",\"minClient\": \"\",\"maxClient\": \"\",\"maxTimediff\": 0,\"shortIds\": [\"47595474\",\"7a5e30\",\"810c1efd750030e8\",\"99\",\"9c19c134b8\",\"35fd\",\"2409c639a707b4\",\"c98fc6b39f45\"],\"settings\": {\"publicKey\": \"2UqLjQFhlvLcY7VzaKRotIDQFOgAJe1dYD1njigp9wk\",\"fingerprint\": \"random\",\"serverName\": \"\",\"spiderX\": \"/\"}},\"tcpSettings\": {\"acceptProxyProtocol\": false,\"header\": {\"type\": \"none\"}}}",
                "tag": "inbound-55421",
                "sniffing": "{\"enabled\": true,\"destOverride\": [\"http\",\"tls\",\"quic\",\"fakedns\"],\"metadataOnly\": false,\"routeOnly\": false}",
                "allocate": "{\"strategy\": \"always\",\"refresh\": 5,\"concurrency\": 3}"
            }
        }
        response = self.session.post(url, headers=headers, params=payload)
        if response.status_code == HTTPStatus.OK:
            self._store_cookies()
            return response.json()
        raise Exception(response.reason, response.status_code)

# dd9ebef2-ce00-47fe-adc3-31d4a13343a5

    def add_user_to_inbound(self, inbound_id: int, email: str = None):
        if not email:
            string = ascii_lowercase + digits
            idx = []
            gen_length = [8, 4, 4, 4, 12]
            for i in gen_length:
                idx.append([random.choice(string) for _ in range(i)])
            idx = '-'.join([''.join(i) for i in idx])
        url = self._build_url(f'{self.base_url}/addClient')
        payload = {
        "id": inbound_id,
        "settings": "{\"clients\": [{\"id\": \"bbfad557-28f2-47e5-9f3d-e3c7f539fbda\",\"flow\": \"xtls-rprx-vision\",\"email\": \"dp1plm9lt8\",\"limitIp\": 0,\"totalGB\": 0,\"expiryTime\": 0,\"enable\": true,\"tgId\": \"\",\"subId\": \"2rv0gb458kbfl592\",\"reset\": 0}]}"
    }