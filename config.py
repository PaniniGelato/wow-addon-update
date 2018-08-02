import configparser

config = configparser.ConfigParser()
config.read("config.ini")

wow_root = config["WOW"]["ROOT"]
addons = config["WOW"]["ADDONS"]
dbm = config["WOW"]["DBM"]
ft = config["WOW"]["FT"]
thread = int(config["WOW"]["THREAD"])
release_type = config["WOW"]["RELEASE_TYPE"]


def load_ft_map():
    """
    load faultTolerance.csv
    :return:
    """
    ret = {}
    with open(ft, "r") as ff:
        for ll in ff.readlines():
            arr = ll.strip().split(",")
            ret[arr[0]] = arr[1]
    return ret


ft_map = load_ft_map()