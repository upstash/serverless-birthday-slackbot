from chalicelib.utils import sendPostRequest, getRealName, allSlackUsers, diffWithTodayFromString, totalTimefromString
import os

UPSTASH_REST_URL = os.getenv("UPSTASH_REST_URL")
UPSTASH_TOKEN = os.getenv("UPSTASH_TOKEN")

# Posts to Upstash Rest Url with parameters given.
def postToUpstash(parameters):
    requestURL = UPSTASH_REST_URL
    for parameter in parameters:
        requestURL += ("/" + parameter)
    
    resultDict = sendPostRequest(requestURL, UPSTASH_TOKEN)
    return resultDict['result']


# Sets key-value pair for the event with given parameters.
def setEvent(parameterArray):

    postQueryParameters = ['SET']

    for parameter in parameterArray:
        parameter = parameter.split()
        for subparameter in parameter:
            postQueryParameters.append(subparameter)

    resultDict = postToUpstash(postQueryParameters)

    return resultDict


# Returns event details from the event given.
def getEvent(eventName):
    postQueryParameters = ['GET', eventName]
    date = postToUpstash(postQueryParameters)
    
    timeDiff = diffWithTodayFromString(date)
    totalTime = totalTimefromString(date)
    mergedDict = [date, timeDiff, totalTime]
    return mergedDict

# Fetches all keys (events) from the database
def getAllKeys():
    return postToUpstash(['KEYS', '*'])
    
# Deletes given event from the database.
def removeEvent(eventName):
    postQueryParameters = ['DEL', eventName]
    resultDict = postToUpstash(postQueryParameters)
    return resultDict


# Handles set request by parsing and configuring setEvent function parameters.
def setHandler(commandArray):
    eventType = commandArray.pop(0)
    date = commandArray.pop(0)
    user = commandArray.pop(0)

    if eventType == "birthday":
        listName = "birthday-" + user
        return setEvent( [listName, date] )

    elif eventType == "anniversary":
        listName = "anniversary-" + user
        return setEvent( [listName, date] )

    elif eventType == "custom":
        message = ""
        for string in commandArray:
            message += string + "_"

        listName = "custom-" + user + "-" + message
        user = commandArray[1]
        return setEvent( [listName, date] )  
    else:
        return

# Handles get-all requests.
def getAllHandler(commandArray):
    filterParameter = None
    if len(commandArray) == 1:
        filterParameter = commandArray[0]

    allKeys = getAllKeys()
    birthdays = []
    anniversaries = []
    customs = []

    slackUsers = allSlackUsers()

    stringResult = "\n"
    for key in allKeys:
        if key[0] == 'b':
            birthdays.append(key)
        elif key[0] == 'a':
            anniversaries.append(key)
        elif key[0] == 'c':
            customs.append(key)

    if filterParameter is None or filterParameter == "birthday":
        stringResult += "Birthdays:\n"
        for bday in birthdays:
            tag = bday.split('-')[1]
            username = tag[1:]
            realName = getRealName(slackUsers, username)
            details = getEvent(bday)

            stringResult += "`{}` ({}): {} - `{} days` remaining!\n".format(tag, realName, details[0], details[1])

    if filterParameter is None or filterParameter == "anniversary":
        stringResult += "\nAnniversaries:\n"
        for ann in anniversaries:
            tag = ann.split('-')[1]
            username = tag[1:]
            realName = getRealName(slackUsers, username)
            details = getEvent(ann)
            
            stringResult += "`{}` ({}): {} - `{} days` remaining!\n".format(tag, realName, details[0], details[1])
        
    if filterParameter is None or filterParameter == "custom":
        stringResult += "\nCustom Reminders:\n"
        for cstm in customs:
            splitted = cstm.split('-')
            username = splitted[2]
            realName = getRealName(slackUsers, username)
            details = getEvent(cstm)
            
            stringResult += "`{}-{}` ({}): {}\n".format(splitted[1], splitted[2], getRealName(slackUsers, username), details[0])

    return stringResult