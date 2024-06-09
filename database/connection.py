from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from config import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME

engine = create_async_engine(
    url=f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

db_session = async_sessionmaker(engine)