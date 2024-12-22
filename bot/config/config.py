from dataclasses import dataclass
from environs import Env


@dataclass
class Bot:
    token: str
    admin_ids: list[int]


@dataclass
class Db:
    user: str
    host: str
    password: str
    db: str
    dsn: str
    echo: bool


@dataclass
class Config:
    bot: Bot
    db: Db


def get_config():
    env = Env()
    env.read_env()

    return Config(
        bot=Bot(
            token=env.str("BOT_TOKEN"),
            admin_ids=env.list("ADMIN_IDS", subcast=int),
        ),
        db=Db(
            user=env.str("POSTGRES_USER"),
            host=env.str("DB_HOST"),
            password=env.str("POSTGRES_PASSWORD"),
            db=env.str("POSTGRES_DB"),
            dsn=f'postgresql+asyncpg://{env.str("POSTGRES_USER")}:{env.str("POSTGRES_PASSWORD")}@{env.str("DB_HOST")}/{env.str("POSTGRES_DB")}',
            echo=env.bool("DB_ECHO")
        ),
    )
