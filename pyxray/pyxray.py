import os
import json
from http import HTTPStatus

from requests import Session


class Client:

    SESSION_FILE = 'session.json'

    def __init__(self, host: str, port: int, web_base_path: str) -> None:
        self.host = host
        self.port = port
        self.web_base_path = web_base_path
        self.base_url = '/panel/api/inbounds'
        self.session = Session()
        self._load_session_cookies()

    def _save_session_cookies(self) -> None:
        cookies = [
            {
                'name': c.name,
                'value': c.value,
                'domain': c.domain,
                'path': c.path,
                'secure': c.secure,
                'expires': c.expires
            }
            for c in self.session.cookies
        ]
        with open(self.SESSION_FILE, 'w') as f:
            json.dump(cookies, f, indent=2)

    def _load_session_cookies(self) -> None:
        if not os.path.exists(self.SESSION_FILE):
            return

        with open(self.SESSION_FILE, 'r') as f:
            cookies = json.load(f)
            for c in cookies:
                self.session.cookies.set(
                    name=c['name'],
                    value=c['value'],
                    domain=c['domain'],
                    path=c['path']
                )

    def login(self, username: str, password: str) -> dict:
        url = f'http://{self.host}:{self.port}/{self.web_base_path}/login'
        payload = {'username': username, 'password': password}
        response = self.session.post(url, data=payload)
        if response.status_code == HTTPStatus.OK:
            self._save_session_cookies()
            return response.json()
        raise Exception(response.reason, response.status_code)

    def inbounds(self) -> dict:
        url = f'http://{self.host}:{self.port}/{self.web_base_path}{self.base_url}/list'
        headers = {'Accept': 'application/json'}
        response = self.session.get(url, headers=headers)
        if response.status_code == HTTPStatus.OK:
            self._save_session_cookies()
            return response.json()
        raise Exception(response.reason, response.status_code)
