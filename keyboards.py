from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_admin_keyboard(chat_id: int, user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Одобрить", callback_data=f"approve:{chat_id}:{user_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"decline:{chat_id}:{user_id}"),
        ]
    ])
