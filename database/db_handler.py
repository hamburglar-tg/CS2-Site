import json

import mysql.connector.errors

from database.db_start import db, cursor
from src.logging import log

try:
    def get_data(query, params=None):
        cursor.execute(query, params)
        result = cursor.fetchone()
        db.commit()
        return result if result else None

    def insert_data(query, params):
        cursor.execute(query, params)
        db.commit()

    def update_data(query, params):
        cursor.execute(query, params)
        db.commit()

    def get_all_info(table, params):
        return get_data(f"SELECT {', '.join(params)} FROM {table}")

    def project():
        cursor.execute('SELECT open_data FROM project')
        result = cursor.fetchone()
        db.commit()
        return result if result else None


    def insert_project_data(open_data, games_count, today_games_count):
        if project() is None:
            insert_data("INSERT INTO project (open_data, games_count, today_games_count) VALUES (%s, %s, %s)", (open_data, games_count, today_games_count))
        else:
            ...


    def check_user(steam_id):
        return get_data("SELECT steam_id FROM users WHERE steam_id = %s", (steam_id,))


    def insert_new_user(steam_id, avatar_url, nickname, participation_num, max_win, win_percent, win_count, trade_link):
        insert_data("INSERT INTO users (steam_id, avatar_url, nickname, participation_num, max_win, win_percent, win_count, trade_link) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (steam_id, avatar_url, nickname, participation_num, max_win, win_percent, win_count, trade_link))


    def get_all_user_info(steam_id):
        return get_data("SELECT steam_id, avatar_url, nickname, participation_num, max_win, win_percent, win_count, trade_link FROM users WHERE steam_id = %s", (steam_id,))


    def update_user_trade_link(steam_id, new_link):
        update_data("UPDATE users SET trade_link = %s WHERE steam_id = %s", (new_link, steam_id))


    def update_user_info(steam_id, new_participation_num, new_win_count):
        update_data("UPDATE users SET participation_num = %s, win_count = %s WHERE steam_id = %s", (new_participation_num, new_win_count, steam_id))


    def get_project_info():
        result = get_all_info("project", ["open_data", "games_count", "today_games_count"])
        db.commit()
        return result if result else None


    def get_last_game_id():
        game_id = get_data("SELECT MAX(game_id) FROM games")[0]
        return int(game_id) + 1 if game_id is not None else 1


    def insert_game(game_id, game_json):
        insert_data("INSERT INTO games (game_id, game_info) VALUES (%s, %s)", (game_id, game_json))


    def update_game(new_game_json, game_id):
        update_data("UPDATE games SET game_info = %s WHERE game_id = %s", (json.dumps(new_game_json), game_id))

except mysql.connector.errors.OperationalError as dbWorkError:
    log("DB", f"OperationalError on the database. Stopping the script. Error: {dbWorkError}")
    exit()