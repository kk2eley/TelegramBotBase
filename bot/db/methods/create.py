from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.config import get_config
from app.db import Tariff, Category, Chat, User, CategoryChat, Subscription, Card, Wallet, Mailing
from app.db.methods.read import get_setting_flag, get_categories, get_first_card, get_first_wallet
from app.db.models.payments import Payment
from app.db.models.referral import ReferralChat, ReferralSubscription
from app.db.models.settings import Setting


async def set_setting(session, setting_name, flag, value: int):
    setting = await session.get(Setting, setting_name)

    if setting is not None:
        setting.flag = flag  # Обновляем существующую настройку
        setting.value = value
    else:
        new_setting = Setting(name=setting_name, flag=flag, value=value)
        session.add(new_setting)  # Создаем новую настройку

    await session.commit()  # Сохраняем изменения


async def set_category(session: AsyncSession, name):
    stmt = select(Category).where(Category.name == name)
    result = await session.execute(stmt)
    category = result.scalar_one_or_none()

    if not category:
        new_category = Category(name=name)
        session.add(new_category)
    await session.commit()


async def set_tariff_without_commit(session: AsyncSession, tariff_id: int | None, duration: int, price: float,
                                    category_id: int):
    if tariff_id is not None:
        # Получаем существующий тариф
        tariff = await session.get(Tariff, tariff_id)

        # Обновляем значения тарифа
        tariff.duration = duration
        tariff.price = price

        result = tariff
    else:
        # Создаем новый тариф
        new_tariff = Tariff(duration=duration, price=price, category_id=category_id)
        session.add(new_tariff)

        result = new_tariff

    return result


async def create_tariff_with_category(session: AsyncSession, category_id: int, duration: int, price: float):
    # Проверяем, существует ли категория с указанным именем
    category = await session.get(Category, category_id)
    print(f"!!!!!!!!category.id {category.id} - {category.name} ")

    # Создаем новый тариф и привязываем его к категории
    new_tariff = Tariff(duration=duration, price=price, category=category)
    session.add(new_tariff)

    # Сохраняем изменения в базе данных
    await session.commit()


async def set_user(session: AsyncSession, telegram_id, username, fullname, status):
    user = await session.get(User, telegram_id)
    if user:
        user.username = username
        user.fullname = fullname
        user.status = status
    else:
        user = User(telegram_id=telegram_id, username=username, fullname=fullname, status=status)
        session.add(user)
    await session.commit()


async def set_new_chat(session: AsyncSession, chat_id: int, chat_title: str, chat_username: str):
    chat = await session.get(Chat, chat_id)
    if chat is not None:
        chat.title = chat_title
        chat.username = chat_username
    else:
        chat = Chat(chat_id=chat_id, title=chat_title, username=chat_username)
        session.add(chat)
    await session.commit()


async def set_category_chat(session: AsyncSession, category_id: int, chat_id: int):
    category_chat = CategoryChat(category_fk=category_id, chat_fk=chat_id)
    session.add(category_chat)
    await session.commit()


async def set_subscription(session: AsyncSession, user_id: int, tariff_id: int, start: datetime, end: datetime):
    new_sub = Subscription(user_fk=user_id, tariff_fk=tariff_id, start=start, end=end)
    session.add(new_sub)
    await session.commit()


async def set_card(session: AsyncSession, number: int, bank_name: str, phone: str):
    card = await get_first_card(session)
    if card is not None:
        card.number = number
        card.phone = phone
        card.bank_name=bank_name
        card.is_active = True
    else:
        card = Card(number=number, phone=phone, bank_name=bank_name, is_active=True)
        session.add(card)
    await session.commit()


async def set_wallet(session: AsyncSession, number: str):
    wallet = await get_first_wallet(session)
    if wallet is not None:
        wallet.number = number,
        wallet.is_active = True,
    else:
        wallet = Wallet(number=number, is_active=True)
        session.add(wallet)
    await session.commit()


async def set_defaults(session: AsyncSession):
    # записываем настройки в БД
    delete_message_setting = await get_setting_flag(session, "delete_messages")
    if delete_message_setting is None:
        await set_setting(session, "delete_messages", True, 0)
    referral_setting = await get_setting_flag(session, "referral")
    if referral_setting is None:
        await set_setting(session, "referral", True, 20)

    # записываем тарифы в БД
    tariffs = {
        "Фея": [
            (1, 5000),
            (7, 15000),
            (30, 40000),
        ],
        "Салон/Диспетчер": [
            (1, 7000),
            (7, 20000),
            (30, 60000),
        ],
        "Клиент": [
            (1, 2500),
            (7, 10000),
            (30, 25000),
        ],
        "Вирт": [
            (1, 4000),
            (7, 16000),
            (30, 30000),
        ],
    }
    old_categories = await get_categories(session)
    if not old_categories:
        for (category, dur_price), i in zip(tariffs.items(), range(1, 5, 1)):
            await set_category(session, category)
            for duration, price in dur_price:
                await set_tariff_without_commit(session, None, duration, price, i)

    bot_settings = get_config().bot

    # устанавливаем карту по умолчанию, если другой нет
    card = (await session.execute(select(Card))).scalars().first()
    if card is None:
        await set_card(session, bot_settings.default_card_number, bot_settings.default_bank_name,
                       bot_settings.default_phone_number)

    wallet = (await session.execute(select(Wallet))).scalars().first()
    if wallet is None:
        await set_wallet(session, bot_settings.default_crypto_wallet)


async def set_referral_chat(session: AsyncSession, user_fk: int, referral_id: int, chat_id: int):
    referral_chat = ReferralChat(user_fk=user_fk, referral_id=referral_id, chat_id=chat_id)
    session.add(referral_chat)
    await session.commit()


async def set_referral_subscription(session: AsyncSession, user_fk: int, referral_chats: list[ReferralChat],
                                    chat_id: int, start: datetime, end: datetime, referral_count: int):
    referral_subscription = ReferralSubscription(user_fk=user_fk, referral_chats=referral_chats, chat_id=chat_id,
                                                 start=start, end=end, referral_count=referral_count)
    for chat in referral_chats:
        chat.been_used = True
        session.add(chat)

    session.add(referral_subscription)
    await session.commit()


async def set_payment(session: AsyncSession, user_fk: int, tariff_fk: int, method: str, status: str):
    payment = Payment(user_fk=user_fk, tariff_fk=tariff_fk, method=method, status=status)
    session.add(payment)
    await session.flush()
    payment_id = payment.id
    await session.commit()
    return payment_id


async def set_mailing(session: AsyncSession, recipients: str, total: int, processed: int, blocked: int):
    mailing = Mailing(recipients=recipients, total=total, processed=processed, blocked=blocked)
    session.add(mailing)
    await session.flush()
    mailing_id = mailing.id
    await session.commit()
    return mailing_id
