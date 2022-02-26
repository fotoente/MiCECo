import configparser
import os
import re
import sys
from datetime import *
# import dateutil.relativedelta

import requests
import emoji as emojilib


def check_str_to_bool(input_text) -> bool:
    if input_text == "True" or input_text == "true" or input_text == "TRUE":
        return True
    elif input_text == "False" or input_text == "false" or input_text == "FALSE":
        return False
    else:
        return True


noteList = []
reactionList = []
reactList = []
emojiList = []
emojisTotal = 0
doubleList = []
text = ""
getReactions = False

configfilePath = os.path.join(os.path.dirname(__file__), 'miceco.cfg')

if not os.path.exists(configfilePath):
    print("No config File found!")
    print("Exit program!")
    sys.exit(1)

# Load configuration
config = configparser.ConfigParser()
config.read(configfilePath)

url = "https://" + config.get("misskey", "instance") + "/api"
token = config.get("misskey", "token")
user = config.get("misskey", "user")

try:
    getReactions = check_str_to_bool(config.get("misskey", "getReaction"))
except (TypeError, ValueError) as err:
    getReactions = False

try:
    req = requests.post(url + "/users/show", json={"username": user, "host": None, "i": token})
    req.raise_for_status()
except requests.exceptions.HTTPError as err:
    print("Couldn't get Username!\n" + str(err))
    sys.exit(1)

userid = req.json()["id"]
nickname = req.json()["name"]

today = date.today()
formerDate = today - timedelta(days=1)
# formerDate = today - timedelta(weeks=1) #Last week
# formerDate = today - dateutil.relativedelta.relativedelta(months=1)
formerDateMidnight = datetime.combine(formerDate, time(0, 0, 0))
todayMidnight = datetime.combine(today, time(0, 0, 0))

seit = int(formerDateMidnight.timestamp()) * 1000  # Javascript uses millisecond timestamp and Python uses float
bis = int(todayMidnight.timestamp()) * 1000

lastTimestamp = bis
formerTimestamp = 0

while True:

    if (bis != lastTimestamp) and (formerTimestamp == lastTimestamp):
        break

    try:
        req = requests.post(url + "/users/notes", json={
            "i": token,
            "userId": userid,
            "sinceDate": seit,
            "untilDate": lastTimestamp,
            "includeReplies": True,
            "limit": 100,
            "includeMyRenotes": False,
            "withFiles": False,
            "excludeNsfw": False
        })
        req.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("Couldn't get Posts! " + str(err))
        sys.exit(1)

    for jsonObj in req.json():
        # textDict = jsonObj
        noteList.append(jsonObj)

    formerTimestamp = lastTimestamp

    if not len(noteList) <= 1:  # If there is one or less notes, then break the while loop
        lastTime = noteList[len(noteList) - 1]["createdAt"]
        lastTimestamp = int(datetime.timestamp(datetime.strptime(lastTime, '%Y-%m-%dT%H:%M:%S.%f%z')) * 1000)
    else:
        break

for element in noteList:
    if element["text"] is None:  # Skip Notes without text
        print("Skip Note " + element["id"] + " without Text\nTime noted: " + element["createdAt"])
        continue

    if element["text"].find(chr(8203) + chr(8203) + chr(8203)) > 0:  # Skip notes with three Zero-Width-Space in a
        # row (Marker to skip older MiCECo notes)
        print("Skip Note " + element["id"] + " with Zero-Width-Space\nTime noted: " + element["createdAt"])
        continue

    # Process and count custom Emojis
    emojis = element["emojis"]

    if emojis is not None:
        for emoji in emojis:
            if emoji["name"].find(
                    "@") == -1:  # Only emojis from the own instance, because reactions will be in "emojis"
                # too
                if not emoji["name"] in doubleList:
                    doubleList.append(emoji["name"])  # Easy way to prevent a double emoji in the list.
                    emojiDict = {"emoji": ":" + emoji["name"] + ":", "count": 0}
                    emojiList.append(emojiDict)
            else:
                continue

            index = doubleList.index(emoji["name"])

            emojiList[index]["count"] += element["text"].count(emojiList[index]["emoji"])

            if element["cw"] is not None:
                emojiList[index]["count"] += element["cw"].count(emojiList[index]["emoji"])  # Count those Emojis, that
                # are in this note CW text

    # Process UTF8 Emojis
    if element["cw"] is not None:
        UTF8text = element["text"] + " " + element["cw"]
    else:
        UTF8text = element["text"]
    UTF8List = re.findall(emojilib.get_emoji_regexp(), UTF8text)  # Find all UTF8 Emojis in Text and CW text

    if len(UTF8List) > 0:
        UTF8List = list(set(UTF8List))
        for emoji in UTF8List:
            if emoji not in doubleList:
                doubleList.append(emoji)  # Easy way to prevent a double emoji in the list.
                emojiDict = {"emoji": emoji, "count": 0}
                emojiList.append(emojiDict)

            index = doubleList.index(emoji)
            emojiList[index]["count"] += UTF8text.count(emoji)

doubleList = []
emojiList = sorted(emojiList, reverse=True, key=lambda d: d["count"])  # Sort it by the most used Emojis!

reactionCount = 0

if getReactions:
    lastTimestamp = bis

    while True:

        if (bis != lastTimestamp) and (formerTimestamp == lastTimestamp):
            break

        try:
            req = requests.post(url + "/users/reactions", json={
                "i": token,
                "userId": userid,
                "sinceDate": seit,
                "untilDate": lastTimestamp
            })
            req.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print("Couldn't get Posts! " + str(err))
            sys.exit(1)

        for jsonObj in req.json():
            # textDict = jsonObj
            reactionList.append(jsonObj)

        formerTimestamp = lastTimestamp
        if not len(reactionList) <=1:
            lastTime = reactionList[len(reactionList) - 1]["createdAt"]
            lastTimestamp = int(datetime.timestamp(datetime.strptime(lastTime, '%Y-%m-%dT%H:%M:%S.%f%z')) * 1000)
        else:
            break

    react = ""
    index = None
    reactionElement: dict

    for reactionElement in reactionList:
        react = reactionElement["type"]
        react = react.replace("@.", "")

        if react not in doubleList:
            doubleList.append(react)
            emojiDict = {"reaction": react, "count": 0}
            reactList.append(emojiDict)

        index = doubleList.index(react)

        reactList[index]["count"] += 1

    doubleList = []
    reactList = sorted(reactList, reverse=True, key=lambda d: d["count"])

    if len(reactList) > 0:
        for react in reactList:  # Summarize the number of Reactions used
            reactionCount += react["count"]

        reactText = "\n\n\nAnd used " + str(reactionCount) + " reactions:\n\n" + chr(9553) + " "

        for reactionElement in reactList:
            reactText += str(reactionElement["count"]) + "x " + reactionElement["reaction"] + " " + chr(9553) + " "
    else:
        reactText = "\n\nAnd didn't use any reactions."
else:
    reactText = ""

for count in emojiList:
    emojisTotal += count["count"]

if emojisTotal > 0:
    text = nickname + " has written " + str(len(noteList)) + " Notes yesterday, " + formerDate.strftime(
        '%a %d-%m-%Y') + "\nand used a total of " + str(emojisTotal) + " Emojis. #miceco" + chr(8203) + chr(8203) + chr(
        8203) + "\n\n" + chr(
        9553) + " "
    for element in emojiList:
        text += str(element["count"]) + "x\u00A0" + element["emoji"] + " " + chr(9553) + " "
else:
    text = nickname + " has written " + str(len(noteList)) + " Notes yesterday, " + formerDate.strftime(
        '%a %d-%m-%Y') + "\nand didn't used any emojis. #miceco" + chr(8203) + chr(8203) + chr(
        8203)

text += reactText

# print(text)

try:
    req = requests.post(url + "/notes/create", json={
        "i": token,
        "visibility": "public",
        "text": text
    })
    req.raise_for_status()
except requests.exceptions.HTTPError as err:
    print("Couldn't create Posts! " + str(err))
    sys.exit(1)
