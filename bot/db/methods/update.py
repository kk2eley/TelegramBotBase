import logging

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import Tariff, User, Mailing, Card, Wallet
from app.db.methods.read import get_referral_chat, get_first_card, get_first_wallet
from app.db.models.payments import Payment
from app.db.models.settings import Setting

logger = logging.getLogger(__name__)


async def update_tariff_values(session: AsyncSession, tariff_id, duration, price):
    tariff = await session.get(Tariff, tariff_id)

    tariff.duration = duration
    tariff.price = price

    session.add(tariff)

    await session.commit()


async def set_recently_added_chat(session: AsyncSession, telegram_id: int, username: str, fullname: str, chat_id: int):
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    logger.debug(f"got user {user}")
    if user is None:
        user = User(telegram_id=telegram_id, username=username, fullname=fullname, status='never_subscribed')
        session.add(user)
    else:
        user.recently_added_chat_id = chat_id
    await session.commit()


async def set_user_status(session: AsyncSession, telegram_id: int, status: str):
    user = await session.get(User, telegram_id)
    user.status = status
    session.add(user)
    await session.commit()


async def update_setting_value(session: AsyncSession, setting_name: str, value: int):
    setting = await session.get(Setting, setting_name)
    setting.value = value
    session.add(setting)
    await session.commit()


async def update_setting_flag(session: AsyncSession, setting_name: str, flag: bool):
    setting = await session.get(Setting, setting_name)
    setting.flag = flag
    session.add(setting)
    await session.commit()


async def update_user_referral_id(session: AsyncSession, user_id: int, referral_id: int):
    user = await session.get(User, user_id)
    user.referral_id = referral_id
    session.add(user)
    await session.commit()


async def unbind_referral_chat(session: AsyncSession, referral_id: int, chat_id: int):
    referral_chat = await get_referral_chat(session, referral_id, chat_id)

    if referral_chat is None:
        raise ValueError(f"No referral chat found for referral_id={referral_id} and chat_id={chat_id}")

    # Удаляем связь через relationship
    referral_chat.referral_subscription = None
    await session.commit()


async def change_payment_status(session: AsyncSession, payment_id: int, status):
    payment = await session.get(Payment, payment_id)
    payment.status = status
    await session.commit()


async def update_mailing_counter(session: AsyncSession, mailing_id: int, new_processed: int, new_blocked: int):
    mailing = await session.get(Mailing, mailing_id)
    mailing.processed += new_processed
    mailing.blocked += new_blocked
    await session.commit()


async def done_mailing(session: AsyncSession, mailing_id: int):
    mailing = await session.get(Mailing, mailing_id)
    mailing.done = True
    await session.commit()


async def set_payment_text_and_photo(session: AsyncSession, payment_id: int, text: str, photo: str):
    payment = await session.get(Payment, payment_id)
    payment.user_text = text
    payment.user_photo = photo
    await session.commit()


async def set_payment_photo(session: AsyncSession, payment_id: int, photo: str):
    payment = await session.get(Payment, payment_id)
    payment.user_photo = photo
    await session.commit()


async def set_payment_text(session: AsyncSession, payment_id: int, text: str):
    payment = await session.get(Payment, payment_id)
    payment.user_text = text
    await session.commit()


async def update_first_card_activity(session: AsyncSession, is_active: bool):
    card = await session.execute(select(Card))
    card = card.scalars().first()
    card.is_active = is_active
    await session.commit()


async def update_fist_wallet_activity(session: AsyncSession, is_active: bool):
    wallet = await session.execute(select(Wallet))
    wallet = wallet.scalars().first()
    wallet.is_active = is_active
    await session.commit()


async def update_card_bank_name(session: AsyncSession, bank_name: str):
    card = await get_first_card(session)
    card.bank_name = bank_name
    await session.commit()


async def update_card_number(session: AsyncSession, number: int):
    card = await get_first_card(session)
    card.number = number
    await session.commit()


async def update_card_phone_number(session: AsyncSession, phone_number: str):
    card = await get_first_card(session)
    card.phone = phone_number
    await session.commit()


async def update_wallet_number(session: AsyncSession, number: str):
    wallet = await get_first_wallet(session)
    wallet.number = number
    await session.commit()
