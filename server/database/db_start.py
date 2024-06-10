import mysql.connector

from src.cfg_parser import cfg
from src.logging import log

def connect():
    log("DB", "Connecting to the database...")
    try:

        connect_db = mysql.connector.connect(
            host=cfg("Database", "host"),
            user=cfg("Database", "user"),
            password=cfg("Database", "password"),
            database=cfg("Database", "database")
        )
        connect_cursor = connect_db.cursor()
        log("DB", "The database has been successfully connected.")
        return connect_db, connect_cursor
    except mysql.connector.Error as connectorError:
        log("DB", f"Error loading the database. Stopping the script. Error: {connectorError}")
        exit()

db, cursor = connect()

def load_tables():
    log("DB", "Uploading tables to the database...")
    try:
        cursor.execute("CREATE TABLE IF NOT EXISTS users (steam_id VARCHAR(255), avatar_url VARCHAR(255), nickname VARCHAR(255), participation_num VARCHAR(255), max_win INT, win_percent FLOAT, win_count INT, trade_link VARCHAR(255))")
        cursor.execute("CREATE TABLE IF NOT EXISTS project (open_data VARCHAR(255), games_count INT, today_games_count INT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS games (game_id INT, game_info LONGTEXT)")
        db.commit()
        log("DB", "The tables have been uploaded to the database.")
    except mysql.connector.Error as tableError:
        log("DB", f"Error when uploading tables. Error: {tableError}")
        exit()