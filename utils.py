# -*- coding: utf-8 -*-
import os
import re
import configparser
import updater

config = configparser.ConfigParser()
config.read("config.ini")

wow_root = config["WOW"]["ROOT"]
addons = config["WOW"]["ADDONS"]
dbm = config["WOW"]["DBM"]
ft = config["WOW"]["FT"]


def init_addon_config(wow_root, addons_config):
    """
    loop wow addOns directory and init addon list.
    gather addon info base on their toc file.
    skip directory contains Blizzard or '_'.
    :param wow_root:
    :param addons:
    :return:
    """
    addon_list=[]
    for f in os.listdir(wow_root):
        addonDir = wow_root + os.sep + f
        sublist = os.listdir(addonDir)
        toc = [ff for ff in sublist if re.match(r'.*\.toc', ff)]
        if len(toc)>0:
            toc = toc[0]
            with open(addonDir+os.sep+toc, "r", encoding='utf-8') as t:
                lines = t.readlines()
                version = "0"
                url = "null"
                dep = False
                for l in lines:
                    l = l.strip()
                    if l.startswith("## Version"):
                        version = l[11:]
                    if l.startswith("## Dependencies"):
                        dep = True
                    if l.startswith("## X-Website"):
                        url = l[13:]
                if f == "MeetingStone":
                    addon_list.append({"name": f, "version": version, "url": url})
                if not dep and not str(f).startswith("DBM-"):
                    if updater.ft_map.get(f):
                        f = updater.ft_map.get(f)
                    if f != "NULL":
                        f, data = updater.fetch_addon_data(f)
                        if data:
                            addon_list.append({"name": f, "version": version, "url": url})
    with open(addons_config, "w", encoding='utf-8') as w:
        for aa in addon_list:
            line = aa["name"].strip()+","+aa["version"].strip()+",0"
            w.write(line)
            w.write("\n")
        w.flush()
