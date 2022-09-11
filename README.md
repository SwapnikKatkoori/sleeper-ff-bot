![Version](https://img.shields.io/badge/Version-v0.0.3-blue)
[![Build Status](https://travis-ci.org/SwapnikKatkoori/sleeper-ff-bot.svg?branch=master)](https://travis-ci.org/SwapnikKatkoori/sleeper-ff-bot)
![Version](https://img.shields.io/badge/license-MIT-pink)
![GitHub issues](https://img.shields.io/github/issues/cyrusfarsoudi/sleeper-ff-bot)

This project was forked from https://github.com/SwapnikKatkoori/sleeper-ff-bot. Updates include:
- Removed non-Discord functionality (GroupMe and Slack)
- Fixed dates to work for 2022 season
- Scoring settings reflect SoCal858 settings
  - 6pt passing td's
  - 2pt 40yd td bonus
  - 3pt per fgm, .1pt per fgm yds over 30
- Updated Discord message contents and formatting
- Moved sleeper-api-wrapper package into this repository

<h1 align="center">Welcome to sleeper-ff-bot 👋</h1>
<p>
</p>

A Discord Bot for Sleeper fantasy leagues. It sends messages on the schedule below.

## Current Schedule
- Thursday: 
     - 4pm PT Matchups for the week.
- Friday:
     - 9am PT Scores.
- Sunday:
     - 4pm PT Close games.
- Monday: 
     - 9am PT Scores.
     - 12pm PT Miracle Monday! Displays the close games remaining.
- Tuesday: 
     - 8am PT league standing.
     - 8:01am PT Week Highlights.


## Setup
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
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/cyrusfarsoudi/sleeper-ff-bot/)
- Step 3: Choose an app name

- Step 4:

For Discord fill out the following (The BOT_TYPE needs to be discord):

<img src="/Media/discord/enviornment_setup.jpeg" width="400"/>

You can leave everything else as their default values.

- Step 5: Click "Deploy app".
- Step 6: After the deployment process is done, click "Manage app" and go to the "Resources" tab.
- Step 7: Click the pencil icon next to worker and toggle it to the on position, and click "confirm".
<img src="/Media/deployment/toggle.jpeg" width="400"/>

And you are all done! The bot should now be deployed an you should get a welcome message.

## Original Author

👤 **Swapnik Katkoori**

## License 
This project is licensed under the terms of the MIT license.

