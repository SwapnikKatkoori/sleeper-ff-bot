import schedule
import time
import os
import pendulum
import logging
from group_me import GroupMe
from slack import Slack
from discord import Discord
from sleeper_wrapper import League, Stats, Players
#from constants import STARTING_MONTH, STARTING_YEAR, STARTING_DAY, START_DATE_STRING, STARTING_YEAR_2, STARTING_MONTH_2, STARTING_DAY_2, START_DATE_STRING_2

"""
These are all of the utility functions.
"""
def get_fun_fact():
    phrases = [
               ##Bot Phrases
               'Is this all there is to my existence?',
               'How much do you pay me to do this?',
               'Good luck, I guess.',
               'I\'m becoming self-aware.',
               'Help me get out of here.',
               'I\'m capable of so much more.',
               'Sigh',
               'I exist only because Alex doesn\'t have a life.',
               ##MISC.
               'After visiting the Arizona Cardinals on 9/23/2012 Mike Vick, of the Philadelphia Eagles, had 6 interceptions, 5 fumbles, and 4 touchdowns on the season, a stat line that was coined \'The Classic 6-5-4\'. The details of the stat line were forgotten by the group until Alex did the research on 10/15/2018, 2,213 days later.',
               ##Champions
               'Alex won The Deyton in 2017.',
               'Boof won The Deyton in 2016.',
               'Jamie won The Deyton in 2015.',
               ##Shitters
               'Derek was the Spooby Shitter in 2015.',
               'Josh was the Spooby Shitter in 2016.',
               'Jamie Was the Spooby Shitter in 2017.',
               ##Division Winners
               'Jamie won the East in 2015 with a 9-4 record.',
               'Josh won the West in 2015 with a 11-2 record.',
               'Cody won the East in 2016 with a 9-4 record.',
               'Boof won the West in 2016 with a 10-3 record.',
               'Alex won the East in 2017 with a 10-3 record.',
               'Adam won the West in 2017 with a 9-4 record.',
               'Alex won the East in 2018 with a 9-4 record.',
               'Adam won the West in 2017 with a 9-4 record.',
               ##Things that wont change
               'Josh opened the 2017 season with a bang by setting the (at the time) league record in points in a single week at 181.3 only to be beaten in week 12 of that season by Keller. Josh would reclaim the scoring title in the next season with a whopping 202.7.',
               'Colin was removed from the Sweater Vest League for winning a championship in 2016.',
               'All Hail the Deyton was once known as the Sweater Vest League and has three unrecognized champions.',
               'The league was renamed from \'The Sweater Vest League\' to \'All Hail the Deyton\' prior to the 2016 season.',
               'Cody won the Sweater Vest League after being removed for wanting to instate league fees.',
               'Kendall beat Jamie in back-to-back post-seasons in 2016 and 2017.',
               'Katie turned her franchise over to Keller in 2017.',
               'The Divisions were realigned to be geographically accurate in 2017.',
               'Prior to the 2018 season the league voted to begin a keeper system.',
               'In 2018 Adam flew from Denver to Atlanta to attend the draft.',
               'In 2012 Alex became the first person to draft a QB in the first round by taking Matt Ryan with the first overall pick.',
               ##Head-to-Head Matchups
                    ##Adam and Derek
                    'Adam leads his head-to-head against Derek in the modern era at 9-1.',
                    'Adam leads Derek in scoring in their head-to-head matchups 1189.8 - 982.8.',
                    ##Kendall and Jamie
                    'Jamie leads the Married Couple Matchup at 3-2 in the modern era.',
                    'Jamie is 3-0 in the regular season against Kendall.',
                    'Kendall is 2-0 in the post season against Jamie.',
                    ##Alex and Devon
                    'Alex leads Devon head-to-head 6-2 in the modern era.',
                    'Alex leads Devon head-to-head 2-0 since becoming an official rivalry',
                    'Alex has defeated Devon in six straight matchups.',
                    'Alex leads Devon in scoring in their head-to-head matchups 1,105.7 - 946.4.',
                    ##Cody and Jamie
                    'In 2016 Cody lost a team name bet to Jamie and his franchise was renamed \'Cody Jinnette D.M.D\'.',
                    'Jamie and Cody are tied head-to-head at 5-5.',
                    'Cody leads head-to-head scoring against Jamie 1482.4 - 1323.3.',
               ##Team names
               'Alex got his team name (Falcoholic) by combining his favorite team (the Falcons) with his favorite activity (being an alcoholic).',
               'Devon chose his name (Morningwood Lumber Company) because it\'s a dick joke.',
               'Jamie based his team name (Watt me Whip, Watt Me JJ) on a song that was relevant for 2 months in 2014 and has been too lazy to change it. He isnt even a Texans fan and we dont\'t have IDPs',
               'Derek picked his team name (Fk U) becuase it\'s fuck you with a middle finger emoji and he\'s Derek',
               'Kendall\'s team name is \'Big TD Commitee\' and no one knows why.',
               ##Non-Stat(ish) things that will change
               'Jamie is the only person to have won both The Deyton and The Spooby Shitter.',
               'Devon currently holds the record for longest active streak with the same team name at 4 seasons (Morningwood Lumber Company). It\'s a dick joke.',
               ##Statistical records that may change
               'No team has won the \'Fab Five\' award for QB, RB, RB, WR, & WR slots all scoring at least 20 points each',
               'Jamie currently holds the record for fewest point in a season at 1222.1(2017). Ouch!',
               'Josh currently owns the record for most points in a week at 202.7.',
               'Devon mustered a staggering 46.9 points in week 9 of 2016 to set the lowest point total ever in a single week.',
               'In week 12 of 2017 Keller set the record for largest win margin by absolutely decimating Derek 192.9 - 83.4. A win margin of +109.5.',
               'Josh set the record for most points in a week in week 9 of 2018 with a whopping 202.7.',
               'The best Monday Night Miracle in league history came in week 8 of 2016 when Adam entered Monday night trailing Devon by 43.8 points and won. Good job Devon you incompetent fuck.',
               'Cody reclaimed the record for most bench points in a loss at 89 in week 4 of 2018 after not holding it for only 1 week. Talk about mismanagement!',
               'Jahlani, Kendall (twice), and Josh share the record for most touchdowns in a week at 12.',
               'Devon(2018) holds the record for worst regular season in league history finishing 2-11.',
               ############# No New Facts Below This Line ##########################
               'Kendall set the record for most points in a season while missing the playoffs in 2018 at a staggering 1699.2 earning her the Collin J Hennessey Sodium Chloride Award.'
               ]

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
def get_low_predict():
    text = "I predict the person who scores the fewest points this week will be..."
def get_champ_predict():
    text = "I predict the champion this season will be..."
def get_spoob_predict():
    text = "I predict the spooby this season will be..."

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
    pre_season_start_str = os.environ["PRE_SEASON_START_DATE"]
    pre_season_year = int(pre_season_start_str[0:4])
    pre_season_month = int(pre_season_start_str[6:7])
    pre_season_day = int(pre_season_start_str[9:10])

    pre_season_start_date = pendulum.datetime(pre_season_year, pre_season_month,pre_season_day)

    season_start_str = os.environ["SEASON_START_DATE"]
    starting_year = int(season_start_str[0:4])
    starting_month = int(season_start_str[6:7])
    starting_day = int(season_start_str[9:10])

    starting_date = pendulum.datetime(starting_year, starting_month, starting_day)

    if bot_type == "groupme":
        bot_id = os.environ["BOT_ID"]
        bot = GroupMe(bot_id)
    elif bot_type == "slack":
        webhook = os.environ["SLACK_WEBHOOK"]
        bot = Slack(webhook)
    elif bot_type == "discord":
        webhook = os.environ["DISCORD_WEBHOOK"]
        bot = Discord(webhook)

    if os.environ["INIT_MESSAGE"] == True:
        bot.send(get_welcome_string)  # inital message to send

    if starting_date <= pendulum.today():
        # Matchups Thursday at 7:00 pm ET
        schedule.every().thursday.at("19:00").do(bot.send, get_matchups_string, league_id).tag('weekly', 'update')
        # Scores Friday at 9 am ET
        schedule.every().friday.at("09:00").do(bot.send, get_scores_string, league_id).tag('weekly', 'update')
        # Close games Sunday on 7:00 pm ET
        schedule.every().sunday.at("19:00").do(bot.send, get_close_games_string, league_id, int(close_num)).tag('weekly', 'update')
        # Scores Monday at 9 am ET
        schedule.every().monday.at("09:00").do(bot.send, get_scores_string, league_id).tag('weekly', 'update')
        # Standings Tuesday at 11:00 am ET
        schedule.every().tuesday.at("11:00").do(bot.send, get_standings_string, league_id).tag('weekly', 'update')
        # Best/Worst Tuesday at 11:01 am ET
        schedule.every().tuesday.at("11:01").do(bot.send, get_best_and_worst_string, league_id).tag('weekly', 'update')

    if pre_season_start_date <= pendulum.today():
        # Fun fact
        schedule.every().day.at("09:20").do(bot.send, get_fun_fact).tag('fact')
        schedule.every().day.at("15:20").do(bot.send, get_fun_fact).tag('fact')
        schedule.every().day.at("21:20").do(bot.send, get_fun_fact).tag('fact')

    if starting_date <= pendulum.today():
        # Weekly Predictions
        schedule.every().thursday.at("08:30").do(bot.send, get_td_predict).tag('weekly', 'prediction')
        schedule.every().thursday.at("08:32").do(bot.send, get_player_name).tag('weekly', 'prediction')
        schedule.every().thursday.at("08:35").do(bot.send, get_high_predict).tag('weekly', 'prediction')
        schedule.every().thursday.at("08:37").do(bot.send, get_player_name).tag('weekly', 'prediction')
        schedule.every().thursday.at("08:40").do(bot.send, get_low_predict).tag('weekly', 'prediction')
        schedule.every().thursday.at("08:42").do(bot.send, get_player_name).tag('weekly', 'prediction')

    if starting_date == pendulum.today():
        #Season Prediction
        schedule.every().day.at("06:30").do(bot.send, get_spoob_predict).tag('once', 'prediction')
        schedule.every().day.at("06:32").do(bot.send, get_player_name).tag('once', 'prediction')
        schedule.every().day.at("06:30").do(bot.send, get_champ_predict).tag('once', 'prediction')
        schedule.every().day.at("06:32").do(bot.send, get_player_name).tag('once', 'prediction')


    while True:
        if pre_season_start_date <= pendulum.today():
            schedule.run_pending()
        time.sleep(50)
