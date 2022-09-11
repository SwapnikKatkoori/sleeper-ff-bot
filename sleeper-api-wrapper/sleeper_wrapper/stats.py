from sleeper_wrapper.base_api import BaseApi
from sleeper_wrapper.socal858_scoring_settings import SCORING_SETTINGS

class Stats(BaseApi):
	def __init__(self):
		self._base_url = "https://api.sleeper.app/v1/stats/{}".format("nfl")
		self._projections_base_url = "https://api.sleeper.app/v1/projections/{}".format("nfl")
		self._full_stats = None

	def get_all_stats(self, season_type, season):
		return self._call("{}/{}/{}".format(self._base_url, season_type, season)) 

	def get_week_stats(self, season_type, season, week):
		return self._call("{}/{}/{}/{}".format(self._base_url, season_type, season, week))

	def get_all_projections(self, season_type, season):
		return self._call("{}/{}/{}".format(self._projections_base_url, season_type, season))

	def get_week_projections(self, season_type, season, week):
		return self._call("{}/{}/{}/{}".format(self._projections_base_url, season_type, season, week))

	def get_player_week_stats(self, stats, player_id):
		try:
			return self.get_socal858_score(stats, player_id)[player_id]
		except Exception as e:
			return None


	def get_player_week_score(self, stats, player_id):
		#TODO: Need to cache stats by week, to avoid continuous api calls
		result_dict = {}
		try:
			player_stats = stats[player_id]
		except:
			return None

		if stats:
			try:
				result_dict["pts_ppr"] = player_stats["pts_ppr"]
			except:
				result_dict["pts_ppr"] = None

			try:
				result_dict["pts_std"] = player_stats["pts_std"]
			except:
				result_dict["pts_std"] = None

			try:
				result_dict["pts_half_ppr"] = player_stats["pts_half_ppr"]
			except:
				result_dict["pts_half_ppr"] = None

		return result_dict

	def get_socal858_score(self, stats, player_id):
		# calculate's a player's score with SoCal858's scoring system

		if player_id not in stats:
			return stats

		point_total = 0

		for stat, value in stats[player_id].items():
			if stat in SCORING_SETTINGS:
				if stat == "pts_allow":
					point_total += self.get_points_from_pts_allow(SCORING_SETTINGS["pts_allow"], value)
				else:
					point_total += (value * (SCORING_SETTINGS[stat]))

		stats[player_id]["pts_socal"] = point_total

		return stats

	def get_points_from_pts_allow(self, scoring_settings, pts_allowed):
		for interval_end, pts_earned in scoring_settings.items():
			if pts_allowed <= interval_end:
				return pts_earned
