import asyncio

import src.game as game
import src.bot as bot

from datetime import datetime
from src.cfg_parser import cfg
from src.socket_server import sio


class MainManager:
    def __init__(self):
        self.start_date = datetime.now().strftime("%d.%m.%y")
        self.current_game = None
        self.current_bot = None
        self.games_today = 0
        self.strike = 21690
        self.peak_online = 127
        self.last_winner_dict = {"avatar": "../img/default_avatar.jpg", "nickname": "", "steam_id": 0, "bank": 0}
        self.load_bot()
        self.load_game()

    def load_bot(self):
        self.current_bot = bot.BotManager(cfg("Bot", "api_key"), cfg("Bot", "username"), cfg("Bot", "password"), cfg("Bot", "settings_file_path"))

    async def create_game(self):
        self.current_game = game.GameManager()
        self.games_today += 1
        await sio.emit('newGame', {})

    def load_game(self):
        asyncio.run(self.create_game())


project = MainManager()
