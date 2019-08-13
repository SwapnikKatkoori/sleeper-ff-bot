from sleeper_ff_bot.bot import get_draft_order
import os
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from flask import Flask, request

app = Flask(__name__)
bot_id = "REPLACE THIS WITH YOUR BOT ID ONCE BOT IS ADDED TO THE CHAT"

# Called whenever the app's callback URL receives a POST request
# That'll happen every time a message is sent in the group
@app.route('/', methods=['POST'])
def webhook():
	# 'message' is an object that represents a single GroupMe message.
	message = request.get_json()

	# TODO: Your bot's logic here

	return "ok", 200



# Checks whether the message sender is a bot
def sender_is_bot(message):
	return message['sender_type'] == "bot"
