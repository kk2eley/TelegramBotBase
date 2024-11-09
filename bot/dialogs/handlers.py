import asyncio
import logging

from aiogram import Bot
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.input import ManagedTextInput, MessageInput
from aiogram_dialog.widgets.kbd import Button
from sqlalchemy.ext.asyncio import AsyncSession

from bot.dialogs.states import MenuSG

logger = logging.getLogger(__name__)



async def on_cancel(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    # await c.message.delete()  # Удаляем сообщение при нажатии кнопки Cancel
    await dialog_manager.start(MenuSG.OPTIONS, mode=StartMode.RESET_STACK,
                               data=dialog_manager.start_data)
