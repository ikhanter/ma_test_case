import json
import random
import requests

import aiohttp
import asyncio
import pandas as pd

# Получены через get_categories() и get_subcategories()
HOME_URL = 'https://online.metro-cc.ru'

QUERY_SQL = 'https://online.metro-cc.ru/api/graphql'

# Подготовка запроса и поиск необходимых для парсинга магазинов
response = requests.get('https://api.metro-cc.ru/api/v1/C98BB1B547ECCC17D8AEBEC7116D6/tradecenters/')
all_shops = json.loads(response.text)['data']
shops_amount = len(all_shops)

# ID магазинов Москвы и Петербурга
id_moscow_shops = []
id_spb_shops = []
found = []
for shop in all_shops:
    if shop['city'] == 'Москва':
        id_moscow_shops.append(shop['store_id'])
    elif shop['city'] == 'Санкт-Петербург':
        id_spb_shops.append(shop['store_id'])


def get_random_shop_id(shop_list: list) -> int:
    """Return random shop ID from the list."""
    shop = random.choice(shop_list)
    return shop['id']


def get_random_category(category_list: list) -> dict:
    """Return random category dictionary from the list."""
    choice = random.choice(category_list)
    return choice


def get_categories(store_id: int) -> list:
    """Return a list of categories based on store, which ID was taken."""
    query = f'''query Query {{
        search(storeId: {store_id}) {{
            categories(asTree: true) {{
                id
                name
                slug
            }}
        }}
    }}'''

    response = requests.post(QUERY_SQL, json={'query': query})
    return json.loads(response.text)['data']['search']['categories']


def get_subcategories(store_id: int, slug: str) -> list:
    """Return subcategory list from the chosen category,
    which was defined by slug, based on a store."""
    query = f'''query Query {{
        category(
            storeId: {store_id},
            slug: "{slug}"
        ) {{
            id
            name
            slug
            total
            groups {{
                id
                name
            }}
        }}
    }}'''
    response = requests.post(QUERY_SQL, json={'query': query})
    jsoned = json.loads(response.text)['data']
    return jsoned['category']['groups']


async def get_goods_for_one_store(
    session: aiohttp.ClientSession,
    store_id: int,
    subcategory_list: list,
) -> list:
    """Return list of products of the chosen
    list of subcategories from the store defined by ID."""
    subcategory_ids = []
    for sc in subcategory_list:
        subcategory_ids.append(sc['id'])
    subcategory_str = []
    for el in subcategory_ids:
        temp = f'"{el}"'
        subcategory_str.append(temp)
    subcategory_str = '[' + ', '.join(subcategory_str) + ']'
    query = f'''query Query{{
            search(storeId: {store_id}) {{
                products(from: 0, size: 9999, fieldFilters: [ {{field: "category.id",values: {subcategory_str}}}]) {{  
                products {{
                    id
                    article
                    name
                    manufacturer {{
                    name
                    }}
                    url
                    stocks {{
                    prices {{
                        price
                        old_price
                        discount
                    }}
                    value
                    }}
                }}
                }}
            }}
    }}'''

    async with session.post(QUERY_SQL, json={'query': query}) as resp:
        response = await resp.json()

    return response['data']['search']['products']['products']

async def get_goods_for_city(
    shop_id_list: list,
    subcategory_list: list,
    category_name: str,
    city_name: str,
) -> None:
    """Make a file with csv-table of goods. Goods are defined by their
    subcategories. Search is going for the stores in the given list."""
    table = {
        'goods_id': [],
        'article': [],
        'name': [],
        'url': [],
        'regular_price': [],
        'promo_price': [],
        'amount': [],
        'brand': [],
        'store_id': [],
    }

    async with aiohttp.ClientSession() as session:

        for id in shop_id_list:
            goods = await get_goods_for_one_store(session, id, subcategory_list)

            for good in goods:
                table['goods_id'].append(good['id'])
                table['article'].append(good['article'])
                table['name'].append(good['name'])
                table['url'].append(f"{HOME_URL}{good['url']}")
                regular_price = good['stocks'][0]['prices']['old_price']
                promo_price = good['stocks'][0]['prices']['price']

                if regular_price:
                    table['regular_price'].append(regular_price)
                    table['promo_price'].append(promo_price)
                else:
                    table['regular_price'].append(promo_price)
                    table['promo_price'].append('-')

                table['amount'].append(good['stocks'][0]['value'])
                table['brand'].append(good['manufacturer']['name'])
                table['store_id'].append(id)

        df = pd.DataFrame(table)

        name_parts = []
        temp_name = category_name.split(',')
        for temp in temp_name:
            name_parts.append(temp.rstrip())
        file_name = '_'.join(name_parts) + '_' + city_name + '.csv'
        df.to_csv(file_name)


async def main():
    """Execute all tasks."""
    store_id = get_random_shop_id(all_shops)
    categories = get_categories(store_id)

    # Некоторые магазины, передающиеся через API, без категорий товаров
    while not categories:
        store_id = get_random_shop_id(all_shops)
        categories = get_categories(store_id)

    print(f'Store id category reference: {store_id}')
    category = get_random_category(categories)
    slug = category['slug']
    subcategories = get_subcategories(store_id, slug)
    while not subcategories:
        category = get_random_category(categories)
        slug = category['slug']
        subcategories = get_subcategories(store_id, slug)
    print(f"Category for parsing: {category['name']}")
    print('Subcategories:')
    for sc in subcategories:
        print(f"- {sc['name']}: id - {sc['id']}")
    spb_task = asyncio.create_task(get_goods_for_city(id_spb_shops, subcategories, category['name'], 'SPb'))
    msk_task = asyncio.create_task(get_goods_for_city(id_moscow_shops, subcategories, category['name'], 'Moscow'))

    await asyncio.gather(spb_task, msk_task)


if __name__ == '__main__':
    asyncio.run(main())
