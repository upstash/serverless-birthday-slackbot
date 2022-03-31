from urllib import request
import urllib
from urllib.parse import parse_qsl
import json
import os
import hmac
import hashlib
from datetime import date


SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")

# Returns real name of the slack user.
def getRealName(slackUsers, username):
    for user in slackUsers:
        if user[0] == username:
            return user[2]
    return "Nameless"

# Returns all slack users in the workspace.
def allSlackUsers():
    resultDict = sendPostRequest("https://slack.com/api/users.list", SLACK_BOT_TOKEN)
    members = resultDict['members']
    
    userMembers = []
    for member in members:
        if not member['deleted'] and not member['is_bot']:
            userMembers.append([member['name'], member['id'], member['real_name']])

    return userMembers

# Returns the id of the given channel.
def channelNameToId(channelName) :
    resultDict = sendPostRequest("https://slack.com/api/conversations.list", SLACK_BOT_TOKEN)
    for channel in resultDict['channels']:
        if (channel['name'] == channelName):
            return channel['id']
    return None

# Posts to given slack channelId with given message.  
def postToSlack(channelId, messageText):
    data = {
        "channel": channelId,
        "text": messageText
    }
    data = json.dumps(data)
    data = str(data)
    data = data.encode('utf-8')
    resultDict = sendPostRequest("https://slack.com/api/chat.postMessage", SLACK_BOT_TOKEN, data)
    return resultDict

# Posts to a slack channel.
def postToChannel(channel, messageText):
    channelId = channelNameToId(channel)
    return postToSlack(channelId, messageText)

# Sends a private message to a user with userId.
def sendDm(userId, messageText):
    return postToSlack(userId, messageText)

# Sends generic post request and returns the result.
def sendPostRequest(requestURL, bearerToken, data={}):
    req = request.Request(requestURL, method="POST", data=data)
    req.add_header("Authorization", "Bearer {}".format(bearerToken))
    req.add_header("Content-Type", "application/json; charset=utf-8")
    
    r = request.urlopen(req)
    resultDict = json.loads(r.read().decode()) 
    return resultDict

# Parses and converts the res to dict.
def responseToDict(res):
    return dict(parse_qsl(res.decode()))


# Dates are given as: YYYY-MM-DD
# Returns difference between current day and the anniversary.
def diffWithTodayFromString(dateString):
    now = date.today()
    currentYear = now.year

    dateTokens = dateString.split("-")
    month = int(dateTokens[1])
    day = int(dateTokens[2])

    if now > date(currentYear, month, day):
        return (date((currentYear + 1), month, day) - now).days
    return (date(currentYear, month, day) - now).days


# Dates are given as: YYYY-MM-DD
# Calculates the total time that has passed until current date.
def totalTimefromString(dateString):
    now = date.today()

    dateTokens = dateString.split("-")
    year = int(dateTokens[0])
    month = int(dateTokens[1])
    day = int(dateTokens[2])

    then = date(year, month, day)

    years = now.year - then.year
    return years + 1

# Validate requests coming to endpoint.
# Hashes request body with timestamp and signing secret.
# Then, compares that hash with slack signature.
def validateRequest(header, body):

    bodyAsString = urllib.parse.urlencode(body)

    timestamp = header['x-slack-request-timestamp']
    slackSignature = header['x-slack-signature'] 
    baseString = "v0:{}:{}".format(timestamp, bodyAsString)

    h =  hmac.new(SLACK_SIGNING_SECRET.encode(), baseString.encode(), hashlib.sha256)
    hashResult = h.hexdigest()
    mySignature = "v0=" + hashResult

    return mySignature == slackSignature

# Converts given name to mention string.
def convertToCorrectMention(name):
    if name == "channel" or name == "here" or name == "everyone":
        return "<!{}>".format(name)
    else:
        return "<@{}>".format(name)