import configparser

config = configparser.ConfigParser()
config.read("../scripts/config.ini")

def cfg(heading, key):
    return config[heading][key]