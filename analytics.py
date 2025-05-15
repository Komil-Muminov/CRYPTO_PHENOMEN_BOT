# analytics.py

from database import get_portfolio
from crypto_api import get_coin_price


def calculate_portfolio(user_id):
    """
    Рассчитывает текущее состояние портфеля пользователя.

    :param user_id: ID пользователя Telegram
    :return: dict с данными по активам и общему состоянию портфеля
    """
    portfolio = get_portfolio(user_id)
    results = []
    total_invested = 0.0
    total_current = 0.0

    for symbol, amount, avg_price in portfolio:
        current_price = get_coin_price(symbol)
        if not current_price:
            continue

        invested_value = amount * avg_price
        current_value = amount * current_price
        profit = current_value - invested_value
        roi = (profit / invested_value) * 100 if invested_value != 0 else 0

        results.append({
            'symbol': symbol.upper(),
            'amount': amount,
            'avg_price': avg_price,
            'current_price': current_price,
            'invested': invested_value,
            'current': current_value,
            'profit': profit,
            'roi': roi
        })

        total_invested += invested_value
        total_current += current_value

    total_profit = total_current - total_invested
    total_roi = (total_profit / total_invested * 100) if total_invested != 0 else 0

    return {
        'assets': results,
        'total': {
            'invested': round(total_invested, 2),
            'current': round(total_current, 2),
            'profit': round(total_profit, 2),
            'roi': round(total_roi, 2)
        }
    }