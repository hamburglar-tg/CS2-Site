import asyncio
import datetime
import json
import time

import requests

import src.main_manager as ctr

from src.cfg_parser import cfg

api_key = cfg("Bot", "api_key")
session = requests.Session()


def api_call(method, interface, api_method, version, params):
    url = '/'.join(('https://api.steampowered.com', interface, api_method, version))
    response = session.get(url, params=params) if method == 'GET' else session.post(url, data=params)

    return response


def get_profile(steam_id) -> dict:
    try:
        params = {'steamids': steam_id, 'key': api_key}
        response = api_call('GET', 'ISteamUser', 'GetPlayerSummaries', 'v0002', params)
        data = response.json()
        return data['response']['players'][0]
    except:
        time.sleep(120)
        return {}


def generate_random_user(user_id):
    user_profile = get_profile(user_id)
    if user_profile != {}:
        user_avatar = user_profile.get("avatarfull")

        if str(user_avatar) == "https://avatars.steamstatic.com/fef49e7fa7e1997310d705b2a6158ff8dc1cdfeb_full.jpg":
            return False

        user = {'steamId': user_id, 'avatar': user_avatar, 'nickname': user_profile.get("personaname")}

        return user


def generate_users():
    tasks = []
    users = []

    start_user_id = 76561199092345268
    count = 300
    z = 0
    for _ in range(count):
        task = generate_random_user(str(start_user_id))
        print(task)
        if not task:
            pass
        else:
            tasks.append(task)
            count -= 1
        start_user_id += 1
        z += 1
        if count <= 0:
            break
        if z % 30 == 0:
            time.sleep(20)

    for task in tasks:
        users.append(task)

    with open('../src/users.json', 'w', encoding='utf-8') as file:
        json.dump(users, file, ensure_ascii=False, indent=4)

    session.close()