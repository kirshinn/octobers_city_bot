import sqlite3
from datetime import datetime
from typing import Tuple, Dict

PENDING: Dict[Tuple[int, int], Dict] = {}

conn = sqlite3.connect('users.db')

def init_db():
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (chat_id INTEGER,
                  user_id INTEGER,
                  house TEXT,
                  apartment TEXT,
                  full_name TEXT,
                  username TEXT,
                  bio TEXT,
                  created_at TEXT,
                  UNIQUE (chat_id, house, apartment))''')
    conn.commit()

def check_user(chat_id: int, house: str, apartment: str) -> str | None:
    c = conn.cursor()
    c.execute("SELECT full_name FROM users WHERE chat_id=? AND house=? AND apartment=?", (chat_id, house, apartment))
    row = c.fetchone()
    return row[0] if row else None

def add_user(chat_id: int, user_id: int, house: str, apartment: str, full_name: str, username: str | None, bio: str | None):
    c = conn.cursor()
    c.execute("INSERT INTO users (chat_id, user_id, house, apartment, full_name, username, bio, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
              (chat_id, user_id, house, apartment, full_name, username, bio, datetime.now().isoformat()))
    conn.commit()

def approve_and_save(chat_id: int, user_id: int, pending_key: Tuple[int, int]) -> bool:
    if pending_key in PENDING:
        pending_data = PENDING[pending_key]
        if "house" in pending_data and "apartment" in pending_data:
            existing = check_user(chat_id, pending_data["house"], pending_data["apartment"])
            if existing:
                return False
            full_name = pending_data["user_full_name"]
            username = pending_data.get("username")
            bio = pending_data.get("bio")
            house = pending_data["house"]
            apartment = pending_data["apartment"]
            add_user(chat_id, user_id, house, apartment, full_name, username, bio)
    return True
