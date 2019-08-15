import schedule
import time
import os
import pendulum
import logging
import random
import gspread
import json
from prettytable import PrettyTable
from apscheduler.schedulers.blocking import BlockingScheduler
from oauth2client.service_account import ServiceAccountCredentials
from people import names
from phrases import phrases
from rule_changes import changes
from group_me import GroupMe
from slack import Slack
from discord import Discord
from sleeper_wrapper import League, Stats, Players
from constants import STARTING_MONTH, STARTING_YEAR, STARTING_DAY, START_DATE_STRING, OFF_STARTING_YEAR, OFF_STARTING_MONTH, OFF_STARTING_DAY, OFF_START_DATE_STRING, PRE_STARTING_YEAR, PRE_STARTING_MONTH, PRE_STARTING_DAY, PRE_START_DATE_STRING

"""
These are all of the utility functions.
"""

def get_fun_fact():
    text = [random.choice(phrases)]
    return '\n'.join(text)

def get_rule_changes():
    text = "Rule changes taking effect this season: \n\n"
    for i in changes:
        text += i +"\n\n"
    return text

def get_player_name():
    text = [random.choice(names)]
    return '\n'.join(text)

def get_td_predict():
    text = "I predict the person who scores the most touchdowns this week will be..."
    return text

def get_high_predict():
    text = "I predict the person who scores the most points this week will be..."
    return text

def get_low_predict():
    text = "I predict the person who scores the fewest points this week will be..."
    return text

def get_champ_predict():
    text = "I predict the champion this season will be..."
    return text

def get_spoob_predict():
    text = "I predict the spooby this season will be..."
    return text

def get_draft_order():
    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds' + ' ' +'https://www.googleapis.com/auth/drive']
    json_creds = os.environ["KEY"]
    #logging.error(json_creds)
    creds_dict = json.loads(json_creds)
    #logging.error(creds_dict)
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\\\n", "\n")
    #logging.error(creds_dict)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)

    # Find a workbook by url and open the first sheet
    sh = client.open_by_url("https://docs.google.com/spreadsheets/d/1ZFv0u8KYoXdoKMhjloK6EhIJlmzZsn91BidnGHwkRT4/edit#gid=0")
    #logging.error(sh)
    sheet = sh.sheet1

    # Extract and print all of the values
    draft_order_data = sheet.get_all_records()

    final_string = "\nCurrent Draft Order\n\n"
    data = json.dumps(draft_order_data)
    data_clean = json.loads(data)
    #draft_order_data = json.loads(draft_order_data_string)
    for i in data_clean:
        user_name = i["Name"]
        draft_slot = i["Draft Slot"]
        account_balance = i["Account"]
        final_string += "{} - {} ({})\n".format(draft_slot, user_name, account_balance)
    return final_string

def get_league_scoreboards(league_id, week):
    """
    Returns the scoreboards from the specified sleeper league.
    :param league_id: Int league_id
    :param week: Int week to get the scoreboards of
    :return: dictionary of the scoreboards; https://github.com/SwapnikKatkoori/sleeper-api-wrapper#get_scoreboards
    """
    league = League(league_id)
    matchups = league.get_matchups(week)
    users = league.get_users()
    rosters = league.get_rosters()
    scoreboards = league.get_scoreboards(rosters, matchups, users)
    return scoreboards


def get_highest_score(league_id):
    """
    Gets the highest score of the week
    :param league_id: Int league_id
    :return: List [score, team_name]
    """
    week = get_current_week()
    scoreboards = get_league_scoreboards(league_id, week)
    max_score = [0, None]

    for matchup_id in scoreboards:
        matchup = scoreboards[matchup_id]
        # check both teams in the matchup to see if they have the highest score in the league
        if float(matchup[0][1]) > max_score[0]:
            score = matchup[0][1]
            team_name = matchup[0][0]
            max_score[0] = score
            max_score[1] = team_name
        if float(matchup[1][1]) > max_score[0]:
            score = matchup[1][1]
            team_name = matchup[1][0]
            max_score[0] = score
            max_score[1] = team_name
    return max_score


def get_lowest_score(league_id):
    """
    Gets the lowest score of the week
    :param league_id: Int league_id
    :return: List[score, team_name]
    """
    week = get_current_week()
    scoreboards = get_league_scoreboards(league_id, week)
    min_score = [999, None]

    for matchup_id in scoreboards:
        matchup = scoreboards[matchup_id]
        # check both teams in the matchup to see if they have the lowest score in the league
        if float(matchup[0][1]) < min_score[0]:
            score = matchup[0][1]
            team_name = matchup[0][0]
            min_score[0] = score
            min_score[1] = team_name
        if float(matchup[1][1]) < min_score[0]:
            score = matchup[1][1]
            team_name = matchup[1][0]
            min_score[0] = score
            min_score[1] = team_name
    return min_score

def get_player_key(search_name, requestor):
    players = Players().get_all_players()

    found_players = []
    for k in players:
        data = json.dumps(k)
        player = json.load(data)
        if player["search_full_name"] == search_name:
            found_players.append((player, player['full_name'], player['position'], player['team'], [requestor]))
        if len(found_players) > 1:
            text = "which Player are you asking for?\n"
            for p in found_players:
                text += "{}. {} ({} - {})".format(p[0], p[1], p[2], p[3])
            bot.send(send_any_string, text)
            return found_players
        elif len(found_players) == 1:
            get_player_stats(found_players[0])


def get_player_stats(player_key):
    players = Players().get_all_players()
    data = json.dumps(players)
    players_json = json.loads(data)

    for k in players_json:
        if k == player_key:
            text = "Stats for {} here.".format(k["full_name"])
    bot.send(send_any_string, text)


def make_roster_dict(starters_list, bench_list):
    """
    Takes in a teams starter list and bench list and makes a dictionary with positions.
    :param starters_list: List of a teams starters
    :param bench_list: List of a teams bench players
    :return: {starters:{position: []} , bench:{ position: []} }
    """
    week = get_current_week()
    players = Players().get_all_players()
    stats = Stats()
    week_stats = stats.get_week_stats("regular", STARTING_YEAR, week)

    roster_dict = {"starters": {}, "bench": {}}
    for player_id in starters_list:
        player = players[player_id]
        player_position = player["position"]
        player_name = player["first_name"] + " " + player["last_name"]
        try:
            player_std_score = week_stats[player_id]["pts_std"]
        except KeyError:
            player_std_score = None

        player_and_score_tup = (player_name, player_std_score)
        if player_position not in roster_dict["starters"]:
            roster_dict["starters"][player_position] = [player_and_score_tup]
        else:
            roster_dict["starters"][player_position].append(player_and_score_tup)

    for player_id in bench_list:
        player = players[player_id]
        player_position = player["position"]
        player_name = player["first_name"] + " " + player["last_name"]

        try:
            player_std_score = week_stats[player_id]["pts_std"]
        except KeyError:
            player_std_score = None

        player_and_score_tup = (player_name, player_std_score)
        if player_position not in roster_dict["bench"]:
            roster_dict["bench"][player_position] = [player_and_score_tup]
        else:
            roster_dict["bench"][player_position].append(player_and_score_tup)

    return roster_dict


def get_highest_bench_points(bench_points):
    """
    Returns a tuple of the team with the highest scoring bench
    :param bench_points: List [(team_name, std_points)]
    :return: Tuple (team_name, std_points) of the team with most std_points
    """
    max_tup = ("team_name", 0)
    for tup in bench_points:
        if tup[1] > max_tup[1]:
            max_tup = tup
    return max_tup


def map_users_to_team_name(users):
    """
    Maps user_id to team_name
    :param users:  https://docs.sleeper.app/#getting-users-in-a-league
    :return: Dict {user_id:team_name}
    """
    users_dict = {}

    # Maps the user_id to team name for easy lookup
    for user in users:
        try:
            users_dict[user["user_id"]] = user["metadata"]["team_name"]
        except:
            users_dict[user["user_id"]] = user["display_name"]
    return users_dict


def map_roster_id_to_owner_id(league_id):
    """

    :return: Dict {roster_id: owner_id, ...}
    """
    league = League(league_id)
    rosters = league.get_rosters()
    result_dict = {}
    for roster in rosters:
        roster_id = roster["roster_id"]
        owner_id = roster["owner_id"]
        result_dict[roster_id] = owner_id

    return result_dict


def get_bench_points(league_id):
    """

    :param league_id: Int league_id
    :return: List [(team_name, score), ...]
    """
    week = get_current_week()

    league = League(league_id)
    users = league.get_users()
    matchups = league.get_matchups(week)

    stats = Stats()
    # WEEK STATS NEED TO BE FIXED
    week_stats = stats.get_week_stats("regular", STARTING_YEAR, week)

    owner_id_to_team_dict = map_users_to_team_name(users)
    roster_id_to_owner_id_dict = map_roster_id_to_owner_id(league_id)
    result_list = []

    for matchup in matchups:
        starters = matchup["starters"]
        all_players = matchup["players"]
        bench = set(all_players) - set(starters)

        std_points = 0
        for player in bench:
            try:
                std_points += week_stats[str(player)]["pts_std"]
            except:
                continue
        owner_id = roster_id_to_owner_id_dict[matchup["roster_id"]]
        if owner_id is None:
            team_name = "Team name not available"
        else:
            team_name = owner_id_to_team_dict[owner_id]
        result_list.append((team_name, std_points))

    return result_list


def get_negative_starters(league_id):
    """
    Finds all of the players that scores negative points in standard and
    :param league_id: Int league_id
    :return: Dict {"owner_name":[("player_name", std_score), ...], "owner_name":...}
    """
    week = get_current_week()

    league = League(league_id)
    users = league.get_users()
    matchups = league.get_matchups(week)

    stats = Stats()
    # WEEK STATS NEED TO BE FIXED
    week_stats = stats.get_week_stats("regular", STARTING_YEAR, week)

    players = Players()
    players_dict = players.get_all_players()
    owner_id_to_team_dict = map_users_to_team_name(users)
    roster_id_to_owner_id_dict = map_roster_id_to_owner_id(league_id)

    result_dict = {}

    for i, matchup in enumerate(matchups):
        starters = matchup["starters"]
        negative_players = []
        for starter_id in starters:
            try:
                std_pts = week_stats[str(starter_id)]["pts_std"]
            except KeyError:
                std_pts = 0
            if std_pts < 0:
                player_info = players_dict[starter_id]
                player_name = "{} {}".format(player_info["first_name"], player_info["last_name"])
                negative_players.append((player_name, std_pts))

        if len(negative_players) > 0:
            owner_id = roster_id_to_owner_id_dict[matchup["roster_id"]]

            if owner_id is None:
                team_name = "Team name not available" + str(i)
            else:
                team_name = owner_id_to_team_dict[owner_id]
            result_dict[team_name] = negative_players
    return result_dict


def check_starters_and_bench(lineup_dict):
    """

    :param lineup_dict: A dict returned by make_roster_dict
    :return:
    """
    for key in lineup_dict:
        pass


def get_current_week():
    """
    Gets the current week.
    :return: Int current week
    """
    today = pendulum.today()
    starting_week = pendulum.datetime(STARTING_YEAR, STARTING_MONTH, STARTING_DAY)
    week = today.diff(starting_week).in_weeks()
    return week


"""
These are all of the functions that create the final strings to send.
"""


def get_welcome_string():
    """
    Creates and returns the welcome message
    :return: String welcome message
    """
    welcome_message = "👋 Hello, I am Sleeper Bot! \n\nThe bot schedule for the {} ff season can be found here: ".format(
        STARTING_YEAR)
    welcome_message += "https://github.com/AlexHawkins1/sleeper-ff-bot#current-schedule \n\n"
    welcome_message += "Any feature requests, contributions, or issues for the bot can be added here: " \
                       "https://github.com/AlexHawkins1/sleeper-ff-bot \n\n"

    return welcome_message


def send_any_string(string_to_send):
    """
    Send any string to the bot.
    :param string_to_send: The string to send a bot
    :return: string to send
    """
    return string_to_send


def get_matchups_string(league_id):
    """
    Creates and returns a message of the current week's matchups.
    :param league_id: Int league_id
    :return: string message of the current week mathchups.
    """
    week = get_current_week()
    scoreboards = get_league_scoreboards(league_id, week)
    final_message_string = "________________________________\n"
    final_message_string += "Matchups for Week {}:\n".format(week)
    final_message_string += "________________________________\n\n"

    for i, matchup_id in enumerate(scoreboards):
        matchup = scoreboards[matchup_id]
        matchup_string = "Matchup {}:\n".format(i + 1)
        matchup_string += "{} VS. {} \n\n".format(matchup[0][0], matchup[1][0])
        final_message_string += matchup_string

    return final_message_string


def get_playoff_bracket_string(league_id):
    """
    Creates and returns a message of the league's playoff bracket.
    :param league_id: Int league_id
    :return: string message league's playoff bracket
    """
    league = League(league_id)
    bracket = league.get_playoff_winners_bracket()
    return bracket


def get_scores_string(league_id):
    """
    Creates and returns a message of the league's current scores for the current week.
    :param league_id: Int league_id
    :return: string message of the current week's scores
    """
    week = get_current_week()
    scoreboards = get_league_scoreboards(league_id, week)
    final_message_string = "Scores \n____________________\n\n"
    for i, matchup_id in enumerate(scoreboards):
        matchup = scoreboards[matchup_id]
        string_to_add = "Matchup {}\n{:<8} {:<8.2f}\n{:<8} {:<8.2f}\n\n".format(i + 1, matchup[0][0], matchup[0][1],
                                                                                matchup[1][0], matchup[1][1])
        final_message_string += string_to_add

    return final_message_string


def get_close_games_string(league_id, close_num):
    """
    Creates and returns a message of the league's close games.
    :param league_id: Int league_id
    :param close_num: Int what poInt difference is considered a close game.
    :return: string message of the current week's close games.
    """
    league = League(league_id)
    week = get_current_week()
    scoreboards = get_league_scoreboards(league_id, week)
    close_games = league.get_close_games(scoreboards, close_num)

    final_message_string = "___________________\n"
    final_message_string += "Close games😰😰\n"
    final_message_string += "___________________\n\n"

    for i, matchup_id in enumerate(close_games):
        matchup = close_games[matchup_id]
        string_to_add = "Matchup {}\n{:<8} {:<8.2f}\n{:<8} {:<8.2f}\n\n".format(i + 1, matchup[0][0], matchup[0][1],
                                                                                matchup[1][0], matchup[1][1])
        final_message_string += string_to_add
    return final_message_string


def get_standings_string(league_id):
    """
    Creates and returns a message of the league's standings.
    :param league_id: Int league_id
    :return: string message of the leagues standings.
    """
    league = League(league_id)
    rosters = league.get_rosters()
    users = league.get_users()
    standings = league.get_standings(rosters, users)
    final_message_string = "________________________________\n"
    #final_message_string += "Standings \n|{0:^7}|{1:^7}|{2:^7}|{3:^7}\n".format("rank", "team", "wins", "points")
    final_message_string += "Standings\n"
    final_message_string += "________________________________\n\n"
    try:
        playoff_line = os.environ["NUMBER_OF_PLAYOFF_TEAMS"] - 1
    except:
        playoff_line = 5
    for i, standing in enumerate(standings):
        team = standing[0]
        if team is None:
            team = "Team NA"
        #if len(team) >= 7:
            #team_name = team[:7]
        #else:
        team_name = team
        string_to_add = "{} - {} ({}-{})\n".format(i + 1, team_name, standing[1], standing[2])
        if i == playoff_line:
            string_to_add += "________________________________\n\n"
        final_message_string += string_to_add
    return final_message_string


def get_best_and_worst_string(league_id):
    """
    :param league_id: Int league_id
    :return: String of the highest Scorer, lowest scorer, most points left on the bench, and Why bother section.
    """
    highest_scorer = get_highest_score(league_id)[1]
    highest_score = get_highest_score(league_id)[0]
    highest_score_emojis = "🏆🏆"
    lowest_scorer = get_lowest_score(league_id)[1]
    lowest_score = get_lowest_score(league_id)[0]
    lowest_score_emojis = "😢😢"
    final_string = "{} Highest Scorer:\n{}\n{:.2f}\n\n{} Lowest Scorer:\n {}\n{:.2f}\n\n".format(highest_score_emojis,
                                                                                                 highest_scorer,
                                                                                                 highest_score,
                                                                                                 lowest_score_emojis,
                                                                                                 lowest_scorer,
                                                                                                 lowest_score)
    highest_bench_score_emojis = " 😂😂"
    bench_points = get_bench_points(league_id)
    largest_scoring_bench = get_highest_bench_points(bench_points)
    final_string += "{} Most points left on the bench:\n{}\n{:.2f} in standard\n\n".format(highest_bench_score_emojis,
                                                                                           largest_scoring_bench[0],
                                                                                           largest_scoring_bench[1])
    negative_starters = get_negative_starters(league_id)
    if negative_starters:
        final_string += "🤔🤔Why bother?\n"

    for key in negative_starters:
        negative_starters_list = negative_starters[key]
        final_string += "{} Started:\n".format(key)
        for negative_starter_tup in negative_starters_list:
            final_string += "{} who had {} in standard\n".format(negative_starter_tup[0], negative_starter_tup[1])
        final_string += "\n"
    return final_string


def get_bench_beats_starters_string(league_id):
    """
    Gets all bench players that outscored starters at their position.
    :param league_id: Int league_id
    :return: String teams which had bench players outscore their starters in a position.
    """
    week = get_current_week()
    league = League(league_id)
    matchups = league.get_matchups(week)

    final_message_string = "________________________________\n"
    final_message_string += "Worst of the week💩💩\n"
    final_message_string += "________________________________\n\n"

    for matchup in matchups:
        starters = matchup["starters"]
        all_players = matchup["players"]
        bench = set(all_players) - set(starters)


if __name__ == "__main__":
    """
    Main script for the bot
    """
    bot = None

    bot_type = os.environ["BOT_TYPE"]
    league_id = os.environ["LEAGUE_ID"]

    # Check if the user specified the close game num. Default is 20.
    try:
        close_num = os.environ["CLOSE_NUM"]
    except:
        close_num = 20

    # off_season_start_date = pendulum.datetime(OFF_STARTING_YEAR, OFF_STARTING_MONTH, OFF_STARTING_DAY)
    # pre_season_start_date = pendulum.datetime(PRE_STARTING_YEAR, PRE_STARTING_MONTH, PRE_STARTING_DAY)
    # starting_date = pendulum.datetime(STARTING_YEAR, STARTING_MONTH, STARTING_DAY)

    off_season_start_date = os.environ["OFF_SEASON_START_DATE"]
    pre_season_start_date = os.environ["PRE_SEASON_START_DATE"]
    starting_date = os.environ["SEASON_START_DATE"]
    stop_date = os.environ["STOP_DATE"]

    start_day = int(os.environ["SEASON_START_DATE"][8:10])
    start_day += 1
    str_day_after_start = str(start_day).zfill(2)
    str_day_after_start_final = os.environ["SEASON_START_DATE"][0:8] + str_day_after_start

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

    sched = BlockingScheduler(job_defaults={'misfire_grace_time': 15*60})

    # Schedule on UTC (Eastern is -4)
    # Matchups Thursday at 7:00 pm ET
    sched.add_job(bot.send, 'cron', [get_matchups_string, league_id], id='matchups',
        day_of_week='thu', hour=23, start_date=starting_date, end_date=stop_date,
        replace_existing=True)
    # Scores Friday at 9 am ET
    sched.add_job(bot.send, 'cron', [get_scores_string, league_id], id='scores',
        day_of_week='fri,mon', hour=13, start_date=starting_date, end_date=stop_date,
        replace_existing=True)
    # Close games Sunday on 7:00 pm ET
    sched.add_job(bot.send, 'cron', [get_close_games_string, league_id], id='close-game',
        day_of_week='sun,mon', hour=23, start_date=starting_date, end_date=stop_date,
        replace_existing=True)
    # Standings Tuesday at 11:00 am ET
    sched.add_job(bot.send, 'cron', [get_standings_string, league_id], id='standings',
        day_of_week='tue', hour=15, start_date=starting_date, end_date=stop_date,
        replace_existing=True)
    # Best/Worst Tuesday at 11:01 am ET
    sched.add_job(bot.send, 'cron', [get_best_and_worst_string, league_id], id='best-and-worst',
        day_of_week='tue', hour=15, minute=1, start_date=starting_date, end_date=stop_date,
        replace_existing=True)

    # Fun fact
    sched.add_job(bot.send, 'cron', [get_fun_fact], id='fun_fact',
        day_of_week='mon,tue,wed,thu,fri,sat,sun', hour='9,15,21', minute='20', start_date=pre_season_start_date, end_date=stop_date,
        replace_existing=True)
    #
    # Weekly Predictions
    sched.add_job(bot.send, 'cron', [get_td_predict], id='td-predict',
        day_of_week='thu', hour=12, minute=30, start_date=starting_date, end_date=stop_date,
        replace_existing=True)

    sched.add_job(bot.send, 'cron', [get_high_predict], id='fun_fact',
        day_of_week='thu', hour=12, minute=35, start_date=starting_date, end_date=stop_date,
        replace_existing=True)

    sched.add_job(bot.send, 'cron', [get_low_predict], id='fun_fact',
        day_of_week='thu', hour=12, minute=40, start_date=starting_date, end_date=stop_date,
        replace_existing=True)

    sched.add_job(bot.send, 'cron', [get_player_name], id='fun_fact',
        day_of_week='thu', hour=12, minute='32,37,42', start_date=starting_date, end_date=stop_date,
        replace_existing=True)

    # Season Prediction
    sched.add_job(bot.send, 'cron', [get_spoob_predict], id='fun_fact',
        day_of_week='mon,tue,wed,thu,fri,sat,sun', hour=22, minute=30, start_date=starting_date, end_date=str_day_after_start_final,
        replace_existing=True)

    sched.add_job(bot.send, 'cron', [get_champ_predict], id='fun_fact',
        day_of_week='mon,tue,wed,thu,fri,sat,sun', hour=22, minute=34, start_date=starting_date, end_date=str_day_after_start_final,
        replace_existing=True)

    sched.add_job(bot.send, 'cron', [get_player_name], id='fun_fact',
        day_of_week='thu', hour=22, minute='32,36', start_date=starting_date, end_date=str_day_after_start_final,
        replace_existing=True)

    # Rule Changes Update
    sched.add_job(bot.send, 'cron', [get_rule_changes], id='fun_fact',
        day_of_week='mon,tue,wed,thu,fri,sat,sun', hour=13, minute=30, start_date=pre_season_start_date, end_date=pre_season_start_date,
        replace_existing=True)

    # # Off-Season draft order
    sched.add_job(bot.send, 'cron', [get_draft_order], id='fun_fact',
        day_of_week='mon', hour=20, minute=10, start_date=off_season_start_date, end_date=pre_season_start_date,
        replace_existing=True)

    sched.start()
