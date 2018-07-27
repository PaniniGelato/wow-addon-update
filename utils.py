# -*- coding: utf-8 -*-
import os
import re
import updater
import config
from concurrent.futures import ThreadPoolExecutor


def init_addon_config():
    """
    loop wow addOns directory and init addon list.
    gather addon info base on their toc file.
    skip directory contains Blizzard or '_'.
    :param addons:
    :return:
    """
    addon_list = []
    with ThreadPoolExecutor(max_workers=config.thread) as executor:
        for f in os.listdir(config.wow_root):
            addon_dir = config.wow_root + os.sep + f
            sublist = os.listdir(addon_dir)
            toc = [ff for ff in sublist if re.match(r'.*\.toc', ff)]
            if len(toc) > 0:
                toc = toc[0]
                with open(addon_dir + os.sep + toc, "r", encoding='utf-8') as t:
                    lines = t.readlines()
                    version = "0"
                    url = "null"
                    dep = False
                    for line in lines:
                        line = line.strip()
                        if line.startswith("## Version"):
                            version = line[11:]
                        if line.startswith("## Dependencies"):
                            dep = True
                        if line.startswith("## X-Website"):
                            url = line[13:]
                    if f == "MeetingStone":
                        addon_list.append({"name": f, "version": version, "url": url})
                    if not dep and not str(f).startswith("DBM-"):
                        if f in config.ft:
                            f = config.ft_map.get(f)
                        if f != "NULL":
                            executor.submit(fetch_addon_data, f, version, url, addon_list)
    with open(config.addons, "w", encoding='utf-8') as w:
        for aa in addon_list:
            line = aa["name"].strip()+","+aa["version"].strip()+",0"
            w.write(line)
            w.write("\n")


def fetch_addon_data(f, version, url, addon_list):
    f, data = updater.fetch_addon_data(f)
    if data:
        addon_list.append({"name": f, "version": version, "url": url})
