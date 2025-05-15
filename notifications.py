# notifications.py

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import time
from telegram import Bot
import logging
from analytics import calculate_portfolio
from charts import generate_portfolio_chart
from database import get_all_users, get_user_notifications, toggle_daily_notification, toggle_weekly_notification

logging.basicConfig(level=logging.INFO)

bot = Bot("YOUR_BOT_TOKEN")  # Заменяется на config.BOT_TOKEN
scheduler = AsyncIOScheduler()

# === Функции управления уведомлениями ===

def init_scheduler():
    """Инициализирует расписание задач."""
    scheduler.start()

    # Ежедневный отчёт в 9:00
    scheduler.add_job(
        send_daily_report_to_all,
        'cron',
        hour=9,
        minute=0,
        id='daily_report',
        replace_existing=True
    )

    # Еженедельный отчёт по понедельникам в 9:00
    scheduler.add_job(
        send_weekly_report_to_all,
        'cron',
        day_of_week='mon',
        hour=9,
        minute=0,
        id='weekly_report',
        replace_existing=True
    )


async def send_daily_report(user_id):
    """Отправляет пользователю ежедневный отчёт о состоянии портфеля."""
    try:
        data = calculate_portfolio(user_id)
        if not data['assets']:
            return  # Нет активов — не отправляем

        text = "📅 Ежедневный отчёт:\n\n"
        text += f"Общая стоимость: ${data['total']['current']:.2f}\n"
        profit_str = "+" if data['total']['profit'] >= 0 else "-"
        text += f"Прибыль: {profit_str}${abs(data['total']['profit']):.2f} ({data['total']['roi']:+.2f}%)\n"

        chart_img = generate_portfolio_chart(data)
        await bot.send_photo(chat_id=user_id, photo=chart_img, caption=text)
    except Exception as e:
        logging.error(f"Ошибка при отправке ежедневного отчёта для {user_id}: {e}")


async def send_weekly_report(user_id):
    """Отправляет пользователю еженедельный отчёт о состоянии портфеля."""
    try:
        data = calculate_portfolio(user_id)
        if not data['assets']:
            return  # Нет активов — не отправляем

        text = "📆 Еженедельный отчёт:\n\n"
        text += f"Всего вложено: ${data['total']['invested']:.2f}\n"
        text += f"Текущая стоимость: ${data['total']['current']:.2f}\n"
        profit_str = "+" if data['total']['profit'] >= 0 else "-"
        text += f"Прибыль: {profit_str}${abs(data['total']['profit']):.2f} ({data['total']['roi']:+.2f}%)\n\n"
        text += "Самый прибыльный актив:\n"
        top_asset = max(data['assets'], key=lambda x: x['profit']) if data['assets'] else None
        if top_asset:
            text += f"{top_asset['symbol']} (+${top_asset['profit']:.2f})"

        chart_img = generate_portfolio_chart(data)
        await bot.send_photo(chat_id=user_id, photo=chart_img, caption=text)
    except Exception as e:
        logging.error(f"Ошибка при отправке еженедельного отчёта для {user_id}: {e}")


async def send_daily_report_to_all():
    """Отправляет ежедневный отчёт всем, кто его включил."""
    for user_id in get_all_users():
        if get_user_notifications(user_id)[0]:  # daily_report enabled
            await send_daily_report(user_id)


async def send_weekly_report_to_all():
    """Отправляет еженедельный отчёт всем, кто его включил."""
    for user_id in get_all_users():
        if get_user_notifications(user_id)[1]:  # weekly_report enabled
            await send_weekly_report(user_id)


# === Вспомогательные функции ===

def toggle_daily_notification(user_id):
    """Включает или выключает ежедневный отчёт."""
    from database import toggle_daily_notification as db_toggle
    return db_toggle(user_id)


def toggle_weekly_notification(user_id):
    """Включает или выключает еженедельный отчёт."""
    from database import toggle_weekly_notification as db_toggle
    return db_toggle(user_id)


def get_user_notifications(user_id):
    """Возвращает статус уведомлений пользователя."""
    from database import get_user_notifications as db_get
    return db_get(user_id)