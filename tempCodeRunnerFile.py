import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta

# ----------- Metro Station Data (from C++ code) -----------
stations = [
    ("GAIMUKH", 0.0, 180, 35),
    ("GOWNIWADA", 1502.229, 30, 45),
    ("KASARVADVALI", 1385.394, 30, 45),
    ("VIJAYGARDEN", 1024.036, 30, 45),
    ("DONGARI PADA", 1198.778, 30, 45),
    ("TIKUJI NI WADI", 1226.694, 30, 45),
    ("MANPADA", 758.992, 30, 45),
    ("KAPURBAWDI", 815.824, 30, 45),
    ("MAJIWADA", 1453.707, 30, 45),
    ("CADBUARY JUNCTION", 824.707, 180, 45)
]

# ----------- C++ Run Time Logic Recreated -----------
def calculate_run_time(distance, civil_speed, optimized=False):
    # Use optimized speeds if requested
    if optimized:
        vmax_kmph = 38.0 if distance > 800 else 33.0
    else:
        vmax_kmph = 35.0 if distance > 800 else 30.0
    vmax_kmph = min(vmax_kmph, civil_speed)
    vmax = vmax_kmph * 1000 / 3600
    brake_distance = 150.0
    buffer_distance = 50.0

    accelerating_distance = distance / 8.0
    accel = vmax ** 2 / (2 * accelerating_distance)
    t_accel = vmax / accel
    t_decel = np.sqrt(2 * (brake_distance + buffer_distance) / accel)

    d_cruise = distance - accelerating_distance - brake_distance
    t_cruise = d_cruise / vmax if d_cruise > 0 else 0

    if d_cruise < 0:
        d_half = max(distance - brake_distance, distance / 2.0)
        v_peak = np.sqrt(2 * accel * d_half)
        t_accel = v_peak / accel
        t_decel = np.sqrt(2 * brake_distance / accel)
        t_cruise = 0

    return t_accel + t_cruise + t_decel  # in seconds

# ----------- ML Dwell Time Model for Each Station -----------
def generate_dwell_model(station_name, peak_hours):
    times = pd.date_range("05:00", "23:59", freq="3min")
    passengers = np.where(
        times.hour.isin(peak_hours),
        np.random.poisson(45, len(times)),
        np.random.poisson(20, len(times))
    )
    dwell = 30 + (passengers * 0.6721) + np.random.randint(0, 10, len(times))
    df = pd.DataFrame({
        "Station": station_name,
        "Minutes": times.hour * 60 + times.minute,
        "Dwell_Time": dwell
    })
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(df[["Minutes"]], df["Dwell_Time"])
    return model

# ----------- Simulate Train Movement for Both Scenarios -----------
def simulate_train(start_time_str, use_ml=False):
    times = []
    current_time = datetime.strptime(start_time_str, "%H:%M")

    ml_models = {
        station[0]: generate_dwell_model(station[0], peak_hours=[8,9,17,18])
        for station in stations
    }

    for i in range(len(stations)-1):
        from_station, _, _, _ = stations[i]
        to_station, distance, base_dwell, civil_speed = stations[i+1]

        # Runtime calculation from C++
        runtime = calculate_run_time(distance, civil_speed)
        current_time += timedelta(seconds=runtime)

        dwell = ml_models[to_station].predict([[current_time.hour * 60 + current_time.minute]])[0] if use_ml else base_dwell
        dwell = max(dwell, 15)
        times.append((to_station, current_time.strftime("%H:%M")))
        current_time += timedelta(seconds=dwell)

    return times

def simulate_train_full_times(start_time_str, use_ml=False):
    times = []
    current_time = datetime.strptime(start_time_str, "%H:%M")

    ml_models = {
        station[0]: generate_dwell_model(station[0], peak_hours=[8,9,17,18])
        for station in stations
    }

    # First station: departure only
    times.append((stations[0][0], None, current_time.strftime("%H:%M")))  # (station, arrival, departure)

    for i in range(len(stations)-1):
        from_station, _, _, _ = stations[i]
        to_station, distance, base_dwell, civil_speed = stations[i+1]

        # Runtime calculation from C++ logic
        runtime = calculate_run_time(distance, civil_speed)
        current_time += timedelta(seconds=runtime)
        arrival_time = current_time.strftime("%H:%M")

        dwell = ml_models[to_station].predict([[current_time.hour * 60 + current_time.minute]])[0] if use_ml else base_dwell
        dwell = max(dwell, 15)
        current_time += timedelta(seconds=dwell)
        departure_time = current_time.strftime("%H:%M")

        times.append((to_station, arrival_time, departure_time))

    return times

def simulate_train_full_times_optimized(start_time_str, use_ml=True):
    times = []
    current_time = datetime.strptime(start_time_str, "%H:%M")

    ml_models = {
        station[0]: generate_dwell_model(station[0], peak_hours=[8,9,17,18])
        for station in stations
    }

    # First station: departure only
    times.append((stations[0][0], None, current_time.strftime("%H:%M")))

    for i in range(len(stations)-1):
        from_station, _, _, _ = stations[i]
        to_station, distance, base_dwell, civil_speed = stations[i+1]

        # Use optimized speed
        runtime = calculate_run_time(distance, civil_speed, optimized=True)
        current_time += timedelta(seconds=runtime)
        arrival_time = current_time.strftime("%H:%M")

        dwell = ml_models[to_station].predict([[current_time.hour * 60 + current_time.minute]])[0] if use_ml else base_dwell
        dwell = max(dwell, 15)
        current_time += timedelta(seconds=dwell)
        departure_time = current_time.strftime("%H:%M")

        times.append((to_station, arrival_time, departure_time))

    return times

def simulate_train_full_times_optimized_conditional(start_time_str):
    times = []
    current_time = datetime.strptime(start_time_str, "%H:%M")

    ml_models = {
        station[0]: generate_dwell_model(station[0], peak_hours=[8,9,17,18])
        for station in stations
    }

    # First station: departure only
    times.append((stations[0][0], None, current_time.strftime("%H:%M")))

    for i in range(len(stations)-1):
        from_station, _, _, _ = stations[i]
        to_station, distance, base_dwell, civil_speed = stations[i+1]

        # Predict ML dwell
        ml_dwell = ml_models[to_station].predict([[current_time.hour * 60 + current_time.minute]])[0]
        ml_dwell = max(ml_dwell, 15)

        # If ML dwell > fixed dwell, use optimized speed, else use normal speed
        if ml_dwell > base_dwell:
            runtime = calculate_run_time(distance, civil_speed, optimized=True)
        else:
            runtime = calculate_run_time(distance, civil_speed, optimized=False)

        current_time += timedelta(seconds=runtime)
        arrival_time = current_time.strftime("%H:%M")

        # Always use ML dwell for the dwell time
        current_time += timedelta(seconds=ml_dwell)
        departure_time = current_time.strftime("%H:%M")

        times.append((to_station, arrival_time, departure_time))

    return times

# ----------- Plot Control Chart -----------
def plot_control_chart(fixed_times, ml_times):
    station_names = [s[0] for s in stations[1:]]
    y = list(range(len(station_names)))

    fixed_x = [datetime.strptime(t, "%H:%M") for _, t in fixed_times]
    ml_x = [datetime.strptime(t, "%H:%M") for _, t in ml_times]

    plt.figure(figsize=(14, 6))
    plt.plot(fixed_x, y, label="Fixed Dwell Time", marker="o", color="blue")
    plt.plot(ml_x, y, label="Predicted Dwell Time", marker="o", color="red")
    plt.yticks(y, station_names)
    plt.xlabel("Time")
    plt.ylabel("Stations")
    plt.title("Control Chart (Single Train from 8:00 AM)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def plot_control_chart_full(fixed_times, ml_times):
    station_names = [s[0] for s in stations]
    y = []
    x = []

    # Fixed dwell time
    for idx, (station, arr, dep) in enumerate(fixed_times):
        if arr is not None:
            x.append(datetime.strptime(arr, "%H:%M"))
            y.append(idx)
        if dep is not None:
            x.append(datetime.strptime(dep, "%H:%M"))
            y.append(idx)

    plt.figure(figsize=(14, 6))
    plt.step(x, y, where='post', label="Fixed Dwell Time", marker="o", color="blue")

    # ML dwell time
    y_ml = []
    x_ml = []
    for idx, (station, arr, dep) in enumerate(ml_times):
        if arr is not None:
            x_ml.append(datetime.strptime(arr, "%H:%M"))
            y_ml.append(idx)
        if dep is not None:
            x_ml.append(datetime.strptime(dep, "%H:%M"))
            y_ml.append(idx)

    plt.step(x_ml, y_ml, where='post', label="Predicted Dwell Time", marker="o", color="red")

    plt.yticks(range(len(station_names)), station_names)
    plt.xlabel("Time")
    plt.ylabel("Stations")
    plt.title("Control Chart (Flat = Waiting, Slope = Running)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# ----------- Run Simulation -----------
fixed_train = simulate_train("08:00", use_ml=False)
ml_train = simulate_train("08:00", use_ml=True)
plot_control_chart(fixed_train, ml_train)

fixed_train_full = simulate_train_full_times("08:00", use_ml=False)
ml_train_full = simulate_train_full_times("08:00", use_ml=True)
plot_control_chart_full(fixed_train_full, ml_train_full)

# ----------- Run Simulation for Two Trains -----------

# First train at 08:00
fixed_train_full_1 = simulate_train_full_times("08:00", use_ml=False)
ml_train_full_1 = simulate_train_full_times("08:00", use_ml=True)

# Second train at 08:10
fixed_train_full_2 = simulate_train_full_times("08:10", use_ml=False)
ml_train_full_2 = simulate_train_full_times("08:10", use_ml=True)

# Simulate ML dwell with optimized speed for train 2 (08:10)
ml_train_full_3 = simulate_train_full_times_optimized_conditional("08:10")

def plot_multiple_trains(*train_lists, labels, colors):
    station_names = [s[0] for s in stations]
    plt.figure(figsize=(14, 6))
    for train, label, color in zip(train_lists, labels, colors):
        y = []
        x = []
        for idx, (station, arr, dep) in enumerate(train):
            if arr is not None:
                x.append(datetime.strptime(arr, "%H:%M"))
                y.append(idx)
            if dep is not None:
                x.append(datetime.strptime(dep, "%H:%M"))
                y.append(idx)
        plt.step(x, y, where='post', label=label, marker="o", color=color)
    plt.yticks(range(len(station_names)), station_names)
    plt.xlabel("Time")
    plt.ylabel("Stations")
    plt.title("Control Chart for Two Trains (Flat = Waiting, Slope = Running)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Plot both trains for fixed dwell
plot_multiple_trains(
    fixed_train_full_1, fixed_train_full_2,
    labels=["Train 1 (08:00, Fixed Dwell)", "Train 2 (08:10, Fixed Dwell)"],
    colors=["blue", "green"]
)

# Plot both trains for ML dwell
plot_multiple_trains(
    ml_train_full_1, ml_train_full_2,
    labels=["Train 1 (08:00, ML Dwell)", "Train 2 (08:10, ML Dwell)"],
    colors=["red", "orange"]
)

# Plot all four trains on the same graph
plot_multiple_trains(
    fixed_train_full_1,
    fixed_train_full_2,
    ml_train_full_1,
    ml_train_full_2,
    labels=[
        "Train 1 (08:00, Fixed Dwell)",
        "Train 2 (08:10, Fixed Dwell)",
        "Train 1 (08:00, ML Dwell)",
        "Train 2 (08:10, ML Dwell)"
    ],
    colors=["blue", "green", "red", "orange"]
)

# Plot all five trains on the same graph
plot_multiple_trains(
    fixed_train_full_1,
    fixed_train_full_2,
    ml_train_full_1,
    ml_train_full_2,
    ml_train_full_3,
    labels=[
        "Train 1 (08:00, Fixed Dwell)",
        "Train 2 (08:10, Fixed Dwell)",
        "Train 1 (08:00, ML Dwell)",
        "Train 2 (08:10, ML Dwell)",
        "Train 2 (08:10, ML Optimized_ Dwell)"
    ],
    colors=["blue", "green", "red", "orange", "purple"]
)

# ----------- (Optional) Live Feed Integration with OpenCV -----------
# You can use this section to capture live video feed (e.g., for passenger counting or platform monitoring)
# Uncomment and adapt as needed for your use case

import cv2

def process_live_feed():
    cap = cv2.VideoCapture(0)  # 0 for default camera, or provide video file path
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # --- Your processing logic here (e.g., object detection, passenger counting) ---
        # For example, display the frame:
        cv2.imshow('Live Feed', frame)
        # Exit on 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

# To use live feed processing, uncomment the following line:
process_live_feed()
