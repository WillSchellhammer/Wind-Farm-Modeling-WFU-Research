import pandas as pd
import os

# --------------------------------------------------
# TURBINE POSITIONS (3x3)
# --------------------------------------------------

turbine_positions = {
    1:(0,-630), 2:(882,-630), 3:(1764,-630),
    4:(0,0),    5:(882,0),    6:(1764,0),
    7:(0,630),  8:(882,630),  9:(1764,630)
}

dataset = []

# --------------------------------------------------
# LOOP THROUGH A FEW TEST SCENARIOS
# --------------------------------------------------

for i in range(1,4):   # ONLY 3 for quick test

    wind_file = f"Generator_Ambient/genData{i}.csv"
    power_file = f"fastfarm_outputs/wind_{i}.out"

    if not os.path.exists(wind_file) or not os.path.exists(power_file):
        print(f"Skipping {i}, missing file")
        continue

    print(f"Loading scenario {i}")

    # Load wind data
    wind_df = pd.read_csv(wind_file)

    # Load FAST output
    df = pd.read_csv(power_file, delim_whitespace=True, skiprows=8)

    power_cols = [c for c in df.columns if "GenPwr" in c]

    if len(power_cols) == 0:
        print(f"No power columns in {power_file}")
        continue

    avg_power = df[power_cols].mean()

    # Average wind over time
    wind_features = wind_df.mean()

    # Build dataset rows
    for t in range(len(avg_power)):

        x,y = turbine_positions[t+1]

        dataset.append({
            "PointA": wind_features.iloc[0],
            "PointB": wind_features.iloc[1],
            "PointC": wind_features.iloc[2],
            "PointD": wind_features.iloc[3],
            "PointE": wind_features.iloc[4],
            "x": x,
            "y": y,
            "turbine_power": avg_power.iloc[t]
        })

# --------------------------------------------------
# SAVE DATASET
# --------------------------------------------------

data = pd.DataFrame(dataset)

data.to_csv("windfarm_dataset.csv", index=False)

print("Saved dataset")
print(data.head())