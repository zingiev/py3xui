from json import dumps
from random import randint
from http import HTTPStatus

from requests import Session

from .db import DB
from .payload_data import generate_settings
from .utils import expiry_timestamp

db = DB()


class Client:
    def __init__(self, host: str, port: str, web_base_path: str):
        self.host = host
        self.port = port
        self.web_base_path = web_base_path.strip("/")
        self.base_url = "panel/api/inbounds"
        self.session = Session()

        if db.exists_data(self.host):
            self._load_cookies_from_db()
        else:
            self._prompt_login()

    def _prompt_login(self):
        username = input("Username: ")
        password = input("Password: ")
        self._login_and_store_cookies(username, password)

    def _login_and_store_cookies(self, username: str, password: str):
        url = self._build_url("login")
        payload = {"username": username, "password": password}
        response = self.session.post(url, data=payload)

        if response.status_code == HTTPStatus.OK:
            self._store_cookies()
        else:
            raise Exception(response.reason, response.status_code)

    def _build_url(self, path: str):
        return f"http://{self.host}:{self.port}/{self.web_base_path}/{path}"

    def _store_cookies(self):
        if not self.session.cookies:
            raise Exception(
                "No cookies found. Possibly incorrect credentials.")

        for cookie in self.session.cookies:
            cookie_data = {
                "name": cookie.name,
                "value": cookie.value,
                "domain": cookie.domain,
                "path": cookie.path,
                "secure": str(cookie.secure)
            }

            if db.exists_cookie(cookie.domain, cookie.name):
                db.update_data(**cookie_data)
            else:
                db.insert_data(**cookie_data)

    def _load_cookies_from_db(self):
        cookies = db.get_cookies_by_domain(self.host)
        if not cookies:
            raise Exception(
                "No cookies found in database. Please login again.")

        for c in cookies:
            self.session.cookies.set(
                name=c["name"],
                value=c["value"],
                domain=c["domain"],
                path=c["path"]
            )

    def _request(self, method: str, path: str, **kwargs):
        url = self._build_url(path)
        headers = kwargs.pop("headers", {"Accept": "application/json"})
        response = self.session.request(
            method, url, headers=headers, **kwargs)

        if response.status_code == HTTPStatus.OK:
            self._store_cookies()
            return response.json()
        raise Exception(response.reason, response.status_code)

    def inbounds(self):
        path = f"{self.base_url}/list"
        return self._request("GET", path)

    def inbound(self, inbound_id: str):
        path = f"{self.base_url}/get/{inbound_id}"
        return self._request("GET", path)

    def get_traffics_with_email(self, email: str):
        path = f"{self.base_url}/getClientTraffics/{email}"
        return self._request("GET", path)

    def add_inbound(
        self,
        name_inbound: str = "New",
        port: int = None,
        enable: bool = True,
        expiry_time: int = 0,

        email: str = None,
        total_gb: int = 0,
        tg_id: str = ""
    ):
        expiry_time = expiry_timestamp(expiry_time)
        port = randint(12345, 54321) if port is None else port

        client, stream, sniffing, allocate = generate_settings(
            email=email, total_gb=total_gb, tg_id=tg_id,
            expiry_time=expiry_time, enable=enable
        )

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
            "settings": dumps(client),
            "streamSettings": dumps(stream),
            "sniffing": dumps(sniffing),
            "allocate": dumps(allocate)
        }
        path = f'{self.base_url}/add'
        return self._request("POST", path, json=payload)

    def add_user_to_inbound(
        self,
        inbound_id: int = None,
        email: str = None,
        total_gb: int = 0,
        expiry_time: int = 0,
        enable: bool = True,
        tg_id: str = ""
    ):
        expiry_time = expiry_timestamp(expiry_time)

        if inbound_id is None:
            result = self.inbounds()
            inbound_id = result["obj"][-1]["id"]

        client, stream, sniffing, allocate = generate_settings(
            email=email, total_gb=total_gb, tg_id=tg_id,
            expiry_time=expiry_time, enable=enable)
        client.pop("decryption")
        client.pop("fallbacks")

        payload = {
            "id": inbound_id,
            "settings": dumps(client)
        }
        path = f'{self.base_url}/addClient'
        return self._request("POST", path, json=payload)
