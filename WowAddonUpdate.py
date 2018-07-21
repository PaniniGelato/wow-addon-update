import os.path
import utils
import argparse
import updater

parser = argparse.ArgumentParser()
parser.add_argument("-dbm", help="only update dbm", required=False, action="store_true")
parser.add_argument("-f", help="force a full update", required=False, action="store_true")
parser.add_argument("-r", help="re-scan addon directory and generate addons.csv", required=False, action="store_true")
parser.parse_args()

if __name__ == "__main__":
    args = parser.parse_args()
    if not os.path.isdir(utils.wow_root):
        print("wow dir error")
        exit(0)
    if args.r:
        utils.init_addon_config(utils.wow_root, utils.addons)
        exit(0)
    if not os.path.isfile(utils.addons) or os.stat(utils.addons).st_size == 0:
        print("cannot find addons-config-file, trying to generate it...")
        utils.init_addon_config(utils.wow_root, utils.addons)
    if args.dbm:
        updater.only_dbm(args.f)
    else:
        updater.all_addons(args.f)
        updater.only_dbm(args.f)

