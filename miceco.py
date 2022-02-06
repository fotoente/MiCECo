import sys
import os
import requests
from datetime import *
import json
import configparser

def check_str_to_bool(text) -> bool:
    if (text == "True" or text == "true" or text == "TRUE"):
        return True
    elif (text == "False" or text == "false" or text == "FALSE"):
        return False
    else:
        return True

token=""
url=""
noteList = []
reactionList = []
reactList=[]
emojiList = []
emojisTotal = 0
doubleList = []
text = ""
getReactions = False

configfilePath = os.path.join(os.path.dirname(__file__), 'miceco.cfg')

if (not os.path.exists(configfilePath)):
    print("No config File found!")
    print("Exit programm!")
    sys.exit(1)

#Load configuration
config = configparser.ConfigParser()
config.read(configfilePath)

url = "https://" + config.get("misskey","instance") + "/api"
token = config.get("misskey","token")
user = config.get("misskey","user")

try:
    getReactions = check_str_to_bool(config.get("misskey","getReaction"))
except (TypeError, ValueError) as err:
    getReactions = False

try:
        req = requests.post(url+"/users/show", json={"username" : user, "host" : None, "i" : token})
        req.raise_for_status()
except requests.exceptions.HTTPError as err:
        print("Couldn't get Username!\n"+str(err))
        sys.exit(1)
        
    
userid = req.json()["id"]
nickname = req.json()["name"]

heute = date.today()
gestern = heute - timedelta(days = 1)
mitternachtGestern = datetime.combine(gestern, time(0,0,0))
mitternachtHeute = datetime.combine(heute, time(0,0,0))

seit = int(mitternachtGestern.timestamp())*1000 #Javascript uses millisecond timestamp and Python uses float
bis = int(mitternachtHeute.timestamp())*1000

lastTimestamp = bis

while True:
    
    
    if ((bis != lastTimestamp) and (formerTimestamp == lastTimestamp)):
        break
        
    try: 
        req = requests.post(url+"/users/notes", json = {
                                                        "i" : token,
                                                        "userId" : userid,
                                                        "sinceDate" : seit,
                                                        "untilDate" : lastTimestamp,
                                                        "includeReplies" : True,
                                                        "limit" : 100,
                                                        "includeMyRenotes" : False,
                                                        "withFiles" : False,
                                                        "excludeNsfw" : False
                                                        })  
        req.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("Couldn't get Posts! "+str(err))
        sys.exit(1)

    for jsonObj in req.json():
        #textDict = jsonObj
        noteList.append(jsonObj)
    
    formerTimestamp = lastTimestamp
    
    lastTime = noteList[len(noteList)-1]["createdAt"]
    lastTimestamp = int(datetime.timestamp(datetime.strptime(lastTime, '%Y-%m-%dT%H:%M:%S.%f%z'))*1000)

for element in noteList:
    if (element["text"] == None): #Skip Notes without text
        print("Skip Note " + element["id"] + " without Text\nTime noted: " + element["createdAt"])
        continue
        
    if (element["text"].find(chr(8203))>0): #Skip notes with Zero-Width-Space (Marker to skip older MiCECo notes)
        print("Skip Note " + element["id"] + " with Zero-Width-Space\nTime noted: " + element["createdAt"])
        continue
        
    emojis = element["emojis"]
    
    if (not emojis): #Notes without emojis will be skipped
        continue
    
    for emoji in emojis:
        if (emoji["name"].find("@") == -1): #Only emojis from the own instance, because reactions will be in "emojis" too
            if (not emoji["name"] in doubleList):
                doubleList.append(emoji["name"]) #Easy way to prevent a double emoji in the list.
                dict={"emoji" : emoji["name"], "count" : 0}
                emojiList.append(dict) #TODO: Append a dictionary to acces it way easier
    
    for emoji in emojiList:
        emoji["count"] += element["text"].count(emoji["emoji"])

doubleList = []
emojiList = sorted(emojiList, reverse = True , key = lambda d: d["count"]) #Sort it by the most used Emojis!
    
if getReactions:
    lastTimestamp = bis
    
    while True:
    
        if ((bis != lastTimestamp) and (formerTimestamp == lastTimestamp)):
            break
        
        try: 
            req = requests.post(url+"/users/reactions", json = {
                                                            "i" : token,
                                                            "userId" : userid,
                                                            "sinceDate" : seit,
                                                            "untilDate" : lastTimestamp
                                                            })  
            req.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print("Couldn't get Posts! "+str(err))
            sys.exit(1)

        for jsonObj in req.json():
            #textDict = jsonObj
            reactionList.append(jsonObj)
    
        formerTimestamp = lastTimestamp
    
        lastTime = reactionList[len(reactionList)-1]["createdAt"]
        lastTimestamp = int(datetime.timestamp(datetime.strptime(lastTime, '%Y-%m-%dT%H:%M:%S.%f%z'))*1000)

    for reaction in reactionList:
        react = reaction["type"]
        react = react.replace("@.","")
        
        if (not react in doubleList):
            doubleList.append(react)
            dict={"reaction" : react, "count" : 0}
            reactList.append(dict)
    
        for reaction in reactList:
            if (reaction["reaction"] == react):
                reaction["count"] += 1
        
        reactList = sorted(reactList, reverse = True , key = lambda d: d["count"])
        
        reactionCount = 0
        for react in reactList:
            reactionCount += react["count"]
        
    if (len(reactList) > 0):
        reactText="\n\n\nAnd used " + str(reactionCount) + " reactions:\n\n" + chr(9553) + " "
    
        for reaction in reactList:
            reactText += str(reaction["count"]) + "x " + reaction["reaction"] + " " + chr(9553) + " " 
    else:
        reactText="\n\nAnd didn't use any reactions."
else:
    reactText=""

for count in emojiList:
    emojisTotal += count["count"]

if (emojisTotal > 0):
    text = nickname + " has written " + str(len(noteList)) + " Notes yesterday, " + gestern.strftime('%a %d-%m-%Y') + "\nand used a total of " + str(emojisTotal) + " Emojis. #miceco" + chr(8203) + "\n\n" + chr(9553) + " "
    for element in emojiList:
        text += str(element["count"]) + "x\u00A0:" + element["emoji"] + ": " + chr(9553) + " "
else:
    text = nickname + " has written " + str(len(noteList)) + " Notes yesterday, " + gestern.strftime('%a %d-%m-%Y') + "\nand didn't used any emojis. #miceco" + chr(8203)

text += reactText

#print(text)

try: 
    req = requests.post(url+"/notes/create", json = {
                                                        "i" : token,
                                                        "visibility": "public",
                                                        "text": text
                                                        })  
    req.raise_for_status()
except requests.exceptions.HTTPError as err:
    print("Couldn't create Posts! "+str(err))
    sys.exit(1)
