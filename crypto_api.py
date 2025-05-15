# crypto_api.py

from pycoingecko import CoinGeckoAPI

cg = CoinGeckoAPI()

def get_coin_price(coin_id, currency='usd'):
    data = cg.get_coin_by_id(id=coin_id)
    return data['market_data']['current_price'].get(currency.lower(), None)

def search_coin(query):
    coins = cg.get_coins_list()
    for coin in coins:
        if query.lower() in coin['name'].lower() or query.lower() == coin['symbol']:
            return coin
    return None