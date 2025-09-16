from aiogram import Bot, Router
from aiogram.types import ChatJoinRequest
from storage import PENDING
import logging

logger = logging.getLogger(__name__)

router = Router()

@router.chat_join_request()
async def handle_chat_join_request(join_request: ChatJoinRequest, bot: Bot):
    group_chat_id = join_request.chat.id
    user = join_request.from_user
    user_id = user.id

    PENDING[(group_chat_id, user_id)] = {
        "user_full_name": user.full_name,
        "username": getattr(user, "username", None),
        "bio": getattr(join_request, "bio", None),
        "user_id": user_id,
        "step": "house"
    }

    try:
        await bot.send_message(
            user_id,
            "👋 Чтобы вступить в группу, ответьте на пару вопросов.\n\n"
            "Шаг 1️⃣: Введите номер дома"
        )
        logger.info(f"Запрос на ввод номера дома отправлен для user_id={user_id}, group_chat_id={group_chat_id}")
    except Exception as e:
        logger.error(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
        await bot.decline_chat_join_request(chat_id=group_chat_id, user_id=user_id)