from sleeper_ff_bot.utilities import get_draft_order, send_any_string, get_player_name, get_fun_fact, get_rule_changes, get_standings_string, get_scores_string, get_matchups_string, get_player_key,  get_player_stats, get_random_player, get_team_abbr, get_depth_chart, find_position
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
        if os.environ["WAITING_FOR_RESPONSE"] == "True":
            try:
                int(message['text'].lower())
                stat_response = True
            except:
                stat_response = False
            if stat_response == True:
                Utilities.get_player_key(message['text'],message['name'].lower(),1)
                os.environ["WAITING_FOR_RESPONSE"] = "False"
            elif len(message['text']) == 3:
                Utilities.get_player_key(message['text'],message['name'].lower(),1)
            if 'none' in message['text'].lower():
                bot.send(Utilities.send_any_string,"Sorry I failed you.")
                os.environ["WAITING_FOR_RESPONSE"] = "False"
        if '@bot' in message['text'].lower():
            if 'draft order' in message['text'].lower():
                bot.send(Utilities.get_draft_order)
            elif 'who' in message['text'].lower():
                if 'quarterback' in message['text'].lower() or ' qb ' in message['text'].lower() or 'passing' in message['text'].lower():
                    if 'best' in message['text'].lower() or 'most' in message['text'].lower():
                        best_any_flag = 'best'
                    else:
                        best_any_flag = 'any'
                    text = Utilities.get_random_player('qb',best_any_flag)
                if 'running back' in message['text'].lower() or ' rb ' in message['text'].lower() or 'rushing' in message['text'].lower():
                    if 'best' in message['text'].lower() or 'most' in message['text'].lower():
                        best_any_flag = 'best'
                    else:
                        best_any_flag = 'any'
                    text = Utilities.get_random_player('rb',best_any_flag)
                if 'wide receiver' in message['text'].lower() or ' wr ' in message['text'].lower() or 'receiving' in message['text'].lower():
                    if 'best' in message['text'].lower() or 'most' in message['text'].lower():
                        best_any_flag = 'best'
                    else:
                        best_any_flag = 'any'
                    text = Utilities.get_random_player('wr',best_any_flag)
                if 'tight end' in message['text'].lower() or ' te ' in message['text'].lower():
                    if 'best' in message['text'].lower() or 'most' in message['text'].lower():
                        best_any_flag = 'best'
                    else:
                        best_any_flag = 'any'
                    text = Utilities.get_random_player('te',best_any_flag)
                if 'defense' in message['text'].lower() or ' def ' in message['text'].lower():
                    text = Utilities.get_random_player('def', 'any')
                if 'kicker' in message['text'].lower() or ' k ' in message['text'].lower() or 'field goal' in message['text'].lower()  or 'extra point' in message['text'].lower()  or 'fg' in message['text'].lower()  or 'xp' in message['text'].lower():
                    if 'best' in message['text'].lower() or 'most' in message['text'].lower():
                        best_any_flag = 'best'
                    else:
                        best_any_flag = 'any'
                    text = Utilities.get_random_player('k',best_any_flag)

                bot.send(Utilities.send_any_string, text)
            elif 'fun fact' in message['text'].lower():
                bot.send(Utilities.get_fun_fact)
            elif 'rule changes' in message['text'].lower():
                bot.send(Utilities.get_rule_changes)
            elif 'standings' in message['text'].lower():
                bot.send(Utilities.get_standings_string, league_id)
            elif 'score update' in message['text'].lower():
                bot.send(Utilities.get_scores_string, league_id)
            elif 'matchups' in message['text'].lower():
                bot.send(Utilities.get_matchups_string, league_id)
            elif 'stats special' in message['text'].lower():
                text = message['text']
                text = text.replace("@bot","")
                text = text.replace("stats special", "")
                text = text.replace(" ","")
                text = text.lower()
                Utilities.get_player_key(text,message['name'].lower(),1)
            elif 'stats' in message['text'].lower():
                text = message['text']
                text = text.replace("@bot","")
                text = text.replace("stats", "")
                text = text.replace(" ","")
                text = text.lower()
                waiting = Utilities.get_player_key(text, message['name'].lower(),0)
                os.environ["WAITING_FOR_RESPONSE"] = waiting
            elif 'depth chart' in message['text'].lower():
                team_abbr = Utilities.get_team_abbr(message['text'].lower())
                position = Utilities.find_position(message['text'].lower())
                if position == "error" and team_abbr == "error":
                    bot.send(Utilities.send_any_string, 'I was unable to determine what team or position you are looking for.')
                elif position == "error":
                    bot.send(Utilities.send_any_string, 'I was unable to determine what position you are looking for.')
                elif team_abbr == "error":
                    bot.send(Utilities.send_any_string, 'I was unable to determine what team you are looking for.')
                else:
                    Utilities.get_depth_chart(team_abbr.strip(), position.strip())
            else:
                bot.send(Utilities.send_any_string, 'I am unsure.')

    return "ok",200

# Checks whether the message sender is a bot
def sender_is_bot(message):
	return message['sender_type'] == "bot"
