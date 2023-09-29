# Скрипт seller.py

### Описание
Цены на товары формируются продавцом. Цены формируются на основе данных остатков товаров, загруженных с внешнего источника (в данном случае, с сайта casio). Скрипт загружает остатки часов и их цены с этого источника, а затем обновляет цены товаров на платформе OZON, используя эти данные.

### Формирование цен

Сначала скрипт загружает данные об остатках товаров с сайта casio. Эти данные включают в себя информацию о каждом товаре, включая его артикул и цену.
Затем создаётся список цен на основе данных об остатках и артикулах товаров, которые уже есть на OZON.
После этого, цены отправляются на OZON, для обновления цен на товары.

### Что необходимо для запуска
Для работы с Ozon вам потребуется логин или ключ доступа продавца на Ozon
```
SELLER_TOKEN: Логин или ключ доступа продавца на Ozon.
CLIENT_ID: Идентификатор клиента (продавца) на Ozon.
```

# Скрипт market.py

### Описание

Этот скрипт предназначен для обновления информации о ценах и остатках товаров на яндекс маркете. Он взаимодействует с его API, загружая актуальные цены и остатки товаров из источника данных и обновляя их на Маркете.

### Формирование цен

Получает информацию о товарах (артикулах) из источника данных.
Обновляет остатки товаров на Маркете в соответствии с данными из источника.
Обновляет цены товаров на Маркете в соответствии с данными из источника.

Скрипт может быть настроен для работы с разными кампаниями и складами на Яндекс Маркете, что позволяет обновлять информацию для различных групп товаров.

### Что необходимо для запуска

Для работы с Яндекс маркетом:
* Вам потребуется логин или ключ доступа к Яндекс Маркету. Этот ключ позволяет управлять товарами.
* Если вы продаете физические товары, вам нужно будет указать идентификатор кампании FBS.
* Если вы продаете цифровые товары, вам нужно будет указать идентификатор кампании DBS.
* Независимо от типа товаров, вы должны будете указать номер склада, где хранятся ваши товары.

```
MARKET_TOKEN: Логин или ключ доступа.
FBS_ID: Идентификатор кампании (для физических товаров).
DBS_ID: Идентификатор кампании (для цифровых товаров).
WAREHOUSE_FBS_ID: Номер склада (для физических товаров).
WAREHOUSE_DBS_ID: Номер склада (для цифровых товаров).
```