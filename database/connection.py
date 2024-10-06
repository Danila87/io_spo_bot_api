from typing import Union, Type

from psycopg2 import connect
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncEngine
from dataclasses import dataclass
from abc import ABC, abstractmethod
from config import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME

class ConnectionError(Exception):
    def __init__(self, message):
        super().__init__(message)

@dataclass(frozen=True)
class Credentials:
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str


class DBEngineInterface(ABC):
    @abstractmethod
    def get_engine(self) -> AsyncEngine:
        pass

class DBConnectionInterface(ABC):

    @abstractmethod
    def db_session(self):
        pass

    @abstractmethod
    def test_connection(self):
        pass

class PostgresEngine(DBEngineInterface):
    def __init__(self, credentials: Credentials):
        self._engine = create_async_engine(
            'postgresql+asyncpg://{}:{}@{}:{}/{}'.format(
                credentials.DB_USER,
                credentials.DB_PASS,
                credentials.DB_HOST,
                credentials.DB_PORT,
                credentials.DB_NAME,
            )
        )


    def get_engine(self) -> AsyncEngine:
        return self._engine

    @property
    def url(self) -> URL:
        return self._engine.url

class DBConnectionSQL(DBConnectionInterface):
    def __init__(self, engine: DBEngineInterface):
        self._engine = engine.get_engine()
        self._db_session = None

    @property
    def db_session(self):
        if self._db_session is None:
            self._db_session = async_sessionmaker(self._engine)

        return self._db_session

    def switch_db(self, engine: DBEngineInterface):
        self._engine = engine.get_engine()

    async def test_connection(self):
        try:
            async with self._engine.connect() as connection:
                print('Подключение к БД успешно!')
        except Exception as e:
            print(f'Подключение к БД завершилось ошибкой. Ошибка: {e}')
            raise ConnectionError

class DBConnectionNoSQL(DBConnectionInterface):

    def __init__(self):
        pass

    @property
    def db_session(self):
        return None

    def test_connection(self):
        pass

postgres_db = DBConnectionSQL(
    engine=PostgresEngine(
        credentials=Credentials(
            DB_USER=DB_USER,
            DB_PASS=DB_PASS,
            DB_HOST=DB_HOST,
            DB_PORT=DB_PORT,
            DB_NAME=DB_NAME,
        )
    )
)
