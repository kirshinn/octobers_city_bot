from aiogram.types import Message
from storage import PENDING
from keyboards import build_admin_keyboard

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

async def cmd_list_requests(msg: Message):
    if not PENDING:
        await msg.answer("📭 Нет заявок в ожидании.")
        return

    for (chat_id, user_id), data in PENDING.items():
        kb = build_admin_keyboard(chat_id, user_id)
        text = f"📨 Заявка от 👤 {data['user_full_name']} (@{data.get('username')}) (id={user_id})"
        await msg.answer(text, reply_markup=kb)
