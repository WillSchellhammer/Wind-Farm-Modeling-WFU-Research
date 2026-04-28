import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

# --------------------------------------------------
# LOAD DATASET
# --------------------------------------------------

data = pd.read_csv("windfarm_dataset.csv")

# Features
X = data[["PointA","PointB","PointC","PointD","PointE","x","y"]]

# Target
y = data["turbine_power"]

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# --------------------------------------------------
# MODEL
# --------------------------------------------------

model = RandomForestRegressor(
    n_estimators=200,
    random_state=42
)

model.fit(X_train, y_train)

# --------------------------------------------------
# TEST
# --------------------------------------------------

predictions = model.predict(X_test)

error = mean_absolute_error(y_test, predictions)

print("Random Forest MAE:", error)

# --------------------------------------------------
# QUICK PREDICTION TEST
# --------------------------------------------------

example = [[7,7,7,7,7,882,0]]

print("Test prediction:", model.predict(example)[0])