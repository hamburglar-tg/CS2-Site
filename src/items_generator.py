import time
import requests
import re
import json


session = requests.Session()

def extract_skin_name(skin_name):
    print(skin_name)
    try:
        name = skin_name.split(" | ")
        return name[1].split('(')[0].strip()
    except:
        return skin_name

def get_items(main_items_count, sleep_time, max_price=None):
    start = 0
    items_count = 10
    result_list = []

    while True:
        url = f'https://steamcommunity.com/market/search/render/?query=&start={start}&count={items_count}&search_descriptions=0&sort_column=default&sort_dir=asc&appid=730&norender=1&country=RU&language=english&currency=1&max_price=4'
        response = session.get(url)
        data = response.json()

        if response.status_code == 429:
            print("Too many requests")
            time.sleep(sleep_time)
        else:
            for item in data['results']:
                price = item['sale_price_text']
                price_value = float(re.sub(r'[^\d.]', '', price))

                if max_price and price_value > max_price:
                    continue

                name = item['asset_description']['market_hash_name']

                isExists = any(item['name'] == name for item in result_list)
                if not isExists:
                    price = item['sale_price_text']
                    icon = item['asset_description']['icon_url']

                    result_list.append({"name": name, "price": price, "icon": icon})

                    print(f"Скин: {name}\nЦена: {price}\nИконка: https://steamcommunity-a.akamaihd.net/economy/image/{icon}/100x100f\n\n")

            if len(result_list) > main_items_count:
                break

            start += items_count

        time.sleep(20)

    with open('items.json', 'w', encoding='utf-8') as file:
        json.dump(result_list, file, ensure_ascii=False, indent=4)

    return result_list

print(get_items(150, 60, max_price=1))