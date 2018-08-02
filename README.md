# WoW-Adoon-Update
Twitch is rather buggy, so I create this script to update wow-addons

# Get-Start
1. install python3
2. pip install requests and BeautifulSoup4
3. modify config files as you like
4. run it with `python WowAddonUpdate.py`, this will only download the updates
5. -r will re-generate addons.csv, -f will force a full update and -dbm only update DBM-Mods


# Support Sites
1. curseforge
2. Netease MeetingStones


# Config
The config.ini looks like below:
```
[WOW]
ROOT = G:\\World of Warcraft\\interface\\AddOns
ADDONS = addons.csv
DBM = dbm.csv
FT = faultTolerance.csv
THREAD = 2
RELEASE_TYPE = beta
```
1. ROOT defines the location of your wow-addons directory
2. The script will generate the addons.csv on launch if it is not exists. This file contains the detail of your addons, which is grap from .toc files
3. The dbm.csv is for Deadly-Boss-Mod, which has so many folder and mods that is difficult to handle, so I make a static map to solve it. You can edit this file to add or delete DBM-mods as you like.
4. The faultTolerance.csv is a naming map to handle some problems
5. THREAD controls concurrency, larger number can make it faster
6. RELEASE_TYPE defaults to release, can be alpha or beta if you wish