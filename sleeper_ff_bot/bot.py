import os
import pendulum
import logging
import random
import gspread
import json
from fuzzywuzzy import fuzz
from apscheduler.schedulers.blocking import BlockingScheduler
from oauth2client.service_account import ServiceAccountCredentials
from teams import teams, team_abbrs
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
    creds_dict = json.loads(json_creds)
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\\\n", "\n")
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)

    # Find a workbook by url and open the first sheet
    sh = client.open_by_url("https://docs.google.com/spreadsheets/d/1ZFv0u8KYoXdoKMhjloK6EhIJlmzZsn91BidnGHwkRT4/edit#gid=0")
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
    scoreboards = league.get_scoreboards(rosters, matchups, users,"pts_half_ppr",week)
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

def get_team_abbr(search_string):
    team_abbr = None
    for team in teams:
        if team.lower() in search_string.lower():
            i = teams.index(team)
            team_abbr = team_abbrs[i]
    if team_abbr is None:
        for team in team_abbrs:
            if team.lower() in search_string.lower():
                i = team_abbrs.index(team)
                team_abbr = team_abbrs[i]
    if team_abbr is None:
        for team in teams:
            team_array = team.lower().split()
            for t in team_array:
                    if t in search_string.lower():
                        i = teams.index(team)
                        team_abbr = team_abbrs[i]
    if team_abbr is not None:
        return team_abbr
    else:
        return "error"

def find_position(search_string):
    position_abbr = None
    positions = ['quarterback',' qb ','running back',' rb ','wide receiver', ' wr ','tight end',' te ','kicker',' k ']
    positions_abbrs = ['QB','QB','RB','RB','WR','WR','TE','TE','K','K']
    for position in positions:
        if position in search_string.lower():
            i = positions.index(position)
            position_abbr = positions_abbrs[i]
    if position_abbr is not None:
        return position_abbr
    else:
        return "error"

def get_depth_chart(team, position):
    players = Players().get_all_players()

    bot_type = os.environ["BOT_TYPE"]

    if bot_type == "groupme":
        bot_id = os.environ["BOT_ID"]
        bot = GroupMe(bot_id)
    elif bot_type == "slack":
        webhook = os.environ["SLACK_WEBHOOK"]
        bot = Slack(webhook)
    elif bot_type == "discord":
        webhook = os.environ["DISCORD_WEBHOOK"]
        bot = Discord(webhook)

    final_string = "Depth Chart for {} - {}\n\n".format(team, position)
    if position == 'WR':
        lwrdc_num = []
        rwrdc_num = []
        swrdc_num = []
        for player_id in players:
            player = players[player_id]
            if player["team"] == team and player["position"] == position:
                if player["depth_chart_order"] is not None:
                    if player["depth_chart_position"] == 'LWR':
                        lwrdc_num.append(player["depth_chart_order"])
                    elif player["depth_chart_position"] == 'RWR':
                        rwrdc_num.append(player["depth_chart_order"])
                    elif player["depth_chart_position"] == 'SWR':
                        swrdc_num.append(player["depth_chart_order"])
        if len(lwrdc_num) > 0:
            lwrdc_cnt = max(lwrdc_num)
            i =1
            final_string += "WR1:\n"
            while i <= lwrdc_cnt:
                for player_id in players:
                    player = players[player_id]
                    if team == player["team"] and position == player["position"] and player["depth_chart_position"] == 'LWR' and i == player["depth_chart_order"]:
                        final_string += "{}. {}\n".format(i, player["full_name"])
                i += 1
            final_string += "\n"
        if len(rwrdc_num) > 0:
            rwrdc_cnt = max(rwrdc_num)
            i =1
            final_string += "WR2:\n"
            while i <= rwrdc_cnt:
                for player_id in players:
                    player = players[player_id]
                    if team == player["team"] and position == player["position"] and player["depth_chart_position"] == 'RWR' and i == player["depth_chart_order"]:
                        final_string += "{}. {}\n".format(i, player["full_name"])
                i += 1
            final_string += "\n"
        if len(swrdc_num) > 0:
            swrdc_cnt = max(swrdc_num)
            i = 1
            final_string += "WR3:\n"
            while i <= swrdc_cnt:
                for player_id in players:
                    player = players[player_id]
                    if team == player["team"] and position == player["position"] and player["depth_chart_position"] == 'SWR' and i == player["depth_chart_order"]:
                        final_string += "{}. {}\n".format(i, player["full_name"])
                i += 1
            final_string += "\n"
    else:
        dc_num = []
        for player_id in players:
            player = players[player_id]
            if player["team"] == team and player["position"] == position:
                if player["depth_chart_order"] is not None:
                    dc_num.append(player["depth_chart_order"])
        dc_cnt = max(dc_num)
        i = 1
        while i <= dc_cnt:
            for player_id in players:
                player = players[player_id]
                if team == player["team"] and position == player["position"] and i == player["depth_chart_order"]:
                    final_string += "{}. {}\n".format(i, player["full_name"])
            i += 1
    bot.send(send_any_string, final_string)

def get_player_key(search_string, requestor, name_key_switch):
    players = Players().get_all_players()
    bot_type = os.environ["BOT_TYPE"]

    if bot_type == "groupme":
        bot_id = os.environ["BOT_ID"]
        bot = GroupMe(bot_id)
    elif bot_type == "slack":
        webhook = os.environ["SLACK_WEBHOOK"]
        bot = Slack(webhook)
    elif bot_type == "discord":
        webhook = os.environ["DISCORD_WEBHOOK"]
        bot = Discord(webhook)

    found_players = []
    if name_key_switch == 0:
        for player_id in players:
            player = players[player_id]
            try:
                token_set_ratio = fuzz.token_set_ratio(search_string, player["search_full_name"])
                try:
                    injury_status = player["injury_status"]
                except:
                    injury_status = None
                if search_string in player["search_full_name"]:
                    found_players.append((player_id, player["full_name"], player["position"], player["team"], injury_status))
                elif token_set_ratio > 79:
                    found_players.append((player_id, player["full_name"], player["position"], player["team"], injury_status))
            except:
                pass
            if player["position"] == "DEF":
                search_name = player["first_name"].lower() + player["last_name"].lower()
                search_name = search_name.replace(" ","")
                full_name_clean = player["first_name"] + " " + player["last_name"]
                def_ratio = fuzz.ratio(search_string, search_name)
                try:
                    injury_status = player["injury_status"]
                except:
                    injury_status = None
                if def_ratio > 54:
                    found_players.append((player_id, full_name_clean, player["position"], player["team"], injury_status))
        if len(found_players) > 1:
            text = "Which player are you looking for?\n\n"
            for p in found_players:
                text += "for {} ({} - {}) - reply {}\n\n".format(p[1], p[2], p[3], p[0])
            bot.send(send_any_string, text)
            return "True"
        elif len(found_players) == 1:
            get_player_stats(found_players[0])
            return "False"
        elif len(found_players) == 0:
            bot.send(send_any_string, 'Player not found')
            return "False"
    elif name_key_switch == 1:
        player = players[search_string]
        if player["position"] == "DEF":
            full_name_clean = player["first_name"] + " " + player["last_name"]
            try:
                injury_status = player["injury_status"]
            except:
                injury_status = None
            found_players.append((search_string, full_name_clean, player["position"], player["team"], injury_status))
        else:
            try:
                injury_status = player["injury_status"]
            except:
                injury_status = None
            found_players.append((search_string, player["full_name"], player["position"], player["team"], injury_status))
        get_player_stats(found_players[0])
        return "False"


def get_random_player(position,ba_flag):
    players = Players().get_all_players()
    position_players = []

    for player_id in players:
        player = players[player_id]
        try:
            if player["position"].lower() == position:
                if position == 'def':
                    full_name_clean = player["first_name"] + " " + player["last_name"]
                    position_players.append((full_name_clean))
                else:
                    if ba_flag == 'best':
                        if player["team"] is not None and player["status"].lower() == 'active' and player["injury_status"] is None and player["depth_chart_order"] == 1:
                            position_players.append((player["full_name"]))
                    else:
                        position_players.append((player["full_name"]))
        except:
            pass
    response = [random.choice(position_players)]
    return response


def get_player_stats(search_object):

    today = pendulum.today()
    starting_date = pendulum.datetime(STARTING_YEAR, STARTING_MONTH, STARTING_DAY)
    if starting_date >= today:
        year = STARTING_YEAR
    else:
        year = int(STARTING_YEAR) - 1
    stats = Stats(). get_all_stats("regular",year)

    bot_type = os.environ["BOT_TYPE"]


    if bot_type == "groupme":
        bot_id = os.environ["BOT_ID"]
        bot = GroupMe(bot_id)
    elif bot_type == "slack":
        webhook = os.environ["SLACK_WEBHOOK"]
        bot = Slack(webhook)
    elif bot_type == "discord":
        webhook = os.environ["DISCORD_WEBHOOK"]
        bot = Discord(webhook)
    stats_run = True
    player_id = search_object[0]
    player_name = search_object[1]
    position = search_object[2]
    team = search_object[3]
    if search_object[4] == None:
        injury_status = 'Active'
    else:
        injury_status = search_object[4]
    try:
        player = stats[player_id]
    except:
        stats_run = False
        pass
    if position not in ["QB","RB","WR","TE","DEF"]:
        stats_run = False
    if stats_run:
        if position is not "DEF":
            final_string = "{} ({} - {})\n{}\n\n".format(player_name, position, team, injury_status)
        else:
            final_string = "{} ({} - {})\n\n".format(player_name, position, team)

        if position is not "DEF":
            try:
                ga = int(player["gms_active"])
            except:
                ga = 0
                pass
            try:
                gp = int(player["gp"])
            except:
                gp = 0
                pass
            try:
                gs = int(player["gs"])
                pass
            except:
                gs = 0
                pass
            try:
                pts_half_ppr = player["pts_half_ppr"]
            except:
                pts_half_ppr = 0
                pass

            final_string += "Fantasy Points: {}\n\nGames Active: {}\nGames Played: {}\nGames Started: {}\n\n".format(pts_half_ppr, ga, gp, gs)

            try:
                team_snaps = player["tm_off_snp"]
                player_snaps = player["off_snp"]
                snap_perc = round((player_snaps / team_snaps)*100,2)
                final_string += "Snap Share: {}%\n".format(snap_perc)
            except:
                pass

        if "QB" in position:
            #try:
                #rating = player["pass_rtg"]
                #final_string += "Passer Rating: {}\n".format(rating)
            #except:
                #pass
            try:
                pyards = int(player["pass_yd"])
                final_string += "Passing Yards: {}\n".format(pyards)
            except:
                pass
            try:
                ptd = int(player["pass_td"])
                final_string += "Passing TDs: {}\n".format(ptd)
            except:
                pass
            try:
                ryards = int(player["rush_yd"])
                final_string += "Rushing Yards: {}\n".format(ryards)
            except:
                pass
            try:
                rtd = int(player["rush_td"])
                final_string += "Rushing TDs: {}\n".format(rtd)
            except:
                pass
            try:
                pass_int = int(player["pass_int"])
                final_string += "Interceptions {}\n".format(pass_int)
            except:
                pass
            try:
                fum = int(player["fum"])
                final_string += "Fumbles: {}\n".format(fum)
            except:
                pass
        if "RB" in position:
            try:
                ryards = int(player["rush_yd"])
                final_string += "Rushing Yards: {}\n".format(ryards)
            except:
                pass
            try:
                rtd = int(player["rush_td"])
                final_string += "Rushing TDs: {}\n".format(rtd)
            except:
                pass
            try:
                fum = int(player["fum"])
                final_string += "Fumbles: {}\n".format(fum)
            except:
                pass
            try:
                catch_perc = round((player["rec"]/player["rec_tgt"])*100,2)
                final_string += "Catch Rate: {}%\n".format(catch_perc)
            except:
                pass
            try:
                rcyards = int(player["rec_yd"])
                final_string += "Receiving Yards: {}\n".format(rcyards)
            except:
                pass
            try:
                rctd = int(player["rec_td"])
                final_string += "Receiving TDs: {}\n".format(rctd)
            except:
                pass
        if "WR" in position:
            try:
                rcyards = int(player["rec_yd"])
                final_string += "Receiving Yards: {}\n".format(rcyards)
            except:
                pass
            try:
                rctd = int(player["rec_td"])
                final_string += "Receiving TDs: {}\n".format(rctd)
            except:
                pass
            try:
                drop_perc = round((player["rec"]/player["rec_tgt"])*100,2)
                final_string += "Catch Rate: {}%\n".format(drop_perc)
            except:
                pass
            try:
                ryards = int(player["rush_yd"])
                final_string += "Rushing Yards: {}\n".format(ryards)
            except:
                pass
            try:
                rtd = int(player["rush_td"])
                final_string += "Rushing TDs: {}\n".format(rtd)
            except:
                pass
            try:
                fum = int(player["fum"])
                final_string += "Fumbles: {}\n".format(fum)
            except:
                pass
        if "TE" in position:
            try:
                rcyards = int(player["rec_yd"])
                final_string += "Receiving Yards: {}\n".format(rcyards)
            except:
                pass
            try:
                rctd = int(player["rec_td"])
                final_string += "Receiving TDs: {}\n".format(rctd)
            except:
                pass
            try:
                drop_perc = round((player["rec"]/player["rec_tgt"])*100,2)
                final_string += "Catch Rate: {}%\n".format(drop_perc)
            except:
                pass
            try:
                ryards = int(player["rush_yd"])
                final_string += "Rushing Yards: {}\n".format(ryards)
            except:
                pass
            try:
                rtd = int(player["rush_td"])
                final_string += "Rushing TDs: {}\n".format(rtd)
            except:
                pass
            try:
                fum = int(player["fum"])
                final_string += "Fumbles: {}\n".format(fum)
            except:
                pass
        if "K" in position:
            try:
                fga = int(player["fga"])
                fgm = int(player["fgm"])
                fgperc = round((fgm/fga)*100,2)
                final_string += "FG%: {}\n\nField Goals Attempted: {}\nField Goals Made: {}\n".format(fgperc, fga, fgm)
            except:
                pass
            try:
                fgm = int(player["fgm"])
                final_string += "Field Goals Made: {}\n".format(fgm)
            except:
                pass
            try:
                fgm1 = int(player["fgm_0_19"])
                final_string += "0-19: {}\n".format(fgm1)
            except:
                pass
            try:
                fgm2 = int(player["fgm_20_29"])
                final_string += "20-29: {}\n".format(fgm2)
            except:
                pass
            try:
                fgm3 = int(player["fgm_30_39"])
                final_string += "30-39: {}\n".format(fgm3)
            except:
                pass
            try:
                fgm4 = int(player["fgm_40_49"])
                final_string += "40-49: {}\n".format(fgm4)
            except:
                pass
            try:
                fgm5 = int(player["fgm_50p"])
                final_string += "50+: {}\n".format(fgm5)
            except:
                pass
            try:
                xpa = int(player["xpa"])
                xpm = int(player["xpm"])
                xpperc = round((xpm/xpa)*100,2)
                final_string += "XP%: {}\n\nXP Attempted: {}\nXP Made: {}\n".format(xpperc, xpa, xpm)
            except:
                pass
        if "DEF" in position:
            try:
                td = int(player["td"])
                final_string += "Touchdowns: {}\n".format(td)
            except:
                pass
            try:
                ff = int(player["ff"])
                final_string += "Forced Fumbles: {}\n".format(ff)
            except:
                pass
            try:
                fum_rec = int(player["fum_rec"])
                final_string += "Fumbles Recoved: {}\n".format(fum_rec)
            except:
                pass
            try:
                tkl = int(player["tkl_loss"])
                final_string += "Tackles For Loss: {}\n".format(tkl)
            except:
                pass
            try:
                qbh = int(player["qb_hit"])
                final_string += "QB Hits: {}\n".format(qbh)
            except:
                pass
            try:
                sck = int(player["sack"])
                final_string += "Sacks: {}\n".format(sck)
            except:
                pass
    else:
        if player_name == "Aaron Hernandez":
            final_string = "{} hung himself. Gone Forever! Aaron Hernandez.".format(player_name)
        elif position not in ["QB","RB","WR","TE"]:
            final_string = "I do not do IDP stats"
        else:
            final_string = "No {} stats found for {}".format(year, player_name)

    bot.send(send_any_string, final_string)


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
    week = today.diff(starting_week).in_weeks() + 1
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
        print(matchup)
        first_score = 0
        second_score = 0
        if matchup[0][1] is not None:
            first_score = matchup[0][1]
        if matchup[1][1] is not None:
            second_score = matchup[1][1]
        print(matchup)
        first_score = 0
        second_score = 0
        if matchup[0][1] is not None:
            first_score = matchup[0][1]
        if matchup[1][1] is not None:
            second_score = matchup[1][1]
        string_to_add = "Matchup {}\n{:<8} {:<8.2f}\n{:<8} {:<8.2f}\n\n".format(i + 1, matchup[0][0], first_score,
                                                                                matchup[1][0], second_score)
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
        print(matchup)
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
        if len(team) >= 7:
            team_name = team[:7]
        else:
            team_name = team
            string_to_add = "{0:^7} {1:^10} {2:>7} {3:>7}\n".format(i + 1, team_name, standing[1], standing[3])
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
