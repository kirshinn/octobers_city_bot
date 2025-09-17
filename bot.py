import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from storage import init_db
from handlers import callbacks, join_request, questions
from handlers.commands import cmd_start, cmd_pending

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Регистрация команд
dp.message.register(cmd_start, Command(commands=["start"]))
dp.message.register(cmd_pending, Command(commands=["pending"]))

# Подключаем маршруты
dp.include_router(callbacks.router)
dp.include_router(join_request.router)
dp.include_router(questions.router)

async def main():
    init_db()  # Инициализация базы данных
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен")
