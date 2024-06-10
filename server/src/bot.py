import asyncio
import os
import pickle
import json

from steampy.client import SteamClient
from steampy.utils import GameOptions
from src.trades_handler import *


class BotManager:
    def __init__(self, api_key, username, password, steam_guard_file_path):
        self.api_key = api_key
        self.username = username
        self.password = password
        self.steam_guard_file_path = steam_guard_file_path
        self.cs2_game = GameOptions.CS
        self.bot_client = None
        self.init_client()

    def init_client(self):
        try:
            client_path = f"../bot/sessions/{self.username}_client.pkl"

            if os.path.isfile(client_path):
                with open(client_path, 'rb') as f:
                    new_client = pickle.load(f)

            else:
                new_client = SteamClient(self.api_key)
                new_client.login(self.username, self.password, self.steam_guard_file_path)

                with open(client_path, 'wb') as f:
                    pickle.dump(new_client, f)

            self.bot_client = new_client

            log("BOTS", f"Bot with username {self.username} successfully launched!")
        except ValueError as e:
            log("BOTS", f"An error occurred when launching the bot with username {self.username}, error:\n{e}")

    async def trades_manager(self):
        while True:
            if not ctr.project.current_game.isRouletteStarted:
                trade_offers = self.bot_client.get_trade_offers()

                if not trade_offers:
                    log("BOTS", "There are no trades to accept...")
                else:
                    received_offers = trade_offers['response']['trade_offers_received']
                    for offer in received_offers:
                        trade_offer_id = offer.get('tradeofferid')
                        trade_offer_status = offer.get('trade_offer_state')
                        items_to_receive = offer.get('items_to_receive')
                        items_to_give = offer.get('items_to_give')

                        log("BOTS", f"A new exchange offer has been received: {trade_offer_id}")
                        print(offer)
                        first_item_key = next(iter(items_to_receive), None)
                        appid = int(items_to_receive.get(first_item_key, {}).get('appid', 0))
                        if appid != 730:
                            print("ytes")
                            self.bot_client.decline_trade_offer(trade_offer_id)
                            log("BOTS", f"The exchange {trade_offer_id} was rejected, the items are not from CS2.")
                            continue

                        if items_to_give:
                            print("yes2")
                            self.bot_client.decline_trade_offer(trade_offer_id)
                            log("BOTS", f"The exchange {trade_offer_id} is rejected, the user asks for items in return.")
                            continue

                        if trade_offer_status == 2:
                            partner = self.bot_client.fetch_trade_partner_id(trade_offer_id)
                            if ctr.project.current_game:
                                self.bot_client.accept_trade_offer(trade_offer_id, partner)

                                trade_items_count = len(items_to_receive)
                                steam_id_exists = check_user_exists(partner)

                                ctr.project.current_game.items_count += trade_items_count
                                ctr.project.current_game.users_count += 1 if not steam_id_exists else 0

                                if trade_items_count <= 20 and not ctr.project.current_game.isRouletteStarted:
                                    await asyncio.create_task(new_deposit(partner, trade_items_count, trade_offer_id, items_to_receive, steam_id_exists))

                                if ctr.project.current_game.users_count == 2 and not ctr.project.current_game.isTimerStarted:
                                    await asyncio.create_task(ctr.project.current_game.start_timer())

                                if ctr.project.current_game.items_count >= 200:
                                    await asyncio.create_task(ctr.project.current_game.start_roulette())
                        else:
                            log("BOTS", f"The trade {trade_offer_id} has not been accepted, the trade status has changed.")

            await asyncio.sleep(5)

    def logout_bot(self):
        self.bot_client.logout()
        log("BOTS", f"You have successfully logged out of the bot account with username {self.username}.")

    def get_bot_inventory(self):
        log("BOTS", f"Getting the bot inventory {self.username}...")

        item_amounts = {}
        inventory = self.bot_client.get_my_inventory(self.cs2_game)
        for item in inventory.values():
            if item['market_name'] in item_amounts:
                item_amounts[item['market_name']] += 1
            else:
                item_amounts[item['market_name']] = 1

        inventory_path = f'../bot/{self.username}_inventory.json'

        with open(inventory_path, 'w') as file:
            json.dump(item_amounts, file, indent=4)

        log("BOTS", f"Successfully! The inventory is saved in the file: {inventory_path}.")