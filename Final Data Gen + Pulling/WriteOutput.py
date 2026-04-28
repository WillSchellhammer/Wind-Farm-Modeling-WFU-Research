# Writes outputs from FAST.Farm and individual turbines into a .npy file formatted for Machine Learning
# Contact: Will Schellhammer, schewb24@wfu.edu
# Updated: 4/2/2026
# WORK IN PROGRESS

import pandas as pd
import numpy as np
import os
import joblib
from sklearn.preprocessing import MinMaxScaler
from sklearn.utils import shuffle

# -----------------------------------------------------------------------------------------
# Settings
numTurbines = 9
angles = [0, 45, 90, 135, 180]
speeds = [5, 8, 11, 14, 17]
window_size = 50
test_size = 0.3
burn_in_time = 120 

# -----------------------------------------------------------------------------------------
# Functions

def load_dataset(speed, angle):
    data_dir = f"{speed}_mps"
    farm_path = os.path.join(data_dir, f"FAST.Farm_{angle}.out")
    print(f"Processing: {speed} mps | Angle {angle}")

    # 1. Read Farm File Headers
    with open(farm_path, 'r') as f:
        lines = f.readlines()
        # FAST files usually have headers on line 7 (index 6)
        farm_headers = lines[6].split()

    farmDF = pd.read_csv(farm_path, sep=r'\s+', skiprows=8, header=None)
    farmDF = farmDF[farmDF[0] >= burn_in_time].reset_index(drop=True)
    farmTime = farmDF[0].values

    turbineTargets = []
    X_local_list = []
    
    for t in range(1, numTurbines + 1):
        # --- A. Pull from Farm File (Relative Wind & Yaw Error) ---
        try:
            v_rel_idx = farm_headers.index(f"RtVRelT{t}")
            yaw_err_idx = farm_headers.index(f"YawErrT{t}")
            X_local_list.append(farmDF.iloc[:, v_rel_idx].values)
            X_local_list.append(farmDF.iloc[:, yaw_err_idx].values)
        except ValueError:
            print(f"  Warning: RtVRel or YawErr not found for Turbine {t} in Farm file.")
            X_local_list.append(np.zeros_like(farmTime))
            X_local_list.append(np.zeros_like(farmTime))

        # --- B. Pull from Turbine File (Mechanical & Power) ---
        t_path = os.path.join(data_dir, f"FAST.Farm_{angle}.T{t}.out")
        
        with open(t_path, 'r') as f:
            t_lines = f.readlines()
            t_headers = t_lines[6].split()

        t_df = pd.read_csv(t_path, sep=r'\s+', skiprows=8, header=None)
        t_time = t_df[0].values

        # Variables to pull from turbine files
        # We use a dictionary to map your needs to the FAST header names
        mapping = ["RotSpeed", "BldPitch1", "Azimuth"]

        for col_name in mapping:
            if col_name in t_headers:
                idx = t_headers.index(col_name)
                val = np.interp(farmTime, t_time, t_df[idx])
                X_local_list.append(val)
            else:
                X_local_list.append(np.zeros_like(farmTime))

        # Target: GenPwr (The dynamic fix for your Index 17/14 error)
        if "GenPwr" in t_headers:
            pwr_idx = t_headers.index("GenPwr")
            pwr_synced = np.interp(farmTime, t_time, t_df[pwr_idx])
            turbineTargets.append(pwr_synced)
        else:
            raise ValueError(f"GenPwr column not found in {t_path}")

    # Final shape assembly
    X_local = np.array(X_local_list).T
    turbineTargets = np.array(turbineTargets) 
    totalFarmPower = np.sum(turbineTargets, axis=0)
    y_combined = np.vstack([turbineTargets, totalFarmPower]).T 

    return X_local, y_combined

# -----------------------------------------------------------------------------------------
# Execution
# -----------------------------------------------------------------------------------------

X_final_list = []
y_final_list = []

for s in speeds:
    for a in angles:
        try:
            X_data, y_data = load_dataset(s, a)
            X_final_list.append(X_data)
            y_final_list.append(y_data)
        except Exception as e:
            print(f"Error at {s} mps, angle {a}: {e}")

# --- Output 1: Save Raw Concatenated Data ---
X_master_raw = np.concatenate(X_final_list, axis=0)
y_master_raw = np.concatenate(y_final_list, axis=0)

np.save("X_raw_clean.npy", X_master_raw)
np.save("y_raw_clean.npy", y_master_raw)

# --- Output 2: ML Scaling and Windowing ---
scaler_x = MinMaxScaler()
scaler_y = MinMaxScaler()

X_scaled = scaler_x.fit_transform(X_master_raw)
y_scaled = scaler_y.fit_transform(y_master_raw)

X_windows, y_targets = [], []
start_point = 0

for dataset in X_final_list:
    length = len(dataset)
    x_seg = X_scaled[start_point : start_point + length]
    y_seg = y_scaled[start_point : start_point + length]
    
    for i in range(len(x_seg) - window_size):
        X_windows.append(x_seg[i : i + window_size])
        y_targets.append(y_seg[i + window_size])
    start_point += length

# Shuffle & Split
X_sh, y_sh = shuffle(np.array(X_windows), np.array(y_targets), random_state=42)
split_idx = int(len(X_sh) * (1 - test_size))

# Save for Model Training
np.save("X_train.npy", X_sh[:split_idx])
np.save("X_test.npy", X_sh[split_idx:])
np.save("y_train.npy", y_sh[:split_idx])
np.save("y_test.npy", y_sh[split_idx:])
joblib.dump(scaler_x, "scaler_x.pkl")
joblib.dump(scaler_y, "scaler_y.pkl")

print("\n" + "="*80)
print(f"SUCCESS: Processed all available speeds and angles.")
print(f"Final Data Shape: {X_sh.shape}")
print("="*80)