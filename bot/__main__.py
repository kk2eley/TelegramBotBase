import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram_dialog import setup_dialogs
from sqlalchemy.ext.asyncio import async_sessionmaker

from bot.config.config import get_config
from bot.db.requests import get_engine, create_tables
from bot.dialogs import get_dialogs
from bot.handlers import commands, get_routers
from bot.middlewares.session_middleware import DbSessionMiddleware
from bot.misc.set_menu import set_main_menu

from bot.misc.logging_setup import setup_logging


logger = setup_logging()


async def main():
    config = get_config()

    bot = Bot(token=config.bot.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.startup.register(set_main_menu)

    dp.include_routers(commands.router)
    dp.include_routers(*get_dialogs())
    # dp.include_routers(*get_routers())

    bg_factory = setup_dialogs(dp)

    engine = await get_engine(config.db.dsn, config.db.echo)
    Sessionmaker = async_sessionmaker(engine)
    await create_tables(engine)

    dp.update.outer_middleware(DbSessionMiddleware(Sessionmaker))

    try:
        await dp.start_polling(bot, bg_factory=bg_factory)
    except Exception as e:
        logger.exception(e)
    finally:
        await bot.session.close()
        logger.info('Bot stopped')


if __name__ == "__main__":
    asyncio.run(main())
