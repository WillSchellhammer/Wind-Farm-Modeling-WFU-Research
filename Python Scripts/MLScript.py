import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
from tensorflow.keras.callbacks import EarlyStopping
import matplotlib.pyplot as plt
import joblib
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# -----------------------------------------------------------------------------------------
# 1. LOAD DATA
# -----------------------------------------------------------------------------------------
X_train = np.load("X_train.npy")
X_test = np.load("X_test.npy")
y_train = np.load("y_train.npy")
y_test = np.load("y_test.npy")
scaler_y = joblib.load("scaler_y.pkl") 

# Verify shapes: (Samples, Window_Size, Features)
print(f"X_train Shape: {X_train.shape}")
print(f"y_train Shape: {y_train.shape}")

# -----------------------------------------------------------------------------------------
# 2. DEFINE & TRAIN MODEL
# -----------------------------------------------------------------------------------------
# The input_shape is (window_size, number_of_features)
# The output layer size is y_train.shape[1] (9 turbines + 1 total = 10)
model = Sequential([
    Input(shape=(X_train.shape[1], X_train.shape[2])),
    LSTM(128, return_sequences=True), # Increased capacity for multi-speed complexity
    Dropout(0.2),
    LSTM(64, return_sequences=False),
    Dropout(0.2),
    Dense(64, activation='relu'),
    Dense(y_train.shape[1])  # Predicts all 10 power values simultaneously
])

model.compile(optimizer='adam', loss='mse', metrics=['mae'])

# Monitor validation loss to prevent overfitting across the 5 wind speed profiles
early_stop = EarlyStopping(
    monitor='val_loss', 
    patience=12, 
    restore_best_weights=True,
    verbose=1
)

print("\n--- Training Model on Multi-Speed Data ---")
history = model.fit(
    X_train, y_train, 
    epochs=100, 
    batch_size=64, # Increased batch size for more stable gradients with larger data
    validation_split=0.2, 
    callbacks=[early_stop], 
    verbose=1
)

# -----------------------------------------------------------------------------------------
# 3. EVALUATION (Loss Curves)
# -----------------------------------------------------------------------------------------
plt.figure(figsize=(12, 4))
plt.subplot(1, 2, 1)
plt.plot(history.history['loss'], label='Train Loss (MSE)')
plt.plot(history.history['val_loss'], label='Val Loss (MSE)')
plt.title('Model Convergence')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()

# -----------------------------------------------------------------------------------------
# 4. PREDICTIONS & RESCALING
# -----------------------------------------------------------------------------------------
print("\n--- Running Predictions ---")
y_pred_scaled = model.predict(X_test)

# Convert from [0, 1] back to Kilowatts
y_test_rescaled = scaler_y.inverse_transform(y_test)
y_pred_rescaled = scaler_y.inverse_transform(y_pred_scaled)

# -----------------------------------------------------------------------------------------
# 5. VISUALIZING TOTAL FARM POWER
# -----------------------------------------------------------------------------------------
# Index -1 represents the very last column (Total Farm Power)
plt.subplot(1, 2, 2)
plt.plot(y_test_rescaled[:200, -1], label='Actual Total', color='black', linewidth=1.5)
plt.plot(y_pred_rescaled[:200, -1], label='Predicted Total', color='red', linestyle='--', alpha=0.8)
plt.title('Total Farm Power (Multi-Speed Test Set)')
plt.ylabel('Power (kW)')
plt.xlabel('Time Steps')
plt.legend()
plt.tight_layout()
plt.show()

# -----------------------------------------------------------------------------------------
# 6. TURBINE-SPECIFIC CHECK (Turbine 1)
# -----------------------------------------------------------------------------------------
plt.figure(figsize=(10, 4))
plt.plot(y_test_rescaled[:200, 0], label='Actual Turbine 1', color='blue')
plt.plot(y_pred_rescaled[:200, 0], label='Predicted Turbine 1', color='orange', alpha=0.8)
plt.title('Individual Turbine Prediction (Turbine 1)')
plt.ylabel('Power (kW)')
plt.xlabel('Time Steps')
plt.legend()
plt.show()

# Save the trained model
model.save("wake_steering_multi_speed_lstm.keras")
print("\n[SUCCESS] Model trained on 5 wind speeds and saved.")

# -----------------------------------------------------------------------------------------
# 7. AUTOMATED METRIC EXPORT
# -----------------------------------------------------------------------------------------

# Target the Total Farm Power (the last column: index -1)
actual_total = y_test_rescaled[:, -1]
pred_total = y_pred_rescaled[:, -1]

# Calculate Metrics
total_rmse = np.sqrt(mean_squared_error(actual_total, pred_total))
total_mae = mean_absolute_error(actual_total, pred_total)
total_r2 = r2_score(actual_total, pred_total)

# Calculate Global Average Metrics (Average across all 10 output columns)
avg_rmse_all = np.sqrt(mean_squared_error(y_test_rescaled, y_pred_rescaled))
avg_mae_all = mean_absolute_error(y_test_rescaled, y_pred_rescaled)

# Export to Text File
log_file = "model_performance_log.txt"
with open(log_file, "w") as f:
    f.write("WIND FARM MODEL EVALUATION\n")
    f.write("-" * 30 + "\n")
    f.write(f"TOTAL FARM POWER METRICS:\n")
    f.write(f"  RMSE: {total_rmse:.4f} kW\n")
    f.write(f"  MAE:  {total_mae:.4f} kW\n")
    f.write(f"  R^2:  {total_r2:.4f}\n\n")
    f.write(f"GLOBAL MULTI-OUTPUT AVERAGE:\n")
    f.write(f"  Avg RMSE: {avg_rmse_all:.4f} kW\n")
    f.write(f"  Avg MAE:  {avg_mae_all:.4f} kW\n")
    f.write("-" * 30 + "\n")

print(f"[METRICS] Performance results saved to {log_file}")