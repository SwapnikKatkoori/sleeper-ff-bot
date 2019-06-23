import schedule
import os
from .group_me import GroupMe
from .slack import Slack
from .discord import Discord
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

	final_message_string = "STANDINGS \n{0:<8} {1:<8} {2:<8} {3:<15}\n".format("rank", "team", "wins", "points")

	for i,standing in enumerate(standings):
		team = standing[0]
		if team is None:
			team = "Team NA"
		string_to_add = "{0:<8} {1:<8} {2:<8} {3:<8}\n".format(i+1 , team, standing[1] , standing[2])
		final_message_string += string_to_add
	print(final_message_string)
	return final_message_string
	
def get_close_games( league_id, week, close_num):
	league = League(league_id)
	matchups = league.get_matchups(week)
	users = league.get_users()
	rosters = league.get_rosters()
	scoreboards = league.get_scoreboards(rosters, matchups, users)
	close_games = league.get_close_games(scoreboards, close_num)

	final_message_string = "CLOSE GAMES \n"
	for i,matchup_id in enumerate(close_games):
		matchup = close_games[matchup_id]
		string_to_add = "Matchup {}\n{:<8} {:<8.2f}\n{:<8} {:<8.2f}\n\n".format(i+1, matchup[0][0], matchup[0][1], matchup[1][0], matchup[1][1])
		final_message_string += string_to_add
	return final_message_string

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

	bot.send_message(get_close_games(355526480094113792, 11, 20))


main()