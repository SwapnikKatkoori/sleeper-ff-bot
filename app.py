from sleeper_ff_bot.bot import get_draft_order, send_any_string, get_player_name, get_fun_fact, get_rule_changes, get_standings_string, get_scores_string, get_matchups_string, get_player_key,  get_player_stats
from sleeper_ff_bot.group_me import GroupMe
from sleeper_ff_bot.slack import Slack
from sleeper_ff_bot.discord import Discord
import os
import json
import time
import logging
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from flask import Flask, request


app = Flask(__name__)

bot = None

bot_type = os.environ["BOT_TYPE"]
league_id = os.environ["LEAGUE_ID"]


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
    if not sender_is_bot(message):
        time.sleep(3)
        logging.error(os.environ["WAITING_FOR_RESPONSE"])
        if os.environ["WAITING_FOR_RESPONSE"] == "True":
            try:
                int(message['text'].lower())
                stat_response = True
            except:
                stat_response = False
            if stat_response == True:
                get_player_key(message['text'],message['name'].lower(),1)
                os.environ["WAITING_FOR_RESPONSE"] = "False"
            elif len(message['text']) == 3:
                get_player_key(message['text'],message['name'].lower(),1)
            if 'none' in message['text'].lower():
                bot.send(send_any_string,"Sorry I failed you.")
                os.environ["WAITING_FOR_RESPONSE"] = "False"
        if '@bot' in message['text'].lower():
            if 'adam' in message['name'].lower():
                bot.send(send_any_string,'Fuck off Adam')
            elif 'draft order' in message['text'].lower():
                bot.send(get_draft_order)
            elif 'who' in message['text'].lower():
                bot.send(get_player_name)
            elif 'fun fact' in message['text'].lower():
                bot.send(get_fun_fact)
            elif 'rule changes' in message['text'].lower():
                bot.send(get_rule_changes)
            elif 'standings' in message['text'].lower():
                bot.send(get_standings_string, league_id)
            elif 'score update' in message['text'].lower():
                bot.send(get_scores_string, league_id)
            elif 'matchups' in message['text'].lower():
                bot.send(get_matchups_string, league_id)
            elif 'stats' in message['text'].lower():
                text = message['text']
                text = text.replace("@bot","")
                text = text.replace("stats", "")
                text = text.replace(" ","")
                text = text.lower()
                waiting = get_player_key(text, message['name'].lower(),0)
                logging.error(waiting)
                if waiting == True:
                    os.environ["WAITING_FOR_RESPONSE"] = "True"
                    
            else:
                bot.send(send_any_string, 'I am unsure.')

    return "ok",200

# Checks whether the message sender is a bot
def sender_is_bot(message):
	return message['sender_type'] == "bot"
