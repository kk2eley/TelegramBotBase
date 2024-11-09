from aiogram import F
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import SwitchTo, Url, Select, Column, Back, Button
from aiogram_dialog.widgets.text import Const, Format, Multi

from bot.dialogs.admin_panel import start_admin_dialog
from bot.dialogs.filters import is_admin
from bot.dialogs.states import MenuSG

dialog = Dialog(
    Window(
        Const("Меню:"),
        Button(Const("Панель администратора"), id="admin_panel", when=is_admin, on_click=start_admin_dialog),
        state=MenuSG.OPTIONS,
    ),
)
