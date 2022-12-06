import xlrd
import pandas
import math
from statistics import mean

FILE_URL = 'https://www.dropbox.com/s/69vox9xxxlbfqrr/nbaodds_v1.xlsx?dl=1'

raw_data = pandas.read_excel(FILE_URL, 'data')
output_by_team = pandas.read_excel(FILE_URL, 'output_by_team')
result = open('sport_output.txt', 'w')

spread_wins = 0
spread_losses = 0
spread_ties = 0
ou_wins = 0
ou_losses = 0
ou_ties = 0

def earlier_than(a, b):
	if a > 1000 and b < 1000:
		return True
	elif a < 1000 and b > 1000:
		return False
	else:
		return a < b

def get_next_date(date):
	if date == 1031:
		return 1101
	if date == 1130:
		return 1201
	if date == 1231:
		return 101
	if date == 131:
		return 201
	if date == 228:
		return 301
	else:
		return date + 1

scores = {}

def input_daily_scores(date):
	daily_scores = raw_data.loc[raw_data['Date'] == date]
	for index, _ in daily_scores.iloc[::2].iterrows():
		row = raw_data.iloc[index]
		against_index = index + 1
		against_row = raw_data.iloc[against_index]

		if row['Team'] in scores:
			scores[row['Team']]['for'].append(row['Final'])
			scores[row['Team']]['against'].append(against_row['Final'])
		else:
			scores[row['Team']] = {'for': [row['Final']], 'against': [against_row['Final']]}

def calc_diff(team_points_for, team_points_against, opp_points_for, opp_points_against):
	return math.sqrt(team_points_for * opp_points_against) - math.sqrt(opp_points_for * team_points_against)

def calc_score(team_points_for, team_points_against, opp_points_for, opp_points_against):
	return math.sqrt(team_points_for * opp_points_against) + math.sqrt(opp_points_for * team_points_against)

def calc_spread(expected_diff, actual_diff, spread):
	global spread_wins
	global spread_losses
	global spread_ties
	if expected_diff < spread and actual_diff < spread:
		spread_wins = spread_wins + 1
	elif expected_diff > spread and actual_diff > spread:
		spread_wins = spread_wins + 1
	elif expected_diff == spread and actual_diff == spread:
		spread_wins = spread_wins + 1
	elif actual_diff == spread:
		spread_ties = spread_ties + 1
	else:
		spread_losses = spread_losses + 1

def calc_ou(expected_score, actual_score, ou_score):
	global ou_wins
	global ou_losses
	global ou_ties
	if expected_score < ou_score and actual_score < ou_score:
		ou_wins = ou_wins + 1
	elif expected_score > ou_score and actual_score > ou_score:
		ou_wins = ou_wins + 1
	elif expected_score == ou_score and actual_score == ou_score:
		ou_wins = ou_wins + 1
	elif actual_score == ou_score:
		ou_ties = ou_ties + 1
	else:
		ou_losses = ou_losses + 1

def output_odds(date):
	daily_scores = raw_data.loc[raw_data['Date'] == date]
	for index, _ in daily_scores.iloc[::2].iterrows():
		row = raw_data.iloc[index]
		against_index = index + 1
		against_row = raw_data.iloc[against_index]

		avg_team_score = mean(scores[row['Team']]['for'])
		avg_team_against_score = mean(scores[row['Team']]['against'])
		avg_opp_score = mean(scores[against_row['Team']]['for'])
		avg_opp_against_score = mean(scores[against_row['Team']]['against'])

		if row['Open'] != 'pk' and row['Open'] < 60:
			calc_spread(calc_diff(avg_team_score, avg_team_against_score, avg_opp_score, avg_opp_against_score), row['Final'] - against_row['Final'], row['Open'])
		if against_row['Open'] != 'pk' and against_row['Open'] >= 60:
			calc_ou(calc_score(avg_team_score, avg_team_against_score, avg_opp_score, avg_opp_against_score), row['Final'] + against_row['Final'], against_row['Open'])
		if row['Open'] != 'pk' and row['Open'] >= 60:
			calc_ou(calc_score(avg_team_score, avg_team_against_score, avg_opp_score, avg_opp_against_score), row['Final'] + against_row['Final'], row['Open'])
		if against_row['Open'] != 'pk' and against_row['Open'] < 60:
			calc_spread(calc_diff(avg_team_score, avg_team_against_score, avg_opp_score, avg_opp_against_score), row['Final'] - against_row['Final'], -against_row['Open'])

dates = sorted(set(raw_data['Date']))
dates_ordered = []
for date in dates:
	if date > 1000:
		dates_ordered.append(date)
for date in dates:
	if date < 1000:
		dates_ordered.append(date)

for i in range(len(dates_ordered)-1):
	input_daily_scores(dates_ordered[i])
	if earlier_than(1101, dates_ordered[i+1]):
		output_odds(dates_ordered[i+1])

result.writelines('spread: {wins}-{losses}-{ties}\n'.format(wins=spread_wins, losses=spread_losses, ties=spread_ties))
result.writelines('ou: {wins}-{losses}-{ties}\n'.format(wins=ou_wins, losses=ou_losses, ties=ou_ties))



# for i in range(len(output_by_team)-1):
# 	for j in range(i+1, len(output_by_team)-1):
# 		matchup = []
# 		matchup.append('{team} {opp}  -  '.format(team=output_by_team.iloc[i]['Team'], opp=output_by_team.iloc[j]['Team']))

# 		team_points_for = output_by_team.iloc[i]['Points For']
# 		team_points_against = output_by_team.iloc[i]['Average of Opp Score']
# 		opp_points_for = output_by_team.iloc[j]['Points For']
# 		opp_points_against = output_by_team.iloc[j]['Average of Opp Score']
# 		# spread calculated using a sqrt transformation based on quality of opponent
# 		spread = math.sqrt(opp_points_for * team_points_against) - math.sqrt(team_points_for * opp_points_against)
# 		matchup.append('({team} {spread:.2f})  '.format(team=output_by_team.iloc[i]['Team'], spread=spread))

# 		total_score = spread = math.sqrt(opp_points_for * team_points_against) + math.sqrt(team_points_for * opp_points_against)
# 		matchup.append('{total_score:.2f}'.format(total_score=total_score))
# 		matchup.append('\n')
# 		result.writelines(matchup)

result.close()
