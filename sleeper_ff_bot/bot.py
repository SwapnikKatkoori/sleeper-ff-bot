import schedule
import os
from group_me import GroupMe
from slack import Slack
from discord import Discord
from sleeper_wrapper import League


def get_matchups(league_id, week):
	league = League(league_id)
	matchups = league.get_matchups(week)
	users = league.get_users()
	rosters = league.get_rosters()
	scoreboards = league.get_scoreboards(rosters, matchups, users)

	final_message_string = ""

	for matchup_id in scoreboards:
		matchup = scoreboards[matchup_id]
		matchup_string = "{} VS. {} \n".format(matchup[0][0], matchup[1][0])
		final_message_string += matchup_string

	return final_message_string
	
def get_standings(league_id, week):
	league = League(league_id)
	rosters = league.get_rosters()
	users = league.get_users()
	standings = league.get_standings(rosters,users)

	

def main():
	bot = None
	bot_type = os.environ["BOT_TYPE"]
	bot_id = os.environ["BOT_ID"]

	if bot_type == "groupme": 
		bot = GroupMe(bot_id)
	elif bot_type == "slack":
		bot = Slack(bot_id)
	else:
		bot = Discord(bot_id)

	bot.send_message(get_matchups(355526480094113792, 11))


main()