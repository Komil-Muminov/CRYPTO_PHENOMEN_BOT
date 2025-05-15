# utils.py

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("💼 Портфель", callback_data="portfolio"),
         InlineKeyboardButton("📊 График", callback_data="chart")],
        [InlineKeyboardButton("🔍 Рекомендации", callback_data="recommend"),
         InlineKeyboardButton("➕ Добавить сделку", callback_data="add_transaction")],
        [InlineKeyboardButton("🔔 Напоминания", callback_data="reminders"),
         InlineKeyboardButton("⚙️ Настройки", callback_data="settings")]
    ]
    return InlineKeyboardMarkup(keyboard)


def back_to_main_menu():
    keyboard = [
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)