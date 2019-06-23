import pytest
from sleeper_ff_bot import bot

def test_get_matchups():
	matchups_string = bot.get_matchups(355526480094113792, 11)
	assert isinstance(matchups_string, str)

def test_get_standings():
	standings_string = bot.get_standings(355526480094113792, 11)
	assert isinstance(standings_string, str)

def test_get_close_games():
	close_game_string = bot.get_close_games(355526480094113792, 11, 20)
	assert isinstance(close_game_string, str)