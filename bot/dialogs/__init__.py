from aiogram_dialog import Dialog

from . import menu, admin_panel


def get_dialogs() -> [Dialog]:
    return [
        admin_panel.dialog,
        menu.dialog,
    ]
