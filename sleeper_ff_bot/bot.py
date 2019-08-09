import schedule as schedule1
import schedule as schedule2
import schedule as schedule3
import schedule as schedule4
import time
import os
import pendulum
import logging
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from phrases import phrases
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

def get_player_name():
    names = ['Adam','Alex','Boof','Cody','Derek','Devon','Jamie','Josh','Keller','Kendall']
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
    logging.error("I Ran")
    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds']
    creds = ServiceAccountCredentials.from_json(os.environ["KEY"])
    logging.error(creds)
    client = gspread.authorize(creds)
    sh = client.open("New Market")
    sheet = sh.worksheet("League Info")


    # Find a workbook by name and open the first sheet
    # Make sure you use the right name here
    # Extract and print all of the values
    list_of_hashes = sheet.get_all_records()
    logging.error(list_of_hashes)
    return list_of_hashes

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
    return week + 1


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
    final_message_string += "Standings \n|{0:^7}|{1:^7}|{2:^7}|{3:^7}\n".format("rank", "team", "wins", "points")
    final_message_string += "________________________________\n\n"
    try:
        playoff_line = os.environ["NUMBER_OF_PLAYOFF_TEAMS"] - 1
    except:
        playoff_line = 5
    for i, standing in enumerate(standings):
        team = standing[0]
        if team is None:
            team = "Team NA"
        if len(team) >= 7:
            team_name = team[:7]
        else:
            team_name = team
        string_to_add = "{0:^7} {1:^10} {2:>7} {3:>7}\n".format(i + 1, team_name, standing[1], standing[2])
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

    off_season_start_date = pendulum.datetime(OFF_STARTING_YEAR, OFF_STARTING_MONTH, OFF_STARTING_DAY)
    pre_season_start_date = pendulum.datetime(PRE_STARTING_YEAR, PRE_STARTING_MONTH, PRE_STARTING_DAY)
    starting_date = pendulum.datetime(STARTING_YEAR, STARTING_MONTH, STARTING_DAY)

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

    while True:
        # Schedule on UTC (Eastern is -4)
        # Matchups Thursday at 7:00 pm ET
        schedule3.every().thursday.at("23:00").do(bot.send, get_matchups_string, league_id).tag('weekly', 'update', 'schedule-3')
        # Scores Friday at 9 am ET
        schedule3.every().friday.at("13:00").do(bot.send, get_scores_string, league_id).tag('weekly', 'update', 'schedule-3')
        # Close games Sunday on 7:00 pm ET
        schedule3.every().sunday.at("23:00").do(bot.send, get_close_games_string, league_id, int(close_num)).tag('weekly', 'update', 'schedule-3')
        # Scores Monday at 9 am ET
        schedule3.every().monday.at("13:00").do(bot.send, get_scores_string, league_id).tag('weekly', 'update', 'schedule-3')
        # Close games Monday at 7:00 pm ET
        schedule3.every().monday.at("23:00").do(bot.send, get_close_games_string, league_id, int(close_num)).tag('weekly', 'update', 'schedule-3')
        # Standings Tuesday at 11:00 am ET
        schedule3.every().tuesday.at("15:00").do(bot.send, get_standings_string, league_id).tag('weekly', 'update', 'schedule-3')
        # Best/Worst Tuesday at 11:01 am ET
        schedule3.every().tuesday.at("15:01").do(bot.send, get_best_and_worst_string, league_id).tag('weekly', 'update', 'schedule-3')

        # Fun fact
        schedule2.every().day.at("13:20").do(bot.send, get_fun_fact).tag('fact', 'schedule-2')
        schedule2.every().day.at("17:20").do(bot.send, get_fun_fact).tag('fact', 'schedule-2')
        schedule2.every().day.at("00:20").do(bot.send, get_fun_fact).tag('fact', 'schedule-2')

        # Weekly Predictions
        schedule3.every().thursday.at("12:30").do(bot.send, get_td_predict).tag('weekly', 'prediction', 'schedule-3')
        schedule3.every().thursday.at("12:32").do(bot.send, get_player_name).tag('weekly', 'prediction', 'schedule-3')
        schedule3.every().thursday.at("12:35").do(bot.send, get_high_predict).tag('weekly', 'prediction', 'schedule-3')
        schedule3.every().thursday.at("12:37").do(bot.send, get_player_name).tag('weekly', 'prediction', 'schedule-3')
        schedule3.every().thursday.at("12:40").do(bot.send, get_low_predict).tag('weekly', 'prediction', 'schedule-3')
        schedule3.every().thursday.at("12:42").do(bot.send, get_player_name).tag('weekly', 'prediction', 'schedule-3')

        # Season Prediction
        schedule1.every().day.at("22:30").do(bot.send, get_spoob_predict).tag('once', 'prediction', 'schedule-1')
        schedule1.every().day.at("22:32").do(bot.send, get_player_name).tag('once', 'prediction', 'schedule-1')
        schedule1.every().day.at("22:30").do(bot.send, get_champ_predict).tag('once', 'prediction', 'schedule-1')
        schedule1.every().day.at("22:32").do(bot.send, get_player_name).tag('once', 'prediction', 'schedule-1')

        # Off-Season
        schedule4.every().thursday.at("20:58").do(bot.send, get_draft_order).tag('preseason', 'schedule-4')

        if starting_date <= pendulum.today():
            logging.error("Running Sequence 1")
            schedule.clear('schedule-1')
            schedule.clear('schedule-4')
            logging.error("Running Schedule-2 & schedule-3")
            schedule.run_pending()
            schedule.clear('schedule-2')
            schedule.clear('schedule-3')
        elif pre_season_start_date < pendulum.today():
            logging.error("Running Sequence 2")
            schedule.clear('schedule-1')
            schedule.clear('schedule-3')
            schedule.clear('schedule-4')
            logging.error("Running Schedule 2")
            schedule.run_pending()
            schedule.clear('schedule-2')
        elif pre_season_start_date == pendulum.today():
            logging.error("Running Sequence 3")
            schedule.clear('schedule-3')
            schedule.clear('schedule-4')
            logging.error("Running Schedule-1 & schedule-2")
            schedule.run_pending()
            schedule.clear('schedule-1')
            schedule.clear('schedule-2')
        elif off_season_start_date <= pendulum.today():
            logging.error("Running Sequence 4")
            logging.error("Running Schedule 4")
            schedule.clear('schedule-1')
            schedule.clear('schedule-2')
            schedule.clear('schedule-3')
            schedule.run_pending()
            schedule.clear('schedule-4')

        time.sleep(50)
