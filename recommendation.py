# recommendation.py

from crypto_api import search_coin, get_coin_price


def recommend_investment(amount, desired_profit, days):
    """
    Возвращает список монет с потенциалом для достижения цели пользователя.

    :param amount: сумма инвестиции (в USD)
    :param desired_profit: желаемая прибыль (в USD)
    :param days: срок (в днях)
    :return: list of dict — список рекомендаций
    """
    coins_to_check = [
        'bitcoin', 'ethereum', 'solana', 'cardano',
        'dogecoin', 'pepecoin', 'bonk', 'litecoin', 'chainlink'
    ]
    recommendations = []

    for coin_name in coins_to_check:
        coin = search_coin(coin_name)
        if not coin:
            continue

        current_price = get_coin_price(coin['symbol'])
        if not current_price:
            continue

        # Оценка риска
        risk_level = 'medium'
        if any(keyword in coin_name.lower() for keyword in ['pepe', 'doge', 'shib']):
            risk_level = 'high'

        # Прогноз роста в %
        expected_growth = {
            'high': 15,
            'medium': 8,
            'low': 3
        }[risk_level]

        # Расчёт ожидаемой прибыли
        expected_return = amount * (expected_growth / 100)

        # Проверяем, соответствует ли монета цели
        if expected_return >= desired_profit:
            recommendations.append({
                'name': coin['name'],
                'symbol': coin['symbol'].upper(),
                'risk': risk_level,
                'forecast': f"+{expected_growth}% за {days} дней",
                'expected_return': expected_return
            })

    # Сортируем по ожидаемому возврату
    recommendations.sort(key=lambda x: x['expected_return'], reverse=True)
    return recommendations[:2]  # Возвращаем топ-2