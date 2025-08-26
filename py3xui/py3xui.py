from json import dumps, loads
from http import HTTPStatus

from requests import Session

from .db import db, Cookies
from .payload import generate_payload
from .utils import expiry_timestamp, bytes_from_gb


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
        self.base_url = 'panel/api/inbounds'
        self.protocol = 'https' if ssl_certificate else 'http'
        self.session = Session()

        if db.query(Cookies).filter_by(domain=self.host).first():
            self._load_cookies_from_db()
        else:
            self._prompt_login()

    def _build_url(self, path: str):
        return (f'{self.protocol}://{self.host}:'
                f'{self.port}/{self.web_base_path}/{path}')

    def _load_cookies_from_db(self):
        cookies = db.query(Cookies).filter_by(domain=self.host).first()
        if not cookies:
            raise Exception(
                'No cookies found in database. Please login again.')

        self.session.cookies.set(
            name=cookies.name,
            value=cookies.value,
            domain=cookies.domain,
            path=cookies.path
        )

    def _prompt_login(self):
        username = input('Username: ')
        password = input('Password: ')
        self._login_and_store_cookies(username, password)

    def _login_and_store_cookies(self, username: str, password: str):
        url = self._build_url('login')
        payload = {'username': username, 'password': password}
        response = self.session.post(url, data=payload)
        if response.status_code == HTTPStatus.OK:
            return self._store_cookies()
        raise Exception(response.reason, response.status_code)

    def _store_cookies(self):
        if not self.session.cookies:
            raise Exception(
                'No cookies found. Possibly incorrect credentials.')
        cookie = [cookie for cookie in self.session.cookies][0]
        cookie_from_db = db.query(Cookies).filter_by(
            domain=cookie.domain).first()
        if cookie_from_db:
            cookie_from_db.name = cookie.name
            cookie_from_db.value = cookie.value
            cookie_from_db.domain = cookie.domain
            cookie_from_db.path = cookie.path
            cookie_from_db.secure = cookie.secure
        else:
            db.add(Cookies(
                name=cookie.name,
                value=cookie.value,
                domain=cookie.domain,
                path=cookie.path,
                secure=cookie.secure
            ))
        db.commit()

    def _request(self, method: str, path: str, **kwargs):
        url = self._build_url(path)
        headers = kwargs.pop('headers', {'Accept': 'application/json'})
        response = self.session.request(
            method, url, headers=headers, **kwargs)

        if response.status_code == HTTPStatus.OK:
            self._store_cookies()
            return response.json()
        raise Exception(response.reason, response.status_code)

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

    def inbounds(self):
        path = f'{self.base_url}/list'
        return self._request('GET', path)

    def inbound(self, inbound_id: int):
        path = f'{self.base_url}/get/{inbound_id}'
        return self._request('GET', path)

    def get_traffics_with_email(self, email: str):
        path = f'{self.base_url}/getClientTraffics/{email}'
        return self._request('GET', path)

    def add_inbound(
        self,
        name_inbound: str = 'New',
        port: int | None = None,
        enable: bool = True,
        expiry_time: int = 0,
        email: str | None = None,
        total_gb: int = 0,
        tg_id: str = ''
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
        return self._request('POST', path, json=payload)

    def add_client_to_inbound(
        self,
        inbound_id: int | None = None,
        email: str | None = None,
        total_gb: int = 0,
        expiry_time: int = 0,
        enable: bool = True,
        tg_id: str = ''
    ):
        expiry_time = expiry_timestamp(expiry_time)

        if not inbound_id:
            result = self.inbounds()
            inbound_id = result['obj'][-1]['id']

        _, client = generate_payload(
            email=email,
            total_gb=total_gb,
            expiry_time=expiry_time,
            enable=enable,
            tg_id=tg_id
        )
        client.pop('decryption')
        client.pop('fallbacks')

        payload = {
            'id': inbound_id,
            'settings': dumps(client)
        }
        path = f'{self.base_url}/addClient'
        return self._request('POST', path, json=payload)

    def update_client(
        self,
        email: str,
        enable=None,
        tg_id=None,
        total_gb=None,
        expiry_time=None,
    ):
        inbound_id, client = self._get_client_uuid_by_email(email)
        if not client:
            return 'Client not found'

        uuid = client.get('id')
        if total_gb is not None:
            client['totalGB'] = bytes_from_gb(total_gb)
        if expiry_time is not None:
            client['expiryTime'] = expiry_timestamp(expiry_time)
        if enable is not None:
            client['enable'] = enable
        if tg_id is not None:
            client['tgId'] = tg_id

        payload = {
            'id': inbound_id,
            'settings': dumps({'clients': [client]})
        }
        path = f'{self.base_url}/updateClient/{uuid}'
        return self._request('POST', path, json=payload)

    def reset_all_traffics(self):
        url = f'{self.base_url}/resetAllTraffics'
        return self._request('POST', url)

    def reset_client_traffic(self, email: str):
        inbound_id, client = self._get_client_uuid_by_email(email)
        if not client:
            return 'Client not found'
        email = client.get('email')
        url = f'{self.base_url}/{inbound_id}/resetClientTraffic/{email}'
        return self._request('POST', url)

    def delete_client(self, email: str):
        inbound_id, client = self._get_client_uuid_by_email(email)
        if not client:
            return 'Client not found'
        uuid = client.get('id')
        url = f'{self.base_url}/{inbound_id}/delClient/{uuid}'
        return self._request('POST', url)

    def delete_inbound(self, inbound_id: int):
        url = f'{self.base_url}/del/{inbound_id}'
        return self._request('POST', url)

    def get_online_clients(self):
        url = f'{self.base_url}/onlines'
        return self._request('POST', url).get('obj')
