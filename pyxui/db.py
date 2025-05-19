import sqlite3
from typing import Optional, List, Dict


class DB:

    def __init__(self, db_name: str = 'pyxui.session'):
        self.connect = sqlite3.connect(db_name)
        self.connect.row_factory = sqlite3.Row  # Позволяет возвращать словари
        self.cursor = self.connect.cursor()
        self._create_table()

    def _create_table(self) -> None:
        with self.connect:
            self.cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS session (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    value TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    path TEXT NOT NULL,
                    secure TEXT NOT NULL
                )
                '''
            )

    def insert_data(self, **cookie: str) -> None:
        with self.connect:
            self.cursor.execute(
                '''
                INSERT INTO session (name, value, domain, path, secure)
                VALUES (:name, :value, :domain, :path, :secure)
                ''',
                cookie
            )

    def update_data(self, **cookie: str) -> None:
        with self.connect:
            self.cursor.execute(
                '''
                UPDATE session
                SET name = :name,
                    value = :value,
                    path = :path,
                    secure = :secure
                WHERE domain = :domain AND name = :name
                ''',
                cookie
            )

    def exists_data(self, domain: str) -> bool:
        self.cursor.execute(
            '''SELECT 1
               FROM session
               WHERE domain = ?
               LIMIT 1''', (domain,)
        )
        return self.cursor.fetchone() is not None

    def exists_cookie(self, domain: str, name: str) -> bool:
        self.cursor.execute(
            '''SELECT 1
               FROM session
               WHERE domain = ?
               AND name = ?
               LIMIT 1''', (domain, name)
        )
        return self.cursor.fetchone() is not None

    def get_cookies_by_domain(self, domain: str) -> List[Dict[str, str]]:
        self.cursor.execute(
            '''SELECT name, value, domain, path, secure
               FROM session
               WHERE domain = ?''', (domain,)
        )
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]

    def get_all(self) -> List[Dict[str, str]]:
        self.cursor.execute('SELECT * FROM session')
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]
