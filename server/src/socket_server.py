import socketio
from aiohttp import web

import src.main_manager as ctr

from src.utils import *
from database.db_handler import *
from src.cfg_parser import cfg


def connection():
    conn_sio = socketio.AsyncServer(cors_allowed_origins=cfg("Server", "allowed_origins"), async_mode='aiohttp', async_handlers=True)
    con_app = web.Application()
    conn_sio.attach(con_app)
    return conn_sio, con_app


sio, app = connection()


@sio.event
async def connect(sid, environ):
    log("EVENTS", f"New event (client connect), client sid: {sid}")


@sio.event
async def disconnect(sid):
    log("EVENTS", f"New event (client disconnect), client sid: {sid}")


@sio.event
async def login(sid, data):
    try:
        user_steam_id = data["steamId"]
        log("EVENTS", f"New event (login), client sid: {sid}, steamId: {user_steam_id}")
        if check_user(user_steam_id) is None:
            user_avatar = ctr.project.current_bot.bot_client.get_profile(user_steam_id).get("avatarfull")
            user_nickname = ctr.project.current_bot.bot_client.get_profile(user_steam_id).get("personaname")
            insert_new_user(user_steam_id, user_avatar, user_nickname, 0, 0, 0, 0, None)
    except ValueError as Error:
        log("EVENTS", f"Error in event (login), error: {Error}")


@sio.event
async def profile(sid, data):
    try:
        user_steam_id = data["steamId"]
        log("EVENTS", f"New event (profile), client sid: {sid}, steamId: {user_steam_id}")
        if check_user(user_steam_id):
            user_id, avatar_url, nickname, participation_num, max_win, win_percent, win_count, trade_link = get_all_user_info(user_steam_id)
            response_data = {
                "steam_id": user_id,
                "avatar_url": avatar_url,
                "nickname": nickname,
                "participation_num": participation_num,
                "max_win": max_win,
                "win_percent": win_percent,
                "win_count": win_count,
                "trade_link": trade_link
            }
            await sio.emit('userProfile', response_data, room=sid)
    except ValueError as Error:
        log("EVENTS", f"Error in event (profile), error: {Error}")


@sio.event
async def change_link(sid, data):
    try:
        user_steam_id = data["steamId"]
        response_trade_link = data["trade_link"]
        log("EVENTS", f"New event (change link), client sid: {sid}, steamId: {user_steam_id}, new_link: {response_trade_link}")
        if check_user(user_steam_id):
            update_user_trade_link(user_steam_id, response_trade_link)
    except ValueError as Error:
        log("EVENTS", f"Error in event (change link), error: {Error}")


@sio.event
async def project_info(sid):
    try:
        log("EVENTS", f"New event (project info), client sid: {sid}")
        response_data = {
            "games_today": ctr.project.games_today,
            "last_winner": ctr.project.last_winner_dict,
            "last_game_id": ctr.project.current_game.game_id,
            "game_bank": round_decimal(ctr.project.current_game.game_bank, '0.1'),
            "items_count": ctr.project.current_game.items_count,
            "isRouletteStarted": ctr.project.current_game.isRouletteStarted,
            "current_game_users": ctr.project.current_game.get_game()["users"],
            "shuffle_winners": ctr.project.current_game.shuffle_winners,
            "roulette_timer_value": ctr.project.current_game.roulette_timer,
            "timer_value": ctr.project.current_game.timer_value,
            "strike": ctr.project.strike,
            "peak_online": ctr.project.peak_online
        }
        await sio.emit('projectInfo', response_data, room=sid)
    except ValueError as Error:
        log("EVENTS", f"Error in event (project info), error: {Error}")


@sio.event
async def bot_trade_link(sid):
    try:
        log("EVENTS", f"New event (bot trade link), client sid: {sid}")
        response_data = {
            "bot_trade_link": cfg("Bot", "trade_url")
        }
        await sio.emit('botTradeLink', response_data, room=sid)
    except ValueError as Error:
        log("EVENTS", f"Error in event (bot trade link), error: {Error}")


@sio.event
async def get_online(sid):
    try:
        log("EVENTS", f"New event (get online), client sid: {sid}")
        response_data = {
            "online": generate_online()
        }
        await sio.emit('online', response_data)
    except ValueError as Error:
        log("EVENTS", f"Error in event (get online), error: {Error}")


@sio.event
async def get_game_users(sid):
    try:
        log("EVENTS", f"New event (get game users), client sid: {sid}")
        game_json = ctr.project.current_game.get_game()
        response_data = {
            "users": game_json["users"]
        }
        await sio.emit('getGameUsers', response_data)
    except ValueError as Error:
        log("EVENTS", f"Error in event (get online), error: {Error}")
