from sleeper_ff_bot.bot import get_draft_order
from sleeper_ff_bot.group_me import GroupMe
from sleeper_ff_bot.slack import Slack
from sleeper_ff_bot.discord import Discord
import os
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from flask import Flask, request

app = Flask(__name__)

bot = None

bot_type = os.environ["BOT_TYPE"]
league_id = os.environ["LEAGUE_ID"]

# Check if the user specified the close game num. Default is 20.
try:
    close_num = os.environ["CLOSE_NUM"]
except:
    close_num = 20

if bot_type == "groupme":
    bot_id = os.environ["BOT_ID"]
    bot = GroupMe(bot_id)
elif bot_type == "slack":
    webhook = os.environ["SLACK_WEBHOOK"]
    bot = Slack(webhook)
elif bot_type == "discord":
    webhook = os.environ["DISCORD_WEBHOOK"]
    bot = Discord(webhook)

if os.environ["INIT_MESSAGE"] == "true":
    bot.send(get_welcome_string)  # inital message to send
# Called whenever the app's callback URL receives a POST request
# That'll happen every time a message is sent in the group
@app.route('/', methods=['POST'])
def webhook():
	# 'message' is an object that represents a single GroupMe message.
	message = request.get_json()



	return "ok", 200



# Checks whether the message sender is a bot
def sender_is_bot(message):
	return message['sender_type'] == "bot"
