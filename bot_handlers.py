# bot_handlers.py

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler
from analytics import calculate_portfolio
from recommendation import recommend_investment
from charts import generate_portfolio_chart
from database import add_transaction
from utils import main_menu_keyboard, back_to_main_menu

# Этапы диалога
SELECT_TYPE, ENTER_COIN, ENTER_AMOUNT_OR_VALUE, ENTER_PRICE, ENTER_EXCHANGE = range(5)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    from database import add_user
    add_user(user_id)
    await update.message.reply_text("Добро пожаловать в CryptoKeeper!", reply_markup=main_menu_keyboard())


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "portfolio":
        data = calculate_portfolio(user_id)
        text = "💼 Ваш портфель:\n\n"
        for asset in data['assets']:
            text += f"{asset['symbol']} ({asset['amount']:.4f})\n"
            text += f"Средняя цена: ${asset['avg_price']:.2f}\n"
            text += f"Текущая цена: ${asset['current_price']:.2f}\n"
            text += f"Вложено: ${asset['invested']:.2f}\n"
            text += f"Текущая стоимость: ${asset['current']:.2f}\n"
            profit_str = "+" if asset['profit'] >= 0 else "-"
            text += f"Прибыль: {profit_str}${abs(asset['profit']):.2f} ({asset['roi']:+.2f}%)\n\n"

        text += "📊 ИТОГО:\n"
        text += f"Всего вложено: ${data['total']['invested']:.2f}\n"
        text += f"Текущая стоимость: ${data['total']['current']:.2f}\n"
        profit_str = "+" if data['total']['profit'] >= 0 else "-"
        text += f"Прибыль: {profit_str}${abs(data['total']['profit']):.2f} ({data['total']['roi']:+.2f}%)\n\n"

        await query.edit_message_text(text=text, reply_markup=main_menu_keyboard())

    elif query.data == "analytics":
        data = calculate_portfolio(user_id)
        text = "📈 Аналитика:\n\n"
        text += f"Общая доходность: {data['total']['roi']:+.2f}%\n"
        text += f"Количество активов: {len(data['assets'])}\n"
        top_asset = max(data['assets'], key=lambda x: x['profit']) if data['assets'] else None
        top_name = top_asset['symbol'] if top_asset else '—'
        text += f"Самый прибыльный актив: {top_name}\n"
        await query.edit_message_text(text=text, reply_markup=main_menu_keyboard())

    elif query.data == "recommend":
        recommendations = recommend_investment(amount=100, desired_profit=10, days=7)
        text = "🚀 Рекомендации:\n\n"
        for rec in recommendations:
            text += f"🔸 {rec['name']} ({rec['symbol']})\n"
            text += f"Прогноз: {rec['forecast']}\n"
            text += f"Риск: {rec['risk']}\n\n"
        text += "⚠️ Это не гарантия прибыли. Крипторынок волатилен!"
        await query.edit_message_text(text=text, reply_markup=main_menu_keyboard())

    elif query.data == "add_transaction":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🛒 Покупка", callback_data="type_buy")],
            [InlineKeyboardButton("🔻 Продажа", callback_data="type_sell")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]
        ])
        await query.edit_message_text("Выберите тип сделки:", reply_markup=keyboard)
        return SELECT_TYPE

    elif query.data == "chart":
        data = calculate_portfolio(user_id)
        chart_img = generate_portfolio_chart(data)
        await query.message.reply_photo(photo=chart_img, caption="📊 Распределение вашего портфеля")
        await query.message.delete()
        await query.answer()
        return ConversationHandler.END

    elif query.data == "back_to_main":
        await query.edit_message_text("Выберите действие:", reply_markup=main_menu_keyboard())
        return ConversationHandler.END

    else:
        await query.edit_message_text("Неизвестная команда", reply_markup=main_menu_keyboard())
        return ConversationHandler.END


# === ФОРМА ДОБАВЛЕНИЯ СДЕЛКИ ===

async def handle_add_transaction_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    transaction_type = "buy" if query.data == "type_buy" else "sell"
    context.user_data['transaction_type'] = transaction_type
    await query.edit_message_text("Введите название или символ монеты (например, BTC или Bitcoin):")
    return ENTER_COIN


async def handle_coin_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    coin_input = update.message.text.strip()
    from crypto_api import search_coin
    coin = search_coin(coin_input)
    if not coin:
        await update.message.reply_text("Монета не найдена. Попробуйте ещё раз.")
        return ENTER_COIN
    context.user_data['coin_name'] = coin['name']
    context.user_data['symbol'] = coin['symbol']
    await update.message.reply_text(f"Вы выбрали: {coin['name']} ({coin['symbol'].upper()})\nВведите количество или сумму:")
    return ENTER_AMOUNT_OR_VALUE


async def handle_amount_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    amount_or_value = update.message.text.strip().replace(',', '.')
    try:
        amount_or_value = float(amount_or_value)
    except ValueError:
        await update.message.reply_text("Неверный формат. Введите число.")
        return ENTER_AMOUNT_OR_VALUE

    context.user_data['amount_or_value'] = amount_or_value
    await update.message.reply_text("Введите цену покупки/продажи за 1 монету:")
    return ENTER_PRICE


async def handle_price_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    price = update.message.text.strip().replace(',', '.')
    try:
        price = float(price)
    except ValueError:
        await update.message.reply_text("Неверный формат. Введите число.")
        return ENTER_PRICE

    context.user_data['price'] = price
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("➡️ Пропустить", callback_data="skip_exchange")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]
    ])
    await update.message.reply_text("Введите биржу (необязательно):", reply_markup=keyboard)
    return ENTER_EXCHANGE


async def handle_exchange_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    exchange = update.message.text.strip()
    context.user_data['exchange'] = exchange
    return await confirm_and_save(update, context)


async def skip_exchange(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['exchange'] = None
    # Переход к подтверждению
    return await confirm_and_save(update, context)


async def confirm_and_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    t = context.user_data

    # Определяем количество и сумму
    if t['transaction_type'] == 'buy':
        amount = t['amount_or_value']
        value = amount * t['price']
    else:
        value = t['amount_or_value']
        amount = value / t['price']

    text = "✅ Подтвердите данные сделки:\n\n"
    text += f"Тип: {'Покупка' if t['transaction_type'] == 'buy' else 'Продажа'}\n"
    text += f"Монета: {t['coin_name']} ({t['symbol'].upper()})\n"
    text += f"Количество: {amount:.6f}\n"
    text += f"Цена: ${t['price']:.2f}\n"
    text += f"Сумма: ${value:.2f}\n"
    text += f"Биржа: {t['exchange'] or '—'}\n\n"
    text += "Подтвердите операцию?"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Подтвердить", callback_data="confirm_yes")],
        [InlineKeyboardButton("❌ Отменить", callback_data="confirm_no")]
    ])

    if update.message:
        await update.message.reply_text(text, reply_markup=keyboard)
    else:
        await update.callback_query.message.reply_text(text, reply_markup=keyboard)
    return ConversationHandler.END


async def handle_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    t = context.user_data

    if query.data == "confirm_yes":
        add_transaction(
            user_id=user_id,
            coin_name=t['coin_name'],
            symbol=t['symbol'],
            amount=context.user_data['amount_or_value'],
            price=context.user_data['price'],
            transaction_type=context.user_data['transaction_type'],
            exchange=context.user_data.get('exchange')
        )
        await query.edit_message_text("✅ Сделка успешно добавлена!", reply_markup=main_menu_keyboard())
    else:
        await query.edit_message_text("❌ Сделка отменена.", reply_markup=main_menu_keyboard())
    return ConversationHandler.END