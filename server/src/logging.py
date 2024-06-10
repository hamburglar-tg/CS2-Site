from loguru import logger
import sys

logger.remove(0)
logger.add(sys.stderr, format="\033[97m{time:MMMM D, YYYY, HH:mm:ss}\033[0m | {level} | {message}")

main_level = logger.level("MAIN", no=38, color="<red>")
project_manager_level = logger.level("PM", no=38, color="<yellow>")
events_level = logger.level("EVENTS", no=38, color="<green>")
bots_level = logger.level("BOTS", no=38, color="<blue>")
games_level = logger.level("GAMES", no=38, color="<white>")
database_level = logger.level("DB", no=38, color="magenta")

colors = {
    "MAIN": "\033[91m",    # красный
    "PM": "\033[93m",      # желтый
    "EVENTS": "\033[92m",  # зеленый
    "BOTS": "\033[94m",    # синий
    "GAMES": "\033[97m",   # белый
    "DB": "\033[35m"       # пурпурный
}

def log(level, message):
    logger.log(level, f"{colors[level]}{message}")
