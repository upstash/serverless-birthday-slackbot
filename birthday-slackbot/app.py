from chalice import Chalice, Cron, Rate
import os
import random
from datetime import date
from chalicelib.utils import responseToDict, postToChannel, diffWithTodayFromString, allSlackUsers, sendDm, validateRequest, convertToCorrectMention
from chalicelib.upstash import setHandler, getAllHandler, getEvent, getAllKeys, removeEvent

app = Chalice(app_name='birthday-slackbot')
NOTIFY_TIME_LIMIT = int(os.getenv("NOTIFY_TIME_LIMIT"))


# Sample route for get requests.
@app.route('/', methods=["GET"])
def something():
    return {
        "Hello": "World"
        }

# Configuring POST request endpoint.
# Command is parsed and handled/directed to handler
@app.route('/', methods=["POST"], content_types=["application/x-www-form-urlencoded"])
def index():

    # Parse the body for ease of use
    r = responseToDict(app.current_request.raw_body)
    headers = app.current_request.headers

    # Check validity of the request.
    if not validateRequest(headers, r):
        return {"Status": "Validation failed."}


    commandArray = r['text'].split()
    command = commandArray.pop(0)

    try:
        if command == "set":
            setHandler(commandArray)
            return {
            'response_type': "ephemeral",
            'text': "Set the event."
            }

        elif command == "get":
            eventType = commandArray[0]
            eventName = eventType + "-" + commandArray[1]
            resultDict = getEvent(eventName)
            return {
            'response_type': "ephemeral",
            'text': "`{}` Details:\n\n Date: {}\nRemaining: {} days!".format(eventName, resultDict[0], resultDict[1])
            }

        elif command == "get-all":

            stringResult = getAllHandler(commandArray)
            return {
            'response_type': "ephemeral",
            'text': "{}".format(stringResult)
            }

        elif command == "remove":
            eventName = "{}-{}".format(commandArray[0], commandArray[1])
            removeEvent(eventName)
            return {
            'response_type': "ephemeral",
            'text': "Removed the event."
            }
        else:
            return {
            'response_type': "ephemeral",
            'text': "Wrong usage of the command."
            }
    except:
        print("some stuff")
        return {
            'response_type': "ephemeral",
            'text': "Some problem occured. Please check your command."
        }


# Run at 10:00 am (UTC) every day.
@app.schedule(Cron(0, 10, '*', '*', '?', '*'))
def periodicCheck(event):
    allKeys = getAllKeys()
    for key in allKeys:
        handleEvent(key)


# Generic event is parsed and directed to relevant handlers.
def handleEvent(eventName):
    eventSplitted = eventName.split('-')

    eventType = eventSplitted[0]

    # discard @ or ! as a first character
    personName = eventSplitted[1][1:]
    personMention = convertToCorrectMention(personName)

    eventDict = getEvent(eventName)
    remainingDays = eventDict[1]
    totalTime = eventDict[2]


    if eventType == "birthday":
        birthdayHandler(personMention, personName, remainingDays)
    
    elif eventType == "anniversary":
        anniversaryHandler(personMention, personName, remainingDays, totalTime)

    elif eventType == "custom":
        eventMessage = "Not specified"
        if len(eventSplitted) == 3:
            eventMessage = eventSplitted[2]
        customHandler(eventMessage, personMention, personName, remainingDays)

# Handles birthday events.
def birthdayHandler(personMention, personName, remainingDays):
    if remainingDays == 0:
        sendRandomBirthdayToChannel('general', personMention)
    if remainingDays <= NOTIFY_TIME_LIMIT:
        dmEveryoneExcept("{} day(s) until {}'s birthday!".format(remainingDays, personMention), personName)

# Handles anniversary events.
def anniversaryHandler(personMention, personName, remainingDays, totalTime):
    if remainingDays == 0:
        sendRandomAnniversaryToChannel('general', personMention, totalTime)
    if remainingDays <= NOTIFY_TIME_LIMIT:
        dmEveryoneExcept("{} day(s) until {}'s anniversary! It will be {} year(s) since they joined!".format(remainingDays, personMention, totalTime), personName)

# Handles custom events.
def customHandler(eventMessage, personMention, personName, remainingDays):
    if remainingDays == 0:
        postToChannel('general', "`{}` is here {}!".format(eventMessage, personMention))
    elif remainingDays <= NOTIFY_TIME_LIMIT:
        dmEveryoneExcept("{} day(s) until {} `{}`!".format(remainingDays, personMention, eventMessage), personName)


# Sends private message to everyone except for the person given.
def dmEveryoneExcept(message, person):
    usersAndIds = allSlackUsers()
    for user in usersAndIds:
        if user[0] != person:
            sendDm(user[1], message)
        

# Sends randomly chosen birthday message to specified channel.
def sendRandomBirthdayToChannel(channel, personMention):
    messageList = [
        "Happy Birthday {}! Wishing you the best!".format(personMention),
        "Happy Birthday {}! Wishing you a happy age!".format(personMention),
        "Happy Birthday {}! Wishing you a healthy, happy life!".format(personMention),
    ]
    message = random.choice(messageList)
    return postToChannel('general', message)

# Sends randomly chosen anniversary message to specified channel.
def sendRandomAnniversaryToChannel(channel, personMention, totalTime):
    messageList = [
        "Today is the anniversary of {} joining! It has been {} years since they joined!".format(personMention, totalTime - 1),
        "Celebrating the anniversary of {} joining! It has been {} years!".format(personMention, totalTime - 1),
        "Congratulating {} for entering {}(th) year here!".format(personMention, totalTime),
    ]
    message = random.choice(messageList)
    return postToChannel('general', message)


# We want to run our event handlers when the project is deployed/redeployed.
allKeys = getAllKeys()
for key in allKeys:
    handleEvent(key)