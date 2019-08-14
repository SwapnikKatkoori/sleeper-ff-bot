from sleeper_ff_bot.bot import get_draft_order, send_any_string, get_player_name, get_fun_fact, get_rule_changes
from sleeper_ff_bot.group_me import GroupMe
from sleeper_ff_bot.slack import Slack
from sleeper_ff_bot.discord import Discord
import os
import json
import time
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
    if '@bot' in message['text'].lower()  and not sender_is_bot(message):
        if 'adam' in message['name'].lower():
            time.sleep(2)
            bot.send(send_any_string,'Fuck off Adam')
        elif 'draft order' in message['text'].lower():
            time.sleep(2)
            bot.send(get_draft_order)
        elif 'who' in message['text'].lower():
            time.sleep(2)
            bot.send(get_player_name)
        elif 'fun fact' in message['text'].lower():
            time.sleep(2)
            bot.send(get_fun_fact)
        elif 'rule changes' in message['text'].lower():
            time.sleep(2)
            bot.send(get_rule_changes)
        else:
            bot.send(send_any_string, 'I am unsure.')

    return "ok",200

# Checks whether the message sender is a bot
def sender_is_bot(message):
	return message['sender_type'] == "bot"
