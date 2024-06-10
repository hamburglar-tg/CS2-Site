import asyncio
import json

import src.main_manager as ctr
from src.logging import log

from src.socket_server import sio
from src.trades_handler import get_item_price, update_users_chances, check_user_exists, get_users_chances

from src.utils import *


def get_fake_data():
    users_path = "../data/users.json"
    items_path = "../data/items.json"

    with open(users_path, "rb") as users_file:
        users_list = json.load(users_file)

    with open(items_path, "rb") as items_file:
        items_list = json.load(items_file)

    return users_list, items_list


users, items = get_fake_data()


async def start_fake_trades():
    await asyncio.sleep(5)
    while True:
        if ctr.project.current_game:
            if not ctr.project.current_game.isRouletteStarted:
                await asyncio.create_task(generate_fake_trade())

            if ctr.project.current_game.users_count == 2 and not ctr.project.current_game.isTimerStarted:
                await asyncio.create_task(ctr.project.current_game.start_timer())

            if ctr.project.current_game.items_count >= 200:
                await asyncio.create_task(ctr.project.current_game.start_roulette())

        await asyncio.sleep(5)


async def generate_fake_trade():
    user = random.choice(users)

    user_avatar = user["avatar"]
    user_steam_id = user["steamId"]
    user_nickname = user["nickname"]
    ctr.project.current_game.users_count += 1

    if not check_user_exists(user_steam_id):
        user_items = await get_user_items()
        total_cost = extract_total(user_items, 'item_cost')
        trade_items_count = len(user_items)
        ctr.project.current_game.items_count += trade_items_count
        ctr.project.current_game.game_bank = round_decimal(ctr.project.current_game.game_bank + total_cost, '0.01')

        new_game_json = update_users_chances(ctr.project.current_game.get_game())
        user_percent = calculate_percentage(ctr.project.current_game.game_bank, total_cost)

        user_trade_dict = {
            f"{user_steam_id}": {
                "status": "steam user",
                "avatar": user_avatar,
                "nickname": user_nickname,
                "user_bank": total_cost,
                "user_items_count": trade_items_count,
                "chance": user_percent,
                "items": user_items
            }
        }

        new_game_json["users"].append(user_trade_dict)
        ctr.project.current_game.upd(new_game_json)

        print(new_game_json)

        await sio.emit("newDeposit", user_trade_dict)

        new_users_chances = await get_users_chances(new_game_json["users"])

        project_info_dict = {
            "games_today": ctr.project.games_today,
            "last_winner": ctr.project.last_winner_dict,
            "last_game_id": ctr.project.current_game.game_id,
            "game_bank": round_decimal(ctr.project.current_game.game_bank, '0.1'),
            "items_count": ctr.project.current_game.items_count,
            "timer_value": ctr.project.current_game.timer_value,
            "strike": ctr.project.strike,
            "peak_online": ctr.project.peak_online,
            "new_users_chances": new_users_chances
        }

        await sio.emit("gameInfo", project_info_dict)

        log("BOTS", "New fake trade")


async def get_user_items():
    items_num = random.randint(1, 5)
    user_items = random.sample(items, items_num)

    result = {}
    item_index = 0
    for value in user_items:
        icon_url = value.get('icon')
        market_hash_name = value.get('name')
        item_cost = value.get('price')

        result[f"item_{item_index}"] = {
            "icon_url": f"https://steamcommunity-a.akamaihd.net/economy/image/{icon_url}/100x100f",
            "market_hash_name": market_hash_name,
            "item_cost": item_cost
        }
        item_index += 1
        items_num -= 1

        if items_num <= 0:
            break

    return result
