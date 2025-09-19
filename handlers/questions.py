from aiogram import Router, Bot
from aiogram.types import Message
from storage import PENDING, approve_and_save
import logging

logger = logging.getLogger(__name__)

router = Router()

@router.message(lambda message: message.content_type == "text")
async def process_answer(message: Message, bot: Bot):
    user_id = message.from_user.id
    logger.info(f"Получено сообщение от user_id={user_id}, текст={message.text}")

    # Ищем заявку пользователя в PENDING
    pending_key = None
    for key, data in PENDING.items():
        if data.get("user_id") == user_id:
            pending_key = key
            break

    if not pending_key:
        logger.info(f"Заявка не найдена для user_id={user_id}")
        await message.answer("Сначала подайте заявку на вступление в группу.")
        return

    group_chat_id = pending_key[0]
    step = PENDING[pending_key]["step"]

    if step == "house":
        PENDING[pending_key]["house"] = message.text
        PENDING[pending_key]["step"] = "apartment"
        await message.answer("Шаг 2️⃣: Теперь введите номер квартиры")
        logger.info(f"Сохранён номер дома для user_id={user_id}, переход к шагу apartment")
    elif step == "apartment":
        PENDING[pending_key]["apartment"] = message.text
        house = PENDING[pending_key]["house"]
        apartment = PENDING[pending_key]["apartment"]

        if not approve_and_save(group_chat_id, user_id, pending_key):
            await message.answer(f"❌ Такой дом и квартира уже зарегистрированы.")
            await bot.decline_chat_join_request(group_chat_id, user_id)
            logger.info(f"Заявка отклонена для user_id={user_id}, group_chat_id={group_chat_id}: уже зарегистрировано")
            return

        await message.answer(
            f"✅ Спасибо! Вы указали:\n"
            f"🏠 Дом: {house}\n"
            f"🏢 Квартира: {apartment}\n"
            f"В ближайшее время заявку на вступление будет рассмотрена."
        )

        # await bot.approve_chat_join_request(chat_id=group_chat_id, user_id=user_id)
        # PENDING.pop(pending_key)
        # logger.info(f"Заявка одобрена для user_id={user_id}, group_chat_id={group_chat_id}")
    else:
        logger.info(f"Неизвестный шаг для user_id={user_id}: {step}")
        await message.answer("Произошла ошибка, попробуйте снова.")
