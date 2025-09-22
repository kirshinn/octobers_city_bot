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
        house_number = message.text
        if house_number not in ["1", "2"]:
            await message.answer("Ошибка: номер дома должен быть 1 или 2")
            logger.error(f"Неверный номер дома {house_number} для user_id={user_id}")
            return
        PENDING[pending_key]["house"] = house_number
        PENDING[pending_key]["step"] = "apartment"
        await message.answer("Шаг 2️⃣: Теперь введите номер квартиры")
        logger.info(f"Сохранён номер дома для user_id={user_id}, переход к шагу apartment")
    elif step == "apartment":
        try:
            apartment_number = int(message.text)
            house = PENDING[pending_key]["house"]
            if house == "1" and not (1 <= apartment_number <= 266):
                await message.answer("Ошибка: для дома 1 номер квартиры должен быть от 1 до 266")
                logger.error(f"Неверный номер квартиры {apartment_number} для дома 1, user_id={user_id}")
                return
            elif house == "2" and not (1 <= apartment_number <= 290):
                await message.answer("Ошибка: для дома 2 номер квартиры должен быть от 1 до 290")
                logger.error(f"Неверный номер квартиры {apartment_number} для дома 2, user_id={user_id}")
                return
            PENDING[pending_key]["apartment"] = str(apartment_number)
            logger.info(f"Сохранён номер квартиры {apartment_number} для дома {house}, user_id={user_id}")

            # if not approve_and_save(group_chat_id, user_id, pending_key):
            #     await message.answer(f"❌ Такой дом и квартира уже зарегистрированы.")
            #     await bot.decline_chat_join_request(group_chat_id, user_id)
            #     logger.info(f"Заявка отклонена для user_id={user_id}, group_chat_id={group_chat_id}: уже зарегистрировано")
            #     return

            await message.answer(
                f"✅ Спасибо! Вы указали:\n"
                f"🏠 Дом: {house}\n"
                f"🏢 Квартира: {apartment}\n"
                f"В ближайшее время заявку на вступление будет рассмотрена."
            )

            # await bot.approve_chat_join_request(chat_id=group_chat_id, user_id=user_id)
            # PENDING.pop(pending_key)
            # logger.info(f"Заявка одобрена для user_id={user_id}, group_chat_id={group_chat_id}")
        except ValueError:
            await message.answer("Ошибка: номер квартиры должен быть числом")
            logger.error(f"Некорректный ввод номера квартиры для user_id={user_id}")
            return
    else:
        logger.info(f"Неизвестный шаг для user_id={user_id}: {step}")
        await message.answer("Произошла ошибка, попробуйте снова.")