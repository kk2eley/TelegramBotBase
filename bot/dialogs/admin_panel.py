from aiogram import F
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager, StartMode, ShowMode
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.kbd import SwitchTo, Button, Select, Column, Group, Back, Url, \
    Row, ScrollingGroup
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Const, Format, Progress

from bot.dialogs.handlers import on_cancel
from bot.dialogs.states import AdminSG


async def start_admin_dialog(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(AdminSG.OPTIONS, mode=StartMode.RESET_STACK,
                               data=dialog_manager.start_data,
                               show_mode=ShowMode.AUTO)


dialog = Dialog(
    Window(
        Const("Добро пожаловать в панель администратора:"),
        Button(Const("Назад в меню"), id="back_to_menu", on_click=on_cancel),
        state=AdminSG.OPTIONS,
    ),
)
