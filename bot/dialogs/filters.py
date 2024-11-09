import re
from typing import Dict

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.common import Whenable

from bot.config.config import get_config


def is_admin(data: Dict, widget: Whenable, manager: DialogManager):
    config = get_config()
    admins = config.bot.admin_ids

    return manager.event.from_user.id in admins


def format_russian_phone_number(phone: str) -> str:
    PHONE_REGEX = re.compile(r"^(\+7|8)(\d{10})$")
    # Проверка соответствия регулярному выражению
    match = PHONE_REGEX.match(phone)
    if not match:
        raise ValueError("Неверный формат номера телефона. Введите номер, начиная с +7 или 8 и 10 цифр.")

    # Получаем номер без кода страны
    phone_digits = match.group(2)

    # Приведение номера к единому формату +7 (...) ...-..-..
    formatted_number = f"+7 ({phone_digits[:3]}) {phone_digits[3:6]}-{phone_digits[6:8]}-{phone_digits[8:]}"

    return formatted_number
