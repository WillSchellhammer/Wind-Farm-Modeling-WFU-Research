import numpy as np
import pandas as pd
import os

# ---------------------------------------------------------
# 1. LOAD DATA
# ---------------------------------------------------------
X = np.load("X_raw_clean.npy")
y = np.load("y_raw_clean.npy")

# ---------------------------------------------------------
# 2. DEFINE MASTER HEADERS (Exact order from your script)
# ---------------------------------------------------------
per_turbine_features = ["RtVRel", "YawErr", "RotSpeed", "BldPitch", "Azimuth"]
X_headers = [f"T{t}_{feat}" for t in range(1, 10) for feat in per_turbine_features]
y_headers = [f"PwrT{t}" for t in range(1, 10)] + ["TotalFarmPwr"]

# Convert to DataFrame for easier structural inspection
df_X = pd.DataFrame(X, columns=X_headers)
df_y = pd.DataFrame(y, columns=y_headers)

# ---------------------------------------------------------
# 3. FORMATTED INTEGRITY REPORT
# ---------------------------------------------------------
print("\n" + "="*80)
print(f"{'DATASET FORMATTING & STRUCTURAL INTEGRITY':^80}")
print("="*80)

print(f"\n[ARRAY DIMENSIONS]")
print(f"Input Matrix (X):    {X.shape[0]:<7} samples  x  {X.shape[1]:<2} features")
print(f"Target Matrix (y):   {y.shape[0]:<7} samples  x  {y.shape[1]:<2} columns")

print(f"\n[COLUMN ALIGNMENT CHECK]")
print(f"{'Feature Type':<15} | {'Min Value':<12} | {'Max Value':<12} | {'Status'}")
print("-" * 80)

# Check a sample of each feature type across the farm
check_features = ["RtVRel", "YawErr", "RotSpeed", "BldPitch", "Azimuth"]
for feat in check_features:
    # Select all columns for this specific feature across all turbines
    cols = [c for c in X_headers if feat in c]
    data_min = df_X[cols].min().min()
    data_max = df_X[cols].max().max()
    
    # Simple status logic
    status = "OK" if not np.isnan(data_min) else "ERR: NaN"
    if data_min == 0 and data_max == 0:
        status = "EMPTY/ZERO"

    print(f"{feat:<15} | {data_min:<12.2f} | {data_max:<12.2f} | {status}")

print(f"\n[TARGET ALIGNMENT CHECK]")
pwr_min = df_y.iloc[:, :-1].min().min()
pwr_max = df_y.iloc[:, :-1].max().max()
print(f"{'Turbine Power':<15} | {pwr_min:<12.2f} | {pwr_max:<12.2f} | {'kW'}")
print(f"{'Total Farm Pwr':<15} | {df_y['TotalFarmPwr'].min():<12.2f} | {df_y['TotalFarmPwr'].max():<12.2f} | {'kW'}")

# ---------------------------------------------------------
# 4. DATASET SAMPLE (Row 0)
# ---------------------------------------------------------
print("\n[FIRST ROW SAMPLE - TURBINE 1]")
t1_cols = [c for c in X_headers if "T1" in c]
sample_t1 = df_X[t1_cols].iloc[0].to_dict()
for k, v in sample_t1.items():
    print(f"  {k:<15}: {v:.4f}")

print("\n" + "="*80)
print(f"{'CHECK COMPLETE':^80}")
print("="*80)