import logging
from aiogram import Router, Bot, F
from aiogram.types import CallbackQuery

from storage import PENDING

logger = logging.getLogger(__name__)

# Роутер для callbacks
router = Router()

@router.callback_query(F.data)
async def handle_callback(cb: CallbackQuery, bot: Bot):
    data = cb.data or ""
    parts = data.split(":")
    if len(parts) != 3:
        await cb.answer("Ошибка формата callback")
        return

    action, chat_id_s, user_id_s = parts
    chat_id, user_id = int(chat_id_s), int(user_id_s)

    if action == "approve":
        await bot.approve_chat_join_request(chat_id, user_id)
        PENDING.pop((chat_id, user_id), None)
        await cb.message.edit_text(f"✅ Одобрено {user_id}")
        await cb.answer("Одобрено")

    elif action == "decline":
        await bot.decline_chat_join_request(chat_id, user_id)
        PENDING.pop((chat_id, user_id), None)
        await cb.message.edit_text(f"❌ Отклонено {user_id}")
        await cb.answer("Отклонено")

    else:
        await cb.answer("Неизвестное действие")
