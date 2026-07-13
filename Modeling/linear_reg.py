import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import StandardScaler
import pickle

model_data = pd.read_csv("Data/model_training_dataset.csv")

X = model_data.drop(
    ['Win_Pct', 'season', 'Team', 'QB_player_name', 'RB_player_name', 'WR1_player_name', 'WR2_player_name', 'FLEX_player_name'], 
    axis=1)
y = model_data['Win_Pct']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25)

model = LinearRegression()

model.fit(X_train, y_train)

# scale data for Ridge
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

model_ridge = Ridge(alpha=1.0)
model_ridge.fit(X_train_scaled, y_train)

y_pred = model.predict(X_test)

mse = mean_absolute_error(y_test, y_pred)
rmse = root_mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"R2: {r2}") #.819
print(f"MSE: {mse}") #.062
print(f"RMSE: {rmse}") #.077

y_pred_ridge = model_ridge.predict(X_test_scaled)

mse = mean_absolute_error(y_test, y_pred_ridge)
rmse = root_mean_squared_error(y_test, y_pred_ridge)
r2 = r2_score(y_test, y_pred_ridge)

print(f"Ridge R2: {r2}") #.820
print(f"Ridge MSE: {mse}") #.062
print(f"Ridge RMSE: {rmse}") #.077

# save models
with open("Modeling/linear_model.pkl", "wb") as file:
    pickle.dump(model, file)

with open("Modeling/ridge_model.pkl", "wb") as file:
    pickle.dump(model_ridge, file)