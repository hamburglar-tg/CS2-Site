import src.main_manager as ctr

from src.socket_server import sio

from src.utils import *
from src.logging import *


async def new_deposit(partner, trade_items_count, trade_offer_id, items_to_receive, steam_id_exists):
    trade_items = get_items_dict(ctr.project.current_bot.bot_client, ctr.project.current_bot.cs2_game, items_to_receive, partner)
    total_cost = extract_total(trade_items, 'item_cost')
    ctr.project.current_game.game_bank = round_decimal(ctr.project.current_game.game_bank + total_cost, '0.01')

    new_game_json = update_users_chances(ctr.project.current_game.get_game())

    if steam_id_exists:
        await update_user(new_game_json, partner, trade_items, total_cost, trade_items_count, trade_offer_id, items_to_receive)
        print(ctr.project.current_game.get_game())
    else:
        user_percent = calculate_percentage(ctr.project.current_game.game_bank, total_cost)
        partner_profile = ctr.project.current_bot.bot_client.get_profile(partner)

        user_trade_dict = {
            f"{partner}": {
                "status": "user",
                "avatar": partner_profile.get("avatarfull"),
                "nickname": partner_profile.get("personaname"),
                "user_bank": total_cost,
                "user_items_count": trade_items_count,
                "chance": user_percent,
                "items": trade_items
            }
        }

        new_game_json["users"].append(user_trade_dict)
        ctr.project.current_game.upd(new_game_json)
        print(new_game_json)

        await sio.emit("newDeposit", user_trade_dict)
        log("BOTS", f"The exchange {trade_offer_id} has been successfully accepted!")

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


def accept_trade_offer(trade_offer_id, partner_steam_id):
    ctr.project.current_bot.bot_client.accept_trade_offer(trade_offer_id, partner_steam_id)


async def update_user(game_json, partner, new_items, items_cost, trade_items_count, trade_offer_id, items_to_receive):
    if not ctr.project.current_game.isRouletteStarted:
        if int(game_json["game_info"]["game_id"]) == int(ctr.project.current_game.game_id):
            for user_dict in game_json["users"]:
                if partner in user_dict:
                    new_user_bank = round(user_dict[partner]['user_bank'] + items_cost, 2)
                    items_count = user_dict[partner]['user_items_count'] + trade_items_count
                    user_dict[partner]['chance'] = calculate_percentage(ctr.project.current_game.game_bank, new_user_bank)
                    user_dict[partner]['items'].update(new_items)
                    user_dict[partner]['user_bank'] = new_user_bank
                    user_dict[partner]['user_items_count'] = items_count

                    ctr.project.current_game.upd(game_json)

                    await sio.emit('updateBet', {"items_count": trade_items_count, "user_dict": user_dict})
        else:
            steam_id_exists = check_user_exists(partner)
            await new_deposit(partner, trade_items_count, trade_offer_id, items_to_receive, steam_id_exists)


def update_users_chances(json_obj):
    game_bank = json_obj["game_info"]["game_bank"]

    for user in json_obj["users"]:
        for user_id, user_data in user.items():
            user_bank = user_data.get("user_bank")
            user_percent = calculate_percentage(game_bank, user_bank)
            user_data["chance"] = user_percent

    return json_obj


def get_items_dict(client, game, trade_dict, partner):
    result = {}
    item_index = get_largest_item_number(partner)

    for key, value in trade_dict.items():
        icon_url = value.get('icon_url')
        market_hash_name = value.get('market_hash_name')
        result[f"item_{item_index}"] = {
            "icon_url": f"https://steamcommunity-a.akamaihd.net/economy/image/{icon_url}/100x100f",
            "market_hash_name": market_hash_name,
            "item_cost": get_item_price(client, game, market_hash_name)
        }
        item_index += 1

    return result


def get_item_price(client, game, item_hash_name):
    ft_price = client.market.fetch_price(item_hash_name, game=game)
    price_str = ft_price.get("median_price")
    return extract_cost(price_str) if price_str else None


def check_user_exists(partner):
    game_json = ctr.project.current_game.get_game()
    return any(partner in user_json for user_json in game_json["users"])


def get_largest_item_number(partner):
    game_json = ctr.project.current_game.get_game()
    if game_json["users"]:
        for user in game_json.get("users", []):
            user_data = user.get(partner)
            if user_data:
                user_items = user_data.get("items", {})
                item_names = [name for name in user_items.keys() if re.match(r'item_\d+$', name)]
                if item_names:
                    largest_item_name = max(item_names, key=lambda x: int(x.split('_')[1]))
                    return int(largest_item_name.split('_')[1]) + 1
                else:
                    return 1
    else:
        return 1


async def get_users_chances(users):
    return_list = []
    for user in users:
        for user_id, user_data in user.items():
            chance = user_data.get('chance')
            user_dict = {
                "steamid": user_id,
                "chance": chance
            }
            return_list.append(user_dict)

    return return_list