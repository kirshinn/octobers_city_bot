from aiogram.types import Message
from storage import PENDING

async def cmd_start(message: Message):
    await message.answer("👋 Привет! Я бот для управления заявками на вступление в группу.")

async def cmd_pending(message: Message):
    if not PENDING:
        await message.answer("📭 Нет ожидающих заявок.")
        return

    text = "⏳ Ожидающие заявки:\n\n"
    for (chat_id, user_id), data in PENDING.items():
        text += f"👤 {data['user_full_name']} (@{data.get('username')}) — chat_id={chat_id}, user_id={user_id}\n"
    await message.answer(text)
