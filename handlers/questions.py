import logging
from typing import Optional, Tuple

from aiogram import Router, Bot
from aiogram.types import Message

from config import DEFAULT_GROUP_ID
from storage import PENDING

logger = logging.getLogger(__name__)
router = Router()

MEMBER_CACHE = {}  # user_id -> True/False (в группе или нет)

async def check_member(bot: Bot, user_id: int) -> bool:
    """
    Проверяет, есть ли пользователь в группе, с кэшем.
    """
    if MEMBER_CACHE.get(user_id):
        return True
    try:
        member = await bot.get_chat_member(DEFAULT_GROUP_ID, user_id)
        in_group = member.status in ["member", "administrator", "creator"]
        logger.info(f"статус в группе {member.status}")
    except Exception as e:
        logger.warning(f"Не удалось проверить статус участника {user_id}: {e}")
        in_group = False
    MEMBER_CACHE[user_id] = in_group
    return in_group

async def handle_house_step(message: Message, pending_key: Tuple[int, int]):
    """
    Обрабатывает шаг house: сохраняет номер дома и переводит шаг на apartment
    """
    user_id = message.from_user.id
    house_number = message.text.strip()
    if house_number not in ["1", "2"]:
        await message.answer("Ошибка: номер дома должен быть 1 или 2")
        logger.error(f"Неверный номер дома {house_number} для user_id={user_id}")
        return False

    PENDING[pending_key]["house"] = house_number
    PENDING[pending_key]["step"] = "apartment"
    await message.answer("Шаг 2️⃣: Теперь введите номер квартиры")
    logger.info(f"Сохранён номер дома {house_number} для user_id={user_id}, переход к шагу apartment")
    return True

async def handle_apartment_step(message: Message, pending_key: Tuple[int, int]):
    """
    Обрабатывает шаг apartment: сохраняет номер квартиры и отправляет финальное сообщение
    """
    user_id = message.from_user.id
    try:
        apartment_number = int(message.text.strip())
        house = PENDING[pending_key]["house"]

        # проверка валидности квартиры
        if house == "5a" and not (1 <= apartment_number <= 266):
            await message.answer("Ошибка: для дома 1 номер квартиры должен быть от 1 до 266")
            logger.error(f"Неверный номер квартиры {apartment_number} для дома 1, user_id={user_id}")
            return False
        elif house == "5b" and not (1 <= apartment_number <= 290):
            await message.answer("Ошибка: для дома 2 номер квартиры должен быть от 1 до 290")
            logger.error(f"Неверный номер квартиры {apartment_number} для дома 2, user_id={user_id}")
            return False

        PENDING[pending_key]["apartment"] = str(apartment_number)
        logger.info(f"Сохранён номер квартиры {apartment_number} для дома {house}, user_id={user_id}")

        # финальное сообщение пользователю
        await message.answer(
            f"✅ Спасибо! Вы указали:\n"
            f"🏠 Дом: {house}\n"
            f"🏢 Квартира: {apartment_number}\n"
            f"После проверки заявка на вступление будет рассмотрена.",
            parse_mode='HTML'
        )
        return True
    except ValueError:
        await message.answer("Ошибка: номер квартиры должен быть числом")
        logger.error(f"Некорректный ввод номера квартиры для user_id={user_id}")
        return False

@router.message(lambda message: message.content_type == "text")
async def process_answer(message: Message, bot: Bot):
    user_id = message.from_user.id
    logger.info(f"Получено сообщение от user_id={user_id}, текст={message.text}")

    # ищем заявку пользователя в PENDING
    pending_key: Optional[Tuple[int, int]] = None
    for key, data in PENDING.items():
        if data.get("user_id") == user_id:
            pending_key = key  # key должен быть Tuple[int, int]
            break

    if not pending_key:
        if await check_member(bot, user_id):
            return  # уже в группе, не спамим
        await message.answer("Сначала подайте заявку на вступление в группу.")
        return

    step = PENDING[pending_key]["step"]
    if step == "house":
        await handle_house_step(message, pending_key)
    elif step == "apartment":
        await handle_apartment_step(message, pending_key)
    else:
        await message.answer("Произошла ошибка, попробуйте снова.")
        logger.error(f"Неизвестный шаг {step} для user_id={user_id}")
