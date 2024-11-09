from datetime import datetime

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.db import Chat, User, Subscription, Card, Wallet, CategoryChat, Mailing
from app.db.models.payments import Payment
from app.db.models.referral import ReferralChat, ReferralSubscription
from app.db.models.settings import Setting
from app.db.models.tariffs import Tariff, Category


async def get_tariffs_by_category(session: AsyncSession, category_id: int) -> list[Tariff]:
    stmt = (
        select(Tariff)
        .options(joinedload(Tariff.category))  # Подгружаем связанные данные категории
        .where(Tariff.category_id == category_id)
        .order_by(Tariff.duration.asc())
    )
    result = await session.execute(stmt)
    result = result.scalars().all()
    return result


async def get_tariff(session: AsyncSession, tariff_id):
    tariff = await session.get(Tariff, tariff_id)
    return tariff


async def get_tariff_with_category(session: AsyncSession, tariff_id):
    tariff = await session.get(Tariff, tariff_id, options=[joinedload(Tariff.category)])
    return tariff


async def get_setting_flag(session, setting_name):
    setting = await session.get(Setting, setting_name)
    if setting:
        return setting.flag
    return None  # Если настройка не найдена


async def get_setting(session, setting_name):
    setting = await session.get(Setting, setting_name)
    if setting:
        return setting
    return None  # Если настройка не найдена


async def get_categories(session: AsyncSession) -> list[Category]:
    stmt = select(Category)
    result = await session.execute(stmt)
    result = result.scalars().all()

    return result


async def get_category(session: AsyncSession, category_id):
    result = await session.get(Category, category_id)

    return result


async def get_chats_by_category(session: AsyncSession, category_id: int) -> list[Chat]:
    # Получаем категорию по её ID и загружаем связанные чаты
    stmt = select(Category).options(joinedload(Category.chats)).where(Category.id == category_id)
    result = await session.execute(stmt)
    category = result.scalars().first()

    if category:
        return category.chats  # Возвращаем связанные чаты
    return []


# async def get_chats():

async def get_recently_added_chat(session: AsyncSession, telegram_id) -> Chat:
    user = await session.get(User, telegram_id)
    chat_id = user.recently_added_chat_id
    result = await session.execute(select(Chat).where(Chat.chat_id == chat_id))
    chat = result.scalar_one_or_none()
    return chat


async def get_chat(session: AsyncSession, chat_id: int):
    chat = await session.get(Chat, chat_id)
    return chat


async def get_chats(session: AsyncSession):
    result = await session.execute(select(Chat))
    result = result.scalars().all()
    return result


async def get_user_id_by_telegram_id(session: AsyncSession, telegram_id: int):
    user_id = await session.get(User, telegram_id)
    return user_id


async def get_user_chats(session: AsyncSession, telegram_id: int):
    # Запрос на получение пользователя по telegram_id
    result = await session.execute(
        select(User)
        .options(
            joinedload(User.subscriptions)
            .joinedload(Subscription.tariff)
            .joinedload(Tariff.category)
            .joinedload(Category.chats)
        )
        .where(User.telegram_id == telegram_id)
    )
    user = result.unique().scalar_one_or_none()

    if not user:
        return []  # Если пользователь не найден

    # Собираем все чаты, которые доступны через подписки пользователя
    chats = []
    for subscription in user.subscriptions:
        if subscription.tariff and subscription.tariff.category:
            chats.extend(subscription.tariff.category.chats)
    chats = list(set(chats))
    return chats


async def get_user_referral_chat_ids(session: AsyncSession, telegram_id: int):
    result = await session.execute(
        select(User)
        .options(
            joinedload(User.referral_subscriptions)
            .joinedload(ReferralSubscription.referral_chats)
        )
        .where(User.telegram_id == telegram_id)
    )
    user = result.unique().scalar_one_or_none()

    chat_ids = []
    for referral_subscription in user.referral_subscriptions:
        chat_ids.append(referral_subscription.referral_chats[0].chat_id)

    return chat_ids


# async def get_category_chats(session: AsyncSession, category_id: int):
#     # Используем selectinload для явной подгрузки связанных чатов
#     category = await session.execute(select(Category)
#                                      .options(joinedload(Category.chats))
#                                      .where(Category.id == category_id)
#                                      )
#     category = category.scalars().first()
#
#     # Теперь category.chats будет подгружен сразу
#     return category.chats


# async def get_category_chats(session: AsyncSession, category_id: int):
#     # Используем selectinload для явной подгрузки связанных чатов
#     category = await session.get(Category, category_id, options=[selectinload(Category.chats)])
#
#     # Теперь category.chats будет подгружен сразу
#     return category.chats

async def get_category_chats(session: AsyncSession, category_id: int):
    chats = (await session.execute(select(CategoryChat).where(CategoryChat.category_fk == category_id))).scalars().all()

    return chats


async def get_active_card(session: AsyncSession):
    result = await session.execute(select(Card).where(Card.is_active == True))
    result = result.scalars().first()
    return result


async def get_cards(session: AsyncSession) -> list[Card]:
    result = await session.execute(select(Card))
    result = result.scalars().all()
    return result


async def get_user_actual_subscriptions(session, user_id: int) -> list[Subscription]:
    result = await session.execute(
        select(Subscription)
        .options(
            joinedload(Subscription.tariff)
            .joinedload(Tariff.category)
        )
        .where(Subscription.user_fk == user_id)
        .where(Subscription.end > datetime.now().astimezone())
    )

    result = result.scalars().all()

    return result


async def get_user_actual_referral_subscriptions(session: AsyncSession, user_id: int) -> list[ReferralSubscription]:
    result = await session.execute(
        select(ReferralSubscription)
        .options(
            joinedload(ReferralSubscription.referral_chats)
        )
        .where(ReferralSubscription.user_fk == user_id)
        .where(ReferralSubscription.end > datetime.now().astimezone())
    )

    result = result.unique().scalars().all()

    return result


async def get_latest_subscription_in_category(session: AsyncSession, category_id: int):
    result = await session.execute(
        select(Subscription)
        .options(
            joinedload(Subscription.tariff)
        )
        .where(
            Tariff.category_id == category_id
        )
        .order_by(
            desc(Subscription.end)
        )
    )
    result = result.scalars().first()
    return result


async def get_active_wallet(session: AsyncSession):
    result = await session.execute(select(Wallet).where(Wallet.is_active == True))
    result = result.scalars().first()

    return result


async def get_user(session: AsyncSession, user_id):
    user = await session.get(User, user_id)
    return user


async def get_referral_chats(session: AsyncSession, user_fk: int, chat_id: int):
    result = await session.execute(select(ReferralChat)
                                   .where(ReferralChat.user_fk == user_fk)
                                   .where(ReferralChat.chat_id == chat_id)
                                   .where(ReferralChat.been_used == False)
                                   )
    result = result.scalars().all()
    return result


async def get_latest_referral_subscription(session: AsyncSession, user_fk: int, chat_id: int):
    result = await session.execute(
        select(ReferralSubscription)
        .where(ReferralSubscription.user_fk == user_fk)
        .where(ReferralSubscription.chat_id == chat_id)
        .order_by(
            desc(ReferralSubscription.end)
        )
    )
    result = result.scalars().first()
    return result


async def get_referral_subscription(session, user_fk: int, chat_id: int):
    result = await session.execute(select(ReferralSubscription)
                                   .where(ReferralSubscription.user_fk == user_fk)
                                   .where(ReferralSubscription.chat_id == chat_id))

    result = result.scalars().first()
    return result


async def get_unused_referral_chats(session: AsyncSession, user_fk: int, chat_id: int) -> list[ReferralChat]:
    result = await session.execute(select(ReferralChat)
                                   .where(ReferralChat.user_fk == user_fk)
                                   .where(ReferralChat.chat_id == chat_id)
                                   .where(ReferralChat.been_used == False))

    result = result.scalars().all()
    return result


async def get_referral_chat(session: AsyncSession, referral_id: int, chat_id: int):
    result = await session.execute(
        select(ReferralChat).where(
            ReferralChat.chat_id == chat_id,
            ReferralChat.referral_id == referral_id
        )
    )
    return result.scalars().first()


async def get_users_by_filters(session: AsyncSession, filters: set) -> list[User]:
    result = await session.execute(select(User).where(User.status.in_(filters)))
    result = result.scalars().all()
    return result


async def get_unconfirmed_payments(session: AsyncSession) -> list[Payment]:
    result = await session.execute(
        select(Payment).options(
            selectinload(Payment.user)
            .selectinload(User.referral_chats),
            selectinload(Payment.tariff)
            .selectinload(Tariff.category)
        )
        .where(Payment.method != 'merchant')
        .where(Payment.status == 'waiting_confirmation')
        .order_by(Payment.id)
    )
    result = result.unique().scalars().all()

    return result


async def get_payment(session: AsyncSession, id: int):
    result = await session.execute(select(Payment)
                                   .options(joinedload(Payment.user),
                                            joinedload(Payment.tariff).joinedload(Tariff.category))
                                   .where(Payment.id == id)
                                   )

    result = result.unique().scalars().first()
    return result


async def get_active_mailing(session: AsyncSession, recipients: str) -> Mailing:
    mailing = await session.execute(
        select(Mailing).where(Mailing.recipients == recipients).where(Mailing.done == False))
    mailing = mailing.scalars().first()
    return mailing


async def get_mailing(session: AsyncSession, mailing_id: int):
    mailing = await session.get(Mailing, mailing_id)
    return mailing


async def have_user_active_client_subscription(session: AsyncSession, telegram_id: int) -> bool:
    result = await session.execute(
        select(User)
        .options(
            joinedload(User.subscriptions)
            .joinedload(Subscription.tariff)
            .joinedload(Tariff.category)
        )
        .where(User.telegram_id == telegram_id)
    )
    user = result.unique().scalar_one_or_none()

    if not user:
        return False  # Если пользователь не найден

    for subscription in user.subscriptions:
        if subscription.tariff.category.id == 3:
            return True  # Нашли подписку Клиент

    return False  # Не нашли подписку Клиент

async def get_card(session: AsyncSession, card_id: int):
    card = await session.get(Card, card_id)
    return card

async def get_wallet(session: AsyncSession, wallet_id: int):
    wallet = await session.get(Wallet, wallet_id)
    return wallet

async def get_first_card(session: AsyncSession) -> Card:
    card = await session.execute(select(Card))
    card = card.scalars().first()
    return card

async def get_first_wallet(session: AsyncSession) -> Wallet:
    wallet = await session.execute(select(Wallet))
    wallet = wallet.scalars().first()
    return wallet