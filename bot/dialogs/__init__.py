from aiogram_dialog import Dialog

from . import menu, admin_panel, new_chat, notification, stop_subscription, mailing


def get_dialogs() -> [Dialog]:
    return [
        admin_panel.dialog,
        menu.dialog,
        new_chat.dialog,
        notification.dialog,
        stop_subscription.dialog,
        mailing.dialog
    ]
