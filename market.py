import datetime
import logging.config
from environs import Env
from seller import download_stock
import requests
from seller import divide, price_conversion

logger = logging.getLogger(__file__)


def get_product_list(page, campaign_id, access_token):
    """
    Получает список товаров (артикулов) из кампании на Яндекс.Маркете.

    Args:
        page (str): Токен страницы для пагинации.
        campaign_id (str): Идентификатор кампании на Яндекс.Маркете.
        access_token (str): Токен доступа для аутентификации в API.

    Returns:
        dict: Результат запроса в формате JSON.

    Example:
        result = get_product_list("token123", "campaign456", "access_token_xyz")
    """
    endpoint_url = "https://api.partner.market.yandex.ru/"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Host": "api.partner.market.yandex.ru",
    }
    payload = {
        "page_token": page,
        "limit": 200,
    }
    url = endpoint_url + f"campaigns/{campaign_id}/offer-mapping-entries"
    response = requests.get(url, headers=headers, params=payload)
    response.raise_for_status()
    response_object = response.json()
    return response_object.get("result")


def update_stocks(stocks, campaign_id, access_token):
    """
    Обновляет остатки товаров на Яндекс.Маркете.

    Args:
        stocks (list): Список остатков для обновления.
        campaign_id (str): Идентификатор кампании на Яндекс.Маркете.
        access_token (str): Токен доступа для аутентификации в API.

    Returns:
        dict: Результат запроса в формате JSON.

    Example:
        result = update_stocks([stock1, stock2], "campaign456", "access_token_xyz")
    """
    endpoint_url = "https://api.partner.market.yandex.ru/"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Host": "api.partner.market.yandex.ru",
    }
    payload = {"skus": stocks}
    url = endpoint_url + f"campaigns/{campaign_id}/offers/stocks"
    response = requests.put(url, headers=headers, json=payload)
    response.raise_for_status()
    response_object = response.json()
    return response_object


def update_price(prices, campaign_id, access_token):
    """
    Обновляет цены на товары на Яндекс.Маркете.

    Args:
        prices (list): Список цен для обновления.
        campaign_id (str): Идентификатор кампании на Яндекс.Маркете.
        access_token (str): Токен доступа для аутентификации в API.

    Returns:
        dict: Результат запроса в формате JSON.

    Example:
        result = update_price([price1, price2], "campaign456", "access_token_xyz")
    """
    endpoint_url = "https://api.partner.market.yandex.ru/"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Host": "api.partner.market.yandex.ru",
    }
    payload = {"offers": prices}
    url = endpoint_url + f"campaigns/{campaign_id}/offer-prices/updates"
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    response_object = response.json()
    return response_object


def get_offer_ids(campaign_id, market_token):
    """
       Получает список артикулов товаров на Яндекс.Маркете для указанной кампании.

       Args:
           campaign_id (str): Идентификатор кампании на Яндекс.Маркете.
           market_token (str): Токен доступа для аутентификации в API.

       Returns:
           list: Список артикулов товаров на Яндекс.Маркете.

       Example:
           result = get_offer_ids("campaign456", "access_token_xyz")
       """
    page = ""
    product_list = []
    while True:
        some_prod = get_product_list(page, campaign_id, market_token)
        product_list.extend(some_prod.get("offerMappingEntries"))
        page = some_prod.get("paging").get("nextPageToken")
        if not page:
            break
    offer_ids = []
    for product in product_list:
        offer_ids.append(product.get("offer").get("shopSku"))
    return offer_ids


def create_stocks(watch_remnants, offer_ids, warehouse_id):
    """
    Создает список остатков товаров на основе данных из источника данных.

    Args:
        watch_remnants (list): Список данных об остатках товаров.
        offer_ids (list): Список артикулов товаров на Яндекс.Маркете.
        warehouse_id (str): Идентификатор склада на Яндекс.Маркете.

    Returns:
        list: Список остатков товаров для обновления на Яндекс.Маркете.
    """
    stocks = list()
    date = str(datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z")
    for watch in watch_remnants:
        if str(watch.get("Код")) in offer_ids:
            count = str(watch.get("Количество"))
            if count == ">10":
                stock = 100
            elif count == "1":
                stock = 0
            else:
                stock = int(watch.get("Количество"))
            stocks.append(
                {
                    "sku": str(watch.get("Код")),
                    "warehouseId": warehouse_id,
                    "items": [
                        {
                            "count": stock,
                            "type": "FIT",
                            "updatedAt": date,
                        }
                    ],
                }
            )
            offer_ids.remove(str(watch.get("Код")))
    for offer_id in offer_ids:
        stocks.append(
            {
                "sku": offer_id,
                "warehouseId": warehouse_id,
                "items": [
                    {
                        "count": 0,
                        "type": "FIT",
                        "updatedAt": date,
                    }
                ],
            }
        )
    return stocks


def create_prices(watch_remnants, offer_ids):
    """
    Создает список цен на товары на основе данных из источника данных.

    Args:
        watch_remnants (list): Список данных о ценах на товары.
        offer_ids (list): Список артикулов товаров на Яндекс.Маркете.

    Returns:
        list: Список цен на товары для обновления на Яндекс.Маркете.
    """
    prices = []
    for watch in watch_remnants:
        if str(watch.get("Код")) in offer_ids:
            price = {
                "id": str(watch.get("Код")),
                "price": {
                    "value": int(price_conversion(watch.get("Цена"))),
                    "currencyId": "RUR",
                },
            }
            prices.append(price)
    return prices


async def upload_prices(watch_remnants, campaign_id, market_token):
    """
    Загружает цены на товары на Яндекс.Маркет из списка цен.

    Args:
        watch_remnants (list): Список данных о ценах на товары.
        campaign_id (str): Идентификатор кампании на Яндекс.Маркете.
        market_token (str): Токен доступа для аутентификации в API.

    Returns:
        list: Список цен на товары, загруженных на Яндекс.Маркет.

    Example:
        result = await upload_prices([price1, price2], "campaign456", "access_token_xyz")
    """
    offer_ids = get_offer_ids(campaign_id, market_token)
    prices = create_prices(watch_remnants, offer_ids)
    for some_prices in list(divide(prices, 500)):
        update_price(some_prices, campaign_id, market_token)
    return prices


async def upload_stocks(watch_remnants, campaign_id, market_token, warehouse_id):
    """
    Загружает остатки товаров на Яндекс.Маркет из списка остатков.

    Args:
        watch_remnants (list): Список данных об остатках товаров.
        campaign_id (str): Идентификатор кампании на Яндекс.Маркете.
        market_token (str): Токен доступа для аутентификации в API.
        warehouse_id (str): Идентификатор склада на Яндекс.Маркете.

    Returns:
        tuple: Список остатков товаров, которые были загружены, и полный список остатков.

    Example:
        result = await upload_stocks([stock1, stock2], "campaign456", "access_token_xyz", "warehouse123")
    """
    offer_ids = get_offer_ids(campaign_id, market_token)
    stocks = create_stocks(watch_remnants, offer_ids, warehouse_id)
    for some_stock in list(divide(stocks, 2000)):
        update_stocks(some_stock, campaign_id, market_token)
    not_empty = list(filter(lambda stock: (stock.get("items")[0].get("count") != 0), stocks))
    return not_empty, stocks


def main():
    env = Env()
    market_token = env.str("MARKET_TOKEN")
    campaign_fbs_id = env.str("FBS_ID")
    campaign_dbs_id = env.str("DBS_ID")
    warehouse_fbs_id = env.str("WAREHOUSE_FBS_ID")
    warehouse_dbs_id = env.str("WAREHOUSE_DBS_ID")

    watch_remnants = download_stock()
    try:
        # FBS
        offer_ids = get_offer_ids(campaign_fbs_id, market_token)
        stocks = create_stocks(watch_remnants, offer_ids, warehouse_fbs_id)
        for some_stock in list(divide(stocks, 2000)):
            update_stocks(some_stock, campaign_fbs_id, market_token)
        upload_prices(watch_remnants, campaign_fbs_id, market_token)

        # DBS
        offer_ids = get_offer_ids(campaign_dbs_id, market_token)
        stocks = create_stocks(watch_remnants, offer_ids, warehouse_dbs_id)
        for some_stock in list(divide(stocks, 2000)):
            update_stocks(some_stock, campaign_dbs_id, market_token)
        upload_prices(watch_remnants, campaign_dbs_id, market_token)
    except requests.exceptions.ReadTimeout:
        print("Превышено время ожидания...")
    except requests.exceptions.ConnectionError as error:
        print(error, "Ошибка соединения")
    except Exception as error:
        print(error, "ERROR_2")


if __name__ == "__main__":
    main()
