import pandas as pd
import numpy as np

combined_stats = pd.read_csv('Data/combined_team_player_stats.csv')
combined_stats["TD/INT"] = combined_stats["passing_tds"] / combined_stats["passing_interceptions"]

team_win_pcts = combined_stats[["season", "Team", "Win_Pct"]].drop_duplicates()

team_season_points = pd.read_csv("Data/team_season_points.csv")
base_features = team_season_points[
    ["season", "Team", "Base_Team_Strength"]
].copy()

base_features = pd.merge(
    base_features, team_win_pcts, on=["season", "Team"], how="left"
)

ranked_positions = []

sorting_rules = [
    ("QB", ["passing_yards", "passing_tds", "TD/INT"], [False, False, False]),  # More TD_INT is better
    ("RB", ["rushing_yards", "rushing_tds", "carries"], [False, False, False]),
    ("WR", ["receiving_yards", "receiving_tds", "target_share"], [False, False, False]),
    ("TE", ["receiving_yards", "receiving_tds", "target_share"], [False, False, False])
]

for pos, sort_cols, asc_rules in sorting_rules:
    # 1. Filter down to just this position
    pos_df = combined_stats[combined_stats["position"] == pos].copy()

    # 2. Sort multi-dimensionally (e.g. Yards DESC, TDs DESC, efficiency DESC)
    pos_df = pos_df.sort_values(
        by=["season", "Team"] + sort_cols,
        ascending=[True, True] + asc_rules,  # Keep Season/Team ascending
    )

    # 3. Calculate internal ranking within the Team/Season
    pos_df["Pos_Rank"] = pos_df.groupby(["season", "Team"]).cumcount()
    ranked_positions.append(pos_df)

# Combine the individually ranked positions
ranked_stats = pd.concat(ranked_positions)

# Extract core explicit slots
qbs = ranked_stats[
    (ranked_stats["position"] == "QB") & (ranked_stats["Pos_Rank"] == 0)
].copy()
rbs = ranked_stats[
    (ranked_stats["position"] == "RB") & (ranked_stats["Pos_Rank"] == 0)
].copy()
wr1 = ranked_stats[
    (ranked_stats["position"] == "WR") & (ranked_stats["Pos_Rank"] == 0)
].copy()
wr2 = ranked_stats[
    (ranked_stats["position"] == "WR") & (ranked_stats["Pos_Rank"] == 1)
].copy()

# Track exact player names already locked into roster spots
claimed_players = (
    qbs["player_name"].tolist()
    + rbs["player_name"].tolist()
    + wr1["player_name"].tolist()
    + wr2["player_name"].tolist()
)

# Grab all remaining skill players who weren't explicitly taken
flex_pool = combined_stats[
    ~combined_stats["player_name"].isin(claimed_players)
    & combined_stats["position"].isin(["RB", "WR", "TE"])
].copy()

# Fix the column mismatch by creating unified temporary columns for the pool
flex_pool["flex_yards"] = np.where(
    flex_pool["position"] == "RB",
    flex_pool["rushing_yards"],
    flex_pool["receiving_yards"],
)
flex_pool["flex_tds"] = np.where(
    flex_pool["position"] == "RB",
    flex_pool["rushing_tds"],
    flex_pool["receiving_tds"],
)
flex_pool["FLEX_Volume"] = np.where(
    flex_pool["position"] == "RB",
    flex_pool["carries"],
    flex_pool["target_share"],
)
'''
# 1. Separate the pool by position to calculate independent means and standard deviations
flex_rb = flex_pool[flex_pool["position"] == "RB"].copy()
flex_pass = flex_pool[flex_pool["position"].isin(["WR", "TE"])].copy()

# 2. Standardize Carries for RBs (Z-Score)
rb_mean = flex_rb["carries"].mean()
rb_std = flex_rb["carries"].std()
flex_rb["standardized_volume"] = (flex_rb["carries"] - rb_mean) / rb_std

# 3. Standardize Target Share for WR/TEs (Z-Score)
pass_mean = flex_pass["target_share"].mean()
pass_std = flex_pass["target_share"].std()
flex_pass["standardized_volume"] = (
    flex_pass["target_share"] - pass_mean
) / pass_std

# 4. Merge them back into a single normalized pool
flex_pool = pd.concat([flex_rb, flex_pass])
'''

# Sort the mixed pool by the unified temporary columns
flex_pool = flex_pool.sort_values(
    by=["season", "Team", "flex_yards", "flex_tds"],
    ascending=[True, True, False, False],
)
flex_pool["Flex_Rank"] = flex_pool.groupby(["season", "Team"]).cumcount()

# Grab the top available flex choice
flex = flex_pool[flex_pool["Flex_Rank"] == 0].copy()

# Dynamically assign volume and rename raw production columns for the wide matrix
#flex["FLEX_Volume"] = flex['standardized_volume']
flex["FLEX_Yards"] = flex["flex_yards"]
flex["FLEX_TDs"] = flex["flex_tds"]


# Get final CSV
def merge_slot_to_wide(base_df, slot_df, prefix, stats_to_keep):
    columns = ["season", "Team"] + stats_to_keep
    rename_rules = {
        col: f"{prefix}_{col}"
        for col in stats_to_keep
        if col not in ["season", "Team"]
    }
    filtered_slot = slot_df[columns].rename(columns=rename_rules)
    return pd.merge(base_df, filtered_slot, on=["season", "Team"], how="left")


# Sequentially append prefixed positions to wide matrix
final_dataset = base_features.copy()
final_dataset = merge_slot_to_wide(
    final_dataset, qbs, "QB", ["player_name", "passing_yards", "passing_tds", "TD/INT"]
)
final_dataset = merge_slot_to_wide(
    final_dataset, rbs, "RB", ["player_name", "rushing_yards", "rushing_tds", "carries"]
)
final_dataset = merge_slot_to_wide(
    final_dataset, wr1, "WR1", ["player_name", "receiving_yards", "receiving_tds", "target_share"]
)
final_dataset = merge_slot_to_wide(
    final_dataset, wr2, "WR2", ["player_name", "receiving_yards", "receiving_tds", "target_share"]
)
final_dataset = merge_slot_to_wide(
    final_dataset,
    flex,
    "FLEX",
    ["player_name", "FLEX_Yards", "FLEX_TDs", "FLEX_Volume"],
)

# Fill gaps with 0 and export
final_dataset = final_dataset.dropna(how='any', subset=final_dataset.select_dtypes(include=["object", "string"]).columns)
final_dataset.fillna(0, inplace=True)
print(final_dataset.head())
final_dataset.to_csv("Data/unnormalized_model_training_dataset.csv", index=False)