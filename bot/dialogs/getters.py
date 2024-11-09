import logging

from aiogram import Bot
from aiogram.enums import ContentType
from aiogram.types import User
from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from sqlalchemy.ext.asyncio import AsyncSession



logger = logging.getLogger(__name__)
