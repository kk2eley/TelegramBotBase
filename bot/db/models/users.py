from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, relationship, mapped_column

from bot.db import Base


class User(Base):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, primary_key=True)
    username: Mapped[str] = mapped_column(String, nullable=True)
    fullname: Mapped[str] = mapped_column(String)


