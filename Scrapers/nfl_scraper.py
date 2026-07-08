import pandas as pd
import nflreadpy as nfl

pd.set_option('display.max_columns', None)

schedules = nfl.load_schedules(seasons=[2023]).to_pandas()

#print(schedules.head())

def count_record(team_df):
    wins = (team_df['result'] > 0).sum()
    losses = (team_df['result'] < 0).sum()
    ties = (team_df['result'] == 0).sum()
    return pd.Series({'Wins': wins, 'Losses': losses, 'Ties': ties})

# Applying the grouping for both home and away teams
team_records = schedules.groupby('home_team').apply(count_record)
team_records_away = schedules.groupby('away_team').apply(count_record)

print(team_records)
print(team_records_away)