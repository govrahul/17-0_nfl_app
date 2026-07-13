import numpy as np
import pickle

with open("Modeling/linear_model.pkl", "rb") as file:
    linear_model = pickle.load(file)

with open("Modeling/ridge_model.pkl", "rb") as file:
    ridge_model = pickle.load(file)

with open("Modeling/random_forest_model.pkl", "rb") as file:
    random_forest_model = pickle.load(file)

custom_X = np.array(
    [
        [
            0.8598152618158224,  # Base_Team_Strength (2007 Patriots)
            5543.0,  # QB_passing_yards (2007 Tom Brady)
            56.0,  # QB_passing_tds
            5.090909090909091,  # QB_TD/INT
            2196.0,  # RB_rushing_yards (2012 Adrian Peterson)
            12.0,  # RB_rushing_tds
            370.0,  # RB_carries
            2425.0,  # WR1_receiving_yards (2021 Cooper Kupp)
            22.0,  # WR1_receiving_tds
            0.3157181571815718,  # WR1_target_share
            1897.0,  # WR2_receiving_yards (2011 Calvin Johnson)
            18.0,  # WR2_receiving_tds
            0.2475386779184247,  # WR2_target_share
            1823.0,  # FLEX_Yards (2021 Ja'marr Chase)
            14.0,  # FLEX_TDs
            0.2411242603550296,  # FLEX_Volume
            0,
        ]
    ]
)

predictions = random_forest_model.predict(custom_X)
custom_X = custom_X[:, :-1]
linear_pred = linear_model.predict(custom_X)
print(predictions) # 14-3
print(linear_pred) # 16-1