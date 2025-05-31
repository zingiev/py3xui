from json import dumps, loads
from http import HTTPStatus

from requests import Session

from .db import DB
from .payload import generate_payload
from .utils import expiry_timestamp, bytes_from_gb

db = DB()


class Client:
    def __init__(
        self,
        host: str,
        port: str,
        web_base_path: str,
        ssl_certificate: bool = False
    ):
        self.host = host
        self.port = port
        self.web_base_path = web_base_path
        self.base_url = "panel/api/inbounds"
        self.protocol = 'https' if ssl_certificate else 'http'
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
        return (f"{self.protocol}://{self.host}:"
                f"{self.port}/{self.web_base_path}/{path}")

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

    def inbound(self, inbound_id: int):
        path = f"{self.base_url}/get/{inbound_id}"
        return self._request("GET", path)

    def get_traffics_with_email(self, email: str):
        path = f"{self.base_url}/getClientTraffics/{email}"
        return self._request("GET", path)

    def add_inbound(
        self,
        name_inbound: str = "New",
        port: int | None = None,
        enable: bool = True,
        expiry_time: int = 0,
        email: str | None = None,
        total_gb: int = 0,
        tg_id: str = ""
    ):
        payload, _ = generate_payload(
            name_inbound=name_inbound,
            port=port,
            enable=enable,
            expiry_time=expiry_time,
            email=email,
            total_gb=total_gb,
            tg_id=tg_id
        )
        path = f'{self.base_url}/add'
        return self._request("POST", path, json=payload)

    def add_client_to_inbound(
        self,
        inbound_id: int | None = None,
        email: str | None = None,
        total_gb: int = 0,
        expiry_time: int = 0,
        enable: bool = True,
        tg_id: str = ""
    ):
        expiry_time = expiry_timestamp(expiry_time)

        if not inbound_id:
            result = self.inbounds()
            inbound_id = result["obj"][-1]["id"]

        _, client = generate_payload(
            email=email,
            total_gb=total_gb,
            expiry_time=expiry_time,
            enable=enable,
            tg_id=tg_id
        )
        client.pop("decryption")
        client.pop("fallbacks")

        payload = {
            "id": inbound_id,
            "settings": dumps(client)
        }
        path = f'{self.base_url}/addClient'
        return self._request("POST", path, json=payload)

    def _get_client_uuid_by_email(self, email: str):
        inbounds = self.inbounds().get('obj')
        for inbound in inbounds:
            if inbound.get('protocol') != 'vless':
                continue
            clients = loads(inbound.get('settings')).get('clients')
            for client in clients:
                if client.get('email') == email:
                    return inbound.get('id'), client
        return None

    def update_client(
        self,
        email: str,
        total_gb: int = 0,
        expiry_time: int = 0,
        enable: bool = True,
        tg_id: str = ""
    ):
        inbound_id, client = self._get_client_uuid_by_email(
            email
        )  # type: ignore
        if not client:
            return 'Client not found'

        uuid = client['id']
        client['totalGB'] = bytes_from_gb(total_gb)
        client['expiryTime'] = expiry_timestamp(expiry_time)
        client['enable'] = enable
        client['tgId'] = tg_id

        payload = {
            "id": inbound_id,
            "settings": dumps({"clients": [client]})
        }
        path = f'{self.base_url}/updateClient/{uuid}'
        return self._request("POST", path, json=payload)
