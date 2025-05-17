from http import HTTPStatus
from dataclasses import dataclass
from requests import Session

from .db import DB

db = DB()


@dataclass
class Cookies:
    name: str
    value: str
    domain: str
    path: str
    secure: bool


class Client:
    def __init__(self, host: str, port: int, web_base_path: str) -> None:
        self.host = host
        self.port = port
        self.web_base_path = web_base_path
        self.base_url = '/panel/api/inbounds'
        self.session = Session()

        if db.exists_data(self.host):
            self._load_session_cookies()
        else:
            self._prompt_login()

    def _prompt_login(self) -> None:
        username = input('Username: ')
        password = input('Password: ')
        self._login_and_store(username, password)

    def _login_and_store(self, username: str, password: str) -> None:
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
            raise Exception('No cookies found. Possibly incorrect credentials.')

        for cookie in self.session.cookies:
            cookie_data = {
                'name': cookie.name,
                'value': cookie.value,
                'domain': cookie.domain,
                'path': cookie.path,
                'secure': cookie.secure
            }

            if db.exists_cookie(self.host, cookie.name):
                db.update_data(**cookie_data)
            else:
                db.insert_data(**cookie_data)

    def _load_session_cookies(self) -> None:
        cookies = db.get_cookies_by_domain(self.host)
        if not cookies:
            raise Exception("No cookies found in database. Please login again.")

        for c in cookies:
            self.session.cookies.set(
                name=c["name"],
                value=c["value"],
                domain=c["domain"],
                path=c["path"]
            )

    def inbounds(self) -> dict:
        url = f'{self._build_url("panel/api/inbounds/list")}'
        headers = {'Accept': 'application/json'}
        response = self.session.get(url, headers=headers)

        if response.status_code == HTTPStatus.OK:
            self._store_cookies()
            return response.json()

        raise Exception(response.reason, response.status_code)
