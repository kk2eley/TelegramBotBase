from aiogram import Bot
from aiogram.types import BotCommand

commands = {
    'start': 'перейти в главное меню'
}

# Функция для настройки кнопки Menu бота
async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(
            command=command,
            description=description
        ) for command, description in commands.items()
    ]
    await bot.set_my_commands(main_menu_commands)