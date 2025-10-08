import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta

# ----------- Metro Station Data -----------
stations_data = [
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
stations = [s[0] for s in stations_data]

def calculate_run_time(distance, civil_speed):
    if distance == 0:
        return 0
    vmax_kmph = 38.0 if distance > 800 else 33.0
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

ml_models = {
    station: generate_dwell_model(station, peak_hours=[8,9,17,18])
    for station in stations
}

def get_ml_dwell(station, terminal_station, current_time):
    if station == terminal_station:
        return 180  # Turnaround at terminal
    minutes = current_time.hour * 60 + current_time.minute
    dwell = ml_models[station].predict(pd.DataFrame({"Minutes": [minutes]}))[0]
    return max(dwell, 15)

def simulate_train_round_trip_ml(start_station_idx, direction=1, start_time_str="05:00"):
    current_time = datetime.strptime(start_time_str, "%H:%M")
    times = []
    idx = start_station_idx
    n = len(stations)
    terminal_station = stations[0] if direction == -1 else stations[-1]
    # Forward journey
    while 0 <= idx < n:
        station = stations[idx]
        dwell = get_ml_dwell(station, terminal_station, current_time)
        arrival_time = current_time.strftime("%H:%M")
        current_time += timedelta(seconds=dwell)
        departure_time = current_time.strftime("%H:%M")
        times.append((station, arrival_time, departure_time))
        # Travel to next station
        if (direction == 1 and idx < n-1) or (direction == -1 and idx > 0):
            from_idx, to_idx = idx, idx+direction
            dist = abs(stations_data[to_idx][1])
            speed = stations_data[to_idx][3]
            current_time += timedelta(seconds=calculate_run_time(dist, speed))
        idx += direction
    # At terminal, turnaround dwell already included
    idx -= direction
    # Reverse journey
    direction = -direction
    terminal_station = stations[start_station_idx]
    idx += direction
    while 0 <= idx < n:
        station = stations[idx]
        dwell = get_ml_dwell(station, terminal_station, current_time)
        arrival_time = current_time.strftime("%H:%M")
        current_time += timedelta(seconds=dwell)
        departure_time = current_time.strftime("%H:%M")
        times.append((station, arrival_time, departure_time))
        if (direction == 1 and idx < n-1) or (direction == -1 and idx > 0):
            from_idx, to_idx = idx, idx+direction
            dist = abs(stations_data[to_idx][1])
            speed = stations_data[to_idx][3]
            current_time += timedelta(seconds=calculate_run_time(dist, speed))
        idx += direction
    return times

# ----------- Simulate 7 ML Trains (Round Trip) -----------
train1 = simulate_train_round_trip_ml(0, direction=1, start_time_str="05:00")
train2 = simulate_train_round_trip_ml(0, direction=1, start_time_str="05:05")
train3 = simulate_train_round_trip_ml(0, direction=1, start_time_str="05:10")
train4 = simulate_train_round_trip_ml(len(stations)-1, direction=-1, start_time_str="05:00") in 