import configparser

config = configparser.ConfigParser()
config.read("config.ini")

wow_root = config["WOW"]["ROOT"]
addons = config["WOW"]["ADDONS"]
dbm = config["WOW"]["DBM"]
ft = config["WOW"]["FT"]