import asyncio
from random import randint

from src.socket_server import sio
import src.main_manager as ctr

from database.db_handler import *

class GameManager:
    def __init__(self):
        self.users = []
        self.users_count = 0
        self.items_count = 0
        self.game_bank = 0
        self.timer_value = 5
        self.roulette_timer = 15
        self.special_status = "user"
        self.shuffle_winners = None
        self.isTimerStarted = False
        self.isRouletteStarted = False
        self.game_id = get_last_game_id()
        self.insert_game_in_db()

    def insert_game_in_db(self):
        insert_game(self.game_id, json.dumps(self.get_game()))

    def upd(self, new_game_json):
        self.users = new_game_json["users"]
        self.users_count = new_game_json["game_info"]["users_count"]
        self.items_count = new_game_json["game_info"]["items_count"]
        self.game_bank = new_game_json["game_info"]["game_bank"]

        update_game(new_game_json, self.game_id)

    async def start_timer(self):
        self.isTimerStarted = True
        asyncio.create_task(self.update_timer())
        log("BOTS", f"Timer in the game {ctr.project.current_game.game_id} is running.")

    async def update_timer(self):
        while self.timer_value > 0:
            await sio.emit('timer', self.timer_value)
            self.timer_value -= 1
            await asyncio.sleep(1)

        await sio.emit('timer', self.timer_value)
        await asyncio.sleep(1)
        asyncio.create_task(self.start_roulette())

    async def start_roulette(self):
        self.isRouletteStarted = True
        game_json = self.get_game()

        asyncio.create_task(handle_spin(game_json["users"]))
        asyncio.create_task(timer(25, self.del_game()))
        log("BOTS", f"Roulette in the game {ctr.project.current_game.game_id} is running.")

    async def del_game(self):
        game_json = self.get_game()
        update_game(game_json, self.game_id)
        del ctr.project.current_game
        ctr.project.current_game = None
        await ctr.project.create_game()
        log("BOTS", f"A new game has been launched!")

    def get_game(self):
        return {
            "game_info": {
                "users_count": self.users_count,
                "game_bank": self.game_bank,
                "items_count": self.items_count,
                "game_id": self.game_id
            },
            "users": self.users
        }


async def timer(time, func):
    await asyncio.sleep(time)
    await func


async def handle_spin(users):
    winners = []
    winner_index = 112

    for user_data in users:
        for _ in range(int(130 / len(users))):
            winners.append(user_data)

    winners = await shuffle(winners, winner_index, ctr.project.current_game.special_status, users)
    ctr.project.current_game.shuffle_winners = winners

    await sio.emit('startRoulette', winners)

    while ctr.project.current_game.roulette_timer > 0:
        ctr.project.current_game.roulette_timer -= 1
        await asyncio.sleep(1)

    winner = winners[winner_index % len(winners)]
    winner_steam_id = list(winner.keys())[0]
    winner_data = winner[winner_steam_id]

    winner_avatar = winner_data['avatar']
    winner_nickname = winner_data['nickname']
    winner_user_bank = winner_data['user_bank']

    winner_obj = {
        'winner_avatar': winner_avatar,
        'winner_nickname': winner_nickname,
        'winner_user_bank': winner_user_bank
    }

    ctr.project.last_winner_dict = {"avatar": winner_avatar, "nickname": winner_nickname, "steam_id": winner_steam_id, "bank": winner_user_bank}
    await sio.emit('winner_data', winner_obj)


async def shuffle(array, special_index, special_status, users):
    current_index = len(array)

    while current_index != 0:
        random_index = randint(0, current_index - 1)
        current_index -= 1

        array[current_index], array[random_index] = array[random_index], array[current_index]

    if array[special_index][list(array[special_index].keys())[0]]['status'] == special_status:
        suitable_user = next((user for user in users if user[list(user.keys())[0]]['status'] != special_status), None)

        if suitable_user:
            suitable_user_key = list(suitable_user.keys())[0]
            suitable_user_data = suitable_user[suitable_user_key]
            array[special_index] = {suitable_user_key: suitable_user_data}

    return array
