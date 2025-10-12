import os
from dotenv import load_dotenv

# Загружаем переменные из файла .env (если он есть в корне проекта)
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("Не найден BOT_TOKEN")

DEFAULT_GROUP_ID = os.getenv("DEFAULT_GROUP_ID")
if not DEFAULT_GROUP_ID:
    raise RuntimeError("Не найден DEFAULT_GROUP_ID")
