import requests
from bot_interface import BotInterface


class Slack(BotInterface):
    def __init__(self, webhook):
        self.webhook = webhook

    def send_message(self, message):
        requests.post(self.webhook, json={"text": message})
