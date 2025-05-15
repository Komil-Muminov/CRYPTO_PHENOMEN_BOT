# app.py

from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters
from notifications import scheduler, send_daily_report, send_weekly_report

from bot_handlers import (
    start,
    button_handler,
    handle_add_transaction_start,
    handle_coin_input,
    handle_amount_input,
    handle_price_input,
    handle_exchange_input,
    skip_exchange,
    handle_confirmation
)

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_add_transaction_start, pattern='^type_')],
        states={
            ENTER_COIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_coin_input)],
            ENTER_AMOUNT_OR_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_amount_input)],
            ENTER_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_price_input)],
            ENTER_EXCHANGE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_exchange_input),
                CommandHandler("skip", skip_exchange)
            ],
        },
        fallbacks=[],
        per_user=True
    )

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(handle_confirmation, pattern='^confirm_'))

    # === Запуск планировщика задач ===
    scheduler.start()

    # Ежедневный отчёт в 9:00
    scheduler.add_job(
        send_daily_report,
        'cron',
        hour=9,
        minute=0,
        args=[],
        misfire_grace_time=60,
        coalesce=True,
        executor="default_executor",
        id="daily_report",
        replace_existing=True
    )

    # Еженедельный отчёт по понедельникам в 9:00
    scheduler.add_job(
        send_weekly_report,
        'cron',
        day_of_week='mon',
        hour=9,
        minute=0,
        args=[],
        misfire_grace_time=60,
        coalesce=True,
        executor="default_executor",
        id="weekly_report",
        replace_existing=True
    )

    print("Бот запущен...")
    application.run_polling()