import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

from bot.db import Base


async def get_engine(dsn, echo) -> AsyncEngine:
    engine = create_async_engine(
        url=dsn,
        echo=echo
    )

    try:
        # Открытие нового соединение с базой
        async with engine.begin() as conn:
            # Выполнение обычного текстового запроса
            await conn.execute(text("SELECT 1"))
        logging.log(logging.DEBUG, "Engine created successfully and working right")
    except:
        logging.log(logging.ERROR, "Engine created wrong")

    return engine




async def create_tables(engine: AsyncEngine):
    # Создание таблиц
    async with engine.begin() as connection:
        # Если ловите ошибку "таблица уже существует",
        # раскомментируйте следующую строку:
        # await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)