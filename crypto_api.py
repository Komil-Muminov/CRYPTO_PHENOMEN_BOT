# crypto_api.py

from pycoingecko import CoinGeckoAPI
import logging
import time

cg = CoinGeckoAPI()
logger = logging.getLogger(__name__)

# Простое кэширование (в реальном проекте можно использовать Redis или TTLCache)
PRICE_CACHE_TTL = 60 * 5  # 5 минут
_price_cache = {}  # {coin_id: {'price': ..., 'timestamp': ...}}


def get_coin_price(coin_id: str, currency: str = 'usd'):
    """
    Возвращает текущую цену монеты в указанной валюте.
    
    :param coin_id: ID монеты в CoinGecko
    :param currency: валюта (например, 'usd', 'eur')
    :return: цена монеты или None, если не найдена
    """
    currency = currency.lower()

    # Проверяем кэш
    if coin_id in _price_cache:
        cached = _price_cache[coin_id]
        if time.time() - cached['timestamp'] < PRICE_CACHE_TTL:
            return cached['price'].get(currency)

    try:
        data = cg.get_coin_by_id(id=coin_id)
        current_price = data['market_data']['current_price'].get(currency)
        
        # Обновляем кэш
        _price_cache[coin_id] = {
            'price': data['market_data']['current_price'],
            'timestamp': time.time()
        }

        return current_price
    except Exception as e:
        logger.error(f"Ошибка при получении цены для {coin_id}: {e}")
        return None


def search_coin(query: str):
    """
    Ищет монету по названию или символу.
    
    :param query: строка поиска
    :return: dict с информацией о монете или None
    """
    try:
        coins = cg.get_coins_list()
        for coin in coins:
            if query.lower() in coin['name'].lower() or query.lower() == coin['symbol']:
                return coin
        return None
    except Exception as e:
        logger.error(f"Ошибка при поиске монеты '{query}': {e}")
        return None