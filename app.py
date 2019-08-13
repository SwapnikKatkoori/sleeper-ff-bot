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


@app.route('/', methods=['POST'])
def webhook():
	# 'message' is an object that represents a single GroupMe message.
	message = request.get_json()

    if 'draft order' in message['text'].lower() and not sender_is_bot(message):
        bot.send(get_draft_order)

	return "ok", 200



# Checks whether the message sender is a bot
def sender_is_bot(message):
	return message['sender_type'] == "bot"
