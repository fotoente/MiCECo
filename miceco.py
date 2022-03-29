import configparser
import os
import re
import sys
import argparse
from datetime import *
import requests
import emoji as emojilib
# TODO: Replace with emojis library!


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

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config", help="location of the configuration file")
parser.add_argument("-i", "--ignored", help="location of the file which emojis are ignored while counting")
args = parser.parse_args()

if args.config is None:
    configfilePath = os.path.join(os.path.dirname(__file__), 'miceco.cfg')
else:
    configfilePath = args.config

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
    ignoreEmojis = check_str_to_bool(config.get("misskey", "ignoreEmojis"))
except (TypeError, ValueError) as err:
    ignoreEmojis = False

if ignoreEmojis:
    if args.ignored is None:
        ignored_path = os.path.join(os.path.dirname(__file__), "ignoredemojis.txt")
    else:
        ignored_path = args.ignored

    if not os.path.exists(ignored_path):
        print("No file for ignored emojis found!")
        print("Setting skipped!")

    if os.path.exists(ignored_path):
        with open(ignored_path, "r", encoding="utf8") as ignored_file:
            ignored_emojis = []
            for element in ignored_file.readlines():
                i = element.strip()
                ignored_emojis.append(emojilib.demojize(i))

noteVisibility = config.get("misskey", "noteVisibility")  # How should the note be printed?
if noteVisibility != "public" and noteVisibility != "home" and noteVisibility != "followers" and noteVisibility != \
        "specified":
    noteVisibility = "followers"

try:
    req = requests.post(url + "/users/show", json={"username": user, "host": None, "i": token})
    req.raise_for_status()
except requests.exceptions.HTTPError as err:
    print("Couldn't get Username!\n" + str(err))
    sys.exit(1)

userid = req.json()["id"]
if req.json()["name"] is not None:  # If no nickname is set, just user the username instead
    nickname = req.json()["name"]
else:
    nickname = req.json()["username"]

# Get max note length
try:
    req = requests.post(url + "/meta", json={"detail": True, "i": token})
    req.raise_for_status()
except requests.exceptions.HTTPError as err:
    print("Couldn't get maximal note length!\n" + str(err))
    print("Setting max note length to 3.000 characters")
    max_note_length = 3000

max_note_length = int(req.json()["maxNoteTextLength"])

today = date.today()
formerDate = today - timedelta(days=1)
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
        noteList.append(jsonObj)

    formerTimestamp = lastTimestamp

    if not len(noteList) <= 0:  # If there is zero notes, then break the while loop
        lastTime = noteList[len(noteList) - 1]["createdAt"]
        lastTimestamp = int(datetime.timestamp(datetime.strptime(lastTime, '%Y-%m-%dT%H:%M:%S.%f%z')) * 1000)
    else:
        break

if len(noteList) == 0:
    print("Nothing to count, exiting script.")
    sys.exit(1)

if len(noteList) == 1:
    if noteList[0]["text"].find(chr(8203) + chr(8203) + chr(8203)) > 0:
        print("Only note is MiCECo note.")
        print("Nothing to count, exiting script")
        sys.exit(1)

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
            if emoji["name"].find("@") == -1:  # Only emojis from the own instance, because reactions will be in
                # "emojis" too
                emojiname = ":" + emoji["name"] + ":"
                if emojiname not in doubleList:
                    doubleList.append(emojiname)  # Easy way to prevent a double emoji in the list.
                    emojiDict = {"emoji": emojiname, "count": 0}
                    emojiList.append(emojiDict)
            else:
                continue

            index = doubleList.index(":" + emoji["name"] + ":")

            emojiList[index]["count"] += element["text"].count(emojiList[index]["emoji"])

            if element["cw"] is not None:
                emojiList[index]["count"] += element["cw"].count(emojiList[index]["emoji"])  # Count those Emojis, that
                # are in this note CW text

    # Process UTF8 Emojis
    if element["cw"] is not None:
        UTF8text = element["text"] + " " + element["cw"]
    else:
        UTF8text = element["text"]
    UTF8ListRaw = re.findall(emojilib.get_emoji_regexp(), UTF8text)  # Find all UTF8 Emojis in Text and CW text
    UTF8text = emojilib.demojize(UTF8text)
    # TODO urgent! replace "get_emoji_regexp"
    if len(UTF8ListRaw) > 0:
        UTF8List = list(set(UTF8ListRaw))
        for emoji in UTF8List:
            emoji = emojilib.demojize(emoji)
            if emoji not in doubleList:
                doubleList.append(emoji)  # Easy way to prevent a double emoji in the list without checking the whole
                # dictionary
                emojiDict = {"emoji": emoji, "count": 0}
                emojiList.append(emojiDict)

            index = doubleList.index(emoji)
            emojiList[index]["count"] += UTF8text.count(emoji)

if ignoreEmojis:
    for ignoredEmoji in ignored_emojis:
        if ignoredEmoji in doubleList:
            indx = doubleList.index(ignoredEmoji)
            del doubleList[indx]
            del emojiList[indx]

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
        if not len(reactionList) <= 0:
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

        initial_react_text = "\n\n\nAnd used " + str(reactionCount) + " reactions:\n\n" + chr(9553) + " "
        reactText = initial_react_text

        for reactionElement in reactList:
            count = reactionElement["count"]
            reaction = reactionElement["reaction"]
            reactText += f"{count}x {reaction} " + chr(9553) + " "
    else:
        reactText = "\n\nAnd didn't use any reactions."
else:
    reactText = ""

for count in emojiList:
    emojisTotal += count["count"]

initial_text = ""
initial_react_text = ""

if emojisTotal > 0:
    initial_text = nickname + " has written " + str(len(noteList)) + " Notes yesterday, " + formerDate.strftime(
        '%a %d-%m-%Y') + "\nand used a total of " + str(emojisTotal) + " Emojis. #miceco" + chr(8203) + chr(8203) + chr(
        8203) + "\n\n" + chr(9553) + " "
    text = initial_text
    emoji_text = ""

    for element in emojiList:
        count = element["count"]
        emoji = element["emoji"]
        emoji_text += f"{count}x {emoji} " + chr(9553) + " "

else:
    emoji_text = nickname + " has written " + str(len(noteList)) + " Notes yesterday, " + formerDate.strftime(
        '%a %d-%m-%Y') + "\nand didn't used any emojis. #miceco" + chr(8203) + chr(8203) + chr(8203)

text += emoji_text + reactText
text = emojilib.emojize(text)
# print(text)

if max_note_length < len(text):
    emoji_text = initial_text
    for item in range(0, 5):
        count = emojiList[item]["count"]
        emoji = emojiList[item]["emoji"]
        emoji_text += f"{count}x {emoji} " + chr(9553) + " "
    emoji_text += " and more..."

    if getReactions:
        reactText = initial_react_text
        for item in range(0, 5):
            count = reactList[item]["count"]
            reaction = reactList[item]["reaction"]
            reactText += f"{count}x {reaction} " + chr(9553) + " "
        reactText += " and more..."

    text = emoji_text + reactText
    text = emojilib.emojize(text)

# print(text)

try:
    req = requests.post(url + "/notes/create", json={
        "i": token,
        "visibility": noteVisibility,
        "text": text
    })
    req.raise_for_status()
except requests.exceptions.HTTPError as err:
    print("Couldn't create Posts! " + str(err))
    sys.exit(1)
