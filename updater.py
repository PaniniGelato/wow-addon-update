import requests
import json
from bs4 import BeautifulSoup
import zipfile
import io
import re
import traceback
import config

ft_map = {}
with open("faultTolerance.csv", "r") as ft:
    for ll in ft.readlines():
        arr = ll.strip().split(",")
        ft_map[arr[0]] = arr[1]


def only_dbm(force=False):
    dbm_new_lines=[]
    with open("dbm.csv", "r") as dbm:
        lines = dbm.readlines()
        for line in lines:
            arr = line.strip().split(",")
            fName = arr[1]
            current_ver = int(arr[2])
            # eg:{"ProjectFileID": 2585875, "FileName": "2.16.1"}
            _, dd = fetch_addon_data(arr[0])
            print(dd)
            flag = False
            if dd["FileName"] != arr[1] and arr[1] != "_":
                flag = True
                fName = dd["FileName"]
            elif dd["ProjectFileID"] > current_ver > 0:
                flag = True
            if flag or force:
                print("updating %s ..." % arr[0])
                url = "https://www.curseforge.com/wow/addons/%s/download/%s/file" % (arr[0], str(dd["ProjectFileID"]))
                res = requests.get(url, headers={
                    "Referer": "https://www.curseforge.com",
                    "Useragent": "Mozilla / 5.0(Windows NT 10.0; Win64; x64) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 66.0.3359.170 Safari / 537.36"}
                )
                z = zipfile.ZipFile(io.BytesIO(res.content))
                z.extractall(path=config.wow_root)
            dbm_new_lines.append("%s,%s,%s" % (arr[0], fName, str(dd["ProjectFileID"])))
    with open("dbm.csv", "w") as dbm:
        for ll in dbm_new_lines:
            # print(ll)
            dbm.write(ll)
            dbm.write("\n")


def all_addons(force=False):
    new_lines = []
    with open("addons.csv", "r") as addons:
        lines = addons.readlines()
        for line in lines:
            if not line.strip():
                continue
            new_line = line.strip()
            try:
                arr = line.strip().split(",")
                real_name = arr[0]
                fName = arr[1]
                current_ver = int(arr[2])
                if ft_map.get(real_name):
                    real_name = ft_map.get(real_name)
                if real_name == "NULL":
                    continue
                elif real_name == "MeetingStone":
                    new_ver = download_meeting_stone(fName)
                    new_line = "%s,%s,%s" % ("MeetingStone", new_ver, "0")
                else:
                    # eg:{"ProjectFileID": 2585875, "FileName": "2.16.1"}
                    _, dd = fetch_addon_data(arr[0])
                    if not dd:
                        print("unable to update %s..." % real_name)
                        new_lines.append("%s,%s,%s" % (arr[0], fName, "0"))
                        continue
                    print(dd)
                    flag = False
                    if dd["FileName"] != arr[1] and arr[1] != "_":
                        flag = True
                        fName = dd["FileName"]
                    elif dd["ProjectFileID"] > current_ver > 0:
                        flag = True
                    if flag or force:
                        url = "https://www.curseforge.com/wow/addons/%s/download/%s/file" % (arr[0], str(dd["ProjectFileID"]))
                        print("updating %s, %s" % (arr[0], url))
                        res = requests.get(url, headers={
                            "Referer": "https://www.curseforge.com",
                            "Useragent": "Mozilla / 5.0(Windows NT 10.0; Win64; x64) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 66.0.3359.170 Safari / 537.36"}
                        )
                        z = zipfile.ZipFile(io.BytesIO(res.content))
                        z.extractall(path=config.wow_root)
                        new_line = "%s,%s,%s" % (arr[0], fName, str(dd["ProjectFileID"]))
            except Exception:
                traceback.print_exc()
            new_lines.append(new_line)
    with open("addons.csv", "w") as addons:
        for ll in new_lines:
            # print(ll)
            addons.write(ll)
            addons.write("\n")


def fetch_addon_data(addon_name):
    url = "https://www.curseforge.com/wow/addons/%s/files" % addon_name
    print(url)
    resp = requests.get(url)
    soup = BeautifulSoup(resp.content, "html.parser")
    el = soup.find("a", attrs={"data-action": "install-file"})
    data = None
    if el:
        data = json.loads(el.get("data-action-value"))
    else:
        addon_name = re.sub(r'[A-Z]', lambda m: "-" + m.group(0).lower(), addon_name)[1:]
        addon_name = addon_name.replace(".", "-")
        url = "https://www.curseforge.com/wow/addons/%s/files" % addon_name
        print(url)
        resp = requests.get(url)
        soup = BeautifulSoup(resp.content, "html.parser")
        el = soup.find("a", attrs={"data-action": "install-file"})
        if el:
            data = json.loads(el.get("data-action-value"))
    return addon_name, data


def download_meeting_stone(file_name):
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
        if file_name != new_ver:
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
