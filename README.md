Birthday slackbot implementation...
# Birthday - Anniversary - Custom Reminder Slackbot
This slackbot is written in python, using `AWS Chalice` to configure AWS Lambda and API Gateway automatically. Project uses Upstash Redis for database.

## Docs
- ### [What the Bot Does](#what-this-bot-does)
- ### [Configuring Upstash](#configure-upstash)
- ### [Configuring Slack - 1](#configure-slack-bot-1)
- ### [Configuring AWS Credentials](#configure-aws-credentials)
- ### [Deployment using Chalice](#deploy-on-chalice)
    - #### [Running Locally](#run-locally)
    - #### [Deploying to AWS](#deploy-to-aws)
- ### [Configuring Slack - 2](#configure-slack-bot-2)


### What The Bot Does
<a id="what-this-bot-does"></a>
<!-- You can set birthdays, anniversaries and custom events to be automatically reminded of them. Threshold value can be configured so that an approaching event can be reminded before the actual date comes.
After setting the events, serverless functions run periodically to see whether there are events approaching. -->

* Commands:
    * set:
        * `/event set birthday <YYYY-MM-DD> <user>` :
            * Sets the birthday of the user.
        * `/event set anniversary <YYYY-MM-DD> <user>` :
            * Sets the anniversary for the user, when they started working there.
        * `/event set custom <YYYY-MM-DD> <user> <any kind of message with whitespaces>` :
            * Sets a custom reminder using the message provided.
    * get-all:
        * `/event get-all birthday` :
            * Shows all birthdays that are set.
        * `/event get-all anniversary` :
            * Shows all anniversaries that are set.
        * `/event get-all custom` :
            * Shows all custom events that are set.
    * get:
        * `/event get birthday <user>` :
            * Shows the birthday details of the user.
        * `/event get anniversary <user>` :
            * Shows the anniversary details for the user, when they started working there.
        * `/event get custom <event_name>(can be found with get-all)` :
            * Shows the custom event details using the message provided.
    * remove:
        * `/event remove birthday <user>` :
            * Removes the birthday of the user.
        * `/event remove anniversary <user>` :
            * Removes the anniversary for the user, when they started working there.
        * `/event remove custom <event_name>(can be found with get-all)` :
            * Removes the custom event using the message provided.

* If a single user is mentioned while setting the event:
    * When the actual event date comes, mentions them in the general channel with a celebratory message.
    * Sends a private message to everyone except the mentioned user before the actual date comes. 
#### Add some SS here.

### Configuring Upstash
<a id="configure-upstash"></a>
1. Go to the [Upstash Console](https://console.upstash.com/) and create a new database

    #### Upstash environment
    Find the variables in the database details page in Upstash Console:
    `UPSTASH_REDIS_REST_URL` and `UPSTASH_REDIS_REST_TOKEN` 

    (These will be the env variables for chalice deployment) 




### Configuring Slack - 1
<a id="configure-slack-bot-1"></a>
 May need to revise permissions and what not

1. Go to [Slack API Apps Page](https://api.slack.com/apps):
    * Create new App
        * From Scratch
        * Name your app & pick a workspace 
    * Go to Oauth & Permissions
        * Add the following scopes
            * channels:read
            * chat:write
            * chat:write.public
            * commands
            * groups:read
            * users:read
        * Install App to workspace
            * Basic Information --> Install Your App --> Install To Workspace
2. Note the variables (These will be the env variables for vercel deployment) : 
    * `SLACK_SIGNING_SECRET`:
        * Go to Basic Information
            * App Credentials --> Signing Secret
    * `SLACK_BOT_TOKEN`:
        * Go to OAuth & Permissions
            * Bot User OAuth Token




### Configuring AWS Credentials
<a id="configure-aws-credentials"></a>

(Taken from [Official Chalice Repo](https://github.com/aws/chalice). You can refer for more info there.)
```
$ mkdir ~/.aws
$ cat >> ~/.aws/config
[default]
aws_access_key_id=YOUR_ACCESS_KEY_HERE
aws_secret_access_key=YOUR_SECRET_ACCESS_KEY
region=YOUR_REGION (such as us-west-2, us-west-1, etc)
```

### Deployment Using Chalice
<a id="deploy-on-chalice"></a>
* Install `chalice` if not installed:

    `
    pip install chalice
    `

* Create chalice project by running:

    `
    chalice new-project <project-name>
    `

* Configure `config.json` file inside the `.chalice` directory by adding:
    ```
    "environment_variables": {
        "UPSTASH_REST_URL": <UPSTASH_REDIS_REST_URL>,
        "UPSTASH_TOKEN": <UPSTASH_REDIS_REST_TOKEN>,
        "SLACK_BOT_TOKEN": <SLACK_BOT_TOKEN>,
        "SLACK_SIGNING_SECRET": <SLACK_SIGNING_SECRET>,
        "NOTIFY_TIME_LIMIT": "<amount of days before getting notifications for events>"
    }
    ```
    ### Running Locally
    <a id="run-locally"></a>

    To run locally: 
        
        chalice local

    Using services such as ngrok, tunnel the relevant port, then use the public domain for Slack.
    ### Deploy to AWS Lambda and Gateway
    <a id="deploy-to-aws"></a>

        chalice deploy

    Use the `REST API URL` for Slack.
### Configuring Slack - 2
<a id="configure-slack-bot-2"></a>

* After deployment, you can use the provided `REST API URL`.

1. Go to [Slack API Apps Page](https://api.slack.com/apps) and choose relevant app:
    * Go to Slash Commands:
        * Create New Command:
            * Command : `event`
            * Request URL : `<REST_API_URL>`
            * Configure the rest however you like.

After these changes, Slack may require reinstalling of the app.



<!-- # Link to relevant blogpost. -->