# database.py

import sqlite3
from config import DB_NAME


def init_db():
    """Создаёт таблицы базы данных, если их ещё нет."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                currency TEXT DEFAULT 'usd',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                coin_name TEXT,
                symbol TEXT,
                amount REAL,
                price REAL,
                type TEXT,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                exchange TEXT,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                coin TEXT,
                target_price REAL,
                notified BOOLEAN DEFAULT 0,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                user_id INTEGER PRIMARY KEY,
                daily_report BOOLEAN DEFAULT 1,
                weekly_report BOOLEAN DEFAULT 1,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        """)
        conn.commit()


def add_user(user_id: int):
    """Добавляет пользователя в БД, если его ещё нет."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()


def add_transaction(user_id: int, coin_name: str, symbol: str, amount: float,
                    price: float, transaction_type: str, exchange: str = None):
    """Добавляет новую сделку в БД."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO transactions (user_id, coin_name, symbol, amount, price, type, exchange)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, coin_name, symbol, amount, price, transaction_type, exchange))
        conn.commit()


def get_portfolio(user_id: int):
    """Возвращает портфель пользователя — монеты, которые он купил и всё ещё держит."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT symbol, SUM(amount) as total_amount, AVG(price) as avg_price
            FROM transactions
            WHERE user_id = ? AND type = 'buy'
            GROUP BY symbol
            HAVING total_amount > 0
        """, (user_id,))
        return cursor.fetchall()


def get_all_transactions(user_id: int):
    """Возвращает историю всех сделок пользователя."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM transactions
            WHERE user_id = ?
            ORDER BY date DESC
        """, (user_id,))
        return cursor.fetchall()


def set_reminder(user_id: int, coin: str, target_price: float):
    """Устанавливает напоминание о целевой цене монеты."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO reminders (user_id, coin, target_price)
            VALUES (?, ?, ?)
        """, (user_id, coin, target_price))
        conn.commit()


def get_active_reminders(user_id: int):
    """Возвращает активные напоминания пользователя."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, coin, target_price FROM reminders
            WHERE user_id = ? AND notified = 0
        """, (user_id,))
        return cursor.fetchall()


def mark_reminder_as_notified(reminder_id: int):
    """Помечает напоминание как отправленное."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE reminders SET notified = 1
            WHERE id = ?
        """, (reminder_id,))
        conn.commit()


def set_user_currency(user_id: int, currency: str):
    """Устанавливает валюту отображения для пользователя."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users SET currency = ? WHERE user_id = ?
        """, (currency.lower(), user_id))
        conn.commit()


def get_user_currency(user_id: int) -> str:
    """Возвращает установленную пользователем валюту."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT currency FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        return result[0] if result else 'usd'


def get_all_users():
    """Возвращает список всех пользователей бота."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users")
        return [row[0] for row in cursor.fetchall()]