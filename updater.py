import requests
import json
from bs4 import BeautifulSoup
import zipfile
import io
import re
import traceback
import config
from concurrent.futures import ThreadPoolExecutor


request_headers = {
    "Referer": "https://www.curseforge.com",
    "Useragent": "Mozilla / 5.0(Windows NT 10.0; Win64; x64) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 66.0.3359.170 Safari / 537.36"
}


def only_dbm(force=False):
    """
    only update DBM, defined in dbm.csv
    :param force: force update without version checks
    :return:
    """
    future_list = []
    dbm_map = read_dbm()
    with ThreadPoolExecutor(max_workers=config.thread) as executor:
        for key in dbm_map:
            d = dbm_map.get(key)
            fName = d["file"]
            current_ver = int(d["version"])
            # eg:{"ProjectFileID": 2585875, "FileName": "2.16.1"}
            ff = executor.submit(do_update, d["name"], fName, current_ver, force)
            future_list.append(ff)
    for ff in future_list:
        a = ff.result()
        if a:
            key = a[0]
            dbm_mod = dbm_map.get(key)
            if dbm_mod:
                dbm_mod["file"] = a[1]
                dbm_mod["version"] = a[2]
    with open(config.dbm, "w") as dbm:
        for key in dbm_map:
            d = dbm_map.get(key)
            line = "%s,%s,%s" % (d["name"], d["file"], d["version"])
            dbm.write(line)
            dbm.write("\n")


def do_update(addon_name, current_file_name, current_file_ver, force=False):
    _, dd = fetch_addon_data(addon_name, guess=False)
    if not dd:
        return None
    print(dd)
    flag = False
    new_file_name = dd["FileName"]
    new_file_id = dd["ProjectFileID"]
    if new_file_name != current_file_name and current_file_name != "_":
        flag = True
    elif new_file_id > current_file_ver > 0:
        flag = True
    if flag or force:
        download_extract_curse_addon(addon_name, str(new_file_id))
    return [addon_name, new_file_name, str(new_file_id)]


def download_extract_curse_addon(name, file_id):
    """
    download and extract addon from curseforge.com
    :param name:
    :param file_id:
    :return:
    """
    print("updating %s ..." % name)
    url = "https://www.curseforge.com/wow/addons/%s/download/%s/file" % (name, file_id)
    res = requests.get(url, request_headers)
    z = zipfile.ZipFile(io.BytesIO(res.content))
    z.extractall(path=config.wow_root)


def read_addon():
    """
    load config.addons
    :return:
    """
    ret = []
    with open(config.addons, "r") as addons:
        lines = addons.readlines()
        for line in lines:
            if not line.strip():
                continue
            arr = line.strip().split(",")
            ret.append(arr)
    return ret


def read_dbm():
    """
    load config.dbm
    :return: dict
    """
    ret = {}
    with open(config.dbm, "r") as addons:
        lines = addons.readlines()
        for line in lines:
            if not line.strip():
                continue
            arr = line.strip().split(",")
            ret[arr[0]] = {"name": arr[0].lower(), "file": arr[1], "version": arr[2]}
    return ret


def all_addons(force=False):
    """
    update all addons except DBM
    :param force:
    :return:
    """
    new_line_list = []
    addon_map = read_addon()
    with ThreadPoolExecutor(max_workers=config.thread) as executor:
        for arr in addon_map:
            real_name = arr[0]
            fName = arr[1]
            current_ver = int(arr[2])
            new_line = "%s,%s,%s" % (real_name, fName, current_ver)
            try:
                if config.ft_map.get(real_name):
                    real_name = config.ft_map.get(real_name)
                if real_name == "NULL":
                    continue
                elif real_name == "MeetingStone":
                    new_ver = download_meeting_stone(fName)
                    new_line = "%s,%s,%s" % ("MeetingStone", new_ver, "0")
                else:
                    # eg:{"ProjectFileID": 2585875, "FileName": "2.16.1"}
                    new_arr = do_update(real_name, fName, current_ver, force)
                    new_line = "%s,%s,%s" % (real_name, new_arr[1], new_arr[2])
            except Exception:
                traceback.print_exc()
            new_line_list.append(new_line)
    with open(config.addons, "w") as addons:
        for line in new_line_list:
            addons.write(line)
            addons.write("\n")


def fetch_addon_data(addon_name, guess=True):
    """
    try to get addon data
    :param addon_name:
    :param guess:
    :return:
    """
    # only support curse now
    names = [addon_name]
    if guess:
        names = guess_addon_name(addon_name)
    for name in names:
        url = "https://www.curseforge.com/wow/addons/%s/files" % name
        print(url)
        resp = requests.get(url)
        soup = BeautifulSoup(resp.content, "html.parser")
        el = soup.find("a", attrs={"data-action": "install-file"})
        data = None
        if el:
            data = json.loads(el.get("data-action-value"))
            break
    return name, data


def guess_addon_name(addon_name):
    """
    guess the addon project name base on input param
    :param addon_name:
    :return:
    """
    ret = [addon_name]
    n = addon_name
    if "_" in addon_name:
        n = addon_name.replace("_", "")
        ret.append(n)
    name2 = re.sub(r'[A-Z]', lambda m: "-" + m.group(0).lower(), n)[1:].replace(" ", "")
    if "." in name2:
        name2 = name2.replace(".", "-")
    ret.append(name2)
    return ret


def download_meeting_stone(current_file_name):
    """
    support NetEase MeetingStone
    :param current_file_name:
    :return:
    """
    url = "http://w.163.com/special/wowsocial/"
    resp = requests.get(url)
    soup = BeautifulSoup(resp.content, "html.parser")
    all = soup.find("div", attrs={"class": "download-buttons"}).findChildren()
    for a in all:
        if a.text == "集合石插件包":
            u = a.get("href")
            new_ver = u[u.rfind("-")+1:len(u)-4]
            break
    try:
        if current_file_name != new_ver:
            print("updating meetingStones, %s" % u)
            res = requests.get(u, headers={
                "Referer": "http://w.163.com/special/wowsocial/",
                "Useragent": "Mozilla / 5.0(Windows NT 10.0; Win64; x64) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 66.0.3359.170 Safari / 537.36"}
            )
            z = zipfile.ZipFile(io.BytesIO(res.content))
            z.extractall(path=config.wow_root)
    except Exception:
        traceback.print_exc()
    return new_ver
