![Version](https://img.shields.io/badge/Version-v0.0.3-blue)
[![Build Status](https://travis-ci.org/SwapnikKatkoori/sleeper-ff-bot.svg?branch=master)](https://travis-ci.org/SwapnikKatkoori/sleeper-ff-bot)
![Version](https://img.shields.io/badge/license-MIT-pink)
![GitHub issues](https://img.shields.io/github/issues/SwapnikKatkoori/sleeper-ff-bot)

This project was inspired by https://github.com/dtcarls/ff_bot.
<h1 align="center">Welcome to sleeper-ff-bot 👋</h1>
<p>
</p>

A GroupMe/Slack/Discord Bot for Sleeper fantasy leagues. It sends messages on the schedule below.

## Current Schedule
- Thursday: 
     - 7pm ET Matchups for the week.
- Friday:
     - 12pm ET Scores (Only does half ppr scores for now)
- Sunday:
     - 7pm ET Close games. 
- Monday: 
     - 12pm ET Scores (Only does half ppr scores for now)
     - 3pm ET Miracle Monday! Displays the close games with the number of playes remaining for each roster. 
- Tuesday: 
     - 11am ET league standing.
     - 11:01am ET Highest scoring team, lowest scoring team, most points left on the bench, and teams that started players that scored negative.


## Setup
1. [ GroupMe ](#groupme) 
2. [ Slack ](#slack)
3. [ Discord ](#discord)

<a name="groupme"></a>
### GroupMe
- Step 1: Go to https://dev.groupme.com/ and log in using your groupme account.
- Step 2: Click the bots tab.
- Step 3: Click the "Create Bot" button.
- Step 4: Choose the groupchat that the bot will be in and the Name of the bot and click "Submit". Everything else can be left empty.
- Step 5: Remember the bot_id as you will need it in the next step.
<img src="/Media/groupme/groupme_botid.jpeg" width="400"/>

- Step 6: Follow directions to launch the bot on a Heroku server [here](#heroku)

<a name="slack"></a>
### Slack
- Step 1: Go to https://api.slack.com/apps and click "Create New App".
- Step 2: Choose the name you want to call the FF bot, choose your workspace, and click "Create App".
- Step 3: Click the "Incoming Webhooks" button.
<img src="/Media/Slack/incoming_webhooks.jpeg" width="400"/>

- Step 4: Click the "Off" toggle button so it says "On".
<img src="/Media/Slack/toggle.jpeg" width="400"/>

- Step 5: Click the "Add New Webhook to Workspace" button.
<img src="/Media/Slack/add_new_webhook.jpeg" width="400"/>

- Step 6: Select the channel to post to and click "Install".
- Step 7: Remember the webhook that appears under the "Webhook URL" section as you will need it for the next step.
<img src="/Media/Slack/copy_webhook.jpeg" width="400"/>

- Step 8: Follow directions to launch the bot on a Heroku server [here](#heroku)

<a name="discord"></a>
### Discord
- Step 1: Go to the Discord server that you want to add the bot to.
- Step 2: Go to "Server Settings".
<img src="/Media/discord/server_settings.jpeg" width="400"/>

- Step 3: Click "Webhooks" in the side menu.
- Step 4: Click "Create Webhook" and fill out the information.
- Step 5: Copy the "Webhook Url" as you will need it in step 7.
<img src="/Media/discord/webhook.jpeg" width="400"/>

- Step 6: Click "Save".

- Step 7: Follow directions to launch the bot on a Heroku server [here](#heroku)

<a name="heroku"></a>
## Deploy the bot
- Step 1: Go to https://signup.heroku.com/login and create a Heroku account.
- Step 2: Click this button to deploy the Bot:
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/cyrusfarsoudi/sleeper-ff-bot/2022-fixes)
- Step 3: Choose an app name

- Step 4:

For Groupme fill out the following (The BOT_TYPE needs to be groupme):

<img src="/Media/groupme/enviornment_setup.jpeg" width="400"/>

For Slack fill out the following (The BOT_TYPE needs to be slack):

<img src="/Media/Slack/enviornment_setup.jpeg" width="400"/>

For Discord fill out the following (The BOT_TYPE needs to be discord):

<img src="/Media/discord/enviornment_setup.jpeg" width="400"/>

You can leave everything else as their default values.

- Step 5: Click "Deploy app".
- Step 6: After the deployment process is done, click "Manage app" and go to the "Resources" tab.
- Step 7: Click the pencil icon next to worker and toggle it to the on position, and click "confirm".
<img src="/Media/deployment/toggle.jpeg" width="400"/>

And you are all done! The bot should now be deployed an you should get a welcome message.

## Author

👤 **Swapnik Katkoori**

## License 
This project is licensed under the terms of the MIT license.

