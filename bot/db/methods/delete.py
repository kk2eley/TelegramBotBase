from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import CategoryChat
from app.db.methods.read import get_first_card
from app.db.models.referral import ReferralChat, ReferralSubscription


async def unbind_category_from_chat(session: AsyncSession, chat_id: int, category_id: int):
    stmt = select(CategoryChat).where(
        CategoryChat.category_fk == category_id,
        CategoryChat.chat_fk == chat_id
    )
    result = await session.execute(stmt)
    entry = result.scalar_one_or_none()

    if entry:
        # Удаление записи
        await session.delete(entry)
        await session.commit()


async def delete_referral_chat(session: AsyncSession, referral_id: int, chat_id: int):
    result = await session.execute(
        select(ReferralChat).where(
            ReferralChat.chat_id == chat_id,
            ReferralChat.referral_id == referral_id
        )
    )
    await session.delete(result)
    await session.commit()


async def delete_referral_subscription(session: AsyncSession, referral_subscription_id: int):
    result = await session.get(ReferralSubscription, referral_subscription_id)
    await session.delete(result)
    await session.commit()


async def delete_card_phone_number(session):
    card = await get_first_card(session)
    card.phone = None
    await session.commit()
