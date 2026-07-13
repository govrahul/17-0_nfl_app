import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor
import pickle

model_data = pd.read_csv("Data/unnormalized_model_training_dataset.csv")
model_data["FLEX_is_RB"] = model_data["FLEX_FLEX_Volume"] >= 1.0

X = model_data.drop(
    ['Win_Pct', 'season', 'Team', 'QB_player_name', 'RB_player_name', 'WR1_player_name', 'WR2_player_name', 'FLEX_player_name'], 
    axis=1)
y = model_data['Win_Pct']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25)

model = RandomForestRegressor(
    n_estimators=100,
    max_depth=6,
    min_samples_split=5
)

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

mse = mean_absolute_error(y_test, y_pred)
rmse = root_mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"R2: {r2}") #.820
print(f"MSE: {mse}") #.065
print(f"RMSE: {rmse}") #.083

# save model
with open("Modeling/random_forest_model.pkl", "wb") as file:
    pickle.dump(model, file)