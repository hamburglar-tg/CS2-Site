import asyncio
import sys

from aiohttp import web

import src.main_manager as ctr

from database.db_handler import insert_project_data
from database.db_start import load_tables
from src.cfg_parser import cfg
from src.fake_trade import start_fake_trades
from src.logging import log
from src.socket_server import app


async def start():
    def custom_except(type, value, traceback):
        log("MAIN", f"ERROR: {value}")

    sys.excepthook = custom_except

    load_tables()
    insert_project_data(ctr.project.start_date, 0, 0)

    port = int(cfg("Server", "port"))
    host = cfg("Server", "host")
    index_text = cfg("Server", "index_text")

    async def index(request):
        return web.Response(text=index_text)

    app.router.add_get('/', index)
    runner = web.AppRunner(app)

    await runner.setup()

    site = web.TCPSite(runner, host=host, port=port)
    await site.start()

    log("PM", f"The server was successfully launched on port {port}.")


async def main():
    start_task = asyncio.create_task(start())
    await asyncio.sleep(5)  # Ждем пока все запустится
    trades_manager_task = asyncio.create_task(ctr.project.current_bot.trades_manager())
    fake_trades_task = asyncio.create_task(start_fake_trades())

    await start_task
    await fake_trades_task
    await trades_manager_task

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass