import pandas as pd
import nflreadpy as nfl
import os

pd.set_option('display.max_columns', None)

'''schedules = nfl.load_schedules(seasons=[2025]).to_pandas()

#print(schedules.head())

def count_record(team_df):
    wins = (team_df['result'] > 0).sum()
    losses = (team_df['result'] < 0).sum()
    ties = (team_df['result'] == 0).sum()
    return pd.Series({'Wins': wins, 'Losses': losses, 'Ties': ties})

# Applying the grouping for both home and away teams
team_records = schedules.groupby('home_team').apply(count_record)
team_records_away = schedules.groupby('away_team').apply(count_record)

print(schedules.head())'''

years = list(range(1999, 2026)) # acceptable year range for this dataset is 1999-present (2025)

# load data
schedules = nfl.load_schedules(seasons=years).to_pandas()
player_stats = nfl.load_player_stats(seasons=years,summary_level='reg+post').to_pandas()
team_stats = nfl.load_team_stats(seasons=years,summary_level='reg+post').to_pandas()

# save to CSVs
os.makedirs('Data', exist_ok=True)
schedules.to_csv('Data/schedules.csv', index=False)
player_stats.to_csv('Data/player_stats.csv', index=False)
team_stats.to_csv('Data/team_stats.csv', index=False)